from backend.services.metadata_service import MetadataService
import backend.services.document_path_service as document_path_service


class FakeMetadataRepository:
    def __init__(self, metadata=None):
        self.metadata = metadata

    def metadata_feature_available(self):
        return True

    def get_metadata_by_protocollo_id(self, id_protocollo):
        return self.metadata


def test_get_metadata_found():
    expected = {
        "id_protocollo": 123,
        "numero_protocollo": "18177",
        "data_protocollo": "2026-05-10",
        "pdf_disponibile": False,
    }
    service = MetadataService(
        metadata_repository=FakeMetadataRepository(
            {
                "id_protocollo": 123,
                "numero_protocollo": "18177",
                "data_protocollo": "2026-05-10",
            }
        )
    )

    assert service.get_metadata(123) == expected


def test_get_metadata_adds_pdf_disponibile_true_when_path_resolves(monkeypatch):
    monkeypatch.setattr(
        document_path_service,
        "resolve_document_path",
        lambda path: object(),
    )
    service = MetadataService(
        metadata_repository=FakeMetadataRepository(
            {
                "id_protocollo": 123,
                "percorso_documento_protocollato": "FileServer/2026/05/test.pdf",
            }
        )
    )

    metadata = service.get_metadata(123)

    assert metadata["pdf_disponibile"] is True


def test_get_metadata_adds_pdf_disponibile_false_when_path_missing(monkeypatch):
    monkeypatch.setattr(
        document_path_service,
        "resolve_document_path",
        lambda path: None,
    )
    service = MetadataService(
        metadata_repository=FakeMetadataRepository(
            {
                "id_protocollo": 123,
                "percorso_documento_protocollato": "",
            }
        )
    )

    metadata = service.get_metadata(123)

    assert metadata["pdf_disponibile"] is False


def test_get_metadata_not_found():
    service = MetadataService(
        metadata_repository=FakeMetadataRepository(None)
    )

    assert service.get_metadata(999) is None


def test_get_metadata_without_repository_returns_none():
    service = MetadataService()

    assert service.get_metadata(123) is None
