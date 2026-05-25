from backend.services.document_storage_service import DocumentStorageService
from backend.services.pdf_document_service import PdfDocumentService


class FakeDocumentoRepository:
    def __init__(self, *, update_result=True):
        self.update_result = update_result
        self.updated_id_protocollo = None
        self.updated_path = None

    def update_protocollo_pdf_path(
        self,
        id_protocollo,
        percorso_documento_protocollato,
    ):
        self.updated_id_protocollo = id_protocollo
        self.updated_path = percorso_documento_protocollato
        return self.update_result


def test_save_protocollo_pdf_uses_document_storage_service(tmp_path):
    storage_service = DocumentStorageService(file_server_root=tmp_path)
    service = PdfDocumentService(storage_service=storage_service)

    saved_path = service.save_protocollo_pdf(
        b"%PDF-test",
        "Entrata",
        "DIR-SIC",
        "18177",
        "10/05/2026",
    )

    assert saved_path == tmp_path / "2026" / "05" / "E_DIR-SIC_18177_20260510.pdf"
    assert saved_path.read_bytes() == b"%PDF-test"


def test_save_and_register_protocollo_pdf_saves_file_and_updates_repository(tmp_path):
    storage_service = DocumentStorageService(file_server_root=tmp_path)
    repository = FakeDocumentoRepository(update_result=True)
    service = PdfDocumentService(
        storage_service=storage_service,
        documento_repository=repository,
    )

    result = service.save_and_register_protocollo_pdf(
        123,
        b"%PDF-test",
        "Entrata",
        "DIR-SIC",
        "18177",
        "10/05/2026",
    )

    expected_path = tmp_path / "2026" / "05" / "E_DIR-SIC_18177_20260510.pdf"

    assert expected_path.read_bytes() == b"%PDF-test"
    assert repository.updated_id_protocollo == 123
    assert repository.updated_path == str(expected_path)
    assert result == {
        "saved": True,
        "registered": True,
        "id_protocollo": 123,
        "path": str(expected_path),
        "filename": "E_DIR-SIC_18177_20260510.pdf",
    }


def test_save_and_register_protocollo_pdf_returns_explicit_failure_when_update_false(
    tmp_path,
):
    storage_service = DocumentStorageService(file_server_root=tmp_path)
    repository = FakeDocumentoRepository(update_result=False)
    service = PdfDocumentService(
        storage_service=storage_service,
        documento_repository=repository,
    )

    result = service.save_and_register_protocollo_pdf(
        999,
        b"%PDF-test",
        "Uscita",
        "DIR-SIC",
        "18164",
        "10/05/2026",
    )

    expected_path = tmp_path / "2026" / "05" / "U_DIR-SIC_18164_20260510.pdf"

    assert expected_path.read_bytes() == b"%PDF-test"
    assert repository.updated_id_protocollo == 999
    assert repository.updated_path == str(expected_path)
    assert result == {
        "saved": True,
        "registered": False,
        "id_protocollo": 999,
        "path": str(expected_path),
        "filename": "U_DIR-SIC_18164_20260510.pdf",
        "error": "Protocollo non aggiornato.",
    }
