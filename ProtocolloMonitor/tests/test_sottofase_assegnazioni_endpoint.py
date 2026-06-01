import pytest
from fastapi import HTTPException

from backend.api.routes.protocollo_monitor import (
    applica_regole_assegnazione_sottofase,
    popola_regole_assegnazione_default,
)
from backend.services.sottofase_assegnazioni_service import (
    SottofaseAssegnazioniBackupError,
    SottofaseAssegnazioniNotFoundError,
    SottofaseAssegnazioniWriteError,
)


class FakeAssegnazioniService:
    def __init__(self, *, raises=None):
        self.raises = raises

    def applica_regole_assegnazione_sottofase(self, id_sottofase):
        if self.raises:
            raise self.raises

        return {
            "success": True,
            "id_sottofase": id_sottofase,
            "regole_valutate": 1,
            "partecipanti_creati": [],
        }

    def popola_regole_assegnazione_default(self):
        if self.raises:
            raise self.raises

        return {
            "success": True,
            "regole_create": [],
            "regole_gia_presenti": [],
        }


def test_applica_regole_assegnazione_returns_report():
    response = applica_regole_assegnazione_sottofase(
        7,
        assegnazioni_service=FakeAssegnazioniService(),
    )

    assert response["success"] is True
    assert response["id_sottofase"] == 7


@pytest.mark.parametrize(
    ("error", "status_code"),
    [
        (SottofaseAssegnazioniNotFoundError("non trovata"), 404),
        (SottofaseAssegnazioniBackupError("backup"), 500),
        (SottofaseAssegnazioniWriteError("write"), 500),
    ],
)
def test_applica_regole_assegnazione_maps_errors(error, status_code):
    with pytest.raises(HTTPException) as exc_info:
        applica_regole_assegnazione_sottofase(
            7,
            assegnazioni_service=FakeAssegnazioniService(raises=error),
        )

    assert exc_info.value.status_code == status_code


def test_popola_regole_default_returns_report():
    response = popola_regole_assegnazione_default(
        assegnazioni_service=FakeAssegnazioniService(),
    )

    assert response["success"] is True


@pytest.mark.parametrize(
    ("error", "status_code"),
    [
        (SottofaseAssegnazioniBackupError("backup"), 500),
        (SottofaseAssegnazioniWriteError("write"), 500),
    ],
)
def test_popola_regole_default_maps_errors(error, status_code):
    with pytest.raises(HTTPException) as exc_info:
        popola_regole_assegnazione_default(
            assegnazioni_service=FakeAssegnazioniService(raises=error),
        )

    assert exc_info.value.status_code == status_code
