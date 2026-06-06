import asyncio

import pytest
from fastapi import HTTPException

from backend.api.routes.protocollo_monitor import (
    SottofaseAllegatoProtocolloPayload,
    SottofaseDocumentoPrincipaleMetadatiPayload,
    aggiorna_sottofase_documento_principale_metadati,
    apri_sottofase_documento,
    carica_allegato_file_sottofase,
    carica_documento_word_sottofase,
    collega_protocollo_come_allegato_sottofase,
    crea_sottofase_documento_principale,
    get_sottofase_documentale,
    get_sottofase_allegati,
    get_sottofase_documento_principale,
    get_sottofase_documenti,
    get_sottofase_step_operativi,
    scarica_sottofase_documento,
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


class FakeSottofaseDocumentiService:
    def __init__(
        self,
        *,
        duplicate=False,
        missing_principale=False,
        duplicate_allegato=False,
    ):
        self.duplicate = duplicate
        self.missing_principale = missing_principale
        self.duplicate_allegato = duplicate_allegato

    def get_documenti_sottofase(self, id_sottofase):
        return [{"id_sottofase": id_sottofase, "ruolo_documento": "ALLEGATO"}]

    def get_documento_principale(self, id_sottofase):
        return {"id_sottofase": id_sottofase, "ruolo_documento": "PRINCIPALE"}

    def get_allegati(self, id_sottofase):
        return [{"id_sottofase": id_sottofase, "ruolo_documento": "ALLEGATO"}]

    def create_documento_principale(self, id_sottofase):
        if self.duplicate:
            from backend.services.sottofase_documenti_service import (
                SottofaseDocumentoPrincipaleGiaEsistenteError,
            )

            raise SottofaseDocumentoPrincipaleGiaEsistenteError(
                "Esiste gia un documento PRINCIPALE attivo per la sottofase."
            )

        return {"id_sottofase": id_sottofase, "ruolo_documento": "PRINCIPALE"}

    def update_documento_principale_metadati(self, id_sottofase, payload):
        if self.missing_principale:
            from backend.services.sottofase_documenti_service import (
                SottofaseDocumentoPrincipaleNotFoundError,
            )

            raise SottofaseDocumentoPrincipaleNotFoundError(
                "Documento principale non trovato."
            )

        return {
            "id_sottofase": id_sottofase,
            "ruolo_documento": "PRINCIPALE",
            "titolo_documento": payload["titoloDocumento"],
            "stato_documento": payload["statoDocumento"],
            "tipo_documento": payload["tipoDocumento"],
        }

    def add_protocollo_come_allegato(self, id_sottofase, payload):
        if self.duplicate_allegato:
            from backend.services.sottofase_documenti_service import (
                SottofaseProtocolloAllegatoGiaEsistenteError,
            )

            raise SottofaseProtocolloAllegatoGiaEsistenteError(
                "Protocollo gia collegato alla sottofase."
            )

        return {
            "id_sottofase": id_sottofase,
            "ruolo_documento": "ALLEGATO",
            "tipo_origine": "PROTOCOLLO",
            "id_protocollo_collegato": payload["idProtocollo"],
        }

    def upload_file_allegato(self, **kwargs):
        return {
            "id_sottofase": kwargs["id_sottofase"],
            "ruolo_documento": "ALLEGATO",
            "tipo_origine": "FILE",
            "nome_file": kwargs["original_filename"],
            "dimensione_bytes": len(kwargs["file_bytes"]),
            "mime_type": kwargs["content_type"],
        }


class FailingSottofaseDocumentaleService:
    def get_documento_by_id(self, id_documento):
        raise RuntimeError("errore test")


class FakeRequest:
    def __init__(self, *, body, content_type):
        self._body = body
        self.headers = {
            "content-type": content_type,
            "content-length": str(len(body)),
        }

    async def body(self):
        return self._body


class FakeDocumentUploadService:
    def __init__(self):
        self.calls = []

    def collega_documento_word(self, **kwargs):
        self.calls.append(kwargs)

        return {
            "success": True,
            "id_documento_sottofase": 10,
            "nome_file": "Documento_5_V001.docx",
        }


def build_multipart_body():
    boundary = "----ProtocolloMonitorTestBoundary"
    body = (
        f"--{boundary}\r\n"
        'Content-Disposition: form-data; name="utenteOperatore"\r\n\r\n'
        "Francesco Matranga\r\n"
        f"--{boundary}\r\n"
        'Content-Disposition: form-data; name="file"; filename="bozza.docx"\r\n'
        "Content-Type: application/vnd.openxmlformats-officedocument.wordprocessingml.document\r\n\r\n"
    ).encode("utf-8")
    body += b"docx-content\r\n"
    body += f"--{boundary}--\r\n".encode("utf-8")

    return body, f"multipart/form-data; boundary={boundary}"


def build_allegato_multipart_body():
    boundary = "----ProtocolloMonitorAllegatoBoundary"
    body = (
        f"--{boundary}\r\n"
        'Content-Disposition: form-data; name="file"; filename="planimetria.pdf"\r\n'
        "Content-Type: application/pdf\r\n\r\n"
    ).encode("utf-8")
    body += b"pdf-content\r\n"
    body += f"--{boundary}--\r\n".encode("utf-8")

    return body, f"multipart/form-data; boundary={boundary}"


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
        documenti_service=FakeSottofaseDocumentiService(),
    )

    assert response == [{"id_sottofase": 7, "ruolo_documento": "ALLEGATO"}]


def test_get_sottofase_documenti_returns_404_when_missing():
    with pytest.raises(HTTPException) as exc_info:
        get_sottofase_documenti(
            999,
            sottofase_service=FakeSottofaseDocumentaleService(sottofase=None),
            documenti_service=FakeSottofaseDocumentiService(),
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Sottofase non trovata"


def test_get_sottofase_documento_principale_returns_record():
    response = get_sottofase_documento_principale(
        7,
        documenti_service=FakeSottofaseDocumentiService(),
    )

    assert response == {"id_sottofase": 7, "ruolo_documento": "PRINCIPALE"}


def test_crea_sottofase_documento_principale_returns_record():
    response = crea_sottofase_documento_principale(
        7,
        documenti_service=FakeSottofaseDocumentiService(),
    )

    assert response == {"id_sottofase": 7, "ruolo_documento": "PRINCIPALE"}


def test_crea_sottofase_documento_principale_returns_409_on_duplicate():
    with pytest.raises(HTTPException) as exc_info:
        crea_sottofase_documento_principale(
            7,
            documenti_service=FakeSottofaseDocumentiService(duplicate=True),
        )

    assert exc_info.value.status_code == 409


def test_aggiorna_sottofase_documento_principale_metadati_returns_record():
    response = aggiorna_sottofase_documento_principale_metadati(
        7,
        SottofaseDocumentoPrincipaleMetadatiPayload(
            titoloDocumento="Nota",
            descrizioneDocumento="Descrizione",
            statoDocumento="BOZZA",
            tipoDocumento="NOTA",
        ),
        documenti_service=FakeSottofaseDocumentiService(),
    )

    assert response["titolo_documento"] == "Nota"
    assert response["stato_documento"] == "BOZZA"
    assert response["tipo_documento"] == "NOTA"


def test_aggiorna_sottofase_documento_principale_metadati_returns_404_when_missing():
    with pytest.raises(HTTPException) as exc_info:
        aggiorna_sottofase_documento_principale_metadati(
            7,
            SottofaseDocumentoPrincipaleMetadatiPayload(
                titoloDocumento="Nota",
                descrizioneDocumento="Descrizione",
                statoDocumento="BOZZA",
                tipoDocumento="NOTA",
            ),
            documenti_service=FakeSottofaseDocumentiService(missing_principale=True),
        )

    assert exc_info.value.status_code == 404


def test_get_sottofase_allegati_returns_list():
    response = get_sottofase_allegati(
        7,
        documenti_service=FakeSottofaseDocumentiService(),
    )

    assert response == [{"id_sottofase": 7, "ruolo_documento": "ALLEGATO"}]


def test_collega_protocollo_come_allegato_sottofase_returns_record():
    response = collega_protocollo_come_allegato_sottofase(
        7,
        SottofaseAllegatoProtocolloPayload(idProtocollo=12),
        documenti_service=FakeSottofaseDocumentiService(),
    )

    assert response["ruolo_documento"] == "ALLEGATO"
    assert response["tipo_origine"] == "PROTOCOLLO"
    assert response["id_protocollo_collegato"] == 12


def test_collega_protocollo_come_allegato_sottofase_returns_409_on_duplicate():
    with pytest.raises(HTTPException) as exc_info:
        collega_protocollo_come_allegato_sottofase(
            7,
            SottofaseAllegatoProtocolloPayload(idProtocollo=12),
            documenti_service=FakeSottofaseDocumentiService(
                duplicate_allegato=True
            ),
        )

    assert exc_info.value.status_code == 409


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


def test_scarica_sottofase_documento_returns_attachment_response(tmp_path):
    document_path = tmp_path / "bozza.docx"
    document_path.write_bytes(b"documento")

    response = scarica_sottofase_documento(
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
    assert (
        response.headers["content-disposition"]
        == f'attachment; filename="{document_path.name}"'
    )


def test_apri_sottofase_documento_returns_404_when_document_missing():
    with pytest.raises(HTTPException) as exc_info:
        apri_sottofase_documento(
            999,
            sottofase_service=FakeSottofaseDocumentaleService(documento=None),
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Documento non trovato"


def test_scarica_sottofase_documento_returns_404_when_document_missing():
    with pytest.raises(HTTPException) as exc_info:
        scarica_sottofase_documento(
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


def test_scarica_sottofase_documento_returns_404_when_path_empty():
    with pytest.raises(HTTPException) as exc_info:
        scarica_sottofase_documento(
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


def test_scarica_sottofase_documento_returns_404_when_file_missing(tmp_path):
    missing_path = tmp_path / "missing.docx"

    with pytest.raises(HTTPException) as exc_info:
        scarica_sottofase_documento(
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


def test_carica_documento_word_sottofase_parses_multipart_and_calls_service():
    body, content_type = build_multipart_body()
    service = FakeDocumentUploadService()

    response = asyncio.run(
        carica_documento_word_sottofase(
            5,
            request=FakeRequest(body=body, content_type=content_type),
            upload_service=service,
        )
    )

    assert response["success"] is True
    assert service.calls == [
        {
            "id_sottofase": 5,
            "file_bytes": b"docx-content",
            "original_filename": "bozza.docx",
            "utente_operatore": "Francesco Matranga",
        }
    ]


def test_carica_allegato_file_sottofase_parses_multipart_and_calls_service():
    body, content_type = build_allegato_multipart_body()

    response = asyncio.run(
        carica_allegato_file_sottofase(
            7,
            request=FakeRequest(body=body, content_type=content_type),
            documenti_service=FakeSottofaseDocumentiService(),
        )
    )

    assert response["id_sottofase"] == 7
    assert response["ruolo_documento"] == "ALLEGATO"
    assert response["tipo_origine"] == "FILE"
    assert response["nome_file"] == "planimetria.pdf"
    assert response["dimensione_bytes"] == len(b"pdf-content")
