import pytest
from fastapi import HTTPException

import backend.api.routes.protocollo_monitor as protocollo_monitor
import backend.services.document_path_service as document_path_service
from backend.api.routes.protocollo_monitor import apri_pdf, apri_pdf_protocollo


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
        document_path_service,
        "resolve_document_path",
        lambda raw_path: None,
    )

    with pytest.raises(HTTPException) as exc_info:
        apri_pdf_protocollo(
            123,
            documento_service=FakeDocumentoService("FileServer/2026/05/missing.pdf"),
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "File PDF non trovato"


def test_pdf_endpoint_raises_404_when_protocollo_missing(monkeypatch):
    with pytest.raises(HTTPException) as exc_info:
        apri_pdf_protocollo(999, documento_service=FakeDocumentoService(None))

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Protocollo non trovato"


def test_pdf_endpoint_raises_404_when_pdf_unavailable(monkeypatch):
    with pytest.raises(HTTPException) as exc_info:
        apri_pdf_protocollo(123, documento_service=FakeDocumentoService(""))

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "PDF non disponibile"


def test_apri_pdf_uses_resolved_path_before_opening(monkeypatch, tmp_path):
    pdf_path = tmp_path / "sample.pdf"
    pdf_path.write_bytes(b"%PDF-test")
    popen_calls = []

    monkeypatch.setattr(
        document_path_service,
        "resolve_document_path",
        lambda raw_path: pdf_path,
    )
    monkeypatch.setattr(
        protocollo_monitor.subprocess,
        "Popen",
        lambda args, shell: popen_calls.append((args, shell)),
    )

    result = apri_pdf(
        123,
        documento_service=FakeDocumentoService("FileServer/2026/05/sample.pdf"),
    )

    assert result == {"success": True}
    assert popen_calls == [
        (
            [
                "cmd",
                "/c",
                "start",
                "/max",
                "",
                str(pdf_path),
            ],
            True,
        )
    ]
