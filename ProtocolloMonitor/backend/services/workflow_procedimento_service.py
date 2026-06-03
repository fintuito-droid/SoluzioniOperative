"""Service per fasi verticali e step orizzontali del procedimento."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from backend.core.access_backup import create_access_backup


class WorkflowFaseNotFoundError(Exception):
    """Errore applicativo per fase workflow inesistente."""


class WorkflowFaseValidationError(ValueError):
    """Payload fase non valido."""


class WorkflowConfigurazioneBloccataError(RuntimeError):
    """Cambio configurazione workflow non ammesso per step gia avviati."""


class WorkflowProcedimentoService:
    """Service applicativo per workflow procedimento semplificato."""

    def __init__(
        self,
        *,
        workflow_procedimento_repository: Any | None = None,
        now_factory: Any | None = None,
        backup_factory: Any | None = None,
    ) -> None:
        self.workflow_procedimento_repository = workflow_procedimento_repository
        self.now_factory = now_factory or datetime.now
        self.backup_factory = backup_factory or create_access_backup

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

    def inizializza_step_orizzontali_fase(
        self,
        *,
        id_procedimento: int,
        id_fase: int,
    ) -> dict[str, Any]:
        """Inizializza e restituisce gli step orizzontali fissi della fase."""

        if self.workflow_procedimento_repository is None:
            raise WorkflowFaseNotFoundError()

        fase = self.workflow_procedimento_repository.get_fase_detail(id_fase)
        if fase is None or int(fase.get("id_procedimento") or 0) != int(
            id_procedimento
        ):
            raise WorkflowFaseNotFoundError()

        return self.workflow_procedimento_repository.inizializza_step_orizzontali_fase(
            id_fase=id_fase,
            data_creazione=self.now_factory(),
        )

    def list_step_orizzontali_fase(
        self,
        *,
        id_procedimento: int,
        id_fase: int,
        inizializza: bool = True,
    ) -> list[dict[str, Any]]:
        """Restituisce gli step orizzontali della fase, inizializzandoli se richiesto."""
        if self.workflow_procedimento_repository is None:
            return []

        fase = self.workflow_procedimento_repository.get_fase_detail(id_fase)
        if fase is None or int(fase.get("id_procedimento") or 0) != int(
            id_procedimento
        ):
            raise WorkflowFaseNotFoundError()

        has_step_orizzontali = getattr(
            self.workflow_procedimento_repository,
            "has_step_orizzontali_fase",
            None,
        )
        deve_inizializzare = (
            inizializza
            and (
                has_step_orizzontali is None
                or not has_step_orizzontali(id_fase)
            )
        )

        if deve_inizializzare:
            report = self.inizializza_step_orizzontali_fase(
                id_procedimento=id_procedimento,
                id_fase=id_fase,
            )
            return report.get("step", [])

        return self.workflow_procedimento_repository.list_step_orizzontali_by_fase(
            id_fase
        )

    def configura_step_orizzontali_istanza_fine(
        self,
        *,
        id_procedimento: int,
        id_fase: int,
    ) -> list[dict[str, Any]]:
        """Converte gli step attivi della fase in `Istanza -> Fine`."""

        self._validate_fase_in_procedimento(
            id_procedimento=id_procedimento,
            id_fase=id_fase,
        )
        self._ensure_step_orizzontali_configurabili(id_fase)

        self.backup_factory()
        return self.workflow_procedimento_repository.configura_step_orizzontali_istanza_fine(
            id_fase=id_fase,
            data_modifica=self.now_factory(),
        )

    def configura_step_orizzontali_predefinito(
        self,
        *,
        id_procedimento: int,
        id_fase: int,
    ) -> list[dict[str, Any]]:
        """Converte gli step attivi della fase nel workflow standard."""

        self._validate_fase_in_procedimento(
            id_procedimento=id_procedimento,
            id_fase=id_fase,
        )
        self._ensure_step_orizzontali_configurabili(id_fase)

        self.backup_factory()
        return self.workflow_procedimento_repository.configura_step_orizzontali_predefinito(
            id_fase=id_fase,
            data_modifica=self.now_factory(),
        )

    def inserisci_step_orizzontale_dopo(
        self,
        *,
        id_procedimento: int,
        id_fase: int,
        id_step: int,
        payload: Any,
    ) -> list[dict[str, Any]]:
        """Inserisce un nuovo step subito dopo lo step selezionato."""

        self._validate_fase_in_procedimento(
            id_procedimento=id_procedimento,
            id_fase=id_fase,
        )

        data = self._payload_to_dict(payload)
        titolo_step = self._clean_required(
            data.get("titoloStep")
            or data.get("TitoloStep")
            or data.get("titolo_step")
        )
        codice_step = self._clean_optional(
            data.get("codiceStep")
            or data.get("CodiceStep")
            or data.get("codice_step")
        )
        codice_step = codice_step or self._codice_from_titolo(titolo_step)

        try:
            self.backup_factory()
            return self.workflow_procedimento_repository.inserisci_step_orizzontale_dopo(
                id_fase=id_fase,
                id_step=id_step,
                titolo_step=titolo_step,
                codice_step=codice_step,
                data_creazione=self.now_factory(),
            )
        except ValueError as exc:
            raise WorkflowFaseValidationError(str(exc)) from exc

    def elimina_logicamente_step_orizzontale(
        self,
        *,
        id_procedimento: int,
        id_fase: int,
        id_step: int,
    ) -> list[dict[str, Any]]:
        """Disattiva logicamente uno step e restituisce lo stepper aggiornato."""

        self._validate_fase_in_procedimento(
            id_procedimento=id_procedimento,
            id_fase=id_fase,
        )

        try:
            self.backup_factory()
            return self.workflow_procedimento_repository.elimina_logicamente_step_orizzontale(
                id_fase=id_fase,
                id_step=id_step,
                data_modifica=self.now_factory(),
            )
        except ValueError as exc:
            raise WorkflowFaseValidationError(str(exc)) from exc

    def collega_protocollo_step_istanza(
        self,
        *,
        id_procedimento: int,
        id_fase: int,
        id_step: int,
        payload: Any,
    ) -> list[dict[str, Any]]:
        """Collega un protocollo esistente allo step Istanza e completa lo step."""

        self._validate_fase_in_procedimento(
            id_procedimento=id_procedimento,
            id_fase=id_fase,
        )

        data = self._payload_to_dict(payload)
        id_protocollo = self._clean_required_int(
            data.get("idProtocollo")
            or data.get("IDProtocollo")
            or data.get("id_protocollo")
        )

        try:
            self.backup_factory()
            return self.workflow_procedimento_repository.collega_protocollo_step_istanza(
                id_procedimento=id_procedimento,
                id_fase=id_fase,
                id_step=id_step,
                id_protocollo=id_protocollo,
                data_modifica=self.now_factory(),
            )
        except LookupError as exc:
            raise WorkflowFaseNotFoundError(str(exc)) from exc
        except ValueError as exc:
            raise WorkflowFaseValidationError(str(exc)) from exc

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

    @staticmethod
    def _clean_required_int(value: Any) -> int:
        try:
            normalized = int(value)
        except (TypeError, ValueError) as exc:
            raise WorkflowFaseValidationError("Protocollo obbligatorio.") from exc

        if normalized <= 0:
            raise WorkflowFaseValidationError("Protocollo obbligatorio.")

        return normalized

    def _validate_fase_in_procedimento(
        self,
        *,
        id_procedimento: int,
        id_fase: int,
    ) -> dict[str, Any]:
        if self.workflow_procedimento_repository is None:
            raise WorkflowFaseNotFoundError()

        fase = self.workflow_procedimento_repository.get_fase_detail(id_fase)
        if fase is None or int(fase.get("id_procedimento") or 0) != int(
            id_procedimento
        ):
            raise WorkflowFaseNotFoundError()

        return fase

    def _ensure_step_orizzontali_configurabili(self, id_fase: int) -> None:
        has_avviati = getattr(
            self.workflow_procedimento_repository,
            "has_step_orizzontali_avviati",
            None,
        )
        if has_avviati is None:
            return

        if has_avviati(id_fase):
            raise WorkflowConfigurazioneBloccataError(
                "Workflow non riconfigurabile: esistono step gia avviati."
            )

    @staticmethod
    def _codice_from_titolo(titolo: str) -> str:
        normalized = "".join(
            char.upper() if char.isalnum() else "_"
            for char in str(titolo or "").strip()
        )
        parts = [part for part in normalized.split("_") if part]
        return "_".join(parts)[:50] or "STEP"
