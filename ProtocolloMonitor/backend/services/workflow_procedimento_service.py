"""Service read-only per workflow procedimento.

Il service espone un primo contratto applicativo per leggere fasi, sottofasi e
catalogo workflow senza collegare ancora route FastAPI e senza introdurre
scritture. Tutte le query restano nel repository; il service fornisce fallback
sicuri e mantiene il backend pronto a una futura persistenza PostgreSQL.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any


class WorkflowFaseNotFoundError(Exception):
    """Errore applicativo per fase workflow inesistente."""


class WorkflowFaseValidationError(ValueError):
    """Payload fase non valido."""


class WorkflowSottofaseNotFoundError(Exception):
    """Errore applicativo per sottofase workflow inesistente."""


class WorkflowSottofaseValidationError(ValueError):
    """Payload sottofase non valido."""


class WorkflowProcedimentoService:
    """Service minimale e read-only per il workflow dei procedimenti."""

    def __init__(
        self,
        *,
        workflow_procedimento_repository: Any | None = None,
        now_factory: Any | None = None,
    ) -> None:
        self.workflow_procedimento_repository = workflow_procedimento_repository
        self.now_factory = now_factory or datetime.now

    def crea_fase_procedimento(
        self,
        *,
        id_procedimento: int,
        payload: Any,
    ) -> dict[str, Any]:
        """Crea una fase verticale del procedimento."""

        if self.workflow_procedimento_repository is None:
            raise WorkflowFaseNotFoundError()

        if not self.workflow_procedimento_repository.procedimento_exists(
            id_procedimento
        ):
            raise WorkflowFaseNotFoundError()

        data = self._payload_to_dict(payload)
        titolo = self._clean_required(data.get("Titolo"))
        descrizione = self._clean_optional(data.get("Descrizione"))
        now = self.now_factory()

        return self.workflow_procedimento_repository.crea_fase_procedimento(
            id_procedimento=id_procedimento,
            titolo=titolo,
            descrizione=descrizione,
            data_creazione=now,
        )

    def aggiorna_fase_procedimento(
        self,
        *,
        id_procedimento: int,
        id_fase: int,
        payload: Any,
    ) -> dict[str, Any]:
        """Aggiorna i campi editabili di una fase verticale."""

        if self.workflow_procedimento_repository is None:
            raise WorkflowFaseNotFoundError()

        fase = self.workflow_procedimento_repository.get_fase_detail(id_fase)
        if fase is None:
            raise WorkflowFaseNotFoundError()

        if int(fase.get("id_procedimento") or 0) != int(id_procedimento):
            raise WorkflowFaseNotFoundError()

        data = self._payload_to_dict(payload)
        titolo = self._clean_required(data.get("Titolo"))
        descrizione = self._clean_optional(data.get("Descrizione"))

        updated = self.workflow_procedimento_repository.aggiorna_fase_procedimento(
            id_procedimento=id_procedimento,
            id_fase=id_fase,
            titolo=titolo,
            descrizione=descrizione,
            data_modifica=self.now_factory(),
        )
        if updated is None:
            raise WorkflowFaseNotFoundError()

        return updated

    def crea_sottofase_fase(
        self,
        *,
        id_procedimento: int,
        id_fase: int,
        payload: Any,
    ) -> dict[str, Any]:
        """Crea una sottofase dentro una fase del procedimento."""

        if self.workflow_procedimento_repository is None:
            raise WorkflowSottofaseNotFoundError()

        fase = self.workflow_procedimento_repository.get_fase_detail(id_fase)
        if fase is None or int(fase.get("id_procedimento") or 0) != int(
            id_procedimento
        ):
            raise WorkflowSottofaseNotFoundError()

        data = self._payload_to_dict(payload)
        titolo = self._clean_required_sottofase(data.get("Titolo"))
        descrizione = self._clean_optional(data.get("Descrizione"))
        codice = self._clean_optional(data.get("CodiceSottofase"))
        now = self.now_factory()
        if codice is None:
            codice = now.strftime("SF-%Y%m%d-%H%M%S")

        return self.workflow_procedimento_repository.crea_sottofase_fase(
            id_fase=id_fase,
            codice_sottofase=codice,
            titolo=titolo,
            descrizione=descrizione,
            responsabile=self._clean_optional(data.get("Responsabile")),
            data_scadenza=self._clean_datetime(data.get("DataScadenza")),
            data_creazione=now,
        )

    def aggiorna_sottofase_fase(
        self,
        *,
        id_procedimento: int,
        id_fase: int,
        id_sottofase: int,
        payload: Any,
    ) -> dict[str, Any]:
        """Aggiorna i campi editabili di una sottofase."""

        if self.workflow_procedimento_repository is None:
            raise WorkflowSottofaseNotFoundError()

        fase = self.workflow_procedimento_repository.get_fase_detail(id_fase)
        if fase is None or int(fase.get("id_procedimento") or 0) != int(
            id_procedimento
        ):
            raise WorkflowSottofaseNotFoundError()

        sottofase = self.workflow_procedimento_repository.get_sottofase_detail(
            id_sottofase
        )
        if sottofase is None or int(sottofase.get("id_fase") or 0) != int(id_fase):
            raise WorkflowSottofaseNotFoundError()

        data = self._payload_to_dict(payload)
        titolo = self._clean_required_sottofase(data.get("Titolo"))

        updated = self.workflow_procedimento_repository.aggiorna_sottofase_fase(
            id_fase=id_fase,
            id_sottofase=id_sottofase,
            codice_sottofase=self._clean_optional(data.get("CodiceSottofase")),
            titolo=titolo,
            descrizione=self._clean_optional(data.get("Descrizione")),
            responsabile=self._clean_optional(data.get("Responsabile")),
            data_scadenza=self._clean_datetime(data.get("DataScadenza")),
            data_modifica=self.now_factory(),
        )
        if updated is None:
            raise WorkflowSottofaseNotFoundError()

        return updated

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

    @staticmethod
    def _payload_to_dict(payload: Any) -> dict[str, Any]:
        if payload is None:
            return {}
        if isinstance(payload, dict):
            return payload

        model_dump = getattr(payload, "model_dump", None)
        if model_dump is not None:
            return model_dump()

        dict_method = getattr(payload, "dict", None)
        if dict_method is not None:
            return dict_method()

        return {}

    @staticmethod
    def _clean_optional(value: Any) -> str | None:
        if value is None:
            return None
        normalized = str(value).strip()
        return normalized or None

    @classmethod
    def _clean_required(cls, value: Any) -> str:
        normalized = cls._clean_optional(value)
        if normalized is None:
            raise WorkflowFaseValidationError("Titolo fase obbligatorio.")
        return normalized

    @classmethod
    def _clean_required_sottofase(cls, value: Any) -> str:
        normalized = cls._clean_optional(value)
        if normalized is None:
            raise WorkflowSottofaseValidationError("Titolo sottofase obbligatorio.")
        return normalized

    @staticmethod
    def _clean_datetime(value: Any) -> Any:
        normalized = WorkflowProcedimentoService._clean_optional(value)
        if not isinstance(normalized, str):
            return normalized

        try:
            return datetime.fromisoformat(normalized)
        except ValueError:
            return normalized
