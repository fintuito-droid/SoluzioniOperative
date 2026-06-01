"""Repository Access per partecipanti collegati a una sottofase."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from .base import BaseRepository


TABLE_NAME = "T_SottofasePartecipanti"


class SottofasePartecipantiRepository(BaseRepository):
    """Repository Access-compatible per partecipanti sottofase."""

    @staticmethod
    def _normalize_value(value: Any) -> Any:
        if isinstance(value, datetime):
            return value.isoformat(sep=" ")

        if isinstance(value, date):
            return value.isoformat()

        return value

    @staticmethod
    def _get(row: Any, name: str, default: Any = None) -> Any:
        if row is None:
            return default

        if isinstance(row, dict):
            return row.get(name, default)

        return getattr(row, name, default)

    @classmethod
    def _row_to_dict(cls, row: Any) -> dict[str, Any]:
        return {
            "id_partecipante": cls._normalize_value(cls._get(row, "IDPartecipante")),
            "id_sottofase": cls._normalize_value(cls._get(row, "IDSottofase")),
            "id_step_operativo": cls._normalize_value(
                cls._get(row, "IDStepOperativo")
            ),
            "id_utente": cls._normalize_value(cls._get(row, "IDUtente")),
            "nome_visualizzato": cls._normalize_value(
                cls._get(row, "NomeVisualizzato")
            ),
            "email": cls._normalize_value(cls._get(row, "Email")),
            "ruolo": cls._normalize_value(cls._get(row, "Ruolo")),
            "stato_partecipante": cls._normalize_value(
                cls._get(row, "StatoPartecipante")
            ),
            "partecipante_obbligatorio": bool(
                cls._get(row, "PartecipanteObbligatorio", True)
            ),
            "ordine": cls._normalize_value(cls._get(row, "Ordine")),
            "colore_avatar": cls._normalize_value(cls._get(row, "ColoreAvatar")),
            "iniziali": cls._normalize_value(cls._get(row, "Iniziali")),
            "data_assegnazione": cls._normalize_value(
                cls._get(row, "DataAssegnazione")
            ),
            "data_azione": cls._normalize_value(cls._get(row, "DataAzione")),
            "note_partecipante": cls._normalize_value(
                cls._get(row, "NotePartecipante")
            ),
            "attivo": bool(cls._get(row, "Attivo"))
            if cls._get(row, "Attivo") is not None
            else False,
            "data_creazione": cls._normalize_value(cls._get(row, "DataCreazione")),
            "data_modifica": cls._normalize_value(cls._get(row, "DataModifica")),
        }

    def ensure_schema(self) -> dict[str, Any]:
        """Crea tabella e indici se mancanti, in modo idempotente."""

        conn = self._open_access_connection()
        cursor = conn.cursor()

        created_table = False
        added_columns: list[str] = []
        created_indexes: list[str] = []

        try:
            if not self.table_exists(cursor):
                cursor.execute(
                    """
                    CREATE TABLE T_SottofasePartecipanti (
                        IDPartecipante AUTOINCREMENT PRIMARY KEY,
                        IDSottofase LONG NOT NULL,
                        IDStepOperativo LONG NULL,
                        IDUtente LONG NULL,
                        NomeVisualizzato TEXT(255) NOT NULL,
                        Email TEXT(255) NULL,
                        Ruolo TEXT(50) NOT NULL,
                        StatoPartecipante TEXT(50) NOT NULL,
                        PartecipanteObbligatorio YESNO,
                        Ordine SHORT NULL,
                        ColoreAvatar TEXT(20) NULL,
                        Iniziali TEXT(10) NULL,
                        DataAssegnazione DATETIME NULL,
                        DataAzione DATETIME NULL,
                        NotePartecipante LONGTEXT NULL,
                        Attivo YESNO,
                        DataCreazione DATETIME NULL,
                        DataModifica DATETIME NULL
                    )
                    """
                )
                created_table = True

            if not created_table and not self.column_exists(cursor, "IDStepOperativo"):
                cursor.execute(
                    f"ALTER TABLE {TABLE_NAME} "
                    "ADD COLUMN IDStepOperativo LONG NULL"
                )
                added_columns.append("IDStepOperativo")

            if (
                not created_table
                and not self.column_exists(cursor, "PartecipanteObbligatorio")
            ):
                cursor.execute(
                    f"ALTER TABLE {TABLE_NAME} "
                    "ADD COLUMN PartecipanteObbligatorio YESNO"
                )
                added_columns.append("PartecipanteObbligatorio")

            for index_name, field_name in (
                ("IX_T_SottofasePartecipanti_IDSottofase", "IDSottofase"),
                (
                    "IX_T_SottofasePartecipanti_IDStepOperativo",
                    "IDStepOperativo",
                ),
                ("IX_T_SottofasePartecipanti_Ruolo", "Ruolo"),
                ("IX_T_SottofasePartecipanti_Stato", "StatoPartecipante"),
                ("IX_T_SottofasePartecipanti_Attivo", "Attivo"),
            ):
                if not self.index_exists(cursor, index_name):
                    cursor.execute(
                        f"CREATE INDEX {index_name} "
                        f"ON {TABLE_NAME} ({field_name})"
                    )
                    created_indexes.append(index_name)

            conn.commit()
            return {
                "table_created": created_table,
                "columns_added": added_columns,
                "indexes_created": created_indexes,
            }
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    def table_exists(self, cursor: Any) -> bool:
        """Verifica se la tabella dei partecipanti esiste."""

        tables = getattr(cursor, "tables", None)
        if tables is not None:
            try:
                rows = tables(table=TABLE_NAME)
                fetchone = getattr(rows, "fetchone", None)
                if fetchone is not None:
                    return fetchone() is not None
            except Exception:
                pass

        try:
            cursor.execute(f"SELECT TOP 1 * FROM {TABLE_NAME}")
            return True
        except Exception:
            return False

    def column_exists(self, cursor: Any, column_name: str) -> bool:
        """Verifica se un campo esiste nella tabella partecipanti."""

        columns = getattr(cursor, "columns", None)
        if columns is not None:
            try:
                rows = columns(table=TABLE_NAME, column=column_name)
                fetchone = getattr(rows, "fetchone", None)
                if fetchone is not None:
                    return fetchone() is not None
            except Exception:
                pass

        try:
            cursor.execute(f"SELECT TOP 1 {column_name} FROM {TABLE_NAME}")
            return True
        except Exception:
            return False

    def index_exists(self, cursor: Any, index_name: str) -> bool:
        """Verifica se un indice esiste sulla tabella partecipanti."""

        statistics = getattr(cursor, "statistics", None)
        if statistics is None:
            return False

        try:
            rows = statistics(table=TABLE_NAME)
            fetchall = getattr(rows, "fetchall", None)
            if fetchall is None:
                return False

            for row in fetchall():
                if str(self._get(row, "index_name", "")).upper() == index_name.upper():
                    return True
                if str(self._get(row, "INDEX_NAME", "")).upper() == index_name.upper():
                    return True
        except Exception:
            return False

        return False

    def list_by_sottofase(self, id_sottofase: int) -> list[dict[str, Any]]:
        """Restituisce i partecipanti attivi di una sottofase."""

        query = """
            SELECT
                IDPartecipante,
                IDSottofase,
                IDStepOperativo,
                IDUtente,
                NomeVisualizzato,
                Email,
                Ruolo,
                StatoPartecipante,
                PartecipanteObbligatorio,
                Ordine,
                ColoreAvatar,
                Iniziali,
                DataAssegnazione,
                DataAzione,
                NotePartecipante,
                Attivo,
                DataCreazione,
                DataModifica
            FROM T_SottofasePartecipanti
            WHERE IDSottofase = ? AND Attivo = ?
            ORDER BY Ordine ASC, IDPartecipante ASC
        """

        conn = self._open_access_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(query, (id_sottofase, True))
            return [self._row_to_dict(row) for row in cursor.fetchall()]
        finally:
            cursor.close()
            conn.close()

    def get_by_id(self, id_partecipante: int) -> dict[str, Any] | None:
        """Legge un partecipante per identificativo."""

        query = """
            SELECT
                IDPartecipante,
                IDSottofase,
                IDStepOperativo,
                IDUtente,
                NomeVisualizzato,
                Email,
                Ruolo,
                StatoPartecipante,
                PartecipanteObbligatorio,
                Ordine,
                ColoreAvatar,
                Iniziali,
                DataAssegnazione,
                DataAzione,
                NotePartecipante,
                Attivo,
                DataCreazione,
                DataModifica
            FROM T_SottofasePartecipanti
            WHERE IDPartecipante = ?
        """

        conn = self._open_access_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(query, (id_partecipante,))
            row = cursor.fetchone()
            return self._row_to_dict(row) if row else None
        finally:
            cursor.close()
            conn.close()

    def exists_duplicate(
        self,
        *,
        id_sottofase: int,
        id_step_operativo: int | None,
        email: str,
        ruolo: str,
    ) -> bool:
        """Controlla duplicati evidenti per sottofase, step, email e ruolo."""

        if id_step_operativo is None:
            query = """
                SELECT TOP 1 IDPartecipante
                FROM T_SottofasePartecipanti
                WHERE IDSottofase = ?
                  AND IDStepOperativo IS NULL
                  AND Email = ?
                  AND Ruolo = ?
                  AND Attivo = ?
            """
            params = (id_sottofase, email, ruolo, True)
        else:
            query = """
                SELECT TOP 1 IDPartecipante
                FROM T_SottofasePartecipanti
                WHERE IDSottofase = ?
                  AND IDStepOperativo = ?
                  AND Email = ?
                  AND Ruolo = ?
                  AND Attivo = ?
            """
            params = (id_sottofase, id_step_operativo, email, ruolo, True)

        conn = self._open_access_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(query, params)
            return cursor.fetchone() is not None
        finally:
            cursor.close()
            conn.close()

    def get_step_operativo_by_id(self, id_step_operativo: int) -> dict[str, Any] | None:
        """Legge uno step operativo/timeline per validare collegamenti."""

        query = """
            SELECT
                IDStepSottofase,
                IDSottofase,
                CodiceStep,
                Ordine,
                StatoStep
            FROM T_SottofaseStepOperativi
            WHERE IDStepSottofase = ?
        """

        conn = self._open_access_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(query, (id_step_operativo,))
            row = cursor.fetchone()
            if not row:
                return None

            return {
                "id_step_operativo": self._normalize_value(
                    self._get(row, "IDStepSottofase")
                ),
                "id_sottofase": self._normalize_value(self._get(row, "IDSottofase")),
                "codice_step": self._normalize_value(self._get(row, "CodiceStep")),
                "ordine": self._normalize_value(self._get(row, "Ordine")),
                "stato_step": self._normalize_value(self._get(row, "StatoStep")),
            }
        finally:
            cursor.close()
            conn.close()

    def list_by_step(
        self,
        *,
        id_sottofase: int,
        id_step_operativo: int,
    ) -> list[dict[str, Any]]:
        """Restituisce partecipanti attivi collegati a uno step timeline."""

        query = """
            SELECT
                IDPartecipante,
                IDSottofase,
                IDStepOperativo,
                IDUtente,
                NomeVisualizzato,
                Email,
                Ruolo,
                StatoPartecipante,
                PartecipanteObbligatorio,
                Ordine,
                ColoreAvatar,
                Iniziali,
                DataAssegnazione,
                DataAzione,
                NotePartecipante,
                Attivo,
                DataCreazione,
                DataModifica
            FROM T_SottofasePartecipanti
            WHERE IDSottofase = ?
              AND IDStepOperativo = ?
              AND Attivo = ?
            ORDER BY Ordine ASC, IDPartecipante ASC
        """

        conn = self._open_access_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(query, (id_sottofase, id_step_operativo, True))
            return [self._row_to_dict(row) for row in cursor.fetchall()]
        finally:
            cursor.close()
            conn.close()

    def inserisci_partecipante(
        self,
        *,
        id_sottofase: int,
        id_step_operativo: int | None,
        nome_visualizzato: str,
        email: str | None,
        ruolo: str,
        stato_partecipante: str,
        partecipante_obbligatorio: bool,
        ordine: int | None,
        colore_avatar: str | None,
        iniziali: str,
        note_partecipante: str | None,
        data_creazione: datetime,
    ) -> int:
        """Inserisce un partecipante e restituisce l'ID creato."""

        query = """
            INSERT INTO T_SottofasePartecipanti (
                IDSottofase,
                IDStepOperativo,
                IDUtente,
                NomeVisualizzato,
                Email,
                Ruolo,
                StatoPartecipante,
                PartecipanteObbligatorio,
                Ordine,
                ColoreAvatar,
                Iniziali,
                DataAssegnazione,
                DataAzione,
                NotePartecipante,
                Attivo,
                DataCreazione,
                DataModifica
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        conn = self._open_access_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                query,
                (
                    id_sottofase,
                    id_step_operativo,
                    None,
                    nome_visualizzato,
                    email,
                    ruolo,
                    stato_partecipante,
                    partecipante_obbligatorio,
                    ordine,
                    colore_avatar,
                    iniziali,
                    data_creazione,
                    None,
                    note_partecipante,
                    True,
                    data_creazione,
                    data_creazione,
                ),
            )
            cursor.execute("SELECT @@IDENTITY AS IDPartecipante")
            row = cursor.fetchone()
            id_partecipante = self._identity_from_row(row)
            conn.commit()
            return id_partecipante
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def _identity_from_row(row: Any) -> int:
        if row is None:
            raise RuntimeError("ID partecipante non restituito da Access.")

        if isinstance(row, (tuple, list)):
            value = row[0]
        else:
            try:
                value = row[0]
            except (TypeError, IndexError):
                value = getattr(row, "IDPartecipante", None)

        if value is None:
            raise RuntimeError("ID partecipante non leggibile da Access.")

        return int(value)

    def completa_step_operativo_da_partecipanti(
        self,
        *,
        id_sottofase: int,
        id_step_operativo: int,
        data_completamento: datetime,
    ) -> dict[str, Any]:
        """Marca lo step come completato e chiude la sottofase se tutti gli step sono chiusi."""

        conn = self._open_access_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                UPDATE T_SottofaseStepOperativi
                SET
                    StatoStep = ?,
                    DataCompletamento = ?,
                    DataModifica = ?
                WHERE IDStepSottofase = ?
                  AND IDSottofase = ?
                """,
                (
                    "COMPLETATO",
                    data_completamento,
                    data_completamento,
                    id_step_operativo,
                    id_sottofase,
                ),
            )

            if getattr(cursor, "rowcount", 1) == 0:
                raise RuntimeError("Step operativo non aggiornato.")

            sottofase_completata = False
            if self._all_steps_completed_or_cancelled(
                cursor=cursor,
                id_sottofase=id_sottofase,
            ):
                cursor.execute(
                    """
                    UPDATE T_ProcedimentoSottofasi
                    SET
                        StatoSottofase = ?,
                        DataCompletamento = ?,
                        DataUltimaAzione = ?,
                        DataModifica = ?
                    WHERE IDSottofase = ?
                    """,
                    (
                        "COMPLETATA",
                        data_completamento,
                        data_completamento,
                        data_completamento,
                        id_sottofase,
                    ),
                )
                sottofase_completata = getattr(cursor, "rowcount", 1) != 0

            conn.commit()
            return {
                "step_completato": True,
                "sottofase_completata": sottofase_completata,
            }
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    def _all_steps_completed_or_cancelled(
        self,
        *,
        cursor: Any,
        id_sottofase: int,
    ) -> bool:
        """Verifica se tutti gli step della sottofase sono completati o annullati."""

        cursor.execute(
            """
            SELECT StatoStep
            FROM T_SottofaseStepOperativi
            WHERE IDSottofase = ?
            """,
            (id_sottofase,),
        )
        rows = cursor.fetchall()

        if not rows:
            return False

        for row in rows:
            stato = str(self._get(row, "StatoStep", "") or "").strip().upper()
            if stato not in {"COMPLETATO", "COMPLETED", "CANCELLED", "ANNULLATO"}:
                return False

        return True
