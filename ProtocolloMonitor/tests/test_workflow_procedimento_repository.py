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
            [SimpleNamespace(MaxOrdine=3)],
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


def _step_row(
    *,
    id_step,
    id_fase,
    codice,
    titolo,
    ordine,
    stato="NON_AVVIATO",
    now=None,
):
    return SimpleNamespace(
        IDStepOrizzontale=id_step,
        IDFase=id_fase,
        CodiceStep=codice,
        TitoloStep=titolo,
        Ordine=ordine,
        StatoStep=stato,
        DataAvvio=None,
        DataCompletamento=None,
        Attivo=True,
        DataCreazione=now,
        DataModifica=now,
    )


def test_list_step_orizzontali_by_fase_returns_fixed_steps():
    now = datetime(2026, 6, 1, 10, 36, 0)
    cursor = FakeCursor(
        [
            [
                _step_row(
                    id_step=1,
                    id_fase=8,
                    codice="REDIGI",
                    titolo="Redigi",
                    ordine=1,
                    now=now,
                ),
                _step_row(
                    id_step=2,
                    id_fase=8,
                    codice="REVISIONA",
                    titolo="Revisiona",
                    ordine=2,
                    now=now,
                ),
            ],
        ]
    )
    repository = WorkflowProcedimentoRepositoryForTest(FakeConnection(cursor))

    records = repository.list_step_orizzontali_by_fase(8)

    assert [record["codice_step"] for record in records] == ["REDIGI", "REVISIONA"]
    assert records[0]["stato_step"] == "NON_AVVIATO"
    assert "FROM T_FaseStepOrizzontali" in cursor.executed_queries[0]
    assert cursor.executed_params == [(8, True)]


def test_inizializza_step_orizzontali_creates_missing_fixed_steps():
    now = datetime(2026, 6, 1, 10, 36, 0)
    cursor = FakeCursor(
        [
            [],
            [],
            [],
            [],
            [],
            [],
            [
                _step_row(id_step=1, id_fase=8, codice="REDIGI", titolo="Redigi", ordine=1, now=now),
                _step_row(id_step=2, id_fase=8, codice="REVISIONA", titolo="Revisiona", ordine=2, now=now),
                _step_row(id_step=3, id_fase=8, codice="FIRMA", titolo="Firma", ordine=3, now=now),
                _step_row(id_step=4, id_fase=8, codice="PROTOCOLLA", titolo="Protocolla", ordine=4, now=now),
                _step_row(id_step=5, id_fase=8, codice="FINE", titolo="Fine", ordine=5, now=now),
            ],
        ]
    )
    connection = FakeConnection(cursor)
    repository = WorkflowProcedimentoRepositoryForTest(connection)

    report = repository.inizializza_step_orizzontali_fase(
        id_fase=8,
        data_creazione=now,
    )

    assert report["step_creati"] == [
        "REDIGI",
        "REVISIONA",
        "FIRMA",
        "PROTOCOLLA",
        "FINE",
    ]
    assert report["step_gia_presenti"] == []
    assert [step["codice_step"] for step in report["step"]] == [
        "REDIGI",
        "REVISIONA",
        "FIRMA",
        "PROTOCOLLA",
        "FINE",
    ]
    assert all(step["stato_step"] == "NON_AVVIATO" for step in report["step"])
    assert sum(
        "INSERT INTO T_FaseStepOrizzontali" in query
        for query in cursor.executed_queries
    ) == 5
    assert cursor.executed_params[1][0] == 8
    assert cursor.executed_params[1][1] == "REDIGI"
    assert cursor.executed_params[1][4] == "NON_AVVIATO"
    assert connection.committed is True


def test_inizializza_step_orizzontali_is_idempotent():
    now = datetime(2026, 6, 1, 10, 36, 0)
    cursor = FakeCursor(
        [
            [
                SimpleNamespace(CodiceStep="REDIGI"),
                SimpleNamespace(CodiceStep="REVISIONA"),
                SimpleNamespace(CodiceStep="FIRMA"),
                SimpleNamespace(CodiceStep="PROTOCOLLA"),
                SimpleNamespace(CodiceStep="FINE"),
            ],
            [
                _step_row(id_step=1, id_fase=8, codice="REDIGI", titolo="Redigi", ordine=1, now=now),
                _step_row(id_step=2, id_fase=8, codice="REVISIONA", titolo="Revisiona", ordine=2, now=now),
                _step_row(id_step=3, id_fase=8, codice="FIRMA", titolo="Firma", ordine=3, now=now),
                _step_row(id_step=4, id_fase=8, codice="PROTOCOLLA", titolo="Protocolla", ordine=4, now=now),
                _step_row(id_step=5, id_fase=8, codice="FINE", titolo="Fine", ordine=5, now=now),
            ],
        ]
    )
    connection = FakeConnection(cursor)
    repository = WorkflowProcedimentoRepositoryForTest(connection)

    report = repository.inizializza_step_orizzontali_fase(
        id_fase=8,
        data_creazione=now,
    )

    assert report["step_creati"] == []
    assert report["step_gia_presenti"] == [
        "REDIGI",
        "REVISIONA",
        "FIRMA",
        "PROTOCOLLA",
        "FINE",
    ]
    assert len(report["step"]) == 5
    assert not any(
        "INSERT INTO T_FaseStepOrizzontali" in query
        for query in cursor.executed_queries
    )
    assert cursor.executed_params[0] == (8,)
    assert connection.committed is True


def test_configura_step_orizzontali_istanza_fine_disables_and_recreates_minimal_workflow():
    now = datetime(2026, 6, 1, 10, 36, 0)
    cursor = FakeCursor(
        [
            [],
            [],
            [],
            [
                _step_row(
                    id_step=10,
                    id_fase=8,
                    codice="ISTANZA",
                    titolo="Istanza",
                    ordine=1,
                    now=now,
                ),
                _step_row(
                    id_step=11,
                    id_fase=8,
                    codice="FINE",
                    titolo="Fine",
                    ordine=2,
                    now=now,
                ),
            ],
        ]
    )
    connection = FakeConnection(cursor)
    repository = WorkflowProcedimentoRepositoryForTest(connection)

    records = repository.configura_step_orizzontali_istanza_fine(
        id_fase=8,
        data_modifica=now,
    )

    assert [step["codice_step"] for step in records] == ["ISTANZA", "FINE"]
    assert "SET Attivo = ?" in cursor.executed_queries[0]
    assert cursor.executed_params[0] == (False, now, 8, True)
    assert sum(
        "INSERT INTO T_FaseStepOrizzontali" in query
        for query in cursor.executed_queries
    ) == 2
    assert cursor.executed_params[1][1] == "ISTANZA"
    assert cursor.executed_params[2][1] == "FINE"
    assert connection.committed is True


def test_has_step_orizzontali_avviati_detects_non_initial_active_steps():
    cursor = FakeCursor([[SimpleNamespace(Totale=1)]])
    repository = WorkflowProcedimentoRepositoryForTest(FakeConnection(cursor))

    result = repository.has_step_orizzontali_avviati(8)

    assert result is True
    assert "UCASE(StatoStep)" in cursor.executed_queries[0]
    assert cursor.executed_params == [(8, True, "NON_AVVIATO")]


def test_has_step_orizzontali_fase_counts_inactive_records_too():
    cursor = FakeCursor([[SimpleNamespace(Totale=1)]])
    repository = WorkflowProcedimentoRepositoryForTest(FakeConnection(cursor))

    result = repository.has_step_orizzontali_fase(8)

    assert result is True
    assert "FROM T_FaseStepOrizzontali" in cursor.executed_queries[0]
    assert "Attivo" not in cursor.executed_queries[0]
    assert cursor.executed_params == [(8,)]


def test_configura_step_orizzontali_predefinito_disables_and_recreates_standard_workflow():
    now = datetime(2026, 6, 1, 10, 36, 0)
    cursor = FakeCursor(
        [
            [],
            [],
            [],
            [],
            [],
            [],
            [
                _step_row(id_step=1, id_fase=8, codice="REDIGI", titolo="Redigi", ordine=1, now=now),
                _step_row(id_step=2, id_fase=8, codice="REVISIONA", titolo="Revisiona", ordine=2, now=now),
                _step_row(id_step=3, id_fase=8, codice="FIRMA", titolo="Firma", ordine=3, now=now),
                _step_row(id_step=4, id_fase=8, codice="PROTOCOLLA", titolo="Protocolla", ordine=4, now=now),
                _step_row(id_step=5, id_fase=8, codice="FINE", titolo="Fine", ordine=5, now=now),
            ],
        ]
    )
    connection = FakeConnection(cursor)
    repository = WorkflowProcedimentoRepositoryForTest(connection)

    records = repository.configura_step_orizzontali_predefinito(
        id_fase=8,
        data_modifica=now,
    )

    assert [step["codice_step"] for step in records] == [
        "REDIGI",
        "REVISIONA",
        "FIRMA",
        "PROTOCOLLA",
        "FINE",
    ]
    assert "SET Attivo = ?" in cursor.executed_queries[0]
    assert sum(
        "INSERT INTO T_FaseStepOrizzontali" in query
        for query in cursor.executed_queries
    ) == 5
    assert cursor.executed_params[1][1] == "REDIGI"
    assert cursor.executed_params[5][1] == "FINE"
    assert connection.committed is True


def test_inserisci_step_orizzontale_dopo_shifts_and_renumbers():
    now = datetime(2026, 6, 1, 10, 36, 0)
    cursor = FakeCursor(
        [
            [
                _step_row(
                    id_step=2,
                    id_fase=8,
                    codice="REVISIONA",
                    titolo="Revisiona",
                    ordine=2,
                    now=now,
                )
            ],
            [],
            [],
            [
                SimpleNamespace(IDStepOrizzontale=1),
                SimpleNamespace(IDStepOrizzontale=2),
                SimpleNamespace(IDStepOrizzontale=99),
                SimpleNamespace(IDStepOrizzontale=3),
            ],
            [],
            [],
            [],
            [],
            [
                _step_row(id_step=1, id_fase=8, codice="REDIGI", titolo="Redigi", ordine=1, now=now),
                _step_row(id_step=2, id_fase=8, codice="REVISIONA", titolo="Revisiona", ordine=2, now=now),
                _step_row(id_step=99, id_fase=8, codice="NUOVO_STEP", titolo="Nuovo step", ordine=3, now=now),
                _step_row(id_step=3, id_fase=8, codice="FIRMA", titolo="Firma", ordine=4, now=now),
            ],
        ]
    )
    connection = FakeConnection(cursor)
    repository = WorkflowProcedimentoRepositoryForTest(connection)

    records = repository.inserisci_step_orizzontale_dopo(
        id_fase=8,
        id_step=2,
        titolo_step="Nuovo step",
        codice_step="NUOVO_STEP",
        data_creazione=now,
    )

    assert [step["ordine"] for step in records] == [1, 2, 3, 4]
    assert "Ordine = Ordine + 1" in cursor.executed_queries[1]
    assert cursor.executed_params[1] == (now, 8, True, 2)
    assert cursor.executed_params[2][1] == "NUOVO_STEP"
    assert "SELECT IDStepOrizzontale" in cursor.executed_queries[3]
    assert connection.committed is True


def test_elimina_logicamente_step_orizzontale_disables_and_renumbers():
    now = datetime(2026, 6, 1, 10, 36, 0)
    cursor = FakeCursor(
        [
            [
                _step_row(
                    id_step=2,
                    id_fase=8,
                    codice="REVISIONA",
                    titolo="Revisiona",
                    ordine=2,
                    now=now,
                )
            ],
            [SimpleNamespace(Totale=3)],
            [],
            [
                SimpleNamespace(IDStepOrizzontale=1),
                SimpleNamespace(IDStepOrizzontale=3),
            ],
            [],
            [],
            [
                _step_row(id_step=1, id_fase=8, codice="REDIGI", titolo="Redigi", ordine=1, now=now),
                _step_row(id_step=3, id_fase=8, codice="FIRMA", titolo="Firma", ordine=2, now=now),
            ],
        ]
    )
    connection = FakeConnection(cursor)
    repository = WorkflowProcedimentoRepositoryForTest(connection)

    records = repository.elimina_logicamente_step_orizzontale(
        id_fase=8,
        id_step=2,
        data_modifica=now,
    )

    assert [step["codice_step"] for step in records] == ["REDIGI", "FIRMA"]
    assert "SET Attivo = ?" in cursor.executed_queries[2]
    assert cursor.executed_params[2] == (False, now, 2, 8, True)
    assert connection.committed is True


def test_elimina_logicamente_step_orizzontale_blocks_completed_step_and_rolls_back():
    now = datetime(2026, 6, 1, 10, 36, 0)
    cursor = FakeCursor(
        [
            [
                _step_row(
                    id_step=2,
                    id_fase=8,
                    codice="REVISIONA",
                    titolo="Revisiona",
                    ordine=2,
                    stato="COMPLETATO",
                    now=now,
                )
            ],
            [SimpleNamespace(Totale=3)],
        ]
    )
    connection = FakeConnection(cursor)
    repository = WorkflowProcedimentoRepositoryForTest(connection)

    try:
        repository.elimina_logicamente_step_orizzontale(
            id_fase=8,
            id_step=2,
            data_modifica=now,
        )
    except ValueError as exc:
        assert "completato" in str(exc)
    else:
        raise AssertionError("ValueError atteso")

    assert connection.rolled_back is True


def test_collega_protocollo_step_istanza_updates_step_and_bridge():
    now = datetime(2026, 6, 1, 10, 36, 0)
    cursor = FakeCursor(
        [
            [
                _step_row(
                    id_step=2,
                    id_fase=8,
                    codice="ISTANZA",
                    titolo="Istanza",
                    ordine=1,
                    now=now,
                )
            ],
            [SimpleNamespace(Totale=1)],
            [],
            [SimpleNamespace(Totale=0)],
            [],
            [
                _step_row(
                    id_step=2,
                    id_fase=8,
                    codice="ISTANZA",
                    titolo="Istanza",
                    ordine=1,
                    stato="COMPLETATO",
                    now=now,
                )
            ],
        ]
    )
    connection = FakeConnection(cursor)
    repository = WorkflowProcedimentoRepositoryForTest(connection)

    records = repository.collega_protocollo_step_istanza(
        id_procedimento=7,
        id_fase=8,
        id_step=2,
        id_protocollo=123,
        data_modifica=now,
    )

    assert records[0]["codice_step"] == "ISTANZA"
    assert records[0]["stato_step"] == "COMPLETATO"
    assert "SET IDProtocolloCollegato = ?" in cursor.executed_queries[2]
    assert cursor.executed_params[2] == (
        123,
        "COMPLETATO",
        now,
        now,
        2,
        8,
        True,
    )
    assert "INSERT INTO T_ProcedimentoProtocolli" in cursor.executed_queries[4]
    assert cursor.executed_params[4][0] == 7
    assert cursor.executed_params[4][1] == 123
    assert cursor.executed_params[4][2] == "ISTANZA"
    assert connection.committed is True


def test_avvia_step_redigi_sets_in_corso_and_data_avvio():
    now = datetime(2026, 6, 1, 10, 36, 0)
    cursor = FakeCursor(
        [
            [
                _step_row(
                    id_step=1,
                    id_fase=8,
                    codice="REDIGI",
                    titolo="Redigi",
                    ordine=1,
                    now=now,
                )
            ],
            [],
            [
                _step_row(
                    id_step=1,
                    id_fase=8,
                    codice="REDIGI",
                    titolo="Redigi",
                    ordine=1,
                    stato="IN_CORSO",
                    now=now,
                )
            ],
        ]
    )
    connection = FakeConnection(cursor)
    repository = WorkflowProcedimentoRepositoryForTest(connection)

    records = repository.avvia_step_redigi(
        id_fase=8,
        id_step=1,
        data_modifica=now,
    )

    assert records[0]["stato_step"] == "IN_CORSO"
    assert "SET StatoStep = ?" in cursor.executed_queries[1]
    assert cursor.executed_params[1] == ("IN_CORSO", now, now, 1, 8, True)
    assert connection.committed is True


def test_completa_step_redigi_sets_completed_and_data_completamento():
    now = datetime(2026, 6, 1, 10, 36, 0)
    cursor = FakeCursor(
        [
            [
                _step_row(
                    id_step=1,
                    id_fase=8,
                    codice="REDIGI",
                    titolo="Redigi",
                    ordine=1,
                    stato="IN_CORSO",
                    now=now,
                )
            ],
            [],
            [
                _step_row(
                    id_step=1,
                    id_fase=8,
                    codice="REDIGI",
                    titolo="Redigi",
                    ordine=1,
                    stato="COMPLETATO",
                    now=now,
                )
            ],
        ]
    )
    connection = FakeConnection(cursor)
    repository = WorkflowProcedimentoRepositoryForTest(connection)

    records = repository.completa_step_redigi(
        id_fase=8,
        id_step=1,
        data_modifica=now,
    )

    assert records[0]["stato_step"] == "COMPLETATO"
    assert "SET StatoStep = ?" in cursor.executed_queries[1]
    assert cursor.executed_params[1] == ("COMPLETATO", now, now, 1, 8, True)
    assert connection.committed is True


def test_aggiorna_note_step_redigi_persists_note():
    now = datetime(2026, 6, 1, 10, 36, 0)
    cursor = FakeCursor(
        [
            [
                _step_row(
                    id_step=1,
                    id_fase=8,
                    codice="REDIGI",
                    titolo="Redigi",
                    ordine=1,
                    now=now,
                )
            ],
            [],
            [
                _step_row(
                    id_step=1,
                    id_fase=8,
                    codice="REDIGI",
                    titolo="Redigi",
                    ordine=1,
                    now=now,
                )
            ],
        ]
    )
    connection = FakeConnection(cursor)
    repository = WorkflowProcedimentoRepositoryForTest(connection)

    records = repository.aggiorna_note_step_redigi(
        id_fase=8,
        id_step=1,
        note_operative="Nota operativa",
        data_modifica=now,
    )

    assert records[0]["codice_step"] == "REDIGI"
    assert "SET NoteOperative = ?" in cursor.executed_queries[1]
    assert cursor.executed_params[1] == ("Nota operativa", now, 1, 8, True)
    assert connection.committed is True


def test_avvia_step_redigi_rejects_non_redigi_and_rolls_back():
    now = datetime(2026, 6, 1, 10, 36, 0)
    cursor = FakeCursor(
        [
            [
                _step_row(
                    id_step=2,
                    id_fase=8,
                    codice="FIRMA",
                    titolo="Firma",
                    ordine=2,
                    now=now,
                )
            ],
        ]
    )
    connection = FakeConnection(cursor)
    repository = WorkflowProcedimentoRepositoryForTest(connection)

    try:
        repository.avvia_step_redigi(
            id_fase=8,
            id_step=2,
            data_modifica=now,
        )
    except ValueError as exc:
        assert "Redigi" in str(exc)
    else:
        raise AssertionError("ValueError atteso")

    assert connection.rolled_back is True


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
