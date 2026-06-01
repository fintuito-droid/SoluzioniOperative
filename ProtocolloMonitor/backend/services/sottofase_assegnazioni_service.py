"""Service per assegnazioni automatiche partecipanti agli step."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Callable

from backend.core.access_backup import AccessBackupError, create_access_backup


class SottofaseAssegnazioniNotFoundError(LookupError):
    """La sottofase richiesta non esiste."""


class SottofaseAssegnazioniBackupError(RuntimeError):
    """Backup Access non riuscito."""


class SottofaseAssegnazioniWriteError(RuntimeError):
    """Scrittura assegnazioni non riuscita."""


class SottofaseAssegnazioniService:
    """Applica regole idempotenti di assegnazione partecipanti."""

    def __init__(
        self,
        *,
        assegnazioni_repository: Any | None = None,
        backup_factory: Callable[[], Path] | None = None,
        now_factory: Callable[[], datetime] | None = None,
    ) -> None:
        self.assegnazioni_repository = assegnazioni_repository
        self.backup_factory = backup_factory or create_access_backup
        self.now_factory = now_factory or datetime.now

    DEFAULT_STEP_ROLE_MAP = {
        "REDIGI": "OPERATORE",
        "REVISIONA": "REVISORE",
        "VERIFICA": "REVISORE",
        "APPROVA": "APPROVATORE",
        "FIRMA": "FIRMATARIO",
        "PROTOCOLLA": "PROTOCOLLATORE",
    }

    def popola_regole_assegnazione_default(self) -> dict[str, Any]:
        """Popola regole default usando solo step e utenti reali."""

        if self.assegnazioni_repository is None:
            raise SottofaseAssegnazioniWriteError(
                "Repository assegnazioni non configurato."
            )

        codici_step = self.assegnazioni_repository.list_codici_step_presenti()
        utenti = self.assegnazioni_repository.list_utenti_attivi()

        report = {
            "success": True,
            "codici_step_presenti": codici_step,
            "utenti_attivi": len(utenti),
            "regole_create": [],
            "regole_gia_presenti": [],
            "regole_saltate": [],
            "anomalie": [],
            "backup_creato": None,
        }

        proposte = []
        for index, codice_step in enumerate(codici_step, start=1):
            ruolo = self.DEFAULT_STEP_ROLE_MAP.get(codice_step)
            if ruolo is None:
                report["regole_saltate"].append(
                    {
                        "codice_step": codice_step,
                        "motivo": "Nessun ruolo default prudente previsto.",
                    }
                )
                continue

            utente = self._scegli_utente_default(
                utenti=utenti,
                codice_step=codice_step,
            )
            if utente is None:
                report["regole_saltate"].append(
                    {
                        "codice_step": codice_step,
                        "ruolo": ruolo,
                        "motivo": "Nessun utente attivo disponibile.",
                    }
                )
                continue

            id_utente = self._safe_int(utente.get("id_utente"))
            email = self._normalize_email(utente.get("email"))
            if self.assegnazioni_repository.exists_regola_default(
                codice_step=codice_step,
                ruolo_richiesto=ruolo,
                id_utente=id_utente,
                id_gruppo=None,
                email=email,
            ):
                report["regole_gia_presenti"].append(
                    self._default_rule_report_item(
                        codice_step=codice_step,
                        ruolo=ruolo,
                        utente=utente,
                    )
                )
                continue

            proposte.append(
                {
                    "codice_step": codice_step,
                    "ruolo": ruolo,
                    "utente": utente,
                    "priorita": index,
                }
            )

        if proposte:
            report["backup_creato"] = str(self._create_backup_or_raise())

        for proposta in proposte:
            utente = proposta["utente"]
            try:
                id_regola = self.assegnazioni_repository.inserisci_regola_default(
                    codice_step=proposta["codice_step"],
                    ruolo_richiesto=proposta["ruolo"],
                    id_utente=self._safe_int(utente.get("id_utente")),
                    id_gruppo=None,
                    nome_visualizzato=utente.get("nome_visualizzato"),
                    email=self._normalize_email(utente.get("email")),
                    obbligatorio=True,
                    priorita=proposta["priorita"],
                    data_creazione=self.now_factory(),
                )
                report["regole_create"].append(
                    {
                        **self._default_rule_report_item(
                            codice_step=proposta["codice_step"],
                            ruolo=proposta["ruolo"],
                            utente=utente,
                        ),
                        "id_regola": id_regola,
                        "obbligatorio": True,
                    }
                )
            except Exception as exc:
                report["anomalie"].append(
                    {
                        "codice_step": proposta["codice_step"],
                        "ruolo": proposta["ruolo"],
                        "motivo": str(exc),
                    }
                )

        return report

    def applica_regole_assegnazione_sottofase(
        self,
        id_sottofase: int,
    ) -> dict[str, Any]:
        """Applica regole attive alla timeline della sottofase."""

        if self.assegnazioni_repository is None:
            raise SottofaseAssegnazioniWriteError(
                "Repository assegnazioni non configurato."
            )

        context = self.assegnazioni_repository.get_sottofase_context(id_sottofase)
        if context is None:
            raise SottofaseAssegnazioniNotFoundError("Sottofase non trovata.")

        steps = self.assegnazioni_repository.list_steps_by_sottofase(id_sottofase)
        regole = self.assegnazioni_repository.list_regole_attive(
            tipo_procedimento=context.get("tipo_procedimento"),
            codice_sottofase=context.get("codice_sottofase"),
        )

        report = {
            "success": True,
            "id_sottofase": id_sottofase,
            "regole_valutate": 0,
            "partecipanti_creati": [],
            "partecipanti_gia_presenti": [],
            "regole_senza_utenti": [],
            "errori_non_bloccanti": [],
            "backup_creato": None,
        }

        creazioni = []

        for regola in regole:
            report["regole_valutate"] += 1
            matching_steps = self._matching_steps(steps, regola)

            if not matching_steps:
                report["errori_non_bloccanti"].append(
                    {
                        "id_regola": regola.get("id_regola"),
                        "motivo": "Nessuno step coerente con la regola.",
                    }
                )
                continue

            utenti = self.assegnazioni_repository.resolve_utenti_for_regola(regola)
            if not utenti:
                report["regole_senza_utenti"].append(
                    {
                        "id_regola": regola.get("id_regola"),
                        "codice_step": regola.get("codice_step"),
                        "ruolo": regola.get("ruolo_richiesto"),
                    }
                )
                continue

            for step in matching_steps:
                for utente in utenti:
                    ruolo = str(regola.get("ruolo_richiesto") or "").strip().upper()
                    email = self._normalize_email(utente.get("email"))
                    id_utente = self._safe_int(utente.get("id_utente"))

                    if self.assegnazioni_repository.exists_partecipante(
                        id_sottofase=id_sottofase,
                        id_step_operativo=int(step["id_step_operativo"]),
                        id_utente=id_utente,
                        email=email,
                        ruolo=ruolo,
                    ):
                        report["partecipanti_gia_presenti"].append(
                            self._report_item(
                                regola=regola,
                                step=step,
                                utente=utente,
                                ruolo=ruolo,
                            )
                        )
                        continue

                    creazioni.append(
                        {
                            "regola": regola,
                            "step": step,
                            "utente": {
                                **utente,
                                "email": email,
                                "id_utente": id_utente,
                            },
                            "ruolo": ruolo,
                        }
                    )

        if creazioni:
            report["backup_creato"] = str(self._create_backup_or_raise())

        for index, creazione in enumerate(creazioni, start=1):
            try:
                id_partecipante = (
                    self.assegnazioni_repository.inserisci_partecipante_assegnato(
                        id_sottofase=id_sottofase,
                        id_step_operativo=int(
                            creazione["step"]["id_step_operativo"]
                        ),
                        id_utente=creazione["utente"].get("id_utente"),
                        nome_visualizzato=(
                            creazione["utente"].get("nome_visualizzato")
                            or creazione["utente"].get("email")
                            or "Partecipante"
                        ),
                        email=creazione["utente"].get("email"),
                        ruolo=creazione["ruolo"],
                        obbligatorio=bool(
                            creazione["regola"].get("obbligatorio", True)
                        ),
                        ordine=index,
                        iniziali=self.calcola_iniziali(
                            creazione["utente"].get("nome_visualizzato")
                            or creazione["utente"].get("email")
                            or "Partecipante"
                        ),
                        data_creazione=self.now_factory(),
                    )
                )
                report["partecipanti_creati"].append(
                    {
                        **self._report_item(
                            regola=creazione["regola"],
                            step=creazione["step"],
                            utente=creazione["utente"],
                            ruolo=creazione["ruolo"],
                        ),
                        "id_partecipante": id_partecipante,
                        "obbligatorio": bool(
                            creazione["regola"].get("obbligatorio", True)
                        ),
                    }
                )
            except Exception as exc:
                report["errori_non_bloccanti"].append(
                    {
                        "id_regola": creazione["regola"].get("id_regola"),
                        "id_step_operativo": creazione["step"].get(
                            "id_step_operativo"
                        ),
                        "email": creazione["utente"].get("email"),
                        "motivo": str(exc),
                    }
                )

        return report

    @staticmethod
    def _matching_steps(
        steps: list[dict[str, Any]],
        regola: dict[str, Any],
    ) -> list[dict[str, Any]]:
        codice_step = str(regola.get("codice_step") or "").strip().upper()
        if not codice_step:
            return []

        return [
            step
            for step in steps
            if str(step.get("codice_step") or "").strip().upper() == codice_step
        ]

    @staticmethod
    def _report_item(
        *,
        regola: dict[str, Any],
        step: dict[str, Any],
        utente: dict[str, Any],
        ruolo: str,
    ) -> dict[str, Any]:
        return {
            "id_regola": regola.get("id_regola"),
            "id_step_operativo": step.get("id_step_operativo"),
            "codice_step": step.get("codice_step"),
            "id_utente": utente.get("id_utente"),
            "nome_visualizzato": utente.get("nome_visualizzato"),
            "email": utente.get("email"),
            "ruolo": ruolo,
        }

    @staticmethod
    def _safe_int(value: Any) -> int | None:
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _normalize_email(value: Any) -> str | None:
        normalized = str(value or "").strip()
        return normalized or None

    @staticmethod
    def _scegli_utente_default(
        *,
        utenti: list[dict[str, Any]],
        codice_step: str,
    ) -> dict[str, Any] | None:
        if not utenti:
            return None

        if len(utenti) == 1:
            return utenti[0]

        if codice_step in {"REVISIONA", "FIRMA", "APPROVA", "VERIFICA"}:
            return utenti[1]

        return utenti[0]

    @staticmethod
    def _default_rule_report_item(
        *,
        codice_step: str,
        ruolo: str,
        utente: dict[str, Any],
    ) -> dict[str, Any]:
        return {
            "codice_step": codice_step,
            "ruolo": ruolo,
            "id_utente": utente.get("id_utente"),
            "nome_visualizzato": utente.get("nome_visualizzato"),
            "email": utente.get("email"),
        }

    def _create_backup_or_raise(self) -> Path:
        try:
            return self.backup_factory()
        except AccessBackupError as exc:
            raise SottofaseAssegnazioniBackupError(str(exc))
        except Exception as exc:
            raise SottofaseAssegnazioniBackupError(
                f"Backup Access non riuscito: {exc}"
            )

    @staticmethod
    def calcola_iniziali(nome_visualizzato: str) -> str:
        parts = [part for part in nome_visualizzato.strip().split() if part]
        if not parts:
            return "?"

        if len(parts) == 1:
            return parts[0][:2].upper()

        return f"{parts[0][0]}{parts[-1][0]}".upper()
