import pytest

from backend.services.sottofase_documenti_service import (
    SottofaseDocumentoPrincipaleGiaEsistenteError,
    SottofaseDocumentiService,
    SottofaseDocumentiValidationError,
)


class FakeSottofaseDocumentiRepository:
    def __init__(self, *, principale_exists=False):
        self.principale_exists = principale_exists
        self.created_payloads = []

    def get_documenti_sottofase(self, id_sottofase):
        return [{"id_sottofase": id_sottofase, "ruolo_documento": "ALLEGATO"}]

    def get_documento_principale(self, id_sottofase):
        return {"id_sottofase": id_sottofase, "ruolo_documento": "PRINCIPALE"}

    def get_allegati(self, id_sottofase):
        return [{"id_sottofase": id_sottofase, "ruolo_documento": "ALLEGATO"}]

    def exists_documento_principale_attivo(self, id_sottofase, **kwargs):
        return self.principale_exists

    def create_documento(self, payload):
        self.created_payloads.append(payload)
        return {"id_documento_sottofase": 10, **payload}


def test_get_documenti_sottofase_uses_repository():
    service = SottofaseDocumentiService(
        sottofase_documenti_repository=FakeSottofaseDocumentiRepository()
    )

    result = service.get_documenti_sottofase(7)

    assert result == [{"id_sottofase": 7, "ruolo_documento": "ALLEGATO"}]


def test_get_documento_principale_uses_repository():
    service = SottofaseDocumentiService(
        sottofase_documenti_repository=FakeSottofaseDocumentiRepository()
    )

    result = service.get_documento_principale(7)

    assert result["ruolo_documento"] == "PRINCIPALE"


def test_get_allegati_uses_repository():
    service = SottofaseDocumentiService(
        sottofase_documenti_repository=FakeSottofaseDocumentiRepository()
    )

    result = service.get_allegati(7)

    assert result[0]["ruolo_documento"] == "ALLEGATO"


def test_create_documento_rejects_invalid_role():
    service = SottofaseDocumentiService(
        sottofase_documenti_repository=FakeSottofaseDocumentiRepository(),
        backup_factory=lambda: None,
    )

    with pytest.raises(SottofaseDocumentiValidationError):
        service.create_documento(
            {
                "IDSottofase": 7,
                "RuoloDocumento": "BOZZA",
                "TipoOrigine": "FILE",
            }
        )


def test_create_documento_rejects_invalid_origin():
    service = SottofaseDocumentiService(
        sottofase_documenti_repository=FakeSottofaseDocumentiRepository(),
        backup_factory=lambda: None,
    )

    with pytest.raises(SottofaseDocumentiValidationError):
        service.create_documento(
            {
                "IDSottofase": 7,
                "RuoloDocumento": "ALLEGATO",
                "TipoOrigine": "EMAIL",
            }
        )


def test_create_documento_rejects_protocollo_without_link():
    service = SottofaseDocumentiService(
        sottofase_documenti_repository=FakeSottofaseDocumentiRepository(),
        backup_factory=lambda: None,
    )

    with pytest.raises(SottofaseDocumentiValidationError):
        service.create_documento(
            {
                "IDSottofase": 7,
                "RuoloDocumento": "ALLEGATO",
                "TipoOrigine": "PROTOCOLLO",
            }
        )


def test_create_documento_blocks_second_active_principale():
    service = SottofaseDocumentiService(
        sottofase_documenti_repository=FakeSottofaseDocumentiRepository(
            principale_exists=True
        ),
        backup_factory=lambda: None,
    )

    with pytest.raises(SottofaseDocumentoPrincipaleGiaEsistenteError):
        service.create_documento(
            {
                "IDSottofase": 7,
                "RuoloDocumento": "PRINCIPALE",
                "TipoOrigine": "FILE",
            }
        )


def test_create_documento_normalizes_payload_and_calls_backup():
    calls = []
    repository = FakeSottofaseDocumentiRepository()
    service = SottofaseDocumentiService(
        sottofase_documenti_repository=repository,
        backup_factory=lambda: calls.append("backup"),
    )

    result = service.create_documento(
        {
            "id_sottofase": 7,
            "ruolo_documento": "allegato",
            "tipo_origine": "file",
            "nome_file": "istanza.pdf",
        }
    )

    assert calls == ["backup"]
    assert result["IDSottofase"] == 7
    assert result["RuoloDocumento"] == "ALLEGATO"
    assert result["TipoOrigine"] == "FILE"
    assert result["TitoloDocumento"] == "istanza.pdf"
