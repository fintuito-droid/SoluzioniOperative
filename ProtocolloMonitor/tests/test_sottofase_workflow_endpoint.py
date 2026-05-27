import pytest
from fastapi import HTTPException

from backend.api.routes.protocollo_monitor import get_sottofase_workflow
from backend.api.routes.protocollo_monitor import esegui_azione_workflow_sottofase
from backend.schemas.sottofase_workflow import SottofaseWorkflowAzionePayload
from backend.services.sottofase_workflow_action_service import (
    WorkflowActionValidationError,
)
from backend.services.sottofase_workflow_command_service import (
    SottofaseWorkflowBackupError,
    SottofaseWorkflowNotFoundError,
    SottofaseWorkflowWriteError,
)


class FakeSottofaseWorkflowService:
    def __init__(self, workflow=None):
        self.workflow = workflow

    def get_workflow(self, id_sottofase):
        if self.workflow is None:
            return None

        return {**self.workflow, "id_sottofase": id_sottofase}


class FakeSottofaseWorkflowCommandService:
    def __init__(self, *, raises=None):
        self.raises = raises

    def esegui_azione_workflow_sottofase(self, *, id_sottofase, payload):
        if self.raises:
            raise self.raises

        return {
            "success": True,
            "id_sottofase": id_sottofase,
            "azione": payload.azione.value,
            "workflow": {"workflow": []},
        }


def test_get_sottofase_workflow_returns_summary():
    response = get_sottofase_workflow(
        7,
        workflow_service=FakeSottofaseWorkflowService(
            workflow={
                "stepCorrente": 2,
                "workflow": [
                    {
                        "codice": "REDIGI",
                        "titolo": "Redigi",
                        "completato": True,
                        "attivo": False,
                    }
                ],
                "percentualeAvanzamento": 20,
            }
        ),
    )

    assert response["id_sottofase"] == 7
    assert response["stepCorrente"] == 2
    assert response["percentualeAvanzamento"] == 20
    assert response["workflow"][0]["codice"] == "REDIGI"


def test_get_sottofase_workflow_returns_404_when_missing():
    with pytest.raises(HTTPException) as exc_info:
        get_sottofase_workflow(
            999,
            workflow_service=FakeSottofaseWorkflowService(workflow=None),
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Sottofase non trovata"


def test_esegui_azione_workflow_sottofase_returns_success():
    response = esegui_azione_workflow_sottofase(
        7,
        payload=SottofaseWorkflowAzionePayload(azione="AVVIA_REDAZIONE"),
        command_service=FakeSottofaseWorkflowCommandService(),
    )

    assert response["success"] is True
    assert response["id_sottofase"] == 7
    assert response["azione"] == "AVVIA_REDAZIONE"


def test_esegui_azione_workflow_sottofase_returns_404_when_missing():
    with pytest.raises(HTTPException) as exc_info:
        esegui_azione_workflow_sottofase(
            999,
            payload=SottofaseWorkflowAzionePayload(azione="AVVIA_REDAZIONE"),
            command_service=FakeSottofaseWorkflowCommandService(
                raises=SottofaseWorkflowNotFoundError()
            ),
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Sottofase non trovata"


def test_esegui_azione_workflow_sottofase_returns_400_when_invalid():
    with pytest.raises(HTTPException) as exc_info:
        esegui_azione_workflow_sottofase(
            7,
            payload=SottofaseWorkflowAzionePayload(azione="AVVIA_REDAZIONE"),
            command_service=FakeSottofaseWorkflowCommandService(
                raises=WorkflowActionValidationError("Azione non valida")
            ),
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Azione non valida"


def test_esegui_azione_workflow_sottofase_returns_500_on_backup_error():
    with pytest.raises(HTTPException) as exc_info:
        esegui_azione_workflow_sottofase(
            7,
            payload=SottofaseWorkflowAzionePayload(azione="AVVIA_REDAZIONE"),
            command_service=FakeSottofaseWorkflowCommandService(
                raises=SottofaseWorkflowBackupError("backup fallito")
            ),
        )

    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "backup fallito"


def test_esegui_azione_workflow_sottofase_returns_500_on_write_error():
    with pytest.raises(HTTPException) as exc_info:
        esegui_azione_workflow_sottofase(
            7,
            payload=SottofaseWorkflowAzionePayload(azione="AVVIA_REDAZIONE"),
            command_service=FakeSottofaseWorkflowCommandService(
                raises=SottofaseWorkflowWriteError("scrittura fallita")
            ),
        )

    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "scrittura fallita"
