import pytest
from fastapi import HTTPException

from backend.api.routes.protocollo_monitor import (
    crea_sottofase_partecipante,
    get_sottofase_step_partecipanti,
    get_sottofase_partecipanti,
)
from backend.schemas.sottofase_partecipanti import SottofasePartecipantePayload
from backend.services.sottofase_partecipanti_service import (
    SottofasePartecipantiBackupError,
    SottofasePartecipantiDuplicateError,
    SottofasePartecipantiNotFoundError,
    SottofasePartecipantiValidationError,
    SottofasePartecipantiWriteError,
)


class FakePartecipantiService:
    def __init__(self, *, raises=None):
        self.raises = raises

    def list_partecipanti(self, id_sottofase):
        if self.raises:
            raise self.raises

        return []

    def list_partecipanti_by_step(self, *, id_sottofase, id_step_operativo):
        if self.raises:
            raise self.raises

        return [{"id_step_operativo": id_step_operativo}]

    def crea_partecipante(self, *, id_sottofase, payload):
        if self.raises:
            raise self.raises

        return {
            "success": True,
            "id_sottofase": id_sottofase,
            "id_partecipante": 42,
            "partecipante": {
                "id_step_operativo": payload.idStepOperativo,
                "nome_visualizzato": payload.nomeVisualizzato,
                "ruolo": payload.ruolo.value,
            },
        }


def _payload():
    return SottofasePartecipantePayload(
        nomeVisualizzato="Mario Rossi",
        email="mario.rossi@example.it",
        ruolo="REVISORE",
        statoPartecipante="ASSEGNATO",
    )


def test_get_sottofase_partecipanti_returns_empty_list():
    response = get_sottofase_partecipanti(
        7,
        partecipanti_service=FakePartecipantiService(),
    )

    assert response == []


def test_get_sottofase_partecipanti_returns_404_when_missing():
    with pytest.raises(HTTPException) as exc_info:
        get_sottofase_partecipanti(
            999,
            partecipanti_service=FakePartecipantiService(
                raises=SottofasePartecipantiNotFoundError()
            ),
        )

    assert exc_info.value.status_code == 404


def test_post_sottofase_partecipante_returns_created():
    response = crea_sottofase_partecipante(
        7,
        payload=_payload(),
        partecipanti_service=FakePartecipantiService(),
    )

    assert response["success"] is True
    assert response["id_partecipante"] == 42


def test_post_sottofase_step_partecipante_returns_created():
    payload = SottofasePartecipantePayload(
        idStepOperativo=12,
        nomeVisualizzato="Mario Rossi",
        email="mario.rossi@example.it",
        ruolo="REVISORE",
        statoPartecipante="ASSEGNATO",
    )

    response = crea_sottofase_partecipante(
        7,
        payload=payload,
        partecipanti_service=FakePartecipantiService(),
    )

    assert response["partecipante"]["id_step_operativo"] == 12


def test_get_sottofase_step_partecipanti_returns_list():
    response = get_sottofase_step_partecipanti(
        7,
        12,
        partecipanti_service=FakePartecipantiService(),
    )

    assert response == [{"id_step_operativo": 12}]


def test_get_sottofase_step_partecipanti_maps_validation_error():
    with pytest.raises(HTTPException) as exc_info:
        get_sottofase_step_partecipanti(
            7,
            999,
            partecipanti_service=FakePartecipantiService(
                raises=SottofasePartecipantiValidationError("step non valido")
            ),
        )

    assert exc_info.value.status_code == 400


@pytest.mark.parametrize(
    ("error", "status_code"),
    [
        (SottofasePartecipantiNotFoundError(), 404),
        (SottofasePartecipantiDuplicateError("duplicato"), 409),
        (SottofasePartecipantiValidationError("non valido"), 400),
        (SottofasePartecipantiBackupError("backup"), 500),
        (SottofasePartecipantiWriteError("write"), 500),
    ],
)
def test_post_sottofase_partecipante_maps_errors(error, status_code):
    with pytest.raises(HTTPException) as exc_info:
        crea_sottofase_partecipante(
            7,
            payload=_payload(),
            partecipanti_service=FakePartecipantiService(raises=error),
        )

    assert exc_info.value.status_code == status_code
