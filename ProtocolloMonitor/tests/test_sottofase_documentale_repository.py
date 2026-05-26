from types import SimpleNamespace

from backend.repositories.sottofase_documentale_repository import (
    SottofaseDocumentaleRepository,
)


class FakeCursor:
    def __init__(self, results):
        self.results = list(results)
        self.current_result = []
        self.executed_queries = []
        self.executed_params = []
        self.closed = False

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


class SottofaseDocumentaleRepositoryForTest(SottofaseDocumentaleRepository):
    def __init__(self, connection):
        self.connection = connection

    def _open_access_connection(self):
        return self.connection


def make_sottofase_row(**overrides):
    values = {
        "IDSottofase": 1,
        "IDFase": 10,
        "IDCatalogoSottofase": 5,
        "CodiceSottofase": "DOCUMENTO",
        "Titolo": "Documento",
        "Descrizione": "Predisposizione documento",
        "Ordine": 1,
        "StatoSottofase": "IN_CORSO",
        "Icona": "mdi-file-document-outline",
        "Colore": "deep-purple",
        "Responsabile": "Operatore",
        "DataScadenza": None,
        "DataAvvio": None,
        "DataCompletamento": None,
        "NoteInterne": "nota",
        "Attivo": True,
        "DataCreazione": None,
        "DataModifica": None,
        "StepCorrente": "REDIGI",
        "TestoOperatore": "testo",
        "HaDocumentoCollegato": True,
        "IDDocumentoCorrente": 99,
        "DataUltimaAzione": None,
        "UtenteUltimaAzione": "utente",
        "VersioneDocumento": 2,
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def make_documento_row(**overrides):
    values = {
        "IDDocumentoSottofase": 99,
        "IDSottofase": 1,
        "TipoDocumento": "WORD",
        "NomeFile": "bozza.docx",
        "Estensione": ".docx",
        "PercorsoDocumento": r"C:\Temp\bozza.docx",
        "MimeType": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "DimensioneBytes": 100,
        "HashFile": "abc",
        "VersioneDocumento": 2,
        "DataCollegamento": None,
        "UtenteCollegamento": "utente",
        "Attivo": True,
        "DataCreazione": None,
        "DataModifica": None,
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def make_step_row(**overrides):
    values = {
        "IDStepSottofase": 7,
        "IDSottofase": 1,
        "CodiceStep": "REDIGI",
        "Ordine": 10,
        "StatoStep": "IN_CORSO",
        "DataAvvio": None,
        "DataCompletamento": None,
        "NoteStep": "nota",
        "UtenteAssegnato": "utente",
        "UtenteCompletamento": None,
        "IDDocumentoSottofase": 99,
        "VersioneDocumento": 2,
        "DataCreazione": None,
        "DataModifica": None,
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def test_get_sottofase_documentale_returns_read_only_record():
    cursor = FakeCursor([[make_sottofase_row()]])
    repository = SottofaseDocumentaleRepositoryForTest(FakeConnection(cursor))

    record = repository.get_sottofase_documentale(1)

    assert record["id_sottofase"] == 1
    assert record["step_corrente"] == "REDIGI"
    assert record["ha_documento_collegato"] is True
    assert record["id_documento_corrente"] == 99
    assert "FROM T_ProcedimentoSottofasi" in cursor.executed_queries[0]
    assert cursor.executed_params == [(1,)]
    assert cursor.closed is True
    assert repository.connection.closed is True


def test_get_sottofase_documentale_returns_none_when_missing():
    cursor = FakeCursor([[]])
    repository = SottofaseDocumentaleRepositoryForTest(FakeConnection(cursor))

    assert repository.get_sottofase_documentale(999) is None


def test_list_documenti_by_sottofase_returns_documents():
    cursor = FakeCursor([[make_documento_row()]])
    repository = SottofaseDocumentaleRepositoryForTest(FakeConnection(cursor))

    records = repository.list_documenti_by_sottofase(1)

    assert records[0]["id_documento_sottofase"] == 99
    assert records[0]["tipo_documento"] == "WORD"
    assert records[0]["attivo"] is True
    assert "FROM T_SottofaseDocumenti" in cursor.executed_queries[0]
    assert cursor.executed_params == [(1,)]


def test_get_documento_by_id_returns_document():
    cursor = FakeCursor([[make_documento_row()]])
    repository = SottofaseDocumentaleRepositoryForTest(FakeConnection(cursor))

    record = repository.get_documento_by_id(99)

    assert record["id_documento_sottofase"] == 99
    assert record["nome_file"] == "bozza.docx"
    assert cursor.executed_params == [(99,)]


def test_list_step_operativi_by_sottofase_returns_steps():
    cursor = FakeCursor([[make_step_row()]])
    repository = SottofaseDocumentaleRepositoryForTest(FakeConnection(cursor))

    records = repository.list_step_operativi_by_sottofase(1)

    assert records[0]["id_step_sottofase"] == 7
    assert records[0]["codice_step"] == "REDIGI"
    assert records[0]["stato_step"] == "IN_CORSO"
    assert "FROM T_SottofaseStepOperativi" in cursor.executed_queries[0]
    assert cursor.executed_params == [(1,)]
