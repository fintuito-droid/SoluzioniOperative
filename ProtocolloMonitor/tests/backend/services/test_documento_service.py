from backend.services.documento_service import DocumentoService


class FakeDocumentoRepository:
    def get_pdf_path_by_protocollo_id(self, protocollo_id):
        return f"C:/fake/{protocollo_id}.pdf"


def test_get_pdf_path_without_repository_returns_none():
    service = DocumentoService()

    assert service.get_pdf_path(1) is None


def test_get_pdf_path_delegates_to_repository():
    service = DocumentoService(
        documento_repository=FakeDocumentoRepository()
    )

    assert service.get_pdf_path(42) == "C:/fake/42.pdf"


def test_document_exists_without_repository_returns_false():
    service = DocumentoService()

    assert service.document_exists(1) is False
