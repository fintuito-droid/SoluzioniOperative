import pytest
from fastapi import HTTPException

from backend.api.routes.protocollo_monitor import (
    apri_sottofase_documento,
    get_sottofase_documentale,
    get_sottofase_documenti,
    get_sottofase_step_operativi,
)


class FakeSottofaseDocumentaleService:
    def __init__(self, *, sottofase=None, quadro=None, documento=None):
        self.sottofase = sottofase
        self.quadro = quadro
        self.documento = documento

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

    def get_documento_by_id(self, id_documento):
        if self.documento is None:
            return None
        return {**self.documento, "id_documento_sottofase": id_documento}


class FailingSottofaseDocumentaleService:
    def get_documento_by_id(self, id_documento):
        raise RuntimeError("errore test")


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


def test_apri_sottofase_documento_returns_file_response(tmp_path):
    document_path = tmp_path / "bozza.docx"
    document_path.write_bytes(b"documento")

    response = apri_sottofase_documento(
        10,
        sottofase_service=FakeSottofaseDocumentaleService(
            documento={
                "percorso_documento": str(document_path),
                "mime_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            }
        ),
    )

    assert response.path == str(document_path.resolve())
    assert (
        response.media_type
        == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )


def test_apri_sottofase_documento_returns_404_when_document_missing():
    with pytest.raises(HTTPException) as exc_info:
        apri_sottofase_documento(
            999,
            sottofase_service=FakeSottofaseDocumentaleService(documento=None),
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Documento non trovato"


def test_apri_sottofase_documento_returns_404_when_path_empty():
    with pytest.raises(HTTPException) as exc_info:
        apri_sottofase_documento(
            10,
            sottofase_service=FakeSottofaseDocumentaleService(
                documento={"percorso_documento": ""}
            ),
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Documento non disponibile"


def test_apri_sottofase_documento_returns_404_when_file_missing(tmp_path):
    missing_path = tmp_path / "missing.docx"

    with pytest.raises(HTTPException) as exc_info:
        apri_sottofase_documento(
            10,
            sottofase_service=FakeSottofaseDocumentaleService(
                documento={"percorso_documento": str(missing_path)}
            ),
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "File documento non trovato"


def test_apri_sottofase_documento_returns_500_on_unexpected_error():
    with pytest.raises(HTTPException) as exc_info:
        apri_sottofase_documento(
            10,
            sottofase_service=FailingSottofaseDocumentaleService(),
        )

    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "Errore durante apertura documento"
