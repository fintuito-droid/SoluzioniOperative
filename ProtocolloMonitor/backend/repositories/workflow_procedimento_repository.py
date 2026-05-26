"""Repository read-only per workflow procedimento.

Il modulo legge le nuove tabelle Access introdotte per il workflow del
procedimento:

- `T_ProcedimentoFasi`
- `T_ProcedimentoSottofasi`
- `L_CatalogoSottofasi`

Il repository e volutamente solo in lettura: non crea fasi, non modifica stati,
non inserisce sottofasi e non aggiorna il catalogo. Questa separazione mantiene
prudente l'integrazione backend dopo la creazione reale dello schema Access e
prepara una futura implementazione PostgreSQL con lo stesso contratto logico.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from .base import BaseRepository


class WorkflowProcedimentoRepository(BaseRepository):
    """Repository Access-compatible per leggere il workflow dei procedimenti."""

    @staticmethod
    def _normalize_value(value: Any) -> Any:
        """Converte date Access in stringhe ISO e lascia invariati gli altri valori."""

        if isinstance(value, datetime):
            return value.isoformat(sep=" ")

        if isinstance(value, date):
            return value.isoformat()

        return value

    @staticmethod
    def _get(row: Any, name: str, default: Any = None) -> Any:
        """Legge un campo da righe pyodbc o da fake row usate nei test."""

        if row is None:
            return default

        if isinstance(row, dict):
            return row.get(name, default)

        return getattr(row, name, default)

    def _fase_row_to_dict(self, row: Any) -> dict[str, Any]:
        """Converte una riga `T_ProcedimentoFasi` in dizionario snake_case."""

        return {
            "id_fase": self._normalize_value(self._get(row, "IDFase")),
            "id_procedimento": self._normalize_value(
                self._get(row, "IDProcedimento")
            ),
            "codice_fase": self._normalize_value(self._get(row, "CodiceFase")),
            "titolo": self._normalize_value(self._get(row, "Titolo")),
            "descrizione": self._normalize_value(self._get(row, "Descrizione")),
            "ordine": self._normalize_value(self._get(row, "Ordine")),
            "stato_fase": self._normalize_value(self._get(row, "StatoFase")),
            "responsabile": self._normalize_value(self._get(row, "Responsabile")),
            "data_scadenza": self._normalize_value(self._get(row, "DataScadenza")),
            "data_avvio": self._normalize_value(self._get(row, "DataAvvio")),
            "data_completamento": self._normalize_value(
                self._get(row, "DataCompletamento")
            ),
            "obbligatoria": bool(self._get(row, "Obbligatoria"))
            if self._get(row, "Obbligatoria") is not None
            else False,
            "bloccante": bool(self._get(row, "Bloccante"))
            if self._get(row, "Bloccante") is not None
            else False,
            "attivo": bool(self._get(row, "Attivo"))
            if self._get(row, "Attivo") is not None
            else False,
            "data_creazione": self._normalize_value(self._get(row, "DataCreazione")),
            "data_modifica": self._normalize_value(self._get(row, "DataModifica")),
        }

    def _sottofase_row_to_dict(self, row: Any) -> dict[str, Any]:
        """Converte una riga `T_ProcedimentoSottofasi` in dizionario snake_case."""

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
        }

    def _catalogo_row_to_dict(self, row: Any) -> dict[str, Any]:
        """Converte una riga `L_CatalogoSottofasi` in dizionario snake_case."""

        return {
            "id_catalogo_sottofase": self._normalize_value(
                self._get(row, "IDCatalogoSottofase")
            ),
            "codice_sottofase": self._normalize_value(
                self._get(row, "CodiceSottofase")
            ),
            "titolo": self._normalize_value(self._get(row, "Titolo")),
            "descrizione": self._normalize_value(self._get(row, "Descrizione")),
            "icona": self._normalize_value(self._get(row, "Icona")),
            "colore": self._normalize_value(self._get(row, "Colore")),
            "categoria": self._normalize_value(self._get(row, "Categoria")),
            "ordine_default": self._normalize_value(self._get(row, "OrdineDefault")),
            "attivo": bool(self._get(row, "Attivo"))
            if self._get(row, "Attivo") is not None
            else False,
            "data_creazione": self._normalize_value(self._get(row, "DataCreazione")),
            "data_modifica": self._normalize_value(self._get(row, "DataModifica")),
        }

    def list_fasi_by_procedimento(
        self,
        id_procedimento: int,
    ) -> list[dict[str, Any]]:
        """Legge le fasi associate a un procedimento."""

        query = """
            SELECT
                IDFase,
                IDProcedimento,
                CodiceFase,
                Titolo,
                Descrizione,
                Ordine,
                StatoFase,
                Responsabile,
                DataScadenza,
                DataAvvio,
                DataCompletamento,
                Obbligatoria,
                Bloccante,
                Attivo,
                DataCreazione,
                DataModifica
            FROM T_ProcedimentoFasi
            WHERE IDProcedimento = ?
            ORDER BY Ordine ASC, IDFase ASC
        """

        conn = self._open_access_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(query, (id_procedimento,))
            return [self._fase_row_to_dict(row) for row in cursor.fetchall()]
        finally:
            cursor.close()
            conn.close()

    def get_fase_detail(self, id_fase: int) -> dict[str, Any] | None:
        """Legge il dettaglio di una fase, oppure `None` se non esiste."""

        query = """
            SELECT
                IDFase,
                IDProcedimento,
                CodiceFase,
                Titolo,
                Descrizione,
                Ordine,
                StatoFase,
                Responsabile,
                DataScadenza,
                DataAvvio,
                DataCompletamento,
                Obbligatoria,
                Bloccante,
                Attivo,
                DataCreazione,
                DataModifica
            FROM T_ProcedimentoFasi
            WHERE IDFase = ?
        """

        conn = self._open_access_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(query, (id_fase,))
            row = cursor.fetchone()

            if not row:
                return None

            return self._fase_row_to_dict(row)
        finally:
            cursor.close()
            conn.close()

    def list_sottofasi_by_fase(self, id_fase: int) -> list[dict[str, Any]]:
        """Legge le sottofasi associate a una fase."""

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
                DataModifica
            FROM T_ProcedimentoSottofasi
            WHERE IDFase = ?
            ORDER BY Ordine ASC, IDSottofase ASC
        """

        conn = self._open_access_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(query, (id_fase,))
            return [self._sottofase_row_to_dict(row) for row in cursor.fetchall()]
        finally:
            cursor.close()
            conn.close()

    def list_catalogo_sottofasi(
        self,
        attivo_only: bool = True,
    ) -> list[dict[str, Any]]:
        """Legge il catalogo sottofasi, opzionalmente filtrando gli attivi."""

        where_clause = "WHERE Attivo = ?" if attivo_only else ""
        query = f"""
            SELECT
                IDCatalogoSottofase,
                CodiceSottofase,
                Titolo,
                Descrizione,
                Icona,
                Colore,
                Categoria,
                OrdineDefault,
                Attivo,
                DataCreazione,
                DataModifica
            FROM L_CatalogoSottofasi
            {where_clause}
            ORDER BY OrdineDefault ASC, Titolo ASC, IDCatalogoSottofase ASC
        """

        conn = self._open_access_connection()
        cursor = conn.cursor()

        try:
            if attivo_only:
                cursor.execute(query, (True,))
            else:
                cursor.execute(query)

            return [self._catalogo_row_to_dict(row) for row in cursor.fetchall()]
        finally:
            cursor.close()
            conn.close()
