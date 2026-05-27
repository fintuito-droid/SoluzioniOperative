from datetime import datetime

import pytest

from backend.repositories.sottofase_workflow_action_repository import (
    SottofaseWorkflowActionRepository,
)


class FakeCursor:
    def __init__(self, *, rowcount=1, fail_on_execute=None):
        self.rowcount = rowcount
        self.fail_on_execute = fail_on_execute
        self.executed_queries = []
        self.executed_params = []
        self.execute_count = 0
        self.closed = False

    def execute(self, query, params):
        self.execute_count += 1

        if self.fail_on_execute == self.execute_count:
            raise RuntimeError("errore execute")

        self.executed_queries.append(query)
        self.executed_params.append(params)
        return self

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


class RepositoryForTest(SottofaseWorkflowActionRepository):
    def __init__(self, connection):
        self.connection = connection

    def _open_access_connection(self):
        return self.connection


def test_repository_updates_sottofase_and_inserts_history_in_transaction():
    cursor = FakeCursor()
    connection = FakeConnection(cursor)
    repository = RepositoryForTest(connection)
    now = datetime(2026, 5, 27, 12, 0, 0)

    repository.applica_azione_workflow_sottofase(
        id_sottofase=5,
        step_corrente="REDIGI",
        step_destinazione="REVISIONA",
        ordine_step=10,
        testo_operatore="testo",
        utente_operatore="utente",
        data_azione=now,
    )

    assert len(cursor.executed_queries) == 2
    assert "UPDATE T_ProcedimentoSottofasi" in cursor.executed_queries[0]
    assert "INSERT INTO T_SottofaseStepOperativi" in cursor.executed_queries[1]
    assert cursor.executed_params[0] == (
        "REVISIONA",
        "testo",
        now,
        "utente",
        now,
        5,
    )
    assert cursor.executed_params[1] == (
        5,
        "REDIGI",
        10,
        "COMPLETATO",
        now,
        now,
        "testo",
        "utente",
        "utente",
        now,
        now,
    )
    assert connection.committed is True
    assert connection.rolled_back is False
    assert cursor.closed is True
    assert connection.closed is True


def test_repository_rolls_back_when_update_matches_no_rows():
    cursor = FakeCursor(rowcount=0)
    connection = FakeConnection(cursor)
    repository = RepositoryForTest(connection)

    with pytest.raises(RuntimeError):
        repository.applica_azione_workflow_sottofase(
            id_sottofase=999,
            step_corrente="REDIGI",
            step_destinazione="REVISIONA",
            ordine_step=10,
            testo_operatore=None,
            utente_operatore=None,
            data_azione=datetime(2026, 5, 27, 12, 0, 0),
        )

    assert len(cursor.executed_queries) == 1
    assert connection.committed is False
    assert connection.rolled_back is True
    assert cursor.closed is True
    assert connection.closed is True


def test_repository_rolls_back_when_history_insert_fails():
    cursor = FakeCursor(fail_on_execute=2)
    connection = FakeConnection(cursor)
    repository = RepositoryForTest(connection)

    with pytest.raises(RuntimeError):
        repository.applica_azione_workflow_sottofase(
            id_sottofase=5,
            step_corrente="REDIGI",
            step_destinazione="REVISIONA",
            ordine_step=10,
            testo_operatore=None,
            utente_operatore=None,
            data_azione=datetime(2026, 5, 27, 12, 0, 0),
        )

    assert len(cursor.executed_queries) == 1
    assert connection.committed is False
    assert connection.rolled_back is True
    assert cursor.closed is True
    assert connection.closed is True


def test_repository_closes_sottofase_using_existing_fields():
    cursor = FakeCursor()
    connection = FakeConnection(cursor)
    repository = RepositoryForTest(connection)
    now = datetime(2026, 5, 27, 12, 0, 0)

    repository.applica_azione_workflow_sottofase(
        id_sottofase=5,
        step_corrente="FINE",
        step_destinazione="FINE",
        ordine_step=50,
        testo_operatore="chiusa",
        utente_operatore="utente",
        data_azione=now,
        chiudi_sottofase=True,
    )

    assert "StatoSottofase" in cursor.executed_queries[0]
    assert cursor.executed_params[0] == (
        "FINE",
        "chiusa",
        now,
        "utente",
        now,
        "COMPLETATA",
        now,
        5,
    )
