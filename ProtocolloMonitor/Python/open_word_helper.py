"""Helper locale Windows per aprire documenti Word di sottofase.

Il processo espone solo un endpoint locale:

    POST http://127.0.0.1:8020/open-word

Payload:

    {"idDocumento": 123}

Il helper resta separato dal backend FastAPI principale: legge il percorso del
documento da Access in sola lettura, verifica che il file sia un `.docx` dentro
la radice autorizzata `DocumentiWorkflow` e poi delega l'apertura a Windows
senza usare shell.
"""

from __future__ import annotations

from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
from typing import Any, Callable


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8020
DEFAULT_ACCESS_DB_PATH = (
    r"C:\Users\fintu\CloudVVF\Documents\Sviluppo\Grisu\ProtocolloMonitor.accdb"
)
DEFAULT_DOCUMENT_WORKFLOW_ROOT = (
    r"C:\Users\fintu\CloudVVF\Documents\Sviluppo\Grisu\DocumentiWorkflow"
)
DOCX_SUFFIX = ".docx"
DOCX_MIME_TYPE = (
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
)


class OpenWordHelperError(Exception):
    """Errore controllato restituito come JSON dal helper."""

    def __init__(self, status_code: int, message: str) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.message = message


@dataclass(frozen=True)
class OpenWordHelperConfig:
    """Configurazione locale del helper."""

    access_db_path: Path = Path(
        os.getenv("PM_ACCESS_DB_PATH", DEFAULT_ACCESS_DB_PATH)
    )
    document_workflow_root: Path = Path(
        os.getenv(
            "PM_WORD_HELPER_DOCUMENT_WORKFLOW_ROOT",
            DEFAULT_DOCUMENT_WORKFLOW_ROOT,
        )
    )


class AccessDocumentPathRepository:
    """Repository read-only minimale per recuperare il path documento da Access."""

    def __init__(self, access_db_path: Path | str) -> None:
        self.access_db_path = Path(access_db_path)

    def get_document_path(self, id_documento: int) -> str | None:
        """Restituisce `PercorsoDocumento` da `T_SottofaseDocumenti`."""

        try:
            import pyodbc
        except ImportError as exc:
            raise OpenWordHelperError(
                500,
                "Driver pyodbc non disponibile per leggere il database Access.",
            ) from exc

        connection_string = (
            r"DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};"
            f"DBQ={self.access_db_path};"
        )

        conn = pyodbc.connect(connection_string, readonly=True)
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                SELECT PercorsoDocumento
                FROM T_SottofaseDocumenti
                WHERE IDDocumentoSottofase = ?
                """,
                (id_documento,),
            )
            row = cursor.fetchone()
        finally:
            cursor.close()
            conn.close()

        if row is None:
            return None

        try:
            return row[0]
        except (TypeError, IndexError):
            return getattr(row, "PercorsoDocumento", None)


class OpenWordService:
    """Valida la richiesta e apre il documento Word con il sistema locale."""

    def __init__(
        self,
        *,
        document_repository: Any,
        document_workflow_root: Path | str,
        opener: Callable[[str], Any] | None = None,
    ) -> None:
        self.document_repository = document_repository
        self.document_workflow_root = Path(document_workflow_root)
        self.opener = opener or self._default_opener

    def open_word_by_id(self, id_documento: int) -> dict[str, Any]:
        """Apre un documento Word dopo validazioni conservative."""

        if id_documento <= 0:
            raise OpenWordHelperError(400, "Identificativo documento non valido.")

        raw_path = self.document_repository.get_document_path(id_documento)

        if not raw_path:
            raise OpenWordHelperError(404, "Documento non trovato.")

        document_path = self._validate_document_path(raw_path)
        self.opener(str(document_path))

        return {
            "success": True,
            "idDocumento": id_documento,
            "nomeFile": document_path.name,
        }

    def _validate_document_path(self, raw_path: str) -> Path:
        """Controlla estensione, esistenza e appartenenza alla whitelist."""

        document_path = Path(raw_path).expanduser().resolve(strict=False)
        allowed_root = self.document_workflow_root.expanduser().resolve(
            strict=False
        )

        if not self._is_path_inside_root(document_path, allowed_root):
            raise OpenWordHelperError(
                403,
                "Documento fuori dalla cartella autorizzata.",
            )

        if document_path.suffix.lower() != DOCX_SUFFIX:
            raise OpenWordHelperError(
                400,
                "Formato non valido: sono ammessi solo documenti .docx.",
            )

        if not document_path.exists() or not document_path.is_file():
            raise OpenWordHelperError(404, "File documento non trovato.")

        return document_path

    @staticmethod
    def _is_path_inside_root(path: Path, root: Path) -> bool:
        """Verifica containment normalizzando il confronto per Windows."""

        path_value = os.path.normcase(str(path))
        root_value = os.path.normcase(str(root))

        try:
            return os.path.commonpath([path_value, root_value]) == root_value
        except ValueError:
            return False

    @staticmethod
    def _default_opener(path: str) -> None:
        """Apre il file con l'associazione Windows predefinita."""

        if os.name != "nt":
            raise OpenWordHelperError(
                500,
                "Apri con Word e disponibile solo su Windows.",
            )

        os.startfile(path)  # type: ignore[attr-defined]


def _build_service() -> OpenWordService:
    config = OpenWordHelperConfig()
    return OpenWordService(
        document_repository=AccessDocumentPathRepository(config.access_db_path),
        document_workflow_root=config.document_workflow_root,
    )


class OpenWordRequestHandler(BaseHTTPRequestHandler):
    """Handler HTTP locale con CORS minimo per il frontend Vite."""

    server_version = "ProtocolloMonitorOpenWordHelper/1.0"

    def do_OPTIONS(self) -> None:
        self._send_json(204, {})

    def do_POST(self) -> None:
        if self.path != "/open-word":
            self._send_json(404, {"success": False, "error": "Endpoint non trovato."})
            return

        try:
            payload = self._read_json_payload()
            id_documento = int(payload.get("idDocumento") or 0)
            result = self.server.open_word_service.open_word_by_id(  # type: ignore[attr-defined]
                id_documento
            )
            self._send_json(200, result)
        except OpenWordHelperError as exc:
            self._send_json(
                exc.status_code,
                {"success": False, "error": exc.message},
            )
        except (TypeError, ValueError):
            self._send_json(
                400,
                {
                    "success": False,
                    "error": "Payload non valido: idDocumento obbligatorio.",
                },
            )
        except Exception:
            self._send_json(
                500,
                {
                    "success": False,
                    "error": "Errore interno durante apertura documento Word.",
                },
            )

    def log_message(self, format: str, *args: Any) -> None:
        """Riduce il rumore del server locale."""

    def _read_json_payload(self) -> dict[str, Any]:
        content_length = int(self.headers.get("Content-Length") or "0")

        if content_length <= 0:
            raise OpenWordHelperError(400, "Payload JSON mancante.")

        raw_body = self.rfile.read(content_length)

        try:
            payload = json.loads(raw_body.decode("utf-8"))
        except json.JSONDecodeError as exc:
            raise OpenWordHelperError(400, "Payload JSON non valido.") from exc

        if not isinstance(payload, dict):
            raise OpenWordHelperError(400, "Payload JSON non valido.")

        return payload

    def _send_json(self, status_code: int, payload: dict[str, Any]) -> None:
        body = b"" if status_code == 204 else json.dumps(payload).encode("utf-8")

        self.send_response(status_code)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()

        if body:
            self.wfile.write(body)


class OpenWordHTTPServer(ThreadingHTTPServer):
    """Server HTTP con service iniettato."""

    def __init__(
        self,
        server_address: tuple[str, int],
        service: OpenWordService,
    ) -> None:
        super().__init__(server_address, OpenWordRequestHandler)
        self.open_word_service = service


def run_server(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> None:
    """Avvia il server locale finche il processo resta attivo."""

    server = OpenWordHTTPServer((host, port), _build_service())
    print(f"Open Word helper in ascolto su http://{host}:{port}/open-word")
    server.serve_forever()


if __name__ == "__main__":
    run_server()
