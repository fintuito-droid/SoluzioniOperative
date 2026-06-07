"""Repository per il modello documentale della sottofase.

Il modulo legge le estensioni introdotte nello Step 30L:

- campi documentali in `T_ProcedimentoSottofasi`;
- documenti collegati in `T_SottofaseDocumenti`;
- step interni in `T_SottofaseStepOperativi`.

Le letture non modificano dati. Le scritture ammesse sono comandi espliciti e
testati, mantenendo chiaro il confine tra lettura e mutazione.
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

    def get_step_orizzontale_context(
        self,
        id_step_orizzontale: int,
    ) -> dict[str, Any] | None:
        """Legge i dati minimi di uno step orizzontale per validazioni."""

        query = """
            SELECT
                IDStepOrizzontale,
                IDFase,
                CodiceStep,
                TitoloStep,
                StatoStep,
                Attivo
            FROM T_FaseStepOrizzontali
            WHERE IDStepOrizzontale = ?
        """

        conn = self._open_access_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(query, (id_step_orizzontale,))
            row = cursor.fetchone()
            if not row:
                return None

            return {
                "id_step_orizzontale": self._normalize_value(
                    self._get(row, "IDStepOrizzontale")
                ),
                "id_fase": self._normalize_value(self._get(row, "IDFase")),
                "codice_step": self._normalize_value(self._get(row, "CodiceStep")),
                "titolo_step": self._normalize_value(self._get(row, "TitoloStep")),
                "stato_step": self._normalize_value(self._get(row, "StatoStep")),
                "attivo": bool(self._get(row, "Attivo"))
                if self._get(row, "Attivo") is not None
                else False,
            }
        finally:
            cursor.close()
            conn.close()

    def get_sottofase_aggancio_context(
        self,
        id_sottofase: int,
    ) -> dict[str, Any] | None:
        """Legge i dati minimi della sottofase per l'aggancio allo step."""

        query = """
            SELECT
                IDSottofase,
                IDFase,
                IDStepOrizzontale,
                TipoAggancio,
                SottofasePrincipale,
                StatoSottofase,
                Attivo
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

            return {
                "id_sottofase": self._normalize_value(self._get(row, "IDSottofase")),
                "id_fase": self._normalize_value(self._get(row, "IDFase")),
                "id_step_orizzontale": self._normalize_value(
                    self._get(row, "IDStepOrizzontale")
                ),
                "tipo_aggancio": self._normalize_value(
                    self._get(row, "TipoAggancio")
                ),
                "sottofase_principale": bool(self._get(row, "SottofasePrincipale"))
                if self._get(row, "SottofasePrincipale") is not None
                else False,
                "stato_sottofase": self._normalize_value(
                    self._get(row, "StatoSottofase")
                ),
                "attivo": bool(self._get(row, "Attivo"))
                if self._get(row, "Attivo") is not None
                else False,
            }
        finally:
            cursor.close()
            conn.close()

    def get_sottofase_attiva_by_step(
        self,
        id_step_orizzontale: int,
    ) -> dict[str, Any] | None:
        """Restituisce la prima sottofase attiva collegata allo step, se presente."""

        query = """
            SELECT TOP 1
                IDSottofase,
                IDFase,
                IDStepOrizzontale,
                TipoAggancio,
                SottofasePrincipale,
                StatoSottofase,
                Attivo
            FROM T_ProcedimentoSottofasi
            WHERE IDStepOrizzontale = ?
                AND Attivo = TRUE
            ORDER BY IDSottofase ASC
        """

        conn = self._open_access_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(query, (id_step_orizzontale,))
            row = cursor.fetchone()
            if not row:
                return None

            return {
                "id_sottofase": self._normalize_value(self._get(row, "IDSottofase")),
                "id_fase": self._normalize_value(self._get(row, "IDFase")),
                "id_step_orizzontale": self._normalize_value(
                    self._get(row, "IDStepOrizzontale")
                ),
                "tipo_aggancio": self._normalize_value(
                    self._get(row, "TipoAggancio")
                ),
                "sottofase_principale": bool(self._get(row, "SottofasePrincipale"))
                if self._get(row, "SottofasePrincipale") is not None
                else False,
                "stato_sottofase": self._normalize_value(
                    self._get(row, "StatoSottofase")
                ),
                "attivo": bool(self._get(row, "Attivo"))
                if self._get(row, "Attivo") is not None
                else False,
            }
        finally:
            cursor.close()
            conn.close()

    def list_sottofasi_disponibili_per_step(
        self,
        *,
        id_fase: int,
        id_step_orizzontale: int,
    ) -> list[dict[str, Any]]:
        """Elenca sottofasi candidate all'aggancio manuale allo step."""

        query = """
            SELECT
                sf.IDSottofase,
                sf.IDFase,
                sf.Titolo,
                sf.StatoSottofase,
                sf.Attivo,
                COUNT(d.IDDocumentoSottofase) AS DocumentiCount
            FROM T_ProcedimentoSottofasi AS sf
            LEFT JOIN T_SottofaseDocumenti AS d
                ON d.IDSottofase = sf.IDSottofase
                AND d.Attivo = TRUE
            WHERE sf.IDFase = ?
                AND sf.Attivo = TRUE
                AND sf.IDStepOrizzontale IS NULL
                AND (
                    sf.StatoSottofase IS NULL
                    OR UCASE(sf.StatoSottofase) NOT IN ('ANNULLATA', 'ARCHIVIATA')
                )
            GROUP BY
                sf.IDSottofase,
                sf.IDFase,
                sf.Titolo,
                sf.StatoSottofase,
                sf.Attivo
            ORDER BY sf.IDSottofase ASC
        """

        conn = self._open_access_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(query, (id_fase,))
            items = []
            for row in cursor.fetchall():
                documenti_count = int(self._get(row, "DocumentiCount") or 0)
                items.append(
                    {
                        "id_sottofase": self._normalize_value(
                            self._get(row, "IDSottofase")
                        ),
                        "id_fase": self._normalize_value(self._get(row, "IDFase")),
                        "titolo": self._normalize_value(self._get(row, "Titolo")),
                        "stato_sottofase": self._normalize_value(
                            self._get(row, "StatoSottofase")
                        ),
                        "attivo": bool(self._get(row, "Attivo"))
                        if self._get(row, "Attivo") is not None
                        else False,
                        "ha_documenti": documenti_count > 0,
                        "documenti_count": documenti_count,
                    }
                )
            return items
        finally:
            cursor.close()
            conn.close()

    def associa_sottofase_a_step(
        self,
        *,
        id_sottofase: int,
        id_step_orizzontale: int,
        data_aggancio: datetime,
        utente_aggancio: str,
    ) -> dict[str, Any]:
        """Aggancia una sottofase esistente a uno step orizzontale."""

        query = """
            UPDATE T_ProcedimentoSottofasi
            SET IDStepOrizzontale = ?,
                TipoAggancio = ?,
                SottofasePrincipale = ?,
                DataAggancio = ?,
                UtenteAggancio = ?,
                StatoSottofase = IIF(StatoSottofase IS NULL, ?, StatoSottofase)
            WHERE IDSottofase = ?
        """

        conn = self._open_access_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                query,
                (
                    id_step_orizzontale,
                    "STEP",
                    True,
                    data_aggancio,
                    utente_aggancio,
                    "BOZZA",
                    id_sottofase,
                ),
            )
            rowcount = getattr(cursor, "rowcount", 1)
            if rowcount == 0:
                conn.rollback()
                raise RuntimeError("Aggancio sottofase non applicato.")

            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

        return {
            "success": True,
            "id_step_orizzontale": id_step_orizzontale,
            "id_sottofase": id_sottofase,
            "tipo_aggancio": "STEP",
            "sottofase_principale": True,
        }
