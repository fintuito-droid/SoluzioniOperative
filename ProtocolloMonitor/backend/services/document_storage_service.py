"""Servizio di storage fisico documenti per ProtocolloMonitor.

`DocumentStorageService` centralizza la scrittura fisica dei PDF nel FileServer
del progetto, senza accedere al database, senza chiamare repository e senza
effettuare download HTTP.

Il servizio e pensato per restare compatibile con Windows e con l'attuale
struttura documentale, ma anche per preparare una futura migrazione PostgreSQL:
il database dovra conservare riferimenti al documento, mentre la logica di
filesystem resta isolata qui.
"""

from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
import re
from typing import Any

from backend.core.logging import get_logger, log_event


WINDOWS_RESERVED_NAMES = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    *(f"COM{index}" for index in range(1, 10)),
    *(f"LPT{index}" for index in range(1, 10)),
}


class DocumentStorageService:
    """Gestisce salvataggio e verifica fisica dei PDF.

    Il servizio non conosce Access, PostgreSQL, repository o endpoint FastAPI.
    Riceve bytes e metadati minimi, costruisce cartella/nome file, scrive il
    PDF e restituisce il percorso salvato.
    """

    def __init__(self, file_server_root: str | Path | None = None) -> None:
        if file_server_root is None:
            self.file_server_root = Path(__file__).resolve().parents[1] / "FileServer"
        else:
            self.file_server_root = Path(file_server_root)

        self.logger = get_logger()

    def build_storage_dir(self, data_protocollo: Any) -> Path:
        """Restituisce la cartella FileServer/YYYY/MM per la data indicata."""

        data_file = self._format_date_for_filename(data_protocollo)
        year = data_file[:4]
        month = data_file[4:6]

        return self.file_server_root / year / month

    def build_filename(
        self,
        modalita: Any,
        comando: Any,
        numero_protocollo: Any,
        data_protocollo: Any,
    ) -> str:
        """Costruisce il nome PDF standard `[Tipo]_[Comando]_[Numero]_[Data].pdf`."""

        tipo = self._document_type_from_modalita(modalita)
        comando_sicuro = self._sanitize_filename_part(comando, "ND")
        numero_sicuro = self._sanitize_filename_part(numero_protocollo, "SENZAPROT")
        data_file = self._format_date_for_filename(data_protocollo)

        return f"{tipo}_{comando_sicuro}_{numero_sicuro}_{data_file}.pdf"

    def save_pdf(
        self,
        pdf_bytes: bytes,
        modalita: Any,
        comando: Any,
        numero_protocollo: Any,
        data_protocollo: Any,
    ) -> Path:
        """Salva bytes PDF nel FileServer e restituisce il percorso scritto."""

        if not isinstance(pdf_bytes, bytes):
            raise TypeError("pdf_bytes deve essere di tipo bytes.")

        storage_dir = self.build_storage_dir(data_protocollo)
        filename = self.build_filename(
            modalita,
            comando,
            numero_protocollo,
            data_protocollo,
        )
        target_path = storage_dir / filename

        storage_dir.mkdir(parents=True, exist_ok=True)
        target_path.write_bytes(pdf_bytes)

        log_event(
            logger=self.logger,
            module="PROTOCOLLO_MONITOR",
            operation="document_storage_save_pdf",
            entity_type="documento",
            status="ok",
            message="PDF salvato nel FileServer.",
            file_path=str(target_path),
        )

        return target_path

    def document_exists(self, relative_or_absolute_path: str | Path) -> bool:
        """Verifica se un documento esiste, accettando path relativo o assoluto."""

        candidate_path = Path(relative_or_absolute_path)

        if not candidate_path.is_absolute():
            candidate_path = self.file_server_root / candidate_path

        return candidate_path.exists() and candidate_path.is_file()

    @staticmethod
    def _document_type_from_modalita(modalita: Any) -> str:
        text = str(modalita or "").strip().upper()

        if "ENTRATA" in text:
            return "E"

        if "USCITA" in text:
            return "U"

        return "X"

    @staticmethod
    def _format_date_for_filename(data_protocollo: Any) -> str:
        if isinstance(data_protocollo, datetime):
            return data_protocollo.strftime("%Y%m%d")

        if isinstance(data_protocollo, date):
            return data_protocollo.strftime("%Y%m%d")

        text = str(data_protocollo or "").strip()

        for candidate in (text, text[:10]):
            try:
                return datetime.strptime(candidate, "%d/%m/%Y").strftime("%Y%m%d")
            except ValueError:
                continue

        return "00000000"

    @staticmethod
    def _sanitize_filename_part(value: Any, fallback: str) -> str:
        text = str(value or "").strip()

        if not text:
            text = fallback

        text = re.sub(r'[<>:"/\\|?*\x00-\x1F]', "_", text)
        text = re.sub(r"\s+", "_", text)
        text = text.strip(" ._")

        if not text:
            text = fallback

        if text.upper() in WINDOWS_RESERVED_NAMES:
            text = f"{text}_"

        return text
