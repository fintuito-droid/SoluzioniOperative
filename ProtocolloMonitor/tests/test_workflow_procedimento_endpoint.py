import pytest
from fastapi import HTTPException

from backend.api.routes.protocollo_monitor import (
    get_catalogo_sottofasi,
    get_procedimento_fase_dettaglio,
    get_procedimento_fase_sottofasi,
    get_procedimento_fasi,
)


class FakeWorkflowProcedimentoService:
    def __init__(self, *, fase_detail=None):
        self.fase_detail = fase_detail

    def list_fasi_by_procedimento(self, id_procedimento):
        return [{"id_procedimento": id_procedimento, "id_fase": 1}]

    def get_fase_detail(self, id_fase):
        return self.fase_detail

    def list_sottofasi_by_fase(self, id_fase):
        return [{"id_fase": id_fase, "id_sottofase": 2}]

    def list_catalogo_sottofasi(self, attivo_only=True):
        return [{"codice_sottofase": "EMAIL", "attivo_only": attivo_only}]


def test_get_procedimento_fasi_returns_list():
    response = get_procedimento_fasi(
        10,
        workflow_service=FakeWorkflowProcedimentoService(),
    )

    assert response == [{"id_procedimento": 10, "id_fase": 1}]


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


def test_get_procedimento_fase_sottofasi_returns_list():
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
