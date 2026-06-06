import pytest

from backend.services.sottofase_documenti_service import (
    SottofaseDocumentoPrincipaleGiaEsistenteError,
    SottofaseDocumentoPrincipaleNotFoundError,
    SottofaseDocumentiService,
    SottofaseDocumentiValidationError,
)


class FakeSottofaseDocumentiRepository:
    def __init__(self, *, principale_exists=False, update_missing=False):
        self.principale_exists = principale_exists
        self.update_missing = update_missing
        self.created_payloads = []
        self.updated_metadati = []

    def get_documenti_sottofase(self, id_sottofase):
        return [{"id_sottofase": id_sottofase, "ruolo_documento": "ALLEGATO"}]

    def get_documento_principale(self, id_sottofase):
        return {"id_sottofase": id_sottofase, "ruolo_documento": "PRINCIPALE"}

    def get_allegati(self, id_sottofase):
        return [{"id_sottofase": id_sottofase, "ruolo_documento": "ALLEGATO"}]

    def exists_documento_principale_attivo(self, id_sottofase, **kwargs):
        return self.principale_exists

    def exists_documento_principale(self, id_sottofase):
        return self.principale_exists

    def create_documento_principale(self, *, id_sottofase, data_creazione):
        payload = {
            "IDSottofase": id_sottofase,
            "RuoloDocumento": "PRINCIPALE",
            "TipoOrigine": "GENERATO",
            "TitoloDocumento": "Nuovo Documento",
            "StatoDocumento": "BOZZA",
            "VersioneDocumento": 1,
            "Attivo": True,
            "DataCreazione": data_creazione,
            "DataModifica": data_creazione,
        }
        self.created_payloads.append(payload)
        return {"id_documento_sottofase": 20, **payload}

    def create_documento(self, payload):
        self.created_payloads.append(payload)
        return {"id_documento_sottofase": 10, **payload}

    def update_documento_principale_metadati(self, **kwargs):
        self.updated_metadati.append(kwargs)
        if self.update_missing:
            return None
        return {
            "id_sottofase": kwargs["id_sottofase"],
            "ruolo_documento": "PRINCIPALE",
            "titolo_documento": kwargs["titolo_documento"],
            "descrizione_documento": kwargs["descrizione_documento"],
            "stato_documento": kwargs["stato_documento"],
            "tipo_documento": kwargs["tipo_documento"],
            "data_modifica": kwargs["data_modifica"],
        }


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


def test_create_documento_principale_uses_defaults():
    calls = []
    repository = FakeSottofaseDocumentiRepository()
    service = SottofaseDocumentiService(
        sottofase_documenti_repository=repository,
        backup_factory=lambda: calls.append("backup"),
    )

    result = service.create_documento_principale(7)

    assert calls == ["backup"]
    assert result["RuoloDocumento"] == "PRINCIPALE"
    assert result["TipoOrigine"] == "GENERATO"
    assert result["TitoloDocumento"] == "Nuovo Documento"
    assert result["StatoDocumento"] == "BOZZA"
    assert result["VersioneDocumento"] == 1


def test_create_documento_principale_blocks_duplicate():
    service = SottofaseDocumentiService(
        sottofase_documenti_repository=FakeSottofaseDocumentiRepository(
            principale_exists=True
        ),
        backup_factory=lambda: None,
    )

    with pytest.raises(SottofaseDocumentoPrincipaleGiaEsistenteError):
        service.create_documento_principale(7)


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


def test_update_documento_principale_metadati_updates_allowed_fields():
    calls = []
    repository = FakeSottofaseDocumentiRepository()
    service = SottofaseDocumentiService(
        sottofase_documenti_repository=repository,
        backup_factory=lambda: calls.append("backup"),
    )

    result = service.update_documento_principale_metadati(
        7,
        {
            "titoloDocumento": "Nota richiesta integrazione",
            "descrizioneDocumento": "Descrizione",
            "statoDocumento": "bozza",
            "tipoDocumento": "nota",
            "ruoloDocumento": "ALLEGATO",
            "tipoOrigine": "FILE",
            "versioneDocumento": 99,
        },
    )

    assert calls == ["backup"]
    assert result["titolo_documento"] == "Nota richiesta integrazione"
    assert repository.updated_metadati[0]["stato_documento"] == "BOZZA"
    assert repository.updated_metadati[0]["tipo_documento"] == "NOTA"
    assert "ruolo_documento" not in repository.updated_metadati[0]


def test_update_documento_principale_metadati_rejects_invalid_status():
    service = SottofaseDocumentiService(
        sottofase_documenti_repository=FakeSottofaseDocumentiRepository(),
        backup_factory=lambda: None,
    )

    with pytest.raises(SottofaseDocumentiValidationError):
        service.update_documento_principale_metadati(
            7,
            {
                "titoloDocumento": "Nota",
                "statoDocumento": "CHIUSO",
                "tipoDocumento": "NOTA",
            },
        )


def test_update_documento_principale_metadati_rejects_invalid_type():
    service = SottofaseDocumentiService(
        sottofase_documenti_repository=FakeSottofaseDocumentiRepository(),
        backup_factory=lambda: None,
    )

    with pytest.raises(SottofaseDocumentiValidationError):
        service.update_documento_principale_metadati(
            7,
            {
                "titoloDocumento": "Nota",
                "statoDocumento": "BOZZA",
                "tipoDocumento": "ORDINANZA",
            },
        )


def test_update_documento_principale_metadati_raises_when_missing():
    service = SottofaseDocumentiService(
        sottofase_documenti_repository=FakeSottofaseDocumentiRepository(
            update_missing=True
        ),
        backup_factory=lambda: None,
    )

    with pytest.raises(SottofaseDocumentoPrincipaleNotFoundError):
        service.update_documento_principale_metadati(
            7,
            {
                "titoloDocumento": "Nota",
                "statoDocumento": "BOZZA",
                "tipoDocumento": "NOTA",
            },
        )
