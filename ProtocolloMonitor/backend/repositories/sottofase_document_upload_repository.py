"""Repository di scrittura controllata per documenti Word di sottofase.

Il repository introduce la sola mutazione necessaria allo Step 30L-15:

- inserire una nuova versione documentale in `T_SottofaseDocumenti`;
- aggiornare in `T_ProcedimentoSottofasi` il documento corrente.

Non crea tabelle, non altera campi e non modifica il workflow operativo. La
transazione e unica: se l'insert del documento o l'update della sottofase
falliscono, viene eseguito rollback.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from .base import BaseRepository


class SottofaseDocumentUploadRepository(BaseRepository):
    """Repository Access-compatible per registrare documenti sottofase."""

    def registra_documento_word_sottofase(
        self,
        *,
        id_sottofase: int,
        nome_file: str,
        percorso_documento: str,
        dimensione_bytes: int,
        hash_file: str,
        versione_documento: int,
        utente_operatore: str | None,
        data_collegamento: datetime,
    ) -> int:
        """Inserisce il documento e lo imposta come documento corrente.

        Il metodo non salva file: riceve un path gia creato dal service. Questa
        separazione evita di mischiare filesystem e database, mantenendo il
        rollback Access circoscritto alle query.
        """

        conn = self._open_access_connection()
        cursor = conn.cursor()

        try:
            id_documento = self.inserisci_documento_sottofase(
                cursor=cursor,
                id_sottofase=id_sottofase,
                nome_file=nome_file,
                percorso_documento=percorso_documento,
                dimensione_bytes=dimensione_bytes,
                hash_file=hash_file,
                versione_documento=versione_documento,
                utente_operatore=utente_operatore,
                data_collegamento=data_collegamento,
            )

            updated = self.aggiorna_documento_corrente_sottofase(
                cursor=cursor,
                id_sottofase=id_sottofase,
                id_documento_corrente=id_documento,
                versione_documento=versione_documento,
                utente_operatore=utente_operatore,
                data_azione=data_collegamento,
            )

            if not updated:
                raise RuntimeError("Sottofase non aggiornata.")

            conn.commit()
            return id_documento
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    def inserisci_documento_sottofase(
        self,
        *,
        cursor: Any,
        id_sottofase: int,
        nome_file: str,
        percorso_documento: str,
        dimensione_bytes: int,
        hash_file: str,
        versione_documento: int,
        utente_operatore: str | None,
        data_collegamento: datetime,
    ) -> int:
        """Inserisce una riga in `T_SottofaseDocumenti` e restituisce l'ID."""

        query = """
            INSERT INTO T_SottofaseDocumenti (
                IDSottofase,
                TipoDocumento,
                NomeFile,
                Estensione,
                PercorsoDocumento,
                MimeType,
                DimensioneBytes,
                HashFile,
                VersioneDocumento,
                DataCollegamento,
                UtenteCollegamento,
                Attivo,
                DataCreazione,
                DataModifica
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        cursor.execute(
            query,
            (
                id_sottofase,
                "WORD",
                nome_file,
                ".docx",
                percorso_documento,
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                dimensione_bytes,
                hash_file,
                versione_documento,
                data_collegamento,
                utente_operatore,
                True,
                data_collegamento,
                data_collegamento,
            ),
        )
        cursor.execute("SELECT @@IDENTITY AS IDDocumentoSottofase")
        row = cursor.fetchone()

        return self._identity_from_row(row)

    def aggiorna_documento_corrente_sottofase(
        self,
        *,
        cursor: Any,
        id_sottofase: int,
        id_documento_corrente: int,
        versione_documento: int,
        utente_operatore: str | None,
        data_azione: datetime,
    ) -> bool:
        """Aggiorna solo i campi documentali gia presenti nella sottofase."""

        query = """
            UPDATE T_ProcedimentoSottofasi
            SET
                IDDocumentoCorrente = ?,
                VersioneDocumento = ?,
                HaDocumentoCollegato = ?,
                DataUltimaAzione = ?,
                UtenteUltimaAzione = ?,
                DataModifica = ?
            WHERE IDSottofase = ?
        """

        cursor.execute(
            query,
            (
                id_documento_corrente,
                versione_documento,
                True,
                data_azione,
                utente_operatore,
                data_azione,
                id_sottofase,
            ),
        )

        return getattr(cursor, "rowcount", 1) != 0

    @staticmethod
    def _identity_from_row(row: Any) -> int:
        """Estrae `@@IDENTITY` da righe pyodbc o fake row di test."""

        if row is None:
            raise RuntimeError("ID documento non restituito da Access.")

        if isinstance(row, (tuple, list)):
            value = row[0]
        else:
            try:
                value = row[0]
            except (TypeError, IndexError):
                value = getattr(row, "IDDocumentoSottofase", None)

        if value is None:
            raise RuntimeError("ID documento non leggibile da Access.")

        return int(value)
