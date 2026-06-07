"""Service per il quadro documentale e agganci controllati della sottofase."""

from __future__ import annotations

from datetime import datetime
from typing import Any


class SottofaseStepAssociazioneError(Exception):
    """Errore base per l'associazione sottofase-step."""


class SottofaseStepNotFoundError(SottofaseStepAssociazioneError):
    """Lo step orizzontale richiesto non esiste."""


class SottofaseAssociazioneNotFoundError(SottofaseStepAssociazioneError):
    """La sottofase richiesta non esiste."""


class SottofaseStepFaseMismatchError(SottofaseStepAssociazioneError):
    """Step e sottofase non appartengono alla fase richiesta."""


class SottofaseStepAlreadyLinkedError(SottofaseStepAssociazioneError):
    """Lo step ha gia una sottofase attiva collegata."""


class SottofaseAlreadyLinkedError(SottofaseStepAssociazioneError):
    """La sottofase e gia collegata a un altro step."""


class SottofaseNotAssociableError(SottofaseStepAssociazioneError):
    """La sottofase non puo essere associata."""


class SottofaseStepAssociazioneWriteError(SottofaseStepAssociazioneError):
    """La scrittura di associazione non e riuscita."""


class SottofaseDocumentaleService:
    """Service per comporre dati documentali e associare sottofasi a step."""

    def __init__(
        self,
        *,
        sottofase_documentale_repository: Any | None = None,
        sottofase_assegnazioni_service: Any | None = None,
        now_factory: Any | None = None,
    ) -> None:
        self.sottofase_documentale_repository = sottofase_documentale_repository
        self.sottofase_assegnazioni_service = sottofase_assegnazioni_service
        self.now_factory = now_factory or datetime.now

    def get_sottofase_documentale(
        self,
        id_sottofase: int,
    ) -> dict[str, Any] | None:
        """Restituisce la sottofase documentale oppure `None`."""

        if self.sottofase_documentale_repository is None:
            return None

        get_sottofase = getattr(
            self.sottofase_documentale_repository,
            "get_sottofase_documentale",
            None,
        )

        if get_sottofase is None:
            return None

        try:
            return get_sottofase(id_sottofase)
        except Exception:
            return None

    def list_documenti_by_sottofase(
        self,
        id_sottofase: int,
    ) -> list[dict[str, Any]]:
        """Restituisce i documenti collegati oppure lista vuota."""

        if self.sottofase_documentale_repository is None:
            return []

        list_documenti = getattr(
            self.sottofase_documentale_repository,
            "list_documenti_by_sottofase",
            None,
        )

        if list_documenti is None:
            return []

        try:
            return list_documenti(id_sottofase)
        except Exception:
            return []

    def list_step_operativi_by_sottofase(
        self,
        id_sottofase: int,
    ) -> list[dict[str, Any]]:
        """Restituisce gli step operativi oppure lista vuota."""

        if self.sottofase_documentale_repository is None:
            return []

        list_step = getattr(
            self.sottofase_documentale_repository,
            "list_step_operativi_by_sottofase",
            None,
        )

        if list_step is None:
            return []

        try:
            return list_step(id_sottofase)
        except Exception:
            return []

    def get_documento_corrente(
        self,
        sottofase: dict[str, Any],
    ) -> dict[str, Any] | None:
        """Restituisce il documento corrente indicato dalla sottofase."""

        if self.sottofase_documentale_repository is None:
            return None

        id_documento_corrente = sottofase.get("id_documento_corrente")

        if not id_documento_corrente:
            return None

        get_documento = getattr(
            self.sottofase_documentale_repository,
            "get_documento_by_id",
            None,
        )

        if get_documento is None:
            return None

        try:
            return get_documento(id_documento_corrente)
        except Exception:
            return None

    def get_documento_by_id(
        self,
        id_documento_sottofase: int,
    ) -> dict[str, Any] | None:
        """Restituisce un documento collegato alla sottofase per ID.

        Il metodo resta read-only: delega al repository e non modifica file,
        database o stato applicativo.
        """

        if self.sottofase_documentale_repository is None:
            return None

        get_documento = getattr(
            self.sottofase_documentale_repository,
            "get_documento_by_id",
            None,
        )

        if get_documento is None:
            return None

        try:
            return get_documento(id_documento_sottofase)
        except Exception:
            return None

    def get_quadro_documentale(
        self,
        id_sottofase: int,
    ) -> dict[str, Any] | None:
        """Compone il quadro riepilogativo documentale della sottofase."""

        sottofase = self.get_sottofase_documentale(id_sottofase)

        if sottofase is None:
            return None

        assegnazioni_auto_report = self._applica_assegnazioni_auto(id_sottofase)

        return {
            **sottofase,
            "documento_corrente": self.get_documento_corrente(sottofase),
            "step_operativi": self.list_step_operativi_by_sottofase(id_sottofase),
            "documenti": self.list_documenti_by_sottofase(id_sottofase),
            "assegnazioni_auto_report": assegnazioni_auto_report,
        }

    def associa_sottofase_a_step_orizzontale(
        self,
        *,
        id_fase: int,
        id_step_orizzontale: int,
        id_sottofase: int,
        utente: str | None = None,
    ) -> dict[str, Any]:
        """Associa una sottofase esistente a uno step orizzontale."""

        repository = self.sottofase_documentale_repository
        if repository is None:
            raise SottofaseStepAssociazioneWriteError(
                "Repository sottofase documentale non configurato."
            )

        step = repository.get_step_orizzontale_context(id_step_orizzontale)
        if step is None:
            raise SottofaseStepNotFoundError("Step orizzontale non trovato.")

        sottofase = repository.get_sottofase_aggancio_context(id_sottofase)
        if sottofase is None:
            raise SottofaseAssociazioneNotFoundError("Sottofase non trovata.")

        step_id_fase = self._safe_int(step.get("id_fase"))
        sottofase_id_fase = self._safe_int(sottofase.get("id_fase"))
        expected_id_fase = self._safe_int(id_fase)

        if step_id_fase != expected_id_fase:
            raise SottofaseStepFaseMismatchError(
                "Lo step appartiene a una fase diversa."
            )

        if sottofase_id_fase != expected_id_fase:
            raise SottofaseStepFaseMismatchError(
                "La sottofase appartiene a una fase diversa."
            )

        if not bool(sottofase.get("attivo")):
            raise SottofaseNotAssociableError("La sottofase e inattiva.")

        stato_sottofase = str(sottofase.get("stato_sottofase") or "").upper()
        if stato_sottofase in {"ANNULLATA", "ARCHIVIATA"}:
            raise SottofaseNotAssociableError(
                "La sottofase annullata o archiviata non puo essere associata."
            )

        current_step = self._safe_int(sottofase.get("id_step_orizzontale"))
        if current_step and current_step != self._safe_int(id_step_orizzontale):
            raise SottofaseAlreadyLinkedError(
                "La sottofase e gia collegata a un altro step."
            )

        active_sottofase = repository.get_sottofase_attiva_by_step(
            id_step_orizzontale
        )
        if active_sottofase is not None and self._safe_int(
            active_sottofase.get("id_sottofase")
        ) != self._safe_int(id_sottofase):
            raise SottofaseStepAlreadyLinkedError(
                "Lo step ha gia un'altra sottofase attiva collegata."
            )

        utente_aggancio = (utente or "system").strip() or "system"

        try:
            result = repository.associa_sottofase_a_step(
                id_sottofase=id_sottofase,
                id_step_orizzontale=id_step_orizzontale,
                data_aggancio=self.now_factory(),
                utente_aggancio=utente_aggancio,
            )
        except Exception as exc:
            raise SottofaseStepAssociazioneWriteError(
                f"Associazione sottofase-step non riuscita: {exc}"
            ) from exc

        return {
            **result,
            "id_fase": id_fase,
        }

    def list_sottofasi_disponibili_per_step(
        self,
        *,
        id_fase: int,
        id_step_orizzontale: int,
    ) -> dict[str, Any]:
        """Restituisce sottofasi candidate all'associazione manuale."""

        repository = self.sottofase_documentale_repository
        if repository is None:
            raise SottofaseStepAssociazioneWriteError(
                "Repository sottofase documentale non configurato."
            )

        step = repository.get_step_orizzontale_context(id_step_orizzontale)
        if step is None:
            raise SottofaseStepNotFoundError("Step orizzontale non trovato.")

        expected_id_fase = self._safe_int(id_fase)
        if self._safe_int(step.get("id_fase")) != expected_id_fase:
            raise SottofaseStepFaseMismatchError(
                "Lo step appartiene a una fase diversa."
            )

        try:
            items = repository.list_sottofasi_disponibili_per_step(
                id_fase=id_fase,
                id_step_orizzontale=id_step_orizzontale,
            )
        except Exception as exc:
            raise SottofaseStepAssociazioneWriteError(
                f"Lettura sottofasi disponibili non riuscita: {exc}"
            ) from exc

        return {
            "id_fase": id_fase,
            "id_step_orizzontale": id_step_orizzontale,
            "items": items,
        }

    def _applica_assegnazioni_auto(self, id_sottofase: int) -> dict[str, Any] | None:
        """Applica regole automatiche senza bloccare il caricamento."""

        if self.sottofase_assegnazioni_service is None:
            return None

        applica_regole = getattr(
            self.sottofase_assegnazioni_service,
            "applica_regole_assegnazione_sottofase",
            None,
        )
        if applica_regole is None:
            return None

        try:
            return applica_regole(id_sottofase)
        except Exception as exc:
            return {
                "success": False,
                "id_sottofase": id_sottofase,
                "errore": str(exc),
                "non_bloccante": True,
            }

    @staticmethod
    def _safe_int(value: Any) -> int:
        try:
            return int(value)
        except (TypeError, ValueError):
            return 0
