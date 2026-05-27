import importlib.util
from pathlib import Path
import sys

import pytest


HELPER_PATH = (
    Path(__file__).resolve().parents[1] / "Python" / "open_word_helper.py"
)
spec = importlib.util.spec_from_file_location("open_word_helper", HELPER_PATH)
open_word_helper = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = open_word_helper
spec.loader.exec_module(open_word_helper)


OpenWordHelperError = open_word_helper.OpenWordHelperError
OpenWordService = open_word_helper.OpenWordService


class FakeDocumentRepository:
    def __init__(self, paths):
        self.paths = paths

    def get_document_path(self, id_documento):
        return self.paths.get(id_documento)


class FakeOpener:
    def __init__(self):
        self.paths = []

    def __call__(self, path):
        self.paths.append(path)


def make_service(tmp_path, paths):
    opener = FakeOpener()
    service = OpenWordService(
        document_repository=FakeDocumentRepository(paths),
        document_workflow_root=tmp_path / "DocumentiWorkflow",
        opener=opener,
    )

    return service, opener


def test_open_word_accepts_existing_docx_inside_whitelist(tmp_path):
    document_path = (
        tmp_path
        / "DocumentiWorkflow"
        / "5"
        / "V001"
        / "Documento_5_V001.docx"
    )
    document_path.parent.mkdir(parents=True)
    document_path.write_bytes(b"docx")
    service, opener = make_service(tmp_path, {10: str(document_path)})

    result = service.open_word_by_id(10)

    assert result["success"] is True
    assert result["idDocumento"] == 10
    assert opener.paths == [str(document_path.resolve())]


def test_open_word_rejects_missing_file(tmp_path):
    missing_path = (
        tmp_path
        / "DocumentiWorkflow"
        / "5"
        / "V001"
        / "Documento_5_V001.docx"
    )
    service, opener = make_service(tmp_path, {10: str(missing_path)})

    with pytest.raises(OpenWordHelperError) as exc_info:
        service.open_word_by_id(10)

    assert exc_info.value.status_code == 404
    assert opener.paths == []


def test_open_word_rejects_non_docx_file(tmp_path):
    document_path = tmp_path / "DocumentiWorkflow" / "5" / "V001" / "file.pdf"
    document_path.parent.mkdir(parents=True)
    document_path.write_bytes(b"pdf")
    service, opener = make_service(tmp_path, {10: str(document_path)})

    with pytest.raises(OpenWordHelperError) as exc_info:
        service.open_word_by_id(10)

    assert exc_info.value.status_code == 400
    assert opener.paths == []


def test_open_word_rejects_path_outside_whitelist(tmp_path):
    document_path = tmp_path / "Outside" / "Documento_5_V001.docx"
    document_path.parent.mkdir(parents=True)
    document_path.write_bytes(b"docx")
    service, opener = make_service(tmp_path, {10: str(document_path)})

    with pytest.raises(OpenWordHelperError) as exc_info:
        service.open_word_by_id(10)

    assert exc_info.value.status_code == 403
    assert opener.paths == []


def test_open_word_rejects_unknown_document_id(tmp_path):
    service, opener = make_service(tmp_path, {})

    with pytest.raises(OpenWordHelperError) as exc_info:
        service.open_word_by_id(999)

    assert exc_info.value.status_code == 404
    assert opener.paths == []


def test_open_word_rejects_path_traversal_outside_whitelist(tmp_path):
    document_path = tmp_path / "Outside" / "Documento_5_V001.docx"
    document_path.parent.mkdir(parents=True)
    document_path.write_bytes(b"docx")
    traversal_path = (
        tmp_path
        / "DocumentiWorkflow"
        / ".."
        / "Outside"
        / "Documento_5_V001.docx"
    )
    service, opener = make_service(tmp_path, {10: str(traversal_path)})

    with pytest.raises(OpenWordHelperError) as exc_info:
        service.open_word_by_id(10)

    assert exc_info.value.status_code == 403
    assert opener.paths == []
