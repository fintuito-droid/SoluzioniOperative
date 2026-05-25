from types import SimpleNamespace

from backend.repositories.procedimento_repository import ProcedimentoRepository


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


class ProcedimentoRepositoryForTest(ProcedimentoRepository):
    def __init__(self, connection):
        self.connection = connection

    def _open_access_connection(self):
        return self.connection


def test_list_procedimenti_returns_snake_case_records():
    cursor = FakeCursor(
        [
            [
                SimpleNamespace(
                    IDProcedimento=1,
                    CodiceProcedimento="PROC-1",
                    Titolo="Procedimento test",
                    Descrizione="Descrizione",
                    AziendaSoggetto="Azienda",
                    ComandoCompetenza="COM-PA",
                    SettoreCompetenza="Settore",
                    TipologiaProcedimento="Tipo",
                    StatoProcedimento="Aperto",
                    Priorita="Alta",
                    DataApertura=None,
                    DataUltimoAggiornamento=None,
                    DataScadenza=None,
                    DataChiusura=None,
                    NoteInterne="Note",
                    Attivo=True,
                    DataCreazione=None,
                    DataModifica=None,
                    ProtocolliCollegati=2,
                )
            ]
        ]
    )
    connection = FakeConnection(cursor)
    repository = ProcedimentoRepositoryForTest(connection)

    records = repository.list_procedimenti()

    assert records == [
        {
            "id_procedimento": 1,
            "codice_procedimento": "PROC-1",
            "titolo": "Procedimento test",
            "descrizione": "Descrizione",
            "azienda_soggetto": "Azienda",
            "comando_competenza": "COM-PA",
            "settore_competenza": "Settore",
            "tipologia_procedimento": "Tipo",
            "stato_procedimento": "Aperto",
            "priorita": "Alta",
            "data_apertura": None,
            "data_ultimo_aggiornamento": None,
            "data_scadenza": None,
            "data_chiusura": None,
            "note_interne": "Note",
            "attivo": True,
            "data_creazione": None,
            "data_modifica": None,
            "protocolli_collegati": 2,
        }
    ]
    assert "FROM T_Procedimenti" in cursor.executed_queries[0]
    assert cursor.closed is True
    assert connection.closed is True


def test_get_procedimento_detail_returns_none_when_not_found():
    cursor = FakeCursor([[]])
    connection = FakeConnection(cursor)
    repository = ProcedimentoRepositoryForTest(connection)

    detail = repository.get_procedimento_detail(999)

    assert detail is None
    assert cursor.executed_params == [(999,)]
    assert cursor.closed is True
    assert connection.closed is True


def test_list_protocolli_collegati_returns_linked_protocols():
    cursor = FakeCursor(
        [
            [
                SimpleNamespace(
                    IDProcedimentoProtocollo=10,
                    IDProcedimento=1,
                    IDProtocollo=123,
                    RuoloProtocollo="origine",
                    Principale=True,
                    DataCollegamento=None,
                    NoteCollegamento="nota",
                    NumeroProtocollo="18177",
                    DataProtocollo=None,
                    Oggetto="Oggetto",
                    Modalita="Entrata",
                    ComandoMittente="COM-PA",
                    TipologiaDocumento="Preventivo",
                    PercorsoDocumentoProtocollato="FileServer/test.pdf",
                )
            ]
        ]
    )
    connection = FakeConnection(cursor)
    repository = ProcedimentoRepositoryForTest(connection)

    records = repository.list_protocolli_collegati(1)

    assert records[0]["id_procedimento_protocollo"] == 10
    assert records[0]["id_protocollo"] == 123
    assert records[0]["principale"] is True
    assert records[0]["numero_protocollo"] == "18177"
    assert "INNER JOIN T_Protocolli" in cursor.executed_queries[0]


def test_count_protocolli_collegati_returns_total():
    cursor = FakeCursor([[SimpleNamespace(Totale=3)]])
    connection = FakeConnection(cursor)
    repository = ProcedimentoRepositoryForTest(connection)

    total = repository.count_protocolli_collegati(1)

    assert total == 3
    assert "COUNT(*)" in cursor.executed_queries[0]
    assert cursor.executed_params == [(1,)]
