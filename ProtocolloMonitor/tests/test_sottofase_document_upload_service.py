from pathlib import Path

import pytest

from backend.services import sottofase_document_upload_service as upload_module
from backend.services.sottofase_document_upload_service import (
    SottofaseDocumentUploadBackupError,
    SottofaseDocumentUploadNotFoundError,
    SottofaseDocumentUploadService,
    SottofaseDocumentUploadTooLargeError,
    SottofaseDocumentUploadValidationError,
    SottofaseDocumentUploadWriteError,
)


MISSING = object()


class FakeSottofaseDocumentaleService:
    def __init__(self, *, sottofase=MISSING, documenti=None):
        self.sottofase = (
            {"id_sottofase": 5, "titolo": "Redigi"}
            if sottofase is MISSING
            else sottofase
        )
        self.documenti = documenti or []

    def get_sottofase_documentale(self, id_sottofase):
        if self.sottofase is None:
            return None

        return {**self.sottofase, "id_sottofase": id_sottofase}

    def list_documenti_by_sottofase(self, id_sottofase):
        return self.documenti


class FakeWorkflowService:
    def __init__(self, active_code="REDIGI"):
        self.active_code = active_code

    def get_workflow(self, id_sottofase):
        return {
            "workflow": [
                {"codice": "REDIGI", "attivo": self.active_code == "REDIGI"},
                {
                    "codice": "REVISIONA",
                    "attivo": self.active_code == "REVISIONA",
                },
            ]
        }


class FakeUploadRepository:
    def __init__(self, *, raises=False):
        self.raises = raises
        self.calls = []

    def registra_documento_word_sottofase(self, **kwargs):
        self.calls.append(kwargs)

        if self.raises:
            raise RuntimeError("errore insert")

        return 99


def make_service(tmp_path, **kwargs):
    return SottofaseDocumentUploadService(
        sottofase_documentale_service=kwargs.get(
            "sottofase_documentale_service",
            FakeSottofaseDocumentaleService(documenti=kwargs.get("documenti", [])),
        ),
        workflow_service=kwargs.get(
            "workflow_service",
            FakeWorkflowService(kwargs.get("active_code", "REDIGI")),
        ),
        document_upload_repository=kwargs.get(
            "repository",
            FakeUploadRepository(raises=kwargs.get("repository_raises", False)),
        ),
        document_workflow_root=tmp_path / "DocumentiWorkflow",
        backup_factory=kwargs.get("backup_factory", lambda: Path("backup.accdb")),
    )


def test_upload_valid_docx_creates_v001_and_registers_document(tmp_path):
    repository = FakeUploadRepository()
    service = make_service(tmp_path, repository=repository)

    result = service.collega_documento_word(
        id_sottofase=5,
        file_bytes=b"docx-content",
        original_filename="bozza.docx",
        utente_operatore="Francesco Matranga",
    )

    saved_path = Path(result["percorso_documento"])

    assert result["success"] is True
    assert result["versione_documento"] == 1
    assert result["nome_file"] == "Documento_5_V001.docx"
    assert saved_path.exists()
    assert saved_path.read_bytes() == b"docx-content"
    assert repository.calls[0]["versione_documento"] == 1
    assert repository.calls[0]["utente_operatore"] == "Francesco Matranga"


def test_upload_v002_when_existing_version_is_present(tmp_path):
    service = make_service(
        tmp_path,
        documenti=[{"versione_documento": 1}],
    )

    result = service.collega_documento_word(
        id_sottofase=5,
        file_bytes=b"docx-content",
        original_filename="bozza.docx",
        utente_operatore=None,
    )

    assert result["versione_documento"] == 2
    assert result["nome_file"] == "Documento_5_V002.docx"


def test_upload_rejects_invalid_extension(tmp_path):
    service = make_service(tmp_path)

    with pytest.raises(SottofaseDocumentUploadValidationError):
        service.collega_documento_word(
            id_sottofase=5,
            file_bytes=b"pdf",
            original_filename="bozza.pdf",
            utente_operatore=None,
        )


def test_upload_rejects_too_large_file(tmp_path, monkeypatch):
    monkeypatch.setattr(upload_module, "MAX_DOCX_SIZE_BYTES", 4)
    service = make_service(tmp_path)

    with pytest.raises(SottofaseDocumentUploadTooLargeError):
        service.collega_documento_word(
            id_sottofase=5,
            file_bytes=b"12345",
            original_filename="bozza.docx",
            utente_operatore=None,
        )


def test_upload_requires_existing_sottofase(tmp_path):
    service = make_service(
        tmp_path,
        sottofase_documentale_service=FakeSottofaseDocumentaleService(
            sottofase=None
        ),
    )

    with pytest.raises(SottofaseDocumentUploadNotFoundError):
        service.collega_documento_word(
            id_sottofase=999,
            file_bytes=b"docx",
            original_filename="bozza.docx",
            utente_operatore=None,
        )


def test_upload_requires_active_redigi(tmp_path):
    service = make_service(tmp_path, active_code="REVISIONA")

    with pytest.raises(SottofaseDocumentUploadValidationError):
        service.collega_documento_word(
            id_sottofase=5,
            file_bytes=b"docx",
            original_filename="bozza.docx",
            utente_operatore=None,
        )


def test_upload_stops_when_backup_fails(tmp_path):
    def fail_backup():
        raise RuntimeError("backup ko")

    service = make_service(tmp_path, backup_factory=fail_backup)

    with pytest.raises(SottofaseDocumentUploadBackupError):
        service.collega_documento_word(
            id_sottofase=5,
            file_bytes=b"docx",
            original_filename="bozza.docx",
            utente_operatore=None,
        )


def test_upload_removes_file_when_repository_fails(tmp_path):
    service = make_service(tmp_path, repository_raises=True)

    with pytest.raises(SottofaseDocumentUploadWriteError):
        service.collega_documento_word(
            id_sottofase=5,
            file_bytes=b"docx",
            original_filename="bozza.docx",
            utente_operatore=None,
        )

    assert not (tmp_path / "DocumentiWorkflow" / "5" / "V001").exists() or not (
        tmp_path / "DocumentiWorkflow" / "5" / "V001" / "Documento_5_V001.docx"
    ).exists()
