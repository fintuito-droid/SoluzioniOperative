from datetime import datetime
from datetime import datetime
from types import SimpleNamespace

from backend.repositories.workflow_procedimento_repository import (
    WorkflowProcedimentoRepository,
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
        self.committed = False
        self.rolled_back = False
        self.closed = False

    def cursor(self):
        return self.cursor_instance

    def commit(self):
        self.committed = True

    def rollback(self):
        self.rolled_back = True

    def close(self):
        self.closed = True


class WorkflowProcedimentoRepositoryForTest(WorkflowProcedimentoRepository):
    def __init__(self, connection):
        self.connection = connection

    def _open_access_connection(self):
        return self.connection


def test_list_fasi_by_procedimento_returns_snake_case_records():
    cursor = FakeCursor(
        [
            [
                SimpleNamespace(
                    IDFase=1,
                    IDProcedimento=10,
                    CodiceFase="ISTRUTTORIA",
                    Titolo="Istruttoria",
                    Descrizione="Descrizione",
                    Ordine=1,
                    StatoFase="IN_CORSO",
                    Responsabile="Utente",
                    DataScadenza=None,
                    DataAvvio=None,
                    DataCompletamento=None,
                    Obbligatoria=True,
                    Bloccante=False,
                    Attivo=True,
                    DataCreazione=None,
                    DataModifica=None,
                )
            ]
        ]
    )
    repository = WorkflowProcedimentoRepositoryForTest(FakeConnection(cursor))

    records = repository.list_fasi_by_procedimento(10)

    assert records == [
        {
            "id_fase": 1,
            "id_procedimento": 10,
            "codice_fase": "ISTRUTTORIA",
            "titolo": "Istruttoria",
            "descrizione": "Descrizione",
            "ordine": 1,
            "stato_fase": "IN_CORSO",
            "responsabile": "Utente",
            "data_scadenza": None,
            "data_avvio": None,
            "data_completamento": None,
            "obbligatoria": True,
            "bloccante": False,
            "attivo": True,
            "data_creazione": None,
            "data_modifica": None,
        }
    ]
    assert "FROM T_ProcedimentoFasi" in cursor.executed_queries[0]
    assert cursor.executed_params == [(10,)]
    assert cursor.closed is True
    assert repository.connection.closed is True


def test_get_fase_detail_returns_none_when_missing():
    cursor = FakeCursor([[]])
    repository = WorkflowProcedimentoRepositoryForTest(FakeConnection(cursor))

    detail = repository.get_fase_detail(999)

    assert detail is None
    assert cursor.executed_params == [(999,)]


def test_crea_fase_procedimento_inserts_with_progressive_order():
    now = datetime(2026, 6, 1, 10, 36, 0)
    cursor = FakeCursor(
        [
            [SimpleNamespace(NuovoOrdine=4)],
            [],
            [SimpleNamespace(IDFase=8)],
            [
                SimpleNamespace(
                    IDFase=8,
                    IDProcedimento=10,
                    CodiceFase="NUOVA_FASE",
                    Titolo="Nuova fase",
                    Descrizione="Descrizione",
                    Ordine=4,
                    StatoFase="NON_AVVIATA",
                    Responsabile=None,
                    DataScadenza=None,
                    DataAvvio=None,
                    DataCompletamento=None,
                    Obbligatoria=False,
                    Bloccante=False,
                    Attivo=True,
                    DataCreazione=now,
                    DataModifica=now,
                )
            ],
        ]
    )
    connection = FakeConnection(cursor)
    repository = WorkflowProcedimentoRepositoryForTest(connection)

    created = repository.crea_fase_procedimento(
        id_procedimento=10,
        titolo="Nuova fase",
        descrizione="Descrizione",
        data_creazione=now,
    )

    assert created["id_fase"] == 8
    assert created["titolo"] == "Nuova fase"
    assert created["ordine"] == 4
    assert "INSERT INTO T_ProcedimentoFasi" in cursor.executed_queries[1]
    assert cursor.executed_params[1][0] == 10
    assert cursor.executed_params[1][2] == "Nuova fase"
    assert connection.committed is True


def test_aggiorna_fase_procedimento_updates_title_and_description():
    now = datetime(2026, 6, 1, 10, 36, 0)
    cursor = FakeCursor(
        [
            [],
            [
                SimpleNamespace(
                    IDFase=8,
                    IDProcedimento=10,
                    CodiceFase="NUOVA_FASE",
                    Titolo="Titolo aggiornato",
                    Descrizione="Descrizione aggiornata",
                    Ordine=4,
                    StatoFase="NON_AVVIATA",
                    Responsabile=None,
                    DataScadenza=None,
                    DataAvvio=None,
                    DataCompletamento=None,
                    Obbligatoria=False,
                    Bloccante=False,
                    Attivo=True,
                    DataCreazione=now,
                    DataModifica=now,
                )
            ],
        ]
    )
    connection = FakeConnection(cursor)
    repository = WorkflowProcedimentoRepositoryForTest(connection)

    updated = repository.aggiorna_fase_procedimento(
        id_procedimento=10,
        id_fase=8,
        titolo="Titolo aggiornato",
        descrizione="Descrizione aggiornata",
        data_modifica=now,
    )

    assert updated["id_fase"] == 8
    assert updated["titolo"] == "Titolo aggiornato"
    assert "UPDATE T_ProcedimentoFasi" in cursor.executed_queries[0]
    assert cursor.executed_params[0][0] == "Titolo aggiornato"
    assert cursor.executed_params[0][3] == 8
    assert cursor.executed_params[0][4] == 10
    assert connection.committed is True


def test_list_sottofasi_by_fase_returns_records():
    cursor = FakeCursor(
        [
            [
                SimpleNamespace(
                    IDSottofase=2,
                    IDFase=1,
                    IDCatalogoSottofase=7,
                    CodiceSottofase="EMAIL",
                    Titolo="Email",
                    Descrizione="Invio email",
                    Ordine=2,
                    StatoSottofase="NON_AVVIATA",
                    Icona="mdi-email-outline",
                    Colore="indigo",
                    Responsabile=None,
                    DataScadenza=None,
                    DataAvvio=None,
                    DataCompletamento=None,
                    NoteInterne="nota",
                    Attivo=True,
                    DataCreazione=None,
                    DataModifica=None,
                )
            ]
        ]
    )
    repository = WorkflowProcedimentoRepositoryForTest(FakeConnection(cursor))

    records = repository.list_sottofasi_by_fase(1)

    assert records[0]["id_sottofase"] == 2
    assert records[0]["id_fase"] == 1
    assert records[0]["codice_sottofase"] == "EMAIL"
    assert records[0]["attivo"] is True
    assert "FROM T_ProcedimentoSottofasi" in cursor.executed_queries[0]


def test_crea_sottofase_fase_inserts_with_progressive_order():
    now = datetime(2026, 6, 1, 10, 36, 0)
    cursor = FakeCursor(
        [
            [SimpleNamespace(NuovoOrdine=3)],
            [],
            [SimpleNamespace(IDSottofase=12)],
            [
                SimpleNamespace(
                    IDSottofase=12,
                    IDFase=8,
                    IDCatalogoSottofase=None,
                    CodiceSottofase="SF-TEST",
                    Titolo="Sottofase",
                    Descrizione="Descrizione",
                    Ordine=3,
                    StatoSottofase="NON_AVVIATA",
                    Icona="mdi-checkbox-blank-circle-outline",
                    Colore="grey",
                    Responsabile="Mario Rossi",
                    DataScadenza=None,
                    DataAvvio=None,
                    DataCompletamento=None,
                    NoteInterne=None,
                    Attivo=True,
                    DataCreazione=now,
                    DataModifica=now,
                )
            ],
        ]
    )
    connection = FakeConnection(cursor)
    repository = WorkflowProcedimentoRepositoryForTest(connection)

    created = repository.crea_sottofase_fase(
        id_fase=8,
        codice_sottofase="SF-TEST",
        titolo="Sottofase",
        descrizione="Descrizione",
        responsabile="Mario Rossi",
        data_scadenza=None,
        data_creazione=now,
    )

    assert created["id_sottofase"] == 12
    assert created["codice_sottofase"] == "SF-TEST"
    assert created["titolo"] == "Sottofase"
    assert created["ordine"] == 3
    assert "INSERT INTO T_ProcedimentoSottofasi" in cursor.executed_queries[1]
    assert cursor.executed_params[1][0] == 8
    assert cursor.executed_params[1][2] == "SF-TEST"
    assert cursor.executed_params[1][3] == "Sottofase"
    assert connection.committed is True


def test_aggiorna_sottofase_fase_updates_editable_fields():
    now = datetime(2026, 6, 1, 10, 36, 0)
    cursor = FakeCursor(
        [
            [
                SimpleNamespace(
                    IDSottofase=12,
                    IDFase=8,
                    IDCatalogoSottofase=None,
                    CodiceSottofase="SF-OLD",
                    Titolo="Sottofase vecchia",
                    Descrizione="Old",
                    Ordine=3,
                    StatoSottofase="NON_AVVIATA",
                    Icona="mdi-checkbox-blank-circle-outline",
                    Colore="grey",
                    Responsabile=None,
                    DataScadenza=None,
                    DataAvvio=None,
                    DataCompletamento=None,
                    NoteInterne=None,
                    Attivo=True,
                    DataCreazione=now,
                    DataModifica=now,
                )
            ],
            [],
            [
                SimpleNamespace(
                    IDSottofase=12,
                    IDFase=8,
                    IDCatalogoSottofase=None,
                    CodiceSottofase="SF-UPD",
                    Titolo="Sottofase aggiornata",
                    Descrizione="Nuova",
                    Ordine=3,
                    StatoSottofase="NON_AVVIATA",
                    Icona="mdi-checkbox-blank-circle-outline",
                    Colore="grey",
                    Responsabile="Mario Rossi",
                    DataScadenza=None,
                    DataAvvio=None,
                    DataCompletamento=None,
                    NoteInterne=None,
                    Attivo=True,
                    DataCreazione=now,
                    DataModifica=now,
                )
            ],
        ]
    )
    connection = FakeConnection(cursor)
    repository = WorkflowProcedimentoRepositoryForTest(connection)

    updated = repository.aggiorna_sottofase_fase(
        id_fase=8,
        id_sottofase=12,
        codice_sottofase="SF-UPD",
        titolo="Sottofase aggiornata",
        descrizione="Nuova",
        responsabile="Mario Rossi",
        data_scadenza=None,
        data_modifica=now,
    )

    assert updated["id_sottofase"] == 12
    assert updated["codice_sottofase"] == "SF-UPD"
    assert updated["titolo"] == "Sottofase aggiornata"
    assert "UPDATE T_ProcedimentoSottofasi" in cursor.executed_queries[1]
    assert cursor.executed_params[1][0] == "SF-UPD"
    assert cursor.executed_params[1][1] == "Sottofase aggiornata"
    assert cursor.executed_params[1][6] == 12
    assert cursor.executed_params[1][7] == 8
    assert connection.committed is True


def test_list_catalogo_sottofasi_filters_active_by_default():
    cursor = FakeCursor(
        [
            [
                SimpleNamespace(
                    IDCatalogoSottofase=5,
                    CodiceSottofase="CONTROLLO",
                    Titolo="Controllo finale",
                    Descrizione="Verifica",
                    Icona="mdi-check-decagram",
                    Colore="teal",
                    Categoria="CONTROLLO",
                    OrdineDefault=80,
                    Attivo=True,
                    DataCreazione=None,
                    DataModifica=None,
                )
            ]
        ]
    )
    repository = WorkflowProcedimentoRepositoryForTest(FakeConnection(cursor))

    records = repository.list_catalogo_sottofasi()

    assert records[0]["id_catalogo_sottofase"] == 5
    assert records[0]["codice_sottofase"] == "CONTROLLO"
    assert records[0]["ordine_default"] == 80
    assert "WHERE Attivo = ?" in cursor.executed_queries[0]
    assert cursor.executed_params == [(True,)]


def test_list_catalogo_sottofasi_can_return_all_records():
    cursor = FakeCursor([[]])
    repository = WorkflowProcedimentoRepositoryForTest(FakeConnection(cursor))

    records = repository.list_catalogo_sottofasi(attivo_only=False)

    assert records == []
    assert "WHERE Attivo = ?" not in cursor.executed_queries[0]
    assert cursor.executed_params == [None]
