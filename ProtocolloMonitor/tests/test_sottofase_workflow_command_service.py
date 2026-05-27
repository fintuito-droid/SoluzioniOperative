from datetime import datetime
from pathlib import Path

import pytest

from backend.services.sottofase_workflow_action_service import (
    WorkflowActionValidationError,
)
from backend.services.sottofase_workflow_command_service import (
    SottofaseWorkflowCommandService,
    SottofaseWorkflowNotFoundError,
    SottofaseWorkflowWriteError,
)


def make_workflow(*, active_code="REDIGI", completed_codes=None, percentuale=0):
    completed_codes = set(completed_codes or [])
    steps = [
        ("REDIGI", 1),
        ("REVISIONA", 2),
        ("FIRMA", 3),
        ("PROTOCOLLA", 4),
        ("FINE", 5),
    ]

    return {
        "stepCorrente": next(
            ordine for codice, ordine in steps if codice == active_code
        ),
        "workflow": [
            {
                "codice": codice,
                "titolo": codice.title(),
                "ordine": ordine,
                "completato": codice in completed_codes,
                "attivo": codice == active_code,
            }
            for codice, ordine in steps
        ],
        "percentualeAvanzamento": percentuale,
    }


class FakeWorkflowService:
    def __init__(self, workflows):
        self.workflows = list(workflows)

    def get_workflow(self, id_sottofase):
        if not self.workflows:
            return None

        workflow = self.workflows.pop(0)

        if workflow is None:
            return None

        return {**workflow, "id_sottofase": id_sottofase}


class FakeWorkflowActionRepository:
    def __init__(self, raises=False):
        self.raises = raises
        self.calls = []

    def applica_azione_workflow_sottofase(self, **kwargs):
        self.calls.append(kwargs)

        if self.raises:
            raise RuntimeError("errore repository")


def test_command_service_executes_valid_action_and_returns_updated_workflow():
    repository = FakeWorkflowActionRepository()
    service = SottofaseWorkflowCommandService(
        workflow_service=FakeWorkflowService(
            [
                make_workflow(active_code="REDIGI"),
                make_workflow(
                    active_code="REVISIONA",
                    completed_codes={"REDIGI"},
                    percentuale=20,
                ),
            ]
        ),
        workflow_action_repository=repository,
        backup_factory=lambda: Path(r"C:\Backup\ProtocolloMonitor_BACKUP.accdb"),
        now_factory=lambda: datetime(2026, 5, 27, 12, 0, 0),
    )

    result = service.esegui_azione_workflow_sottofase(
        id_sottofase=5,
        payload={
            "azione": "AVVIA_REDAZIONE",
            "testoOperatore": "testo",
            "utenteOperatore": "Francesco Matranga",
        },
    )

    assert result["success"] is True
    assert result["azione"] == "AVVIA_REDAZIONE"
    assert result["stepDestinazione"] == "REVISIONA"
    assert result["workflow"]["stepCorrente"] == 2
    assert result["backupCreato"] == r"C:\Backup\ProtocolloMonitor_BACKUP.accdb"
    assert repository.calls == [
        {
            "id_sottofase": 5,
            "step_corrente": "REDIGI",
            "step_destinazione": "REVISIONA",
            "ordine_step": 10,
            "testo_operatore": "testo",
            "utente_operatore": "Francesco Matranga",
            "data_azione": datetime(2026, 5, 27, 12, 0, 0),
            "chiudi_sottofase": False,
        }
    ]


def test_command_service_rejects_invalid_action_before_backup_and_write():
    repository = FakeWorkflowActionRepository()
    backup_calls = []
    service = SottofaseWorkflowCommandService(
        workflow_service=FakeWorkflowService([make_workflow(active_code="REDIGI")]),
        workflow_action_repository=repository,
        backup_factory=lambda: backup_calls.append(True),
    )

    with pytest.raises(WorkflowActionValidationError):
        service.esegui_azione_workflow_sottofase(
            id_sottofase=5,
            payload={"azione": "SEGNA_FIRMATO"},
        )

    assert backup_calls == []
    assert repository.calls == []


def test_command_service_returns_not_found_when_sottofase_missing():
    service = SottofaseWorkflowCommandService(
        workflow_service=FakeWorkflowService([None]),
        workflow_action_repository=FakeWorkflowActionRepository(),
        backup_factory=lambda: Path("backup.accdb"),
    )

    with pytest.raises(SottofaseWorkflowNotFoundError):
        service.esegui_azione_workflow_sottofase(
            id_sottofase=999,
            payload={"azione": "AVVIA_REDAZIONE"},
        )


def test_command_service_raises_write_error_when_repository_update_fails():
    service = SottofaseWorkflowCommandService(
        workflow_service=FakeWorkflowService([make_workflow(active_code="REDIGI")]),
        workflow_action_repository=FakeWorkflowActionRepository(raises=True),
        backup_factory=lambda: Path("backup.accdb"),
    )

    with pytest.raises(SottofaseWorkflowWriteError):
        service.esegui_azione_workflow_sottofase(
            id_sottofase=5,
            payload={"azione": "AVVIA_REDAZIONE"},
        )
