"""Service applicativo per collegare documenti Word alle sottofasi.

Lo Step 30L-15 abilita il primo caricamento reale di documenti `.docx` legati
alla REDIGI della sottofase. Lo Step 30L-16 riusa lo stesso flusso
transazionale anche durante REVISIONA, cosi le revisioni V002/V003 entrano
nello storico documenti senza sovrascrivere V001. Il service coordina
validazione, backup Access, salvataggio fisico versionato e registrazione DB,
mantenendo separati:

- controllo funzionale e workflow;
- filesystem `DocumentiWorkflow`;
- transazione Access.
"""

from __future__ import annotations

import hashlib
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

from backend.core.access_backup import AccessBackupError, create_access_backup
from backend.core.config import get_config


MAX_DOCX_SIZE_BYTES = 50 * 1024 * 1024
DOCX_MIME_TYPE = (
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
)
ALLOWED_UPLOAD_STEPS = {"REDIGI", "REVISIONA"}


class SottofaseDocumentUploadValidationError(ValueError):
    """Errore controllato per input upload non valido."""


class SottofaseDocumentUploadTooLargeError(SottofaseDocumentUploadValidationError):
    """Errore controllato per file superiore al limite ammesso."""


class SottofaseDocumentUploadNotFoundError(LookupError):
    """Errore controllato per sottofase non trovata."""


class SottofaseDocumentUploadBackupError(RuntimeError):
    """Errore controllato quando il backup Access non riesce."""


class SottofaseDocumentUploadWriteError(RuntimeError):
    """Errore controllato per salvataggio o registrazione documento falliti."""


class SottofaseDocumentUploadService:
    """Service per upload versionato di documenti Word di sottofase."""

    def __init__(
        self,
        *,
        sottofase_documentale_service: Any | None = None,
        workflow_service: Any | None = None,
        document_upload_repository: Any | None = None,
        document_workflow_root: Path | str | None = None,
        backup_factory: Callable[[], Path] | None = None,
        now_factory: Callable[[], datetime] | None = None,
    ) -> None:
        self.sottofase_documentale_service = sottofase_documentale_service
        self.workflow_service = workflow_service
        self.document_upload_repository = document_upload_repository
        self.document_workflow_root = Path(
            document_workflow_root
            if document_workflow_root is not None
            else self._default_document_workflow_root()
        )
        self.backup_factory = backup_factory or create_access_backup
        self.now_factory = now_factory or datetime.now

    def collega_documento_word(
        self,
        *,
        id_sottofase: int,
        file_bytes: bytes,
        original_filename: str,
        utente_operatore: str | None,
    ) -> dict[str, Any]:
        """Valida, salva e registra una nuova versione Word della sottofase.

        L'upload e consentito quando il workflow espone REDIGI o REVISIONA come
        step attivo. Il backup Access viene creato prima della registrazione
        DB. Se il DB fallisce dopo il salvataggio file, il file appena scritto
        viene rimosso per evitare una versione orfana.
        """

        self._validate_docx_file(
            file_bytes=file_bytes,
            original_filename=original_filename,
        )
        sottofase = self._get_sottofase_or_raise(id_sottofase)
        workflow_step = self._ensure_upload_step_active(id_sottofase)

        existing_documents = self._list_existing_documents(id_sottofase)
        version = self._next_version(existing_documents)
        target_path, version = self._build_target_path(
            id_sottofase=id_sottofase,
            version=version,
        )
        version_label = self._version_label(version)
        now = self.now_factory()
        backup_path = self._create_backup_or_raise()

        saved_path: Path | None = None

        try:
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_bytes(file_bytes)
            saved_path = target_path

            if self.document_upload_repository is None:
                raise SottofaseDocumentUploadWriteError(
                    "Repository upload documenti non configurato."
                )

            id_documento = (
                self.document_upload_repository.registra_documento_word_sottofase(
                    id_sottofase=id_sottofase,
                    nome_file=target_path.name,
                    percorso_documento=str(target_path),
                    dimensione_bytes=len(file_bytes),
                    hash_file=hashlib.sha256(file_bytes).hexdigest(),
                    versione_documento=version,
                    utente_operatore=utente_operatore,
                    data_collegamento=now,
                )
            )
        except SottofaseDocumentUploadWriteError:
            self._remove_saved_file(saved_path)
            raise
        except Exception as exc:
            self._remove_saved_file(saved_path)
            raise SottofaseDocumentUploadWriteError(
                f"Collegamento documento Word non riuscito: {exc}"
            )

        return {
            "success": True,
            "id_sottofase": id_sottofase,
            "id_documento_sottofase": id_documento,
            "tipo_documento": "WORD",
            "nome_file": target_path.name,
            "estensione": ".docx",
            "percorso_documento": str(target_path),
            "mime_type": DOCX_MIME_TYPE,
            "dimensione_bytes": len(file_bytes),
            "hash_file": hashlib.sha256(file_bytes).hexdigest(),
            "versione_documento": version,
            "versione_label": version_label,
            "step_workflow": workflow_step,
            "data_collegamento": now.isoformat(sep=" "),
            "utente_collegamento": utente_operatore,
            "backup_creato": str(backup_path),
            "sottofase": {
                "id_sottofase": sottofase.get("id_sottofase"),
                "titolo": sottofase.get("titolo"),
            },
        }

    def _get_sottofase_or_raise(self, id_sottofase: int) -> dict[str, Any]:
        """Legge la sottofase dal service read-only o solleva 404-oriented."""

        if self.sottofase_documentale_service is None:
            raise SottofaseDocumentUploadNotFoundError("Sottofase non trovata.")

        get_sottofase = getattr(
            self.sottofase_documentale_service,
            "get_sottofase_documentale",
            None,
        )

        if get_sottofase is None:
            raise SottofaseDocumentUploadNotFoundError("Sottofase non trovata.")

        sottofase = get_sottofase(id_sottofase)

        if sottofase is None:
            raise SottofaseDocumentUploadNotFoundError("Sottofase non trovata.")

        return sottofase

    def _ensure_upload_step_active(self, id_sottofase: int) -> str:
        """Verifica che il caricamento sia coerente con REDIGI/REVISIONA."""

        workflow = None

        if self.workflow_service is not None:
            get_workflow = getattr(self.workflow_service, "get_workflow", None)

            if get_workflow is not None:
                workflow = get_workflow(id_sottofase)

        active_step = self._active_step_code(workflow)

        if active_step not in ALLOWED_UPLOAD_STEPS:
            raise SottofaseDocumentUploadValidationError(
                "Documento Word collegabile solo quando REDIGI o REVISIONA "
                "sono lo step attivo."
            )

        return active_step

    def _list_existing_documents(self, id_sottofase: int) -> list[dict[str, Any]]:
        """Legge lo storico documenti per calcolare la versione successiva."""

        if self.sottofase_documentale_service is None:
            return []

        list_documenti = getattr(
            self.sottofase_documentale_service,
            "list_documenti_by_sottofase",
            None,
        )

        if list_documenti is None:
            return []

        return list_documenti(id_sottofase) or []

    def _build_target_path(
        self,
        *,
        id_sottofase: int,
        version: int,
    ) -> tuple[Path, int]:
        """Costruisce path e versione `DocumentiWorkflow/IDSottofase/Vnnn`."""

        candidate_version = version

        while True:
            version_label = self._version_label(candidate_version)
            filename = f"Documento_{id_sottofase}_{version_label}.docx"
            target_path = (
                self.document_workflow_root
                / str(id_sottofase)
                / version_label
                / filename
            )

            if not target_path.exists():
                return target_path, candidate_version

            candidate_version += 1

    def _create_backup_or_raise(self) -> Path:
        """Crea il backup Access obbligatorio prima della scrittura DB."""

        try:
            return self.backup_factory()
        except AccessBackupError as exc:
            raise SottofaseDocumentUploadBackupError(str(exc))
        except Exception as exc:
            raise SottofaseDocumentUploadBackupError(
                f"Backup Access non riuscito: {exc}"
            )

    @staticmethod
    def _validate_docx_file(
        *,
        file_bytes: bytes,
        original_filename: str,
    ) -> None:
        """Valida presenza, estensione `.docx` e limite massimo 50 MB."""

        if not file_bytes:
            raise SottofaseDocumentUploadValidationError("File Word mancante.")

        if not original_filename:
            raise SottofaseDocumentUploadValidationError(
                "Nome file Word mancante."
            )

        if Path(original_filename).suffix.lower() != ".docx":
            raise SottofaseDocumentUploadValidationError(
                "Formato non valido: selezionare un file .docx."
            )

        if len(file_bytes) > MAX_DOCX_SIZE_BYTES:
            raise SottofaseDocumentUploadTooLargeError(
                "File troppo grande: limite massimo 50 MB."
            )

    @staticmethod
    def _next_version(documents: list[dict[str, Any]]) -> int:
        """Calcola la versione successiva usando lo storico gia registrato."""

        versions = []

        for document in documents:
            try:
                versions.append(int(document.get("versione_documento") or 0))
            except (TypeError, ValueError):
                continue

        return max(versions, default=0) + 1

    @staticmethod
    def _version_label(version: int) -> str:
        """Formatta la versione come `V001`, `V002`, ..."""

        return f"V{version:03d}"

    @staticmethod
    def _active_step_code(workflow: dict[str, Any] | None) -> str | None:
        """Ricava lo step attivo dalla risposta del workflow read-only."""

        if workflow is None:
            return None

        for step in workflow.get("workflow") or []:
            if step.get("attivo"):
                return step.get("codice")

        return None

    @staticmethod
    def _remove_saved_file(saved_path: Path | None) -> None:
        """Rimuove il file appena salvato quando la registrazione DB fallisce."""

        if saved_path is None or not saved_path.exists():
            return

        try:
            saved_path.unlink()
        except OSError:
            pass

    @staticmethod
    def _default_document_workflow_root() -> Path:
        """Deriva `DocumentiWorkflow` dalla cartella del database configurato."""

        return Path(get_config().access_db_path).parent / "DocumentiWorkflow"
