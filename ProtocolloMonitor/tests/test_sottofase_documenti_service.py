import pytest
from datetime import datetime
from pathlib import Path

from backend.services.sottofase_documenti_service import (
    SottofaseAllegatoEliminazioneError,
    SottofaseAllegatoFileTooLargeError,
    SottofaseAllegatoNotFoundError,
    SottofaseDocumentoPrincipaleGiaEsistenteError,
    SottofaseDocumentoPrincipaleNotFoundError,
    SottofaseProtocolloAllegatoGiaEsistenteError,
    SottofaseProtocolloAllegatoNotFoundError,
    SottofaseDocumentiService,
    SottofaseDocumentiValidationError,
)


class FakeSottofaseDocumentiRepository:
    def __init__(
        self,
        *,
        principale_exists=False,
        update_missing=False,
        protocollo_allegato_exists=False,
        protocollo_missing=False,
        eliminazione_result=None,
    ):
        self.principale_exists = principale_exists
        self.update_missing = update_missing
        self.protocollo_allegato_exists = protocollo_allegato_exists
        self.protocollo_missing = protocollo_missing
        self.eliminazione_result = eliminazione_result
        self.created_payloads = []
        self.updated_metadati = []
        self.eliminazione_calls = []

    def get_documenti_sottofase(self, id_sottofase):
        return [{"id_sottofase": id_sottofase, "ruolo_documento": "ALLEGATO"}]

    def get_documento_principale(self, id_sottofase):
        return {"id_sottofase": id_sottofase, "ruolo_documento": "PRINCIPALE"}

    def get_allegati(self, id_sottofase):
        return [{"id_sottofase": id_sottofase, "ruolo_documento": "ALLEGATO"}]

    def get_allegati_sottofase(self, id_sottofase):
        return self.get_allegati(id_sottofase)

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

    def exists_protocollo_allegato(self, *, id_sottofase, id_protocollo):
        return self.protocollo_allegato_exists

    def get_protocollo_per_allegato(self, id_protocollo):
        if self.protocollo_missing:
            return None
        return {
            "id_protocollo": id_protocollo,
            "oggetto": "Oggetto protocollo",
        }

    def add_protocollo_come_allegato(
        self,
        *,
        id_sottofase,
        id_protocollo,
        protocollo,
        data_creazione,
    ):
        payload = {
            "IDSottofase": id_sottofase,
            "RuoloDocumento": "ALLEGATO",
            "TipoOrigine": "PROTOCOLLO",
            "TitoloDocumento": protocollo["oggetto"],
            "IDProtocolloCollegato": id_protocollo,
            "DataCreazione": data_creazione,
        }
        self.created_payloads.append(payload)
        return {"id_documento_sottofase": 40, **payload}

    def get_next_ordine_allegato(self, id_sottofase):
        return 3

    def create_allegato_file(self, payload):
        normalized = {
            **payload,
            "RuoloDocumento": "ALLEGATO",
            "TipoOrigine": "FILE",
            "Attivo": True,
        }
        self.created_payloads.append(normalized)
        return {"id_documento_sottofase": 50, **normalized}

    def elimina_logicamente_allegato(
        self,
        id_sottofase,
        id_documento,
        motivo_eliminazione,
        utente_eliminazione,
        *,
        data_eliminazione,
    ):
        self.eliminazione_calls.append(
            {
                "id_sottofase": id_sottofase,
                "id_documento": id_documento,
                "motivo_eliminazione": motivo_eliminazione,
                "utente_eliminazione": utente_eliminazione,
                "data_eliminazione": data_eliminazione,
            }
        )
        if self.eliminazione_result is not None:
            return self.eliminazione_result
        return {
            "success": True,
            "id_documento": id_documento,
            "documento": {
                "id_documento_sottofase": id_documento,
                "id_sottofase": id_sottofase,
                "ruolo_documento": "ALLEGATO",
                "stato_documento": "ELIMINATO",
                "attivo": False,
            },
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


def test_add_protocollo_come_allegato_creates_record():
    calls = []
    repository = FakeSottofaseDocumentiRepository()
    service = SottofaseDocumentiService(
        sottofase_documenti_repository=repository,
        backup_factory=lambda: calls.append("backup"),
    )

    result = service.add_protocollo_come_allegato(7, {"idProtocollo": 12})

    assert calls == ["backup"]
    assert result["RuoloDocumento"] == "ALLEGATO"
    assert result["TipoOrigine"] == "PROTOCOLLO"
    assert result["IDProtocolloCollegato"] == 12


def test_add_protocollo_come_allegato_blocks_duplicate():
    service = SottofaseDocumentiService(
        sottofase_documenti_repository=FakeSottofaseDocumentiRepository(
            protocollo_allegato_exists=True
        ),
        backup_factory=lambda: None,
    )

    with pytest.raises(SottofaseProtocolloAllegatoGiaEsistenteError):
        service.add_protocollo_come_allegato(7, {"idProtocollo": 12})


def test_add_protocollo_come_allegato_raises_when_protocollo_missing():
    service = SottofaseDocumentiService(
        sottofase_documenti_repository=FakeSottofaseDocumentiRepository(
            protocollo_missing=True
        ),
        backup_factory=lambda: None,
    )

    with pytest.raises(SottofaseProtocolloAllegatoNotFoundError):
        service.add_protocollo_come_allegato(7, {"idProtocollo": 12})


def test_upload_file_allegato_saves_file_and_creates_record(tmp_path):
    calls = []
    repository = FakeSottofaseDocumentiRepository()
    service = SottofaseDocumentiService(
        sottofase_documenti_repository=repository,
        backup_factory=lambda: calls.append("backup"),
        storage_root=tmp_path,
        now_factory=lambda: datetime(2026, 6, 6, 13, 0, 0),
    )

    result = service.upload_file_allegato(
        id_sottofase=7,
        file_bytes=b"contenuto allegato",
        original_filename="planimetria.pdf",
        content_type="application/pdf",
    )

    saved_path = tmp_path / "sottofasi" / "7" / "allegati"
    assert calls == ["backup"]
    assert result["id_documento_sottofase"] == 50
    assert result["RuoloDocumento"] == "ALLEGATO"
    assert result["TipoOrigine"] == "FILE"
    assert result["TitoloDocumento"] == "planimetria"
    assert result["NomeFile"] == "planimetria.pdf"
    assert result["Estensione"] == ".pdf"
    assert result["MimeType"] == "application/pdf"
    assert result["DimensioneBytes"] == len(b"contenuto allegato")
    assert result["StatoDocumento"] == "CARICATO"
    assert result["VersioneDocumento"] == 1
    assert result["Ordine"] == 3
    assert str(result["PercorsoDocumento"]).startswith(str(saved_path.resolve()))
    assert Path(result["PercorsoDocumento"]).exists() is True
    assert len(list(saved_path.iterdir())) == 1


def test_upload_file_allegato_rejects_invalid_extension(tmp_path):
    service = SottofaseDocumentiService(
        sottofase_documenti_repository=FakeSottofaseDocumentiRepository(),
        backup_factory=lambda: None,
        storage_root=tmp_path,
    )

    with pytest.raises(SottofaseDocumentiValidationError):
        service.upload_file_allegato(
            id_sottofase=7,
            file_bytes=b"contenuto",
            original_filename="script.exe",
            content_type="application/octet-stream",
        )


def test_upload_file_allegato_rejects_too_large_file(tmp_path, monkeypatch):
    import backend.services.sottofase_documenti_service as service_module

    monkeypatch.setattr(service_module, "MAX_ALLEGATO_FILE_SIZE_BYTES", 4)
    service = SottofaseDocumentiService(
        sottofase_documenti_repository=FakeSottofaseDocumentiRepository(),
        backup_factory=lambda: None,
        storage_root=tmp_path,
    )

    with pytest.raises(SottofaseAllegatoFileTooLargeError):
        service.upload_file_allegato(
            id_sottofase=7,
            file_bytes=b"12345",
            original_filename="documento.pdf",
            content_type="application/pdf",
        )


def test_elimina_logicamente_allegato_uses_defaults_and_keeps_file(tmp_path):
    calls = []
    allegato_path = tmp_path / "allegato.pdf"
    allegato_path.write_bytes(b"contenuto")
    repository = FakeSottofaseDocumentiRepository(
        eliminazione_result={
            "success": True,
            "id_documento": 11,
            "documento": {
                "id_documento_sottofase": 11,
                "id_sottofase": 7,
                "ruolo_documento": "ALLEGATO",
                "stato_documento": "ELIMINATO",
                "attivo": False,
                "percorso_documento": str(allegato_path),
            },
        }
    )
    service = SottofaseDocumentiService(
        sottofase_documenti_repository=repository,
        backup_factory=lambda: calls.append("backup"),
        now_factory=lambda: datetime(2026, 6, 6, 13, 0, 0),
    )

    result = service.elimina_logicamente_allegato(
        id_sottofase=7,
        id_documento=11,
        payload={},
    )

    assert calls == ["backup"]
    assert result["success"] is True
    assert result["idDocumento"] == 11
    assert repository.eliminazione_calls[0]["motivo_eliminazione"] == (
        "Eliminazione logica allegato"
    )
    assert repository.eliminazione_calls[0]["utente_eliminazione"] == "operatore"
    assert allegato_path.exists() is True


def test_elimina_logicamente_allegato_normalizes_payload():
    repository = FakeSottofaseDocumentiRepository()
    service = SottofaseDocumentiService(
        sottofase_documenti_repository=repository,
        backup_factory=lambda: None,
        now_factory=lambda: datetime(2026, 6, 6, 13, 0, 0),
    )

    service.elimina_logicamente_allegato(
        id_sottofase=7,
        id_documento=11,
        payload={
            "motivoEliminazione": "  Documento duplicato  ",
            "utenteEliminazione": "  Mario Rossi  ",
        },
    )

    assert repository.eliminazione_calls[0]["motivo_eliminazione"] == (
        "Documento duplicato"
    )
    assert repository.eliminazione_calls[0]["utente_eliminazione"] == "Mario Rossi"


def test_elimina_logicamente_allegato_raises_when_missing():
    service = SottofaseDocumentiService(
        sottofase_documenti_repository=FakeSottofaseDocumentiRepository(
            eliminazione_result={
                "success": False,
                "reason": "not_found",
                "message": "Documento non trovato.",
            }
        ),
        backup_factory=lambda: None,
    )

    with pytest.raises(SottofaseAllegatoNotFoundError):
        service.elimina_logicamente_allegato(
            id_sottofase=7,
            id_documento=11,
            payload={},
        )


def test_elimina_logicamente_allegato_raises_when_not_allegato():
    service = SottofaseDocumentiService(
        sottofase_documenti_repository=FakeSottofaseDocumentiRepository(
            eliminazione_result={
                "success": False,
                "reason": "not_allegato",
                "message": "Il documento indicato non e un allegato.",
            }
        ),
        backup_factory=lambda: None,
    )

    with pytest.raises(SottofaseAllegatoEliminazioneError):
        service.elimina_logicamente_allegato(
            id_sottofase=7,
            id_documento=11,
            payload={},
        )


def test_elimina_logicamente_allegato_raises_when_already_deleted():
    service = SottofaseDocumentiService(
        sottofase_documenti_repository=FakeSottofaseDocumentiRepository(
            eliminazione_result={
                "success": False,
                "reason": "already_deleted",
                "message": "Allegato gia eliminato.",
            }
        ),
        backup_factory=lambda: None,
    )

    with pytest.raises(SottofaseAllegatoEliminazioneError):
        service.elimina_logicamente_allegato(
            id_sottofase=7,
            id_documento=11,
            payload={},
        )
