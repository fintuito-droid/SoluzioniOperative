"""Service applicativo per eseguire azioni workflow sottofase.

Il service coordina il primo flusso di scrittura controllata:

1. legge il workflow corrente tramite il service read-only;
2. valida payload e transizione con il validatore puro dello Step 30L-10;
3. crea il backup Access obbligatorio prima della scrittura;
4. esegue update sottofase e insert storico tramite repository transazionale;
5. rilegge e restituisce il workflow aggiornato.

Non modifica schema, non crea tabelle e non tocca `Python/server_protocollo.py`.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Mapping

from backend.core.access_backup import AccessBackupError, create_access_backup
from backend.schemas.sottofase_workflow import (
    SottofaseWorkflowAzione,
    SottofaseWorkflowAzionePayload,
)
from backend.services.sottofase_workflow_action_service import (
    STEP_ORDER,
    WorkflowActionValidationError,
    validate_sottofase_workflow_action,
)


class SottofaseWorkflowNotFoundError(LookupError):
    """La sottofase non ha un workflow leggibile."""


class SottofaseWorkflowBackupError(RuntimeError):
    """Il backup obbligatorio Access non e riuscito."""


class SottofaseWorkflowWriteError(RuntimeError):
    """La scrittura controllata del workflow non e riuscita."""


class SottofaseWorkflowCommandService:
    """Service per avanzare realmente una sottofase tramite azione guidata."""

    def __init__(
        self,
        *,
        workflow_service: Any | None = None,
        workflow_action_repository: Any | None = None,
        backup_factory: Callable[[], Path] | None = None,
        now_factory: Callable[[], datetime] | None = None,
    ) -> None:
        self.workflow_service = workflow_service
        self.workflow_action_repository = workflow_action_repository
        self.backup_factory = backup_factory or create_access_backup
        self.now_factory = now_factory or datetime.now

    def esegui_azione_workflow_sottofase(
        self,
        *,
        id_sottofase: int,
        payload: SottofaseWorkflowAzionePayload | Mapping[str, Any],
    ) -> dict[str, Any]:
        """Esegue una transizione workflow validata e restituisce il workflow.

        Se il backup fallisce, il metodo si ferma prima di qualsiasi scrittura.
        Se la transazione fallisce, il rollback e responsabilita del repository.
        """

        workflow_corrente = self._get_workflow_or_raise(id_sottofase)
        validazione = validate_sottofase_workflow_action(
            workflow_corrente,
            payload,
        )
        normalized_payload = self._normalize_payload(payload)
        step_corrente = self._get_active_step_code(workflow_corrente)

        if step_corrente is None:
            raise WorkflowActionValidationError(
                "Workflow corrente privo di step attivo."
            )

        if self.workflow_action_repository is None:
            raise SottofaseWorkflowWriteError(
                "Repository azioni workflow non configurato."
            )

        try:
            backup_path = self.backup_factory()
        except AccessBackupError as exc:
            raise SottofaseWorkflowBackupError(str(exc))
        except Exception as exc:
            raise SottofaseWorkflowBackupError(
                f"Backup Access non riuscito: {exc}"
            )

        data_azione = self.now_factory()

        try:
            self.workflow_action_repository.applica_azione_workflow_sottofase(
                id_sottofase=id_sottofase,
                step_corrente=step_corrente,
                step_destinazione=validazione["stepDestinazione"],
                ordine_step=self._db_order_for_step(step_corrente),
                testo_operatore=normalized_payload.testoOperatore,
                utente_operatore=normalized_payload.utenteOperatore,
                data_azione=data_azione,
                chiudi_sottofase=(
                    normalized_payload.azione
                    == SottofaseWorkflowAzione.CHIUDI_SOTTOFASE
                ),
            )
        except Exception as exc:
            raise SottofaseWorkflowWriteError(
                f"Scrittura workflow sottofase non riuscita: {exc}"
            )

        workflow_aggiornato = self._get_workflow_or_raise(id_sottofase)

        return {
            "success": True,
            "azione": validazione["azione"],
            "stepDestinazione": validazione["stepDestinazione"],
            "messaggio": validazione["messaggio"],
            "workflow": workflow_aggiornato,
            "backupCreato": str(backup_path),
        }

    def _get_workflow_or_raise(self, id_sottofase: int) -> dict[str, Any]:
        """Legge il workflow o solleva errore controllato 404-oriented."""

        if self.workflow_service is None:
            raise SottofaseWorkflowNotFoundError("Workflow non configurato.")

        get_workflow = getattr(self.workflow_service, "get_workflow", None)

        if get_workflow is None:
            raise SottofaseWorkflowNotFoundError("Workflow non configurato.")

        workflow = get_workflow(id_sottofase)

        if workflow is None:
            raise SottofaseWorkflowNotFoundError("Sottofase non trovata.")

        return workflow

    @staticmethod
    def _normalize_payload(
        payload: SottofaseWorkflowAzionePayload | Mapping[str, Any],
    ) -> SottofaseWorkflowAzionePayload:
        """Riusa il modello Pydantic dopo la validazione applicativa."""

        if isinstance(payload, SottofaseWorkflowAzionePayload):
            return payload

        return SottofaseWorkflowAzionePayload(**dict(payload))

    @staticmethod
    def _get_active_step_code(workflow: Mapping[str, Any]) -> str | None:
        """Ricava il codice dello step attivo dalla risposta read-only."""

        for step in workflow.get("workflow") or []:
            if step.get("attivo"):
                return step.get("codice")

        return None

    @staticmethod
    def _db_order_for_step(step_code: str) -> int:
        """Converte ordine logico 1..5 in ordine storico Access 10..50."""

        return STEP_ORDER.get(step_code, 0) * 10
