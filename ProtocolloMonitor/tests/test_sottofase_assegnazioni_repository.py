from backend.repositories.sottofase_assegnazioni_repository import (
    SottofaseAssegnazioniRepository,
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
    def __init__(self, *, table_exists=False, existing_indexes=None):
        self.table_exists_value = table_exists
        self.existing_indexes = existing_indexes or set()
        self.calls = []

    def tables(self, table=None):
        return FakeRows(one=object() if self.table_exists_value else None)

    def statistics(self, table=None):
        return FakeRows(
            rows=[
                {"index_name": index_name}
                for index_name in self.existing_indexes
            ]
        )

    def execute(self, query, params=None):
        self.calls.append((query, params))

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


class FakeRepository(SottofaseAssegnazioniRepository):
    def __init__(self, connection):
        super().__init__()
        self.connection = connection

    def _open_access_connection(self, **connect_options):
        return self.connection


def test_ensure_schema_creates_rules_table_and_indexes_when_missing():
    cursor = FakeCursor(table_exists=False)
    connection = FakeConnection(cursor)
    repository = FakeRepository(connection)

    result = repository.ensure_schema()

    assert result["table_created"] is True
    assert len(result["indexes_created"]) == 5
    assert connection.committed is True
    assert any("CREATE TABLE T_RegoleAssegnazioneStep" in call[0] for call in cursor.calls)


def test_ensure_schema_does_not_recreate_existing_objects():
    existing_indexes = {
        "IX_T_RegoleAssegnazioneStep_Attiva",
        "IX_T_RegoleAssegnazioneStep_Tipo",
        "IX_T_RegoleAssegnazioneStep_Sottofase",
        "IX_T_RegoleAssegnazioneStep_Step",
        "IX_T_RegoleAssegnazioneStep_Priorita",
    }
    cursor = FakeCursor(
        table_exists=True,
        existing_indexes=existing_indexes,
    )
    connection = FakeConnection(cursor)
    repository = FakeRepository(connection)

    result = repository.ensure_schema()

    assert result["table_created"] is False
    assert result["indexes_created"] == []
    assert not any("CREATE TABLE" in call[0] for call in cursor.calls)
