"""Service per partecipanti collegati a una sottofase."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Callable

from pydantic import ValidationError

from backend.core.access_backup import AccessBackupError, create_access_backup
from backend.schemas.sottofase_partecipanti import SottofasePartecipantePayload


STEP_RUOLO_ATTESO = {
    "REVISIONA": "REVISORE",
    "FIRMA": "FIRMATARIO",
    "PROTOCOLLA": "PROTOCOLLATORE",
}


class SottofasePartecipantiNotFoundError(LookupError):
    """La sottofase richiesta non esiste."""


class SottofasePartecipantiValidationError(ValueError):
    """Payload o regola partecipante non valida."""


class SottofasePartecipantiDuplicateError(ValueError):
    """Partecipante duplicato per sottofase/email/ruolo."""


class SottofasePartecipantiBackupError(RuntimeError):
    """Backup Access non riuscito."""


class SottofasePartecipantiWriteError(RuntimeError):
    """Scrittura partecipante non riuscita."""


class SottofasePartecipantiService:
    """Coordina lettura e scrittura controllata dei partecipanti sottofase."""

    def __init__(
        self,
        *,
        partecipanti_repository: Any | None = None,
        sottofase_documentale_service: Any | None = None,
        backup_factory: Callable[[], Path] | None = None,
        now_factory: Callable[[], datetime] | None = None,
    ) -> None:
        self.partecipanti_repository = partecipanti_repository
        self.sottofase_documentale_service = sottofase_documentale_service
        self.backup_factory = backup_factory or create_access_backup
        self.now_factory = now_factory or datetime.now

    def list_partecipanti(self, id_sottofase: int) -> list[dict[str, Any]]:
        """Restituisce i partecipanti della sottofase, dopo verifica esistenza."""

        self._ensure_sottofase_exists(id_sottofase)

        if self.partecipanti_repository is None:
            return []

        list_by_sottofase = getattr(
            self.partecipanti_repository,
            "list_by_sottofase",
            None,
        )
        if list_by_sottofase is None:
            return []

        return list_by_sottofase(id_sottofase)

    def list_partecipanti_by_step(
        self,
        *,
        id_sottofase: int,
        id_step_operativo: int,
    ) -> list[dict[str, Any]]:
        """Restituisce i partecipanti collegati a uno step della sottofase."""

        self._ensure_sottofase_exists(id_sottofase)
        self._get_step_or_raise(
            id_sottofase=id_sottofase,
            id_step_operativo=id_step_operativo,
        )

        if self.partecipanti_repository is None:
            return []

        list_by_step = getattr(self.partecipanti_repository, "list_by_step", None)
        if list_by_step is None:
            return []

        return list_by_step(
            id_sottofase=id_sottofase,
            id_step_operativo=id_step_operativo,
        )

    def crea_partecipante(
        self,
        *,
        id_sottofase: int,
        payload: SottofasePartecipantePayload | dict[str, Any],
    ) -> dict[str, Any]:
        """Valida e inserisce un partecipante con backup Access preventivo."""

        self._ensure_sottofase_exists(id_sottofase)
        normalized_payload = self._normalize_payload(payload)

        if self.partecipanti_repository is None:
            raise SottofasePartecipantiWriteError(
                "Repository partecipanti non configurato."
            )

        email = normalized_payload.email
        ruolo = normalized_payload.ruolo.value
        id_step_operativo = normalized_payload.idStepOperativo

        step = None
        if id_step_operativo is not None:
            step = self._get_step_or_raise(
                id_sottofase=id_sottofase,
                id_step_operativo=id_step_operativo,
            )
            self._validate_ruolo_coerente_con_step(
                ruolo=ruolo,
                step=step,
            )

        if email and self.partecipanti_repository.exists_duplicate(
            id_sottofase=id_sottofase,
            id_step_operativo=id_step_operativo,
            email=email,
            ruolo=ruolo,
        ):
            raise SottofasePartecipantiDuplicateError(
                "Partecipante gia presente per sottofase, step, email e ruolo."
            )

        backup_path = self._create_backup_or_raise()
        now = self.now_factory()
        iniziali = normalized_payload.iniziali or self.calcola_iniziali(
            normalized_payload.nomeVisualizzato
        )

        try:
            id_partecipante = self.partecipanti_repository.inserisci_partecipante(
                id_sottofase=id_sottofase,
                id_step_operativo=id_step_operativo,
                nome_visualizzato=normalized_payload.nomeVisualizzato,
                email=email,
                ruolo=ruolo,
                stato_partecipante=normalized_payload.statoPartecipante.value,
                partecipante_obbligatorio=(
                    normalized_payload.partecipanteObbligatorio
                ),
                ordine=normalized_payload.ordine,
                colore_avatar=normalized_payload.coloreAvatar,
                iniziali=iniziali,
                note_partecipante=normalized_payload.notePartecipante,
                data_creazione=now,
            )
        except Exception as exc:
            raise SottofasePartecipantiWriteError(
                f"Inserimento partecipante sottofase non riuscito: {exc}"
            )

        created = self.partecipanti_repository.get_by_id(id_partecipante)
        return {
            "success": True,
            "id_sottofase": id_sottofase,
            "id_partecipante": id_partecipante,
            "partecipante": created
            or {
                "id_partecipante": id_partecipante,
                "id_sottofase": id_sottofase,
                "id_step_operativo": id_step_operativo,
                "nome_visualizzato": normalized_payload.nomeVisualizzato,
                "email": email,
                "ruolo": ruolo,
                "stato_partecipante": normalized_payload.statoPartecipante.value,
                "partecipante_obbligatorio": (
                    normalized_payload.partecipanteObbligatorio
                ),
                "ordine": normalized_payload.ordine,
                "colore_avatar": normalized_payload.coloreAvatar,
                "iniziali": iniziali,
                "note_partecipante": normalized_payload.notePartecipante,
            },
            "backup_creato": str(backup_path),
        }

    def verifica_e_completa_step_da_partecipanti(
        self,
        *,
        id_sottofase: int,
        id_step_operativo: int,
    ) -> dict[str, Any]:
        """Completa uno step se tutti i partecipanti obbligatori sono completati."""

        self._ensure_sottofase_exists(id_sottofase)
        step = self._get_step_or_raise(
            id_sottofase=id_sottofase,
            id_step_operativo=id_step_operativo,
        )

        stato_step = str(step.get("stato_step") or "").strip().upper()
        partecipanti = self.list_partecipanti_by_step(
            id_sottofase=id_sottofase,
            id_step_operativo=id_step_operativo,
        )
        obbligatori = [
            partecipante
            for partecipante in partecipanti
            if partecipante.get("partecipante_obbligatorio", True)
        ]
        obbligatori_completati = [
            partecipante
            for partecipante in obbligatori
            if str(partecipante.get("stato_partecipante") or "").strip().upper()
            == "COMPLETATO"
        ]
        facoltativi = [
            partecipante
            for partecipante in partecipanti
            if not partecipante.get("partecipante_obbligatorio", True)
        ]

        report = {
            "id_sottofase": id_sottofase,
            "id_step_operativo": id_step_operativo,
            "step_gia_completato": stato_step in {"COMPLETATO", "COMPLETED"},
            "partecipanti_obbligatori": len(obbligatori),
            "partecipanti_obbligatori_completati": len(obbligatori_completati),
            "partecipanti_facoltativi": len(facoltativi),
            "step_completato": False,
            "sottofase_completata": False,
            "backup_creato": None,
            "motivo": "",
        }

        if report["step_gia_completato"]:
            report["motivo"] = "Step gia completato."
            return report

        if not obbligatori:
            report["motivo"] = "Nessun partecipante obbligatorio collegato allo step."
            return report

        if len(obbligatori) != len(obbligatori_completati):
            report["motivo"] = "Partecipanti obbligatori non ancora tutti completati."
            return report

        if self.partecipanti_repository is None:
            raise SottofasePartecipantiWriteError(
                "Repository partecipanti non configurato."
            )

        backup_path = self._create_backup_or_raise()
        now = self.now_factory()

        try:
            completion_result = (
                self.partecipanti_repository.completa_step_operativo_da_partecipanti(
                    id_sottofase=id_sottofase,
                    id_step_operativo=id_step_operativo,
                    data_completamento=now,
                )
            )
        except Exception as exc:
            raise SottofasePartecipantiWriteError(
                f"Completamento automatico step non riuscito: {exc}"
            )

        report.update(completion_result)
        report["backup_creato"] = str(backup_path)
        report["motivo"] = "Step completato automaticamente."
        return report

    def completa_partecipante_step(
        self,
        *,
        id_sottofase: int,
        id_step_operativo: int,
        id_partecipante: int,
    ) -> dict[str, Any]:
        """Completa un partecipante di step e verifica il completamento step."""

        self._ensure_sottofase_exists(id_sottofase)
        try:
            step = self._get_step_or_raise(
                id_sottofase=id_sottofase,
                id_step_operativo=id_step_operativo,
            )
        except SottofasePartecipantiValidationError as exc:
            raise SottofasePartecipantiNotFoundError(str(exc))
        stato_step_iniziale = str(step.get("stato_step") or "").strip() or None

        if self.partecipanti_repository is None:
            raise SottofasePartecipantiWriteError(
                "Repository partecipanti non configurato."
            )

        partecipante = self.partecipanti_repository.get_by_id(id_partecipante)
        if not partecipante:
            raise SottofasePartecipantiNotFoundError("Partecipante non trovato.")

        if (
            self._safe_int(partecipante.get("id_sottofase")) != id_sottofase
            or self._safe_int(partecipante.get("id_step_operativo"))
            != id_step_operativo
        ):
            raise SottofasePartecipantiNotFoundError(
                "Partecipante non appartenente allo step indicato."
            )

        stato_partecipante = (
            str(partecipante.get("stato_partecipante") or "").strip().upper()
        )
        if stato_partecipante in {"COMPLETATO", "COMPLETED"}:
            raise SottofasePartecipantiValidationError(
                "Partecipante gia completato."
            )
        if stato_partecipante in {"ANNULLATO", "CANCELLED", "RESPINTO"}:
            raise SottofasePartecipantiValidationError(
                "Partecipante in stato non completabile."
            )

        completa_partecipante = getattr(
            self.partecipanti_repository,
            "completa_partecipante_step",
            None,
        )
        if completa_partecipante is None:
            raise SottofasePartecipantiWriteError(
                "Completamento partecipante non disponibile."
            )

        backup_path = self._create_backup_or_raise()
        now = self.now_factory()

        try:
            completa_partecipante(
                id_sottofase=id_sottofase,
                id_step_operativo=id_step_operativo,
                id_partecipante=id_partecipante,
                data_azione=now,
            )
        except Exception as exc:
            raise SottofasePartecipantiWriteError(
                f"Completamento partecipante non riuscito: {exc}"
            )

        updated = self.partecipanti_repository.get_by_id(id_partecipante) or {
            **partecipante,
            "stato_partecipante": "COMPLETATO",
            "data_azione": self._normalize_datetime(now),
            "data_modifica": self._normalize_datetime(now),
        }
        auto_report = self.verifica_e_completa_step_da_partecipanti(
            id_sottofase=id_sottofase,
            id_step_operativo=id_step_operativo,
        )

        return {
            "success": True,
            "id_sottofase": id_sottofase,
            "id_step_operativo": id_step_operativo,
            "id_partecipante": id_partecipante,
            "stato_partecipante": "COMPLETATO",
            "partecipante": updated,
            "stato_step": (
                "COMPLETATO"
                if auto_report.get("step_completato")
                or auto_report.get("step_gia_completato")
                else stato_step_iniziale
            ),
            "step_completato": auto_report.get("step_completato", False),
            "sottofase_completata": auto_report.get(
                "sottofase_completata",
                False,
            ),
            "backup_creato": str(backup_path),
            "auto_completamento_step": auto_report,
        }

    def _get_step_or_raise(
        self,
        *,
        id_sottofase: int,
        id_step_operativo: int,
    ) -> dict[str, Any]:
        if self.partecipanti_repository is None:
            raise SottofasePartecipantiValidationError(
                "Repository partecipanti non configurato."
            )

        get_step = getattr(
            self.partecipanti_repository,
            "get_step_operativo_by_id",
            None,
        )
        if get_step is None:
            raise SottofasePartecipantiValidationError(
                "Validazione step operativo non disponibile."
            )

        step = get_step(id_step_operativo)

        if step is None:
            raise SottofasePartecipantiValidationError(
                "Step operativo non trovato."
            )

        try:
            step_sottofase_id = int(step.get("id_sottofase"))
        except (TypeError, ValueError):
            step_sottofase_id = 0

        if step_sottofase_id != id_sottofase:
            raise SottofasePartecipantiValidationError(
                "Step operativo non appartenente alla sottofase."
            )

        return step

    @staticmethod
    def _safe_int(value: Any) -> int | None:
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _normalize_datetime(value: datetime) -> str:
        return value.isoformat(sep=" ")

    @staticmethod
    def _validate_ruolo_coerente_con_step(
        *,
        ruolo: str,
        step: dict[str, Any],
    ) -> None:
        codice_step = str(step.get("codice_step") or "").strip().upper()
        ruolo_atteso = STEP_RUOLO_ATTESO.get(codice_step)

        if ruolo_atteso is None:
            return

        if ruolo != ruolo_atteso:
            raise SottofasePartecipantiValidationError(
                f"Ruolo {ruolo} non coerente con step {codice_step}: "
                f"atteso {ruolo_atteso}."
            )

    def _ensure_sottofase_exists(self, id_sottofase: int) -> None:
        if self.sottofase_documentale_service is None:
            raise SottofasePartecipantiNotFoundError("Sottofase non trovata.")

        get_sottofase = getattr(
            self.sottofase_documentale_service,
            "get_sottofase_documentale",
            None,
        )
        if get_sottofase is None or get_sottofase(id_sottofase) is None:
            raise SottofasePartecipantiNotFoundError("Sottofase non trovata.")

    @staticmethod
    def _normalize_payload(
        payload: SottofasePartecipantePayload | dict[str, Any],
    ) -> SottofasePartecipantePayload:
        if isinstance(payload, SottofasePartecipantePayload):
            return payload

        try:
            return SottofasePartecipantePayload(**dict(payload))
        except ValidationError as exc:
            raise SottofasePartecipantiValidationError(
                _message_from_validation_error(exc)
            )
        except (TypeError, ValueError):
            raise SottofasePartecipantiValidationError(
                "Payload partecipante non valido."
            )

    def _create_backup_or_raise(self) -> Path:
        try:
            return self.backup_factory()
        except AccessBackupError as exc:
            raise SottofasePartecipantiBackupError(str(exc))
        except Exception as exc:
            raise SottofasePartecipantiBackupError(
                f"Backup Access non riuscito: {exc}"
            )

    @staticmethod
    def calcola_iniziali(nome_visualizzato: str) -> str:
        """Calcola iniziali stabili se non vengono passate dal client."""

        parts = [part for part in nome_visualizzato.strip().split() if part]
        if not parts:
            return "?"

        if len(parts) == 1:
            return parts[0][:2].upper()

        return f"{parts[0][0]}{parts[-1][0]}".upper()


def _message_from_validation_error(exc: ValidationError) -> str:
    errors = exc.errors()
    first_error = errors[0] if errors else {}
    location = tuple(first_error.get("loc", ()))
    message = str(first_error.get("msg", "Payload partecipante non valido."))

    if "nomeVisualizzato" in location:
        return "nomeVisualizzato obbligatorio."

    if "ruolo" in location:
        return "Ruolo partecipante non ammesso."

    if "statoPartecipante" in location:
        return "Stato partecipante non ammesso."

    if "email" in location:
        return message

    return "Payload partecipante non valido."
