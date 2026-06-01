"""Service read-only per il quadro documentale della sottofase."""

from __future__ import annotations

from typing import Any


class SottofaseDocumentaleService:
    """Service minimale per comporre dati documentali della sottofase.

    Il service non scrive dati e non apre connessioni direttamente. Delega al
    repository read-only e costruisce un riepilogo utile agli endpoint FastAPI.
    """

    def __init__(
        self,
        *,
        sottofase_documentale_repository: Any | None = None,
        sottofase_assegnazioni_service: Any | None = None,
    ) -> None:
        self.sottofase_documentale_repository = sottofase_documentale_repository
        self.sottofase_assegnazioni_service = sottofase_assegnazioni_service

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
