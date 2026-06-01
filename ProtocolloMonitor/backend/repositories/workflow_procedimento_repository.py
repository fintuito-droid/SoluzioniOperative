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

    def procedimento_exists(self, id_procedimento: int) -> bool:
        """Verifica se il procedimento esiste."""

        query = """
            SELECT COUNT(*) AS Totale
            FROM T_Procedimenti
            WHERE IDProcedimento = ?
        """

        conn = self._open_access_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(query, (id_procedimento,))
            row = cursor.fetchone()
            return int(self._get(row, "Totale", 0) or 0) > 0
        finally:
            cursor.close()
            conn.close()

    def crea_fase_procedimento(
        self,
        *,
        id_procedimento: int,
        titolo: str,
        descrizione: str | None,
        data_creazione: datetime,
    ) -> dict[str, Any]:
        """Inserisce una fase verticale e restituisce il record creato."""

        conn = self._open_access_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                SELECT MAX(Ordine) AS MaxOrdine
                FROM T_ProcedimentoFasi
                WHERE IDProcedimento = ?
                """,
                (id_procedimento,),
            )
            row = cursor.fetchone()
            max_ordine = self._get(row, "MaxOrdine")
            ordine = 1 if max_ordine is None else int(max_ordine) + 1

            cursor.execute(
                """
                INSERT INTO T_ProcedimentoFasi (
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
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    id_procedimento,
                    self._codice_fase_from_titolo(titolo),
                    titolo,
                    descrizione,
                    ordine,
                    "NON_AVVIATA",
                    None,
                    None,
                    None,
                    None,
                    False,
                    False,
                    True,
                    data_creazione,
                    data_creazione,
                ),
            )
            cursor.execute("SELECT @@IDENTITY AS IDFase")
            identity_row = cursor.fetchone()
            id_fase = self._identity_from_row(identity_row, field_name="IDFase")
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

        created = self.get_fase_detail(id_fase)
        if created is None:
            raise RuntimeError("Fase creata ma non rileggibile.")

        return created

    def aggiorna_fase_procedimento(
        self,
        *,
        id_procedimento: int,
        id_fase: int,
        titolo: str,
        descrizione: str | None,
        data_modifica: datetime,
    ) -> dict[str, Any] | None:
        """Aggiorna titolo e descrizione di una fase esistente."""

        query = """
            UPDATE T_ProcedimentoFasi
            SET Titolo = ?,
                Descrizione = ?,
                DataModifica = ?
            WHERE IDFase = ? AND IDProcedimento = ?
        """

        conn = self._open_access_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                query,
                (
                    titolo,
                    descrizione,
                    data_modifica,
                    id_fase,
                    id_procedimento,
                ),
            )
            if getattr(cursor, "rowcount", 1) == 0:
                conn.rollback()
                return None

            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

        return self.get_fase_detail(id_fase)

    @staticmethod
    def _identity_from_row(row: Any, *, field_name: str = "IDFase") -> int:
        if row is None:
            raise RuntimeError("ID non restituito da Access.")

        if isinstance(row, (tuple, list)):
            value = row[0]
        else:
            try:
                value = row[0]
            except (TypeError, IndexError):
                value = getattr(row, field_name, None)

        if value is None:
            raise RuntimeError("ID non leggibile da Access.")

        return int(value)

    @staticmethod
    def _codice_fase_from_titolo(titolo: str) -> str:
        normalized = "".join(
            char.upper() if char.isalnum() else "_"
            for char in str(titolo or "").strip()
        )
        parts = [part for part in normalized.split("_") if part]
        return "_".join(parts)[:50] or "FASE"

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

    def get_sottofase_detail(self, id_sottofase: int) -> dict[str, Any] | None:
        """Legge il dettaglio di una sottofase, oppure `None` se non esiste."""

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

    def crea_sottofase_fase(
        self,
        *,
        id_fase: int,
        codice_sottofase: str,
        titolo: str,
        descrizione: str | None,
        responsabile: str | None,
        data_scadenza: Any,
        data_creazione: datetime,
    ) -> dict[str, Any]:
        """Inserisce una sottofase dentro una fase e restituisce il record."""

        conn = self._open_access_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                SELECT MAX(Ordine) AS MaxOrdine
                FROM T_ProcedimentoSottofasi
                WHERE IDFase = ?
                """,
                (id_fase,),
            )
            row = cursor.fetchone()
            max_ordine = self._get(row, "MaxOrdine")
            ordine = 1 if max_ordine is None else int(max_ordine) + 1

            cursor.execute(
                """
                INSERT INTO T_ProcedimentoSottofasi (
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
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    id_fase,
                    None,
                    codice_sottofase,
                    titolo,
                    descrizione,
                    ordine,
                    "NON_AVVIATA",
                    "mdi-checkbox-blank-circle-outline",
                    "grey",
                    responsabile,
                    data_scadenza,
                    None,
                    None,
                    None,
                    True,
                    data_creazione,
                    data_creazione,
                    None,
                    None,
                    False,
                    None,
                    None,
                    None,
                    None,
                ),
            )
            cursor.execute("SELECT @@IDENTITY AS IDSottofase")
            identity_row = cursor.fetchone()
            id_sottofase = self._identity_from_row(
                identity_row,
                field_name="IDSottofase",
            )
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

        created = self.get_sottofase_detail(id_sottofase)
        if created is None:
            raise RuntimeError("Sottofase creata ma non rileggibile.")

        return created

    def aggiorna_sottofase_fase(
        self,
        *,
        id_fase: int,
        id_sottofase: int,
        codice_sottofase: str | None,
        titolo: str,
        descrizione: str | None,
        responsabile: str | None,
        data_scadenza: Any,
        data_modifica: datetime,
    ) -> dict[str, Any] | None:
        """Aggiorna i campi editabili di una sottofase."""

        query = """
            UPDATE T_ProcedimentoSottofasi
            SET CodiceSottofase = ?,
                Titolo = ?,
                Descrizione = ?,
                Responsabile = ?,
                DataScadenza = ?,
                DataModifica = ?
            WHERE IDSottofase = ? AND IDFase = ?
        """

        conn = self._open_access_connection()
        cursor = conn.cursor()

        try:
            existing = self.get_sottofase_detail(id_sottofase)
            if existing is None:
                return None

            cursor.execute(
                query,
                (
                    codice_sottofase or existing.get("codice_sottofase"),
                    titolo,
                    descrizione,
                    responsabile,
                    data_scadenza,
                    data_modifica,
                    id_sottofase,
                    id_fase,
                ),
            )
            if getattr(cursor, "rowcount", 1) == 0:
                conn.rollback()
                return None

            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

        return self.get_sottofase_detail(id_sottofase)

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
