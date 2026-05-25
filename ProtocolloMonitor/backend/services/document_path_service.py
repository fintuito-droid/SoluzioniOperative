"""Risoluzione sicura dei path documento per gli endpoint FastAPI.

Il modulo centralizza una responsabilita piccola ma delicata: trasformare il
path salvato in Access in un path fisico leggibile dal backend, senza creare
file, senza modificare il database e senza accettare traversal relativi.
"""

from __future__ import annotations

from pathlib import Path


class DocumentPathService:
    """Risolutore prudente per path PDF assoluti o relativi.

    `DocumentStorageService` salva oggi path assoluti quando usa il FileServer
    reale. Tuttavia Access potrebbe contenere path relativi storici o futuri.
    Questa classe permette all'endpoint PDF di gestire entrambi i casi senza
    appesantire `backend/main.py`.
    """

    def __init__(
        self,
        *,
        project_root: str | Path | None = None,
        file_server_root: str | Path | None = None,
    ) -> None:
        self.backend_root = Path(__file__).resolve().parents[1]
        self.project_root = Path(project_root) if project_root else self.backend_root.parent
        self.file_server_root = (
            Path(file_server_root)
            if file_server_root
            else self.backend_root / "FileServer"
        )

    def resolve_document_path(self, raw_path: str | Path | None) -> Path | None:
        """Restituisce un path esistente e sicuro, oppure `None`.

        Regole:
        - path assoluto: viene usato solo se esiste ed e un file;
        - path relativo: viene cercato rispetto a root progetto, backend e
          FileServer;
        - traversal relativo con `..` viene bloccato;
        - nessun file viene creato e nessun dato viene modificato.
        """

        if raw_path is None:
            return None

        candidate = Path(str(raw_path).strip())

        if not str(candidate):
            return None

        if candidate.is_absolute():
            return self._existing_file(candidate)

        if self._contains_parent_traversal(candidate):
            return None

        for base_path in self._relative_base_paths():
            resolved = self._existing_file(base_path / candidate)

            if resolved is not None:
                return resolved

        return None

    @staticmethod
    def _contains_parent_traversal(path: Path) -> bool:
        """Blocca path relativi che tentano di risalire con `..`."""

        return ".." in path.parts

    def _relative_base_paths(self) -> tuple[Path, Path, Path]:
        """Restituisce le basi compatibili con path storici e nuovi."""

        return (
            self.project_root,
            self.backend_root,
            self.file_server_root,
        )

    @staticmethod
    def _existing_file(path: Path) -> Path | None:
        """Normalizza e restituisce il path solo se punta a un file reale."""

        resolved = path.resolve(strict=False)

        if resolved.exists() and resolved.is_file():
            return resolved

        return None


def resolve_document_path(raw_path: str | Path | None) -> Path | None:
    """Helper funzionale usato dagli endpoint FastAPI."""

    return DocumentPathService().resolve_document_path(raw_path)
