import pytest
from fastapi import HTTPException

from backend.api.routes.protocollo_monitor import (
    get_procedimenti,
    get_procedimento_dettaglio,
    get_procedimento_protocolli,
    get_procedimento_protocolli_count,
)


class FakeProcedimentoService:
    def __init__(self, *, detail=None):
        self.detail = detail

    def list_procedimenti(self):
        return [{"id_procedimento": 1, "titolo": "Procedimento test"}]

    def get_procedimento_detail(self, id_procedimento):
        return self.detail

    def list_protocolli_collegati(self, id_procedimento):
        return [{"id_procedimento": id_procedimento, "id_protocollo": 123}]

    def count_protocolli_collegati(self, id_procedimento):
        return 1


def test_get_procedimenti_returns_list():
    response = get_procedimenti(
        procedimento_service=FakeProcedimentoService()
    )

    assert response == [{"id_procedimento": 1, "titolo": "Procedimento test"}]


def test_get_procedimento_dettaglio_returns_detail():
    response = get_procedimento_dettaglio(
        1,
        procedimento_service=FakeProcedimentoService(
            detail={"id_procedimento": 1}
        ),
    )

    assert response == {"id_procedimento": 1}


def test_get_procedimento_dettaglio_returns_404_when_missing():
    with pytest.raises(HTTPException) as exc_info:
        get_procedimento_dettaglio(
            999,
            procedimento_service=FakeProcedimentoService(detail=None),
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Procedimento non trovato"


def test_get_procedimento_protocolli_returns_linked_protocols():
    response = get_procedimento_protocolli(
        1,
        procedimento_service=FakeProcedimentoService(
            detail={"id_procedimento": 1}
        ),
    )

    assert response == [{"id_procedimento": 1, "id_protocollo": 123}]


def test_get_procedimento_protocolli_returns_404_when_missing():
    with pytest.raises(HTTPException) as exc_info:
        get_procedimento_protocolli(
            999,
            procedimento_service=FakeProcedimentoService(detail=None),
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Procedimento non trovato"


def test_get_procedimento_protocolli_count_returns_count():
    response = get_procedimento_protocolli_count(
        1,
        procedimento_service=FakeProcedimentoService(
            detail={"id_procedimento": 1}
        ),
    )

    assert response == {
        "id_procedimento": 1,
        "protocolli_collegati": 1,
    }


def test_get_procedimento_protocolli_count_returns_404_when_missing():
    with pytest.raises(HTTPException) as exc_info:
        get_procedimento_protocolli_count(
            999,
            procedimento_service=FakeProcedimentoService(detail=None),
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Procedimento non trovato"
