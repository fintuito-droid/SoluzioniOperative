import pytest
from fastapi import HTTPException

import backend.core.dependency_container as dependency_container
from backend.main import get_protocollo_metadata


class FakeMetadataService:
    def __init__(self, metadata):
        self.metadata = metadata

    def get_metadata(self, id_protocollo):
        return self.metadata


class FakeContainer:
    def __init__(self, metadata):
        self.metadata = metadata

    def get_metadata_service(self):
        return FakeMetadataService(self.metadata)


def test_metadata_endpoint_returns_200(monkeypatch):
    metadata = {
        "id_protocollo": 123,
        "numero_protocollo": "18177",
        "data_protocollo": "2026-05-10",
        "modalita": "Entrata",
        "comando_mittente": "DIR-SIC",
        "da_lavorare": True,
        "data_scadenza": None,
        "tipologia_documento": "Preventivo",
        "percorso_documento_protocollato": "FileServer/2026/05/E_DIR-SIC_18177_20260510.pdf",
        "pdf_disponibile": True,
    }
    monkeypatch.setattr(
        dependency_container,
        "DependencyContainer",
        lambda: FakeContainer(metadata),
    )

    response = get_protocollo_metadata(123)

    assert response == metadata


def test_metadata_endpoint_returns_404(monkeypatch):
    monkeypatch.setattr(
        dependency_container,
        "DependencyContainer",
        lambda: FakeContainer(None),
    )

    with pytest.raises(HTTPException) as exc_info:
        get_protocollo_metadata(999)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Protocollo non trovato"
