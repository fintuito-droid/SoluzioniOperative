import pytest
from fastapi import HTTPException

from backend.api.routes.protocollo_monitor import get_sottofase_workflow


class FakeSottofaseWorkflowService:
    def __init__(self, workflow=None):
        self.workflow = workflow

    def get_workflow(self, id_sottofase):
        if self.workflow is None:
            return None

        return {**self.workflow, "id_sottofase": id_sottofase}


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
