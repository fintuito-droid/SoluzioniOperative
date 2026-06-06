from types import SimpleNamespace

from backend.repositories.sottofase_documenti_repository import (
    SottofaseDocumentiRepository,
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


class SottofaseDocumentiRepositoryForTest(SottofaseDocumentiRepository):
    def __init__(self, connection):
        self.connection = connection

    def _open_access_connection(self):
        return self.connection


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


def test_exists_documento_principale_attivo_returns_true():
    cursor = FakeCursor([[SimpleNamespace(Totale=1)]])
    repository = SottofaseDocumentiRepositoryForTest(FakeConnection(cursor))

    assert repository.exists_documento_principale_attivo(7) is True
    assert cursor.executed_params == [(7, "PRINCIPALE", True)]


def test_get_documento_by_id_returns_document():
    cursor = FakeCursor([[make_documento_row()]])
    repository = SottofaseDocumentiRepositoryForTest(FakeConnection(cursor))

    result = repository.get_documento_by_id(11)

    assert result["id_documento_sottofase"] == 11
    assert result["nome_file"] == "documento.pdf"
    assert cursor.executed_params == [(11,)]
