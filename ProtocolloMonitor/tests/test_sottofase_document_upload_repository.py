from datetime import datetime

import pytest

from backend.repositories.sottofase_document_upload_repository import (
    SottofaseDocumentUploadRepository,
)


class FakeCursor:
    def __init__(self, *, fail_on_update=False):
        self.fail_on_update = fail_on_update
        self.calls = []
        self.rowcount = 1

    def execute(self, query, params=None):
        self.calls.append((query, params))

        if query.strip().upper().startswith("UPDATE") and self.fail_on_update:
            raise RuntimeError("update fallito")

    def fetchone(self):
        return (42,)

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


class FakeRepository(SottofaseDocumentUploadRepository):
    def __init__(self, connection):
        super().__init__()
        self.connection = connection

    def _open_access_connection(self, **connect_options):
        return self.connection


def test_repository_inserts_document_and_updates_sottofase_in_transaction():
    cursor = FakeCursor()
    connection = FakeConnection(cursor)
    repository = FakeRepository(connection)
    data = datetime(2026, 5, 27, 12, 0, 0)

    id_documento = repository.registra_documento_word_sottofase(
        id_sottofase=5,
        nome_file="Documento_5_V001.docx",
        percorso_documento=r"C:\DocumentiWorkflow\5\V001\Documento_5_V001.docx",
        dimensione_bytes=123,
        hash_file="abc",
        versione_documento=1,
        utente_operatore="Francesco Matranga",
        data_collegamento=data,
    )

    assert id_documento == 42
    assert connection.committed is True
    assert connection.rolled_back is False
    assert any("INSERT INTO T_SottofaseDocumenti" in call[0] for call in cursor.calls)
    assert any("UPDATE T_ProcedimentoSottofasi" in call[0] for call in cursor.calls)


def test_repository_rolls_back_when_update_fails():
    cursor = FakeCursor(fail_on_update=True)
    connection = FakeConnection(cursor)
    repository = FakeRepository(connection)

    with pytest.raises(RuntimeError):
        repository.registra_documento_word_sottofase(
            id_sottofase=5,
            nome_file="Documento_5_V001.docx",
            percorso_documento=r"C:\DocumentiWorkflow\5\V001\Documento_5_V001.docx",
            dimensione_bytes=123,
            hash_file="abc",
            versione_documento=1,
            utente_operatore=None,
            data_collegamento=datetime(2026, 5, 27, 12, 0, 0),
        )

    assert connection.committed is False
    assert connection.rolled_back is True
