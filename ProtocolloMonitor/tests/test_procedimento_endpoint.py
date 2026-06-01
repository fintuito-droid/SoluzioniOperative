import pytest
from fastapi import HTTPException

from backend.services.procedimento_service import (
    ProcedimentoNotFoundError,
    ProcedimentoProtocolloLinkAlreadyExistsError,
    ProtocolloNotFoundError,
)
from backend.api.routes.protocollo_monitor import (
    ProcedimentoCreatePayload,
    ProtocolloProcedimentoLinkPayload,
    collega_protocollo_a_procedimento,
    crea_procedimento,
    get_procedimenti_by_protocollo,
    get_procedimenti,
    get_procedimento_dettaglio,
    get_procedimento_protocolli,
    get_procedimento_protocolli_count,
)


class FakeProcedimentoService:
    def __init__(self, *, detail=None, mode=None):
        self.detail = detail
        self.mode = mode

    def list_procedimenti(self):
        return [{"id_procedimento": 1, "titolo": "Procedimento test"}]

    def get_procedimento_detail(self, id_procedimento):
        return self.detail

    def list_protocolli_collegati(self, id_procedimento):
        return [{"id_procedimento": id_procedimento, "id_protocollo": 123}]

    def count_protocolli_collegati(self, id_procedimento):
        return 1

    def crea_procedimento(self, payload):
        if self.mode == "validation_error":
            raise ValueError("Titolo obbligatorio.")
        return {
            "id_procedimento": 10,
            "titolo": payload.Titolo,
            "codice_procedimento": payload.CodiceProcedimento or "AUTO",
        }

    def list_procedimenti_by_protocollo_id(self, id_protocollo):
        if self.mode == "protocollo_missing":
            raise ProtocolloNotFoundError()
        return [{"id_protocollo": id_protocollo, "id_procedimento": 1}]

    def link_protocollo_to_procedimento(
        self,
        *,
        id_protocollo,
        id_procedimento,
        ruolo_protocollo,
        principale,
        note_collegamento,
    ):
        if self.mode == "protocollo_missing":
            raise ProtocolloNotFoundError()
        if self.mode == "procedimento_missing":
            raise ProcedimentoNotFoundError()
        if self.mode == "duplicate":
            raise ProcedimentoProtocolloLinkAlreadyExistsError()

        return {
            "id_protocollo": id_protocollo,
            "id_procedimento": id_procedimento,
            "ruolo_protocollo": ruolo_protocollo,
            "principale": principale,
            "note_collegamento": note_collegamento,
        }


def test_get_procedimenti_returns_list():
    response = get_procedimenti(
        procedimento_service=FakeProcedimentoService()
    )

    assert response == [{"id_procedimento": 1, "titolo": "Procedimento test"}]


def test_crea_procedimento_returns_created_record():
    response = crea_procedimento(
        ProcedimentoCreatePayload(Titolo="Nuovo procedimento"),
        procedimento_service=FakeProcedimentoService(),
    )

    assert response == {
        "id_procedimento": 10,
        "titolo": "Nuovo procedimento",
        "codice_procedimento": "AUTO",
    }


def test_crea_procedimento_returns_400_when_invalid():
    with pytest.raises(HTTPException) as exc_info:
        crea_procedimento(
            ProcedimentoCreatePayload(Titolo=None),
            procedimento_service=FakeProcedimentoService(mode="validation_error"),
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Titolo obbligatorio."


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


def test_get_procedimenti_by_protocollo_returns_links():
    response = get_procedimenti_by_protocollo(
        123,
        procedimento_service=FakeProcedimentoService(),
    )

    assert response == [{"id_protocollo": 123, "id_procedimento": 1}]


def test_get_procedimenti_by_protocollo_returns_404_when_protocollo_missing():
    with pytest.raises(HTTPException) as exc_info:
        get_procedimenti_by_protocollo(
            999,
            procedimento_service=FakeProcedimentoService(
                mode="protocollo_missing"
            ),
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Protocollo non trovato"


def test_collega_protocollo_a_procedimento_returns_created_link():
    response = collega_protocollo_a_procedimento(
        123,
        1,
        payload=ProtocolloProcedimentoLinkPayload(
            RuoloProtocollo="ORIGINE",
            Principale=True,
            NoteCollegamento="nota",
        ),
        procedimento_service=FakeProcedimentoService(),
    )

    assert response == {
        "id_protocollo": 123,
        "id_procedimento": 1,
        "ruolo_protocollo": "ORIGINE",
        "principale": True,
        "note_collegamento": "nota",
    }


def test_collega_protocollo_a_procedimento_uses_default_payload():
    response = collega_protocollo_a_procedimento(
        123,
        1,
        payload=None,
        procedimento_service=FakeProcedimentoService(),
    )

    assert response["ruolo_protocollo"] == "COLLEGATO"
    assert response["principale"] is False
    assert response["note_collegamento"] is None


def test_collega_protocollo_a_procedimento_returns_404_when_protocollo_missing():
    with pytest.raises(HTTPException) as exc_info:
        collega_protocollo_a_procedimento(
            999,
            1,
            payload=None,
            procedimento_service=FakeProcedimentoService(
                mode="protocollo_missing"
            ),
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Protocollo non trovato"


def test_collega_protocollo_a_procedimento_returns_404_when_procedimento_missing():
    with pytest.raises(HTTPException) as exc_info:
        collega_protocollo_a_procedimento(
            123,
            999,
            payload=None,
            procedimento_service=FakeProcedimentoService(
                mode="procedimento_missing"
            ),
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Procedimento non trovato"


def test_collega_protocollo_a_procedimento_returns_409_when_duplicate():
    with pytest.raises(HTTPException) as exc_info:
        collega_protocollo_a_procedimento(
            123,
            1,
            payload=None,
            procedimento_service=FakeProcedimentoService(mode="duplicate"),
        )

    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == "Protocollo gia collegato al procedimento"
