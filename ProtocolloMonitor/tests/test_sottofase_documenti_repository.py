from types import SimpleNamespace

from backend.repositories.sottofase_documenti_repository import (
    SottofaseDocumentiRepository,
)


class FakeCursor:
    def __init__(self, results, *, rowcount=1):
        self.results = list(results)
        self.current_result = []
        self.executed_queries = []
        self.executed_params = []
        self.closed = False
        self.rowcount = rowcount

    def execute(self, query, params=None):
        self.executed_queries.append(query)
        self.executed_params.append(params)
        self.current_result = self.results.pop(0)
        return self

    def fetchall(self):
        return self.current_result

    def fetchone(self):
        if not self.current_result:
            return None
        return self.current_result[0]

    def close(self):
        self.closed = True


class FakeConnection:
    def __init__(self, cursor):
        self.cursor_instance = cursor
        self.closed = False

    def cursor(self):
        return self.cursor_instance

    def close(self):
        self.closed = True

    def commit(self):
        pass

    def rollback(self):
        pass


class SottofaseDocumentiRepositoryForTest(SottofaseDocumentiRepository):
    def __init__(self, connection):
        self.connection = connection

    def _open_access_connection(self):
        return self.connection


class CapturingSottofaseDocumentiRepository(SottofaseDocumentiRepository):
    def __init__(self):
        self.created_payload = None

    def create_documento(self, payload):
        self.created_payload = payload
        return {"id_documento_sottofase": 30, **payload}


def make_documento_row(**overrides):
    values = {
        "IDDocumentoSottofase": 11,
        "IDSottofase": 7,
        "RuoloDocumento": "PRINCIPALE",
        "TipoOrigine": "FILE",
        "TitoloDocumento": "Documento principale",
        "DescrizioneDocumento": "Descrizione",
        "TipoDocumento": "PDF",
        "NomeFile": "documento.pdf",
        "Estensione": ".pdf",
        "PercorsoDocumento": r"C:\Temp\documento.pdf",
        "IDProtocolloCollegato": None,
        "MimeType": "application/pdf",
        "DimensioneBytes": 100,
        "HashFile": "abc",
        "VersioneDocumento": 1,
        "StatoDocumento": "ATTIVO",
        "Ordine": 1,
        "DataCollegamento": None,
        "UtenteCollegamento": "utente",
        "Attivo": True,
        "DataCreazione": None,
        "DataModifica": None,
        "DataEliminazione": None,
        "UtenteEliminazione": None,
        "MotivoEliminazione": None,
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def test_get_documenti_sottofase_returns_active_documents():
    cursor = FakeCursor([[make_documento_row()]])
    repository = SottofaseDocumentiRepositoryForTest(FakeConnection(cursor))

    result = repository.get_documenti_sottofase(7)

    assert result[0]["id_documento_sottofase"] == 11
    assert result[0]["ruolo_documento"] == "PRINCIPALE"
    assert result[0]["tipo_origine"] == "FILE"
    assert "FROM T_SottofaseDocumenti" in cursor.executed_queries[0]
    assert cursor.executed_params == [(7, True)]
    assert cursor.closed is True
    assert repository.connection.closed is True


def test_get_documento_principale_returns_first_active_principale():
    cursor = FakeCursor([[make_documento_row()]])
    repository = SottofaseDocumentiRepositoryForTest(FakeConnection(cursor))

    result = repository.get_documento_principale(7)

    assert result["ruolo_documento"] == "PRINCIPALE"
    assert result["id_sottofase"] == 7
    assert cursor.executed_params == [(7, "PRINCIPALE", True)]


def test_get_allegati_returns_only_allegati():
    cursor = FakeCursor([[make_documento_row(RuoloDocumento="ALLEGATO")]])
    repository = SottofaseDocumentiRepositoryForTest(FakeConnection(cursor))

    result = repository.get_allegati(7)

    assert result[0]["ruolo_documento"] == "ALLEGATO"
    assert cursor.executed_params == [(7, "ALLEGATO", True)]


def test_get_allegati_sottofase_alias_returns_allegati():
    cursor = FakeCursor([[make_documento_row(RuoloDocumento="ALLEGATO")]])
    repository = SottofaseDocumentiRepositoryForTest(FakeConnection(cursor))

    result = repository.get_allegati_sottofase(7)

    assert result[0]["ruolo_documento"] == "ALLEGATO"


def test_get_allegati_eliminati_returns_only_deleted_allegati():
    row = make_documento_row(
        RuoloDocumento="ALLEGATO",
        Attivo=False,
        StatoDocumento="ELIMINATO",
        DataEliminazione="2026-06-06 13:00:00",
        UtenteEliminazione="operatore",
        MotivoEliminazione="Motivo test",
    )
    cursor = FakeCursor([[row]])
    repository = SottofaseDocumentiRepositoryForTest(FakeConnection(cursor))

    result = repository.get_allegati_eliminati(7)

    assert result[0]["ruolo_documento"] == "ALLEGATO"
    assert result[0]["stato_documento"] == "ELIMINATO"
    assert result[0]["data_eliminazione"] == "2026-06-06 13:00:00"
    assert cursor.executed_params == [(7, "ALLEGATO", False, "ELIMINATO")]


def test_exists_documento_principale_attivo_returns_true():
    cursor = FakeCursor([[SimpleNamespace(Totale=1)]])
    repository = SottofaseDocumentiRepositoryForTest(FakeConnection(cursor))

    assert repository.exists_documento_principale_attivo(7) is True
    assert cursor.executed_params == [(7, "PRINCIPALE", True)]


def test_exists_documento_principale_alias_returns_true():
    cursor = FakeCursor([[SimpleNamespace(Totale=1)]])
    repository = SottofaseDocumentiRepositoryForTest(FakeConnection(cursor))

    assert repository.exists_documento_principale(7) is True


def test_exists_protocollo_allegato_returns_true():
    cursor = FakeCursor([[SimpleNamespace(Totale=1)]])
    repository = SottofaseDocumentiRepositoryForTest(FakeConnection(cursor))

    assert repository.exists_protocollo_allegato(
        id_sottofase=7,
        id_protocollo=12,
    ) is True
    assert cursor.executed_params == [(7, 12, "ALLEGATO", "PROTOCOLLO", True)]


def test_get_protocollo_per_allegato_returns_minimal_data():
    cursor = FakeCursor(
        [[
            SimpleNamespace(
                IDProtocollo=12,
                NumeroProtocollo="123",
                DataProtocollo=None,
                Oggetto="Oggetto protocollo",
            )
        ]]
    )
    repository = SottofaseDocumentiRepositoryForTest(FakeConnection(cursor))

    result = repository.get_protocollo_per_allegato(12)

    assert result["id_protocollo"] == 12
    assert result["oggetto"] == "Oggetto protocollo"


def test_add_protocollo_come_allegato_creates_document_payload():
    repository = CapturingSottofaseDocumentiRepository()

    result = repository.add_protocollo_come_allegato(
        id_sottofase=7,
        id_protocollo=12,
        protocollo={"oggetto": "Oggetto protocollo"},
        data_creazione="2026-06-06 13:00:00",
    )

    assert result["RuoloDocumento"] == "ALLEGATO"
    assert result["TipoOrigine"] == "PROTOCOLLO"
    assert result["TitoloDocumento"] == "Oggetto protocollo"
    assert result["IDProtocolloCollegato"] == 12


def test_create_allegato_file_forces_file_allegato_payload():
    repository = CapturingSottofaseDocumentiRepository()

    result = repository.create_allegato_file(
        {
            "IDSottofase": 7,
            "TitoloDocumento": "Planimetria",
            "NomeFile": "planimetria.pdf",
            "PercorsoDocumento": r"C:\Temp\planimetria.pdf",
        }
    )

    assert result["RuoloDocumento"] == "ALLEGATO"
    assert result["TipoOrigine"] == "FILE"
    assert result["Attivo"] is True
    assert repository.created_payload["RuoloDocumento"] == "ALLEGATO"


def test_crea_documento_principale_bozza_creates_minimal_workflow_payload():
    repository = CapturingSottofaseDocumentiRepository()

    result = repository.crea_documento_principale_bozza(
        id_sottofase=7,
        titolo="Bozza nota",
        descrizione="Descrizione",
        utente="operatore",
        data_creazione="2026-06-06 14:00:00",
    )

    assert result["RuoloDocumento"] == "PRINCIPALE"
    assert result["TipoOrigine"] == "INTERNO"
    assert result["TitoloDocumento"] == "Bozza nota"
    assert result["StatoDocumento"] == "BOZZA"
    assert result["UtenteCollegamento"] == "operatore"


def test_get_documento_by_id_returns_document():
    cursor = FakeCursor([[make_documento_row()]])
    repository = SottofaseDocumentiRepositoryForTest(FakeConnection(cursor))

    result = repository.get_documento_by_id(11)

    assert result["id_documento_sottofase"] == 11
    assert result["nome_file"] == "documento.pdf"
    assert cursor.executed_params == [(11,)]


def test_aggiorna_stato_documento_principale_updates_principale_only():
    updated_row = make_documento_row(
        RuoloDocumento="PRINCIPALE",
        StatoDocumento="REDATTO",
        DescrizioneDocumento="Descrizione\n\n[2026-06-06 14:00] operatore - REDATTO: Nota",
    )
    cursor = FakeCursor(
        [
            [make_documento_row(RuoloDocumento="PRINCIPALE")],
            [],
            [updated_row],
        ]
    )
    repository = SottofaseDocumentiRepositoryForTest(FakeConnection(cursor))

    result = repository.aggiorna_stato_documento_principale(
        id_sottofase=7,
        id_documento=11,
        nuovo_stato="REDATTO",
        note="Nota",
        utente="operatore",
        data_modifica="2026-06-06 14:00:00",
    )

    assert result["success"] is True
    assert result["documento"]["stato_documento"] == "REDATTO"
    assert "UPDATE T_SottofaseDocumenti" in cursor.executed_queries[1]
    assert cursor.executed_params[1] == (
        "REDATTO",
        "Descrizione\n\n[2026-06-06 14:00] operatore - REDATTO: Nota",
        "2026-06-06 14:00:00",
        "operatore",
        11,
        7,
        "PRINCIPALE",
        True,
    )


def test_elimina_logicamente_allegato_updates_audit_fields():
    updated_row = make_documento_row(
        RuoloDocumento="ALLEGATO",
        Attivo=False,
        StatoDocumento="ELIMINATO",
        DataEliminazione="2026-06-06 13:00:00",
        UtenteEliminazione="operatore",
        MotivoEliminazione="Motivo test",
    )
    cursor = FakeCursor(
        [
            [make_documento_row(RuoloDocumento="ALLEGATO")],
            [],
            [updated_row],
        ]
    )
    repository = SottofaseDocumentiRepositoryForTest(FakeConnection(cursor))

    result = repository.elimina_logicamente_allegato(
        7,
        11,
        "Motivo test",
        "operatore",
        data_eliminazione="2026-06-06 13:00:00",
    )

    assert result["success"] is True
    assert result["id_documento"] == 11
    assert result["documento"]["stato_documento"] == "ELIMINATO"
    assert result["documento"]["attivo"] is False
    assert "SET Attivo = ?" in cursor.executed_queries[1]
    assert cursor.executed_params[1] == (
        False,
        "ELIMINATO",
        "2026-06-06 13:00:00",
        "operatore",
        "Motivo test",
        "2026-06-06 13:00:00",
        11,
        7,
        "ALLEGATO",
        True,
    )


def test_elimina_logicamente_allegato_rejects_non_allegato():
    cursor = FakeCursor([[make_documento_row(RuoloDocumento="PRINCIPALE")]])
    repository = SottofaseDocumentiRepositoryForTest(FakeConnection(cursor))

    result = repository.elimina_logicamente_allegato(
        7,
        11,
        "Motivo test",
        "operatore",
    )

    assert result["success"] is False
    assert result["reason"] == "not_allegato"
    assert len(cursor.executed_queries) == 1


def test_elimina_logicamente_allegato_rejects_already_deleted():
    cursor = FakeCursor(
        [[make_documento_row(RuoloDocumento="ALLEGATO", Attivo=False)]]
    )
    repository = SottofaseDocumentiRepositoryForTest(FakeConnection(cursor))

    result = repository.elimina_logicamente_allegato(
        7,
        11,
        "Motivo test",
        "operatore",
    )

    assert result["success"] is False
    assert result["reason"] == "already_deleted"
    assert len(cursor.executed_queries) == 1


def test_ripristina_allegato_updates_status_and_clears_audit_fields():
    updated_row = make_documento_row(
        RuoloDocumento="ALLEGATO",
        Attivo=True,
        StatoDocumento="ATTIVO",
        DataEliminazione=None,
        UtenteEliminazione=None,
        MotivoEliminazione=None,
    )
    cursor = FakeCursor(
        [
            [
                make_documento_row(
                    RuoloDocumento="ALLEGATO",
                    Attivo=False,
                    StatoDocumento="ELIMINATO",
                    DataEliminazione="2026-06-06 13:00:00",
                )
            ],
            [],
            [updated_row],
        ]
    )
    repository = SottofaseDocumentiRepositoryForTest(FakeConnection(cursor))

    result = repository.ripristina_allegato(
        7,
        11,
        "operatore",
        data_ripristino="2026-06-06 14:00:00",
    )

    assert result["success"] is True
    assert result["id_documento"] == 11
    assert result["documento"]["stato_documento"] == "ATTIVO"
    assert result["documento"]["attivo"] is True
    assert "DataEliminazione = NULL" in cursor.executed_queries[1]
    assert cursor.executed_params[1] == (
        True,
        "ATTIVO",
        "2026-06-06 14:00:00",
        11,
        7,
        "ALLEGATO",
        False,
        "ELIMINATO",
    )


def test_ripristina_allegato_rejects_not_deleted():
    cursor = FakeCursor([[make_documento_row(RuoloDocumento="ALLEGATO")]])
    repository = SottofaseDocumentiRepositoryForTest(FakeConnection(cursor))

    result = repository.ripristina_allegato(7, 11, "operatore")

    assert result["success"] is False
    assert result["reason"] == "not_deleted"
    assert len(cursor.executed_queries) == 1


def test_update_documento_principale_metadati_updates_only_allowed_fields():
    cursor = FakeCursor([[], [make_documento_row(TitoloDocumento="Nota")]])
    repository = SottofaseDocumentiRepositoryForTest(FakeConnection(cursor))

    result = repository.update_documento_principale_metadati(
        id_sottofase=7,
        titolo_documento="Nota",
        descrizione_documento="Descrizione aggiornata",
        stato_documento="BOZZA",
        tipo_documento="NOTA",
        data_modifica="2026-06-06 13:00:00",
    )

    assert result["titolo_documento"] == "Nota"
    set_clause = cursor.executed_queries[0].split("WHERE", 1)[0]
    assert "RuoloDocumento =" not in set_clause
    assert "TipoOrigine =" not in set_clause
    assert "VersioneDocumento =" not in set_clause
    assert cursor.executed_params[0] == (
        "Nota",
        "Descrizione aggiornata",
        "BOZZA",
        "NOTA",
        "2026-06-06 13:00:00",
        7,
        "PRINCIPALE",
        True,
    )


def test_update_documento_principale_metadati_returns_none_when_missing():
    cursor = FakeCursor([[]], rowcount=0)
    repository = SottofaseDocumentiRepositoryForTest(FakeConnection(cursor))

    result = repository.update_documento_principale_metadati(
        id_sottofase=7,
        titolo_documento="Nota",
        descrizione_documento=None,
        stato_documento="BOZZA",
        tipo_documento="NOTA",
        data_modifica="2026-06-06 13:00:00",
    )

    assert result is None
