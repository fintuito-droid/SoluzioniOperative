from datetime import datetime

import pytest

from backend.repositories.sottofase_partecipanti_repository import (
    SottofasePartecipantiRepository,
)


class FakeRows:
    def __init__(self, rows=None, one=None):
        self.rows = rows or []
        self.one = one

    def fetchone(self):
        return self.one

    def fetchall(self):
        return self.rows


class FakeCursor:
    def __init__(
        self,
        *,
        table_exists=False,
        existing_columns=None,
        existing_indexes=None,
        fail_on_insert=False,
        fail_on_update=False,
    ):
        self.table_exists_value = table_exists
        self.existing_columns = existing_columns or set()
        self.existing_indexes = existing_indexes or set()
        self.fail_on_insert = fail_on_insert
        self.fail_on_update = fail_on_update
        self.calls = []
        self.rowcount = 1

    def tables(self, table=None):
        return FakeRows(one=object() if self.table_exists_value else None)

    def columns(self, table=None, column=None):
        return FakeRows(one=object() if column in self.existing_columns else None)

    def statistics(self, table=None):
        return FakeRows(
            rows=[
                {"index_name": index_name}
                for index_name in self.existing_indexes
            ]
        )

    def execute(self, query, params=None):
        self.calls.append((query, params))

        if query.strip().upper().startswith("INSERT") and self.fail_on_insert:
            raise RuntimeError("insert fallito")
        if query.strip().upper().startswith("UPDATE") and self.fail_on_update:
            raise RuntimeError("update fallito")

    def fetchone(self):
        return (77,)

    def fetchall(self):
        return []

    def close(self):
        pass


class FakeConnection:
    def __init__(self, cursor):
        self._cursor = cursor
        self.committed = False
        self.rolled_back = False
        self.closed = False

    def cursor(self):
        return self._cursor

    def commit(self):
        self.committed = True

    def rollback(self):
        self.rolled_back = True

    def close(self):
        self.closed = True


class FakeRepository(SottofasePartecipantiRepository):
    def __init__(self, connection):
        super().__init__()
        self.connection = connection

    def _open_access_connection(self, **connect_options):
        return self.connection


def test_ensure_schema_creates_table_and_indexes_when_missing():
    cursor = FakeCursor(table_exists=False)
    connection = FakeConnection(cursor)
    repository = FakeRepository(connection)

    result = repository.ensure_schema()

    assert result["table_created"] is True
    assert result["columns_added"] == []
    assert len(result["indexes_created"]) == 5
    assert connection.committed is True
    assert any("CREATE TABLE T_SottofasePartecipanti" in call[0] for call in cursor.calls)
    assert sum(1 for call in cursor.calls if "CREATE INDEX" in call[0]) == 5


def test_ensure_schema_does_not_recreate_existing_table_or_indexes():
    existing_indexes = {
        "IX_T_SottofasePartecipanti_IDSottofase",
        "IX_T_SottofasePartecipanti_IDStepOperativo",
        "IX_T_SottofasePartecipanti_Ruolo",
        "IX_T_SottofasePartecipanti_Stato",
        "IX_T_SottofasePartecipanti_Attivo",
    }
    cursor = FakeCursor(
        table_exists=True,
        existing_columns={"IDStepOperativo", "PartecipanteObbligatorio"},
        existing_indexes=existing_indexes,
    )
    connection = FakeConnection(cursor)
    repository = FakeRepository(connection)

    result = repository.ensure_schema()

    assert result["table_created"] is False
    assert result["columns_added"] == []
    assert result["indexes_created"] == []
    assert not any("CREATE TABLE" in call[0] for call in cursor.calls)
    assert not any("CREATE INDEX" in call[0] for call in cursor.calls)


def test_ensure_schema_adds_step_field_and_index_when_missing():
    cursor = FakeCursor(table_exists=True)
    connection = FakeConnection(cursor)
    repository = FakeRepository(connection)

    result = repository.ensure_schema()

    assert result["table_created"] is False
    assert result["columns_added"] == ["IDStepOperativo", "PartecipanteObbligatorio"]
    assert "IX_T_SottofasePartecipanti_IDStepOperativo" in result["indexes_created"]
    assert any("ADD COLUMN IDStepOperativo" in call[0] for call in cursor.calls)
    assert any(
        "ADD COLUMN PartecipanteObbligatorio" in call[0]
        for call in cursor.calls
    )


def test_repository_inserts_participant_in_transaction():
    cursor = FakeCursor(table_exists=True)
    connection = FakeConnection(cursor)
    repository = FakeRepository(connection)

    id_partecipante = repository.inserisci_partecipante(
        id_sottofase=5,
        id_step_operativo=12,
        nome_visualizzato="Mario Rossi",
        email="mario.rossi@example.it",
        ruolo="REVISORE",
        stato_partecipante="ASSEGNATO",
        partecipante_obbligatorio=True,
        ordine=1,
        colore_avatar="#1976D2",
        iniziali="MR",
        note_partecipante="Revisore tecnico",
        data_creazione=datetime(2026, 6, 1, 10, 0, 0),
    )

    assert id_partecipante == 77
    assert connection.committed is True
    assert connection.rolled_back is False
    assert any("INSERT INTO T_SottofasePartecipanti" in call[0] for call in cursor.calls)


def test_repository_rolls_back_when_insert_fails():
    cursor = FakeCursor(table_exists=True, fail_on_insert=True)
    connection = FakeConnection(cursor)
    repository = FakeRepository(connection)

    with pytest.raises(RuntimeError):
            repository.inserisci_partecipante(
                id_sottofase=5,
                id_step_operativo=None,
                nome_visualizzato="Mario Rossi",
                email="mario.rossi@example.it",
                ruolo="REVISORE",
                stato_partecipante="ASSEGNATO",
                partecipante_obbligatorio=True,
                ordine=1,
            colore_avatar="#1976D2",
            iniziali="MR",
            note_partecipante=None,
            data_creazione=datetime(2026, 6, 1, 10, 0, 0),
        )

    assert connection.committed is False
    assert connection.rolled_back is True


def test_repository_completes_step_participant_in_transaction():
    cursor = FakeCursor(table_exists=True)
    connection = FakeConnection(cursor)
    repository = FakeRepository(connection)

    repository.completa_partecipante_step(
        id_sottofase=5,
        id_step_operativo=12,
        id_partecipante=42,
        data_azione=datetime(2026, 6, 1, 13, 0, 0),
    )

    assert connection.committed is True
    assert connection.rolled_back is False
    assert any(
        "UPDATE T_SottofasePartecipanti" in call[0]
        for call in cursor.calls
    )


def test_repository_rolls_back_when_complete_participant_fails():
    cursor = FakeCursor(table_exists=True, fail_on_update=True)
    connection = FakeConnection(cursor)
    repository = FakeRepository(connection)

    with pytest.raises(RuntimeError):
        repository.completa_partecipante_step(
            id_sottofase=5,
            id_step_operativo=12,
            id_partecipante=42,
            data_azione=datetime(2026, 6, 1, 13, 0, 0),
        )

    assert connection.committed is False
    assert connection.rolled_back is True
