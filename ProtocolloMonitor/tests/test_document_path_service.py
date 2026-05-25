from backend.services.document_path_service import DocumentPathService


def test_resolve_document_path_supports_existing_absolute_path(tmp_path):
    service = DocumentPathService(project_root=tmp_path, file_server_root=tmp_path)
    pdf_path = tmp_path / "absolute.pdf"
    pdf_path.write_bytes(b"%PDF-test")

    assert service.resolve_document_path(pdf_path) == pdf_path.resolve()


def test_resolve_document_path_supports_existing_relative_file_server_path(tmp_path):
    file_server_root = tmp_path / "backend" / "FileServer"
    pdf_path = file_server_root / "2026" / "05" / "sample.pdf"
    pdf_path.parent.mkdir(parents=True)
    pdf_path.write_bytes(b"%PDF-test")
    service = DocumentPathService(
        project_root=tmp_path,
        file_server_root=file_server_root,
    )

    assert (
        service.resolve_document_path("2026/05/sample.pdf")
        == pdf_path.resolve()
    )


def test_resolve_document_path_supports_relative_backend_file_server_path(tmp_path):
    file_server_root = tmp_path / "backend" / "FileServer"
    pdf_path = file_server_root / "2026" / "05" / "sample.pdf"
    pdf_path.parent.mkdir(parents=True)
    pdf_path.write_bytes(b"%PDF-test")
    service = DocumentPathService(
        project_root=tmp_path,
        file_server_root=file_server_root,
    )

    assert (
        service.resolve_document_path("backend/FileServer/2026/05/sample.pdf")
        == pdf_path.resolve()
    )


def test_resolve_document_path_returns_none_for_missing_path(tmp_path):
    service = DocumentPathService(project_root=tmp_path, file_server_root=tmp_path)

    assert service.resolve_document_path("2026/05/missing.pdf") is None


def test_resolve_document_path_blocks_relative_path_traversal(tmp_path):
    outside_path = tmp_path / "outside.pdf"
    outside_path.write_bytes(b"%PDF-test")
    service = DocumentPathService(project_root=tmp_path, file_server_root=tmp_path)

    assert service.resolve_document_path("../outside.pdf") is None
