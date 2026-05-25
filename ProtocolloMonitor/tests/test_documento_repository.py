from backend.repositories.documento_repository import DocumentoRepository


class FakeCursor:
    def __init__(self, *, rowcount):
        self.rowcount = rowcount
        self.executed_query = None
        self.executed_params = None
        self.closed = False

    def execute(self, query, params):
        self.executed_query = query
        self.executed_params = params
        return self

    def close(self):
        self.closed = True


class FakeConnection:
    def __init__(self, cursor):
        self.cursor_instance = cursor
        self.committed = False
        self.closed = False

    def cursor(self):
        return self.cursor_instance

    def commit(self):
        self.committed = True

    def close(self):
        self.closed = True


class DocumentoRepositoryForTest(DocumentoRepository):
    def __init__(self, connection):
        self.connection = connection

    def _open_access_connection(self):
        return self.connection


def test_update_protocollo_pdf_path_returns_true_when_record_updated():
    cursor = FakeCursor(rowcount=1)
    connection = FakeConnection(cursor)
    repository = DocumentoRepositoryForTest(connection)

    updated = repository.update_protocollo_pdf_path(
        123,
        "FileServer/2026/05/E_DIR-SIC_18177_20260510.pdf",
    )

    assert updated is True
    assert "UPDATE T_Protocolli" in cursor.executed_query
    assert "PercorsoDocumentoProtocollato" in cursor.executed_query
    assert "IDProtocollo" in cursor.executed_query
    assert cursor.executed_params == (
        "FileServer/2026/05/E_DIR-SIC_18177_20260510.pdf",
        123,
    )
    assert connection.committed is True
    assert cursor.closed is True
    assert connection.closed is True


def test_update_protocollo_pdf_path_returns_false_when_no_record_updated():
    cursor = FakeCursor(rowcount=0)
    connection = FakeConnection(cursor)
    repository = DocumentoRepositoryForTest(connection)

    updated = repository.update_protocollo_pdf_path(
        999,
        "FileServer/2026/05/E_DIR-SIC_18177_20260510.pdf",
    )

    assert updated is False
    assert connection.committed is True
    assert cursor.closed is True
    assert connection.closed is True
