"""Repository read-only per il modello documentale della sottofase.

Il modulo legge le estensioni introdotte nello Step 30L:

- campi documentali in `T_ProcedimentoSottofasi`;
- documenti collegati in `T_SottofaseDocumenti`;
- step interni in `T_SottofaseStepOperativi`.

Il repository e volutamente solo in lettura: non inserisce documenti, non cambia
stati e non aggiorna path. Le future scritture dovranno passare da metodi
separati e testati, mantenendo chiaro il confine tra lettura e mutazione.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from .base import BaseRepository


class SottofaseDocumentaleRepository(BaseRepository):
    """Repository Access-compatible per leggere dati documentali sottofase."""

    @staticmethod
    def _normalize_value(value: Any) -> Any:
        """Converte date Access in stringhe JSON-friendly."""

        if isinstance(value, datetime):
            return value.isoformat(sep=" ")

        if isinstance(value, date):
            return value.isoformat()

        return value

    @staticmethod
    def _get(row: Any, name: str, default: Any = None) -> Any:
        """Legge campi da righe pyodbc o da fake row usate nei test."""

        if row is None:
            return default

        if isinstance(row, dict):
            return row.get(name, default)

        return getattr(row, name, default)

    def _sottofase_row_to_dict(self, row: Any) -> dict[str, Any]:
        """Converte una riga `T_ProcedimentoSottofasi` in dizionario."""

        return {
            "id_sottofase": self._normalize_value(self._get(row, "IDSottofase")),
            "id_fase": self._normalize_value(self._get(row, "IDFase")),
            "id_catalogo_sottofase": self._normalize_value(
                self._get(row, "IDCatalogoSottofase")
            ),
            "codice_sottofase": self._normalize_value(
                self._get(row, "CodiceSottofase")
            ),
            "titolo": self._normalize_value(self._get(row, "Titolo")),
            "descrizione": self._normalize_value(self._get(row, "Descrizione")),
            "ordine": self._normalize_value(self._get(row, "Ordine")),
            "stato_sottofase": self._normalize_value(
                self._get(row, "StatoSottofase")
            ),
            "icona": self._normalize_value(self._get(row, "Icona")),
            "colore": self._normalize_value(self._get(row, "Colore")),
            "responsabile": self._normalize_value(self._get(row, "Responsabile")),
            "data_scadenza": self._normalize_value(self._get(row, "DataScadenza")),
            "data_avvio": self._normalize_value(self._get(row, "DataAvvio")),
            "data_completamento": self._normalize_value(
                self._get(row, "DataCompletamento")
            ),
            "note_interne": self._normalize_value(self._get(row, "NoteInterne")),
            "attivo": bool(self._get(row, "Attivo"))
            if self._get(row, "Attivo") is not None
            else False,
            "data_creazione": self._normalize_value(self._get(row, "DataCreazione")),
            "data_modifica": self._normalize_value(self._get(row, "DataModifica")),
            "step_corrente": self._normalize_value(self._get(row, "StepCorrente")),
            "testo_operatore": self._normalize_value(
                self._get(row, "TestoOperatore")
            ),
            "ha_documento_collegato": bool(self._get(row, "HaDocumentoCollegato"))
            if self._get(row, "HaDocumentoCollegato") is not None
            else False,
            "id_documento_corrente": self._normalize_value(
                self._get(row, "IDDocumentoCorrente")
            ),
            "data_ultima_azione": self._normalize_value(
                self._get(row, "DataUltimaAzione")
            ),
            "utente_ultima_azione": self._normalize_value(
                self._get(row, "UtenteUltimaAzione")
            ),
            "versione_documento": self._normalize_value(
                self._get(row, "VersioneDocumento")
            ),
        }

    def _documento_row_to_dict(self, row: Any) -> dict[str, Any]:
        """Converte una riga `T_SottofaseDocumenti` in dizionario."""

        return {
            "id_documento_sottofase": self._normalize_value(
                self._get(row, "IDDocumentoSottofase")
            ),
            "id_sottofase": self._normalize_value(self._get(row, "IDSottofase")),
            "tipo_documento": self._normalize_value(self._get(row, "TipoDocumento")),
            "nome_file": self._normalize_value(self._get(row, "NomeFile")),
            "estensione": self._normalize_value(self._get(row, "Estensione")),
            "percorso_documento": self._normalize_value(
                self._get(row, "PercorsoDocumento")
            ),
            "mime_type": self._normalize_value(self._get(row, "MimeType")),
            "dimensione_bytes": self._normalize_value(
                self._get(row, "DimensioneBytes")
            ),
            "hash_file": self._normalize_value(self._get(row, "HashFile")),
            "versione_documento": self._normalize_value(
                self._get(row, "VersioneDocumento")
            ),
            "stato_documento": self._normalize_value(self._get(row, "StatoDocumento")),
            "data_collegamento": self._normalize_value(
                self._get(row, "DataCollegamento")
            ),
            "utente_collegamento": self._normalize_value(
                self._get(row, "UtenteCollegamento")
            ),
            "attivo": bool(self._get(row, "Attivo"))
            if self._get(row, "Attivo") is not None
            else False,
            "data_creazione": self._normalize_value(self._get(row, "DataCreazione")),
            "data_modifica": self._normalize_value(self._get(row, "DataModifica")),
        }

    def _step_row_to_dict(self, row: Any) -> dict[str, Any]:
        """Converte una riga `T_SottofaseStepOperativi` in dizionario."""

        return {
            "id_step_sottofase": self._normalize_value(
                self._get(row, "IDStepSottofase")
            ),
            "id_sottofase": self._normalize_value(self._get(row, "IDSottofase")),
            "codice_step": self._normalize_value(self._get(row, "CodiceStep")),
            "ordine": self._normalize_value(self._get(row, "Ordine")),
            "stato_step": self._normalize_value(self._get(row, "StatoStep")),
            "data_avvio": self._normalize_value(self._get(row, "DataAvvio")),
            "data_completamento": self._normalize_value(
                self._get(row, "DataCompletamento")
            ),
            "note_step": self._normalize_value(self._get(row, "NoteStep")),
            "utente_assegnato": self._normalize_value(
                self._get(row, "UtenteAssegnato")
            ),
            "utente_completamento": self._normalize_value(
                self._get(row, "UtenteCompletamento")
            ),
            "id_documento_sottofase": self._normalize_value(
                self._get(row, "IDDocumentoSottofase")
            ),
            "versione_documento": self._normalize_value(
                self._get(row, "VersioneDocumento")
            ),
            "data_creazione": self._normalize_value(self._get(row, "DataCreazione")),
            "data_modifica": self._normalize_value(self._get(row, "DataModifica")),
        }

    def get_sottofase_documentale(
        self,
        id_sottofase: int,
    ) -> dict[str, Any] | None:
        """Legge la sottofase con i campi documentali aggiunti."""

        query = """
            SELECT
                IDSottofase,
                IDFase,
                IDCatalogoSottofase,
                CodiceSottofase,
                Titolo,
                Descrizione,
                Ordine,
                StatoSottofase,
                Icona,
                Colore,
                Responsabile,
                DataScadenza,
                DataAvvio,
                DataCompletamento,
                NoteInterne,
                Attivo,
                DataCreazione,
                DataModifica,
                StepCorrente,
                TestoOperatore,
                HaDocumentoCollegato,
                IDDocumentoCorrente,
                DataUltimaAzione,
                UtenteUltimaAzione,
                VersioneDocumento
            FROM T_ProcedimentoSottofasi
            WHERE IDSottofase = ?
        """

        conn = self._open_access_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(query, (id_sottofase,))
            row = cursor.fetchone()

            if not row:
                return None

            return self._sottofase_row_to_dict(row)
        finally:
            cursor.close()
            conn.close()

    def get_documento_by_id(
        self,
        id_documento_sottofase: int,
    ) -> dict[str, Any] | None:
        """Legge un documento di sottofase per identificativo."""

        query = """
            SELECT
                IDDocumentoSottofase,
                IDSottofase,
                TipoDocumento,
                NomeFile,
                Estensione,
                PercorsoDocumento,
                MimeType,
                DimensioneBytes,
                HashFile,
                VersioneDocumento,
                StatoDocumento,
                DataCollegamento,
                UtenteCollegamento,
                Attivo,
                DataCreazione,
                DataModifica
            FROM T_SottofaseDocumenti
            WHERE IDDocumentoSottofase = ?
        """

        conn = self._open_access_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(query, (id_documento_sottofase,))
            row = cursor.fetchone()

            if not row:
                return None

            return self._documento_row_to_dict(row)
        finally:
            cursor.close()
            conn.close()

    def list_documenti_by_sottofase(
        self,
        id_sottofase: int,
    ) -> list[dict[str, Any]]:
        """Legge i documenti collegati a una sottofase."""

        query = """
            SELECT
                IDDocumentoSottofase,
                IDSottofase,
                TipoDocumento,
                NomeFile,
                Estensione,
                PercorsoDocumento,
                MimeType,
                DimensioneBytes,
                HashFile,
                VersioneDocumento,
                StatoDocumento,
                DataCollegamento,
                UtenteCollegamento,
                Attivo,
                DataCreazione,
                DataModifica
            FROM T_SottofaseDocumenti
            WHERE IDSottofase = ?
            ORDER BY VersioneDocumento DESC, DataCollegamento DESC, IDDocumentoSottofase DESC
        """

        conn = self._open_access_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(query, (id_sottofase,))
            return [self._documento_row_to_dict(row) for row in cursor.fetchall()]
        finally:
            cursor.close()
            conn.close()

    def list_step_operativi_by_sottofase(
        self,
        id_sottofase: int,
    ) -> list[dict[str, Any]]:
        """Legge gli step interni documentali di una sottofase."""

        query = """
            SELECT
                IDStepSottofase,
                IDSottofase,
                CodiceStep,
                Ordine,
                StatoStep,
                DataAvvio,
                DataCompletamento,
                NoteStep,
                UtenteAssegnato,
                UtenteCompletamento,
                IDDocumentoSottofase,
                VersioneDocumento,
                DataCreazione,
                DataModifica
            FROM T_SottofaseStepOperativi
            WHERE IDSottofase = ?
            ORDER BY Ordine ASC, IDStepSottofase ASC
        """

        conn = self._open_access_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(query, (id_sottofase,))
            return [self._step_row_to_dict(row) for row in cursor.fetchall()]
        finally:
            cursor.close()
            conn.close()
