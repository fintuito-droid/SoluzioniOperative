import pytest
from fastapi import HTTPException

import backend.core.dependency_container as dependency_container
import backend.services.document_path_service as document_path_service
from backend.main import apri_pdf_protocollo


class FakeDocumentoService:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path

    def get_pdf_path(self, id_protocollo):
        return self.pdf_path


class FakeContainer:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path

    def get_documento_service(self):
        return FakeDocumentoService(self.pdf_path)


def test_pdf_endpoint_raises_404_when_resolved_path_missing(monkeypatch):
    monkeypatch.setattr(
        dependency_container,
        "DependencyContainer",
        lambda: FakeContainer("FileServer/2026/05/missing.pdf"),
    )
    monkeypatch.setattr(
        document_path_service,
        "resolve_document_path",
        lambda raw_path: None,
    )

    with pytest.raises(HTTPException) as exc_info:
        apri_pdf_protocollo(123)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "File PDF non trovato"
