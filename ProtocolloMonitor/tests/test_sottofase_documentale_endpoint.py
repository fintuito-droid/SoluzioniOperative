import pytest
from fastapi import HTTPException

from backend.api.routes.protocollo_monitor import (
    get_sottofase_documentale,
    get_sottofase_documenti,
    get_sottofase_step_operativi,
)


class FakeSottofaseDocumentaleService:
    def __init__(self, *, sottofase=None, quadro=None):
        self.sottofase = sottofase
        self.quadro = quadro

    def get_quadro_documentale(self, id_sottofase):
        if self.quadro is None:
            return None
        return {**self.quadro, "id_sottofase": id_sottofase}

    def get_sottofase_documentale(self, id_sottofase):
        if self.sottofase is None:
            return None
        return {**self.sottofase, "id_sottofase": id_sottofase}

    def list_documenti_by_sottofase(self, id_sottofase):
        return [{"id_sottofase": id_sottofase, "id_documento_sottofase": 1}]

    def list_step_operativi_by_sottofase(self, id_sottofase):
        return [{"id_sottofase": id_sottofase, "codice_step": "REDIGI"}]


def test_get_sottofase_documentale_returns_summary():
    response = get_sottofase_documentale(
        7,
        sottofase_service=FakeSottofaseDocumentaleService(
            quadro={"step_corrente": "REDIGI"}
        ),
    )

    assert response == {"step_corrente": "REDIGI", "id_sottofase": 7}


def test_get_sottofase_documentale_returns_404_when_missing():
    with pytest.raises(HTTPException) as exc_info:
        get_sottofase_documentale(
            999,
            sottofase_service=FakeSottofaseDocumentaleService(quadro=None),
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Sottofase non trovata"


def test_get_sottofase_documenti_returns_list():
    response = get_sottofase_documenti(
        7,
        sottofase_service=FakeSottofaseDocumentaleService(
            sottofase={"step_corrente": "REDIGI"}
        ),
    )

    assert response == [{"id_sottofase": 7, "id_documento_sottofase": 1}]


def test_get_sottofase_documenti_returns_404_when_missing():
    with pytest.raises(HTTPException) as exc_info:
        get_sottofase_documenti(
            999,
            sottofase_service=FakeSottofaseDocumentaleService(sottofase=None),
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Sottofase non trovata"


def test_get_sottofase_step_operativi_returns_list():
    response = get_sottofase_step_operativi(
        7,
        sottofase_service=FakeSottofaseDocumentaleService(
            sottofase={"step_corrente": "REDIGI"}
        ),
    )

    assert response == [{"id_sottofase": 7, "codice_step": "REDIGI"}]


def test_get_sottofase_step_operativi_returns_404_when_missing():
    with pytest.raises(HTTPException) as exc_info:
        get_sottofase_step_operativi(
            999,
            sottofase_service=FakeSottofaseDocumentaleService(sottofase=None),
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Sottofase non trovata"
