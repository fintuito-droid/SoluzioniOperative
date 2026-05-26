"""Service read-only per workflow procedimento.

Il service espone un primo contratto applicativo per leggere fasi, sottofasi e
catalogo workflow senza collegare ancora route FastAPI e senza introdurre
scritture. Tutte le query restano nel repository; il service fornisce fallback
sicuri e mantiene il backend pronto a una futura persistenza PostgreSQL.
"""

from __future__ import annotations

from typing import Any


class WorkflowFaseNotFoundError(Exception):
    """Errore applicativo per fase workflow inesistente."""


class WorkflowProcedimentoService:
    """Service minimale e read-only per il workflow dei procedimenti."""

    def __init__(
        self,
        *,
        workflow_procedimento_repository: Any | None = None,
    ) -> None:
        self.workflow_procedimento_repository = workflow_procedimento_repository

    def list_fasi_by_procedimento(
        self,
        id_procedimento: int,
    ) -> list[dict[str, Any]]:
        """Restituisce le fasi del procedimento oppure lista vuota."""

        if self.workflow_procedimento_repository is None:
            return []

        list_fasi = getattr(
            self.workflow_procedimento_repository,
            "list_fasi_by_procedimento",
            None,
        )

        if list_fasi is None:
            return []

        try:
            return list_fasi(id_procedimento)
        except Exception:
            return []

    def get_fase_detail(self, id_fase: int) -> dict[str, Any] | None:
        """Restituisce il dettaglio fase oppure `None` se non trovata."""

        if self.workflow_procedimento_repository is None:
            return None

        get_detail = getattr(
            self.workflow_procedimento_repository,
            "get_fase_detail",
            None,
        )

        if get_detail is None:
            return None

        try:
            return get_detail(id_fase)
        except Exception:
            return None

    def list_sottofasi_by_fase(self, id_fase: int) -> list[dict[str, Any]]:
        """Restituisce le sottofasi di una fase oppure lista vuota."""

        if self.workflow_procedimento_repository is None:
            return []

        list_sottofasi = getattr(
            self.workflow_procedimento_repository,
            "list_sottofasi_by_fase",
            None,
        )

        if list_sottofasi is None:
            return []

        try:
            return list_sottofasi(id_fase)
        except Exception:
            return []

    def list_catalogo_sottofasi(
        self,
        attivo_only: bool = True,
    ) -> list[dict[str, Any]]:
        """Restituisce il catalogo sottofasi oppure lista vuota."""

        if self.workflow_procedimento_repository is None:
            return []

        list_catalogo = getattr(
            self.workflow_procedimento_repository,
            "list_catalogo_sottofasi",
            None,
        )

        if list_catalogo is None:
            return []

        try:
            return list_catalogo(attivo_only=attivo_only)
        except Exception:
            return []
