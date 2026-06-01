import pytest
from fastapi import HTTPException

from backend.api.routes.protocollo_monitor import (
    ProcedimentoFasePayload,
    aggiorna_procedimento_fase,
    crea_procedimento_fase,
    get_catalogo_sottofasi,
    get_procedimento_fase_dettaglio,
    get_procedimento_fase_sottofasi,
    get_procedimento_fase_step_orizzontali,
    get_procedimento_fasi,
    inizializza_procedimento_fase_step_orizzontali,
)
from backend.services.workflow_procedimento_service import (
    WorkflowFaseNotFoundError,
    WorkflowFaseValidationError,
)


class FakeWorkflowProcedimentoService:
    def __init__(self, *, fase_detail=None, mode=None):
        self.fase_detail = fase_detail
        self.mode = mode

    def list_fasi_by_procedimento(self, id_procedimento):
        return [{"id_procedimento": id_procedimento, "id_fase": 1}]

    def get_fase_detail(self, id_fase):
        return self.fase_detail

    def list_sottofasi_by_fase(self, id_fase):
        return [{"id_fase": id_fase, "id_sottofase": 2}]

    def list_catalogo_sottofasi(self, attivo_only=True):
        return [{"codice_sottofase": "EMAIL", "attivo_only": attivo_only}]

    def crea_fase_procedimento(self, *, id_procedimento, payload):
        if self.mode == "validation":
            raise WorkflowFaseValidationError("Titolo fase obbligatorio.")
        if self.mode == "missing":
            raise WorkflowFaseNotFoundError()

        return {
            "id_procedimento": id_procedimento,
            "id_fase": 9,
            "titolo": payload.Titolo,
            "descrizione": payload.Descrizione,
        }

    def aggiorna_fase_procedimento(self, *, id_procedimento, id_fase, payload):
        if self.mode == "validation":
            raise WorkflowFaseValidationError("Titolo fase obbligatorio.")
        if self.mode == "missing":
            raise WorkflowFaseNotFoundError()

        return {
            "id_procedimento": id_procedimento,
            "id_fase": id_fase,
            "titolo": payload.Titolo,
            "descrizione": payload.Descrizione,
        }

    def list_step_orizzontali_fase(self, *, id_procedimento, id_fase):
        if self.mode == "missing":
            raise WorkflowFaseNotFoundError()
        return [
            {
                "id_procedimento": id_procedimento,
                "id_fase": id_fase,
                "codice_step": "REDIGI",
                "titolo_step": "Redigi",
                "ordine": 1,
                "stato_step": "NON_AVVIATO",
            }
        ]

    def inizializza_step_orizzontali_fase(self, *, id_procedimento, id_fase):
        if self.mode == "missing":
            raise WorkflowFaseNotFoundError()
        return {
            "id_fase": id_fase,
            "step_creati": ["REDIGI", "REVISIONA", "FIRMA", "PROTOCOLLA", "FINE"],
            "step_gia_presenti": [],
            "step": self.list_step_orizzontali_fase(
                id_procedimento=id_procedimento,
                id_fase=id_fase,
            ),
        }


def test_get_procedimento_fasi_returns_list():
    response = get_procedimento_fasi(
        10,
        workflow_service=FakeWorkflowProcedimentoService(),
    )

    assert response == [{"id_procedimento": 10, "id_fase": 1}]


def test_crea_procedimento_fase_returns_created_record():
    response = crea_procedimento_fase(
        10,
        ProcedimentoFasePayload(Titolo="Nuova fase", Descrizione="Desc"),
        workflow_service=FakeWorkflowProcedimentoService(),
    )

    assert response == {
        "id_procedimento": 10,
        "id_fase": 9,
        "titolo": "Nuova fase",
        "descrizione": "Desc",
    }


def test_crea_procedimento_fase_returns_400_without_title():
    with pytest.raises(HTTPException) as exc_info:
        crea_procedimento_fase(
            10,
            ProcedimentoFasePayload(Titolo=None),
            workflow_service=FakeWorkflowProcedimentoService(mode="validation"),
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Titolo fase obbligatorio."


def test_aggiorna_procedimento_fase_returns_updated_record():
    response = aggiorna_procedimento_fase(
        10,
        9,
        ProcedimentoFasePayload(Titolo="Titolo aggiornato"),
        workflow_service=FakeWorkflowProcedimentoService(),
    )

    assert response["id_procedimento"] == 10
    assert response["id_fase"] == 9
    assert response["titolo"] == "Titolo aggiornato"


def test_aggiorna_procedimento_fase_returns_404_when_missing():
    with pytest.raises(HTTPException) as exc_info:
        aggiorna_procedimento_fase(
            10,
            999,
            ProcedimentoFasePayload(Titolo="Titolo"),
            workflow_service=FakeWorkflowProcedimentoService(mode="missing"),
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Fase non trovata"


def test_get_procedimento_fase_dettaglio_returns_detail():
    response = get_procedimento_fase_dettaglio(
        1,
        workflow_service=FakeWorkflowProcedimentoService(
            fase_detail={"id_fase": 1}
        ),
    )

    assert response == {"id_fase": 1}


def test_get_procedimento_fase_dettaglio_returns_404_when_missing():
    with pytest.raises(HTTPException) as exc_info:
        get_procedimento_fase_dettaglio(
            999,
            workflow_service=FakeWorkflowProcedimentoService(fase_detail=None),
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Fase non trovata"


def test_get_procedimento_fase_sottofasi_returns_legacy_empty_or_list():
    response = get_procedimento_fase_sottofasi(
        1,
        workflow_service=FakeWorkflowProcedimentoService(
            fase_detail={"id_fase": 1}
        ),
    )

    assert response == [{"id_fase": 1, "id_sottofase": 2}]


def test_get_procedimento_fase_sottofasi_returns_404_when_fase_missing():
    with pytest.raises(HTTPException) as exc_info:
        get_procedimento_fase_sottofasi(
            999,
            workflow_service=FakeWorkflowProcedimentoService(fase_detail=None),
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Fase non trovata"


def test_get_step_orizzontali_returns_initialized_steps():
    response = get_procedimento_fase_step_orizzontali(
        10,
        9,
        workflow_service=FakeWorkflowProcedimentoService(),
    )

    assert response == [
        {
            "id_procedimento": 10,
            "id_fase": 9,
            "codice_step": "REDIGI",
            "titolo_step": "Redigi",
            "ordine": 1,
            "stato_step": "NON_AVVIATO",
        }
    ]


def test_get_step_orizzontali_returns_404_when_fase_missing():
    with pytest.raises(HTTPException) as exc_info:
        get_procedimento_fase_step_orizzontali(
            10,
            999,
            workflow_service=FakeWorkflowProcedimentoService(mode="missing"),
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Fase non trovata"


def test_inizializza_step_orizzontali_returns_report():
    response = inizializza_procedimento_fase_step_orizzontali(
        10,
        9,
        workflow_service=FakeWorkflowProcedimentoService(),
    )

    assert response["id_fase"] == 9
    assert response["step_creati"] == [
        "REDIGI",
        "REVISIONA",
        "FIRMA",
        "PROTOCOLLA",
        "FINE",
    ]


def test_get_catalogo_sottofasi_returns_active_catalog_by_default():
    response = get_catalogo_sottofasi(
        workflow_service=FakeWorkflowProcedimentoService(),
    )

    assert response == [{"codice_sottofase": "EMAIL", "attivo_only": True}]


def test_get_catalogo_sottofasi_can_return_all_catalog():
    response = get_catalogo_sottofasi(
        attivo_only=False,
        workflow_service=FakeWorkflowProcedimentoService(),
    )

    assert response == [{"codice_sottofase": "EMAIL", "attivo_only": False}]
