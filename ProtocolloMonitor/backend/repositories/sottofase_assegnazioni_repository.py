"""Repository Access per regole di assegnazione automatica step."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from .base import BaseRepository


RULES_TABLE = "T_RegoleAssegnazioneStep"


class SottofaseAssegnazioniRepository(BaseRepository):
    """Accesso dati per regole assegnazione e partecipanti generati."""

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
    def _row_to_rule(cls, row: Any) -> dict[str, Any]:
        return {
            "id_regola": cls._normalize_value(cls._get(row, "IDRegola")),
            "tipo_procedimento": cls._normalize_value(
                cls._get(row, "TipoProcedimento")
            ),
            "codice_sottofase": cls._normalize_value(
                cls._get(row, "CodiceSottofase")
            ),
            "codice_step": cls._normalize_value(cls._get(row, "CodiceStep")),
            "ruolo_richiesto": cls._normalize_value(
                cls._get(row, "RuoloRichiesto")
            ),
            "id_utente": cls._normalize_value(cls._get(row, "IDUtente")),
            "id_gruppo": cls._normalize_value(cls._get(row, "IDGruppo")),
            "nome_visualizzato": cls._normalize_value(
                cls._get(row, "NomeVisualizzato")
            ),
            "email": cls._normalize_value(cls._get(row, "Email")),
            "obbligatorio": bool(cls._get(row, "Obbligatorio", True)),
            "attiva": bool(cls._get(row, "Attiva", True)),
            "priorita": cls._normalize_value(cls._get(row, "Priorita")),
            "data_creazione": cls._normalize_value(cls._get(row, "DataCreazione")),
            "data_modifica": cls._normalize_value(cls._get(row, "DataModifica")),
        }

    @classmethod
    def _row_to_step(cls, row: Any) -> dict[str, Any]:
        return {
            "id_step_operativo": cls._normalize_value(
                cls._get(row, "IDStepSottofase")
            ),
            "id_sottofase": cls._normalize_value(cls._get(row, "IDSottofase")),
            "codice_step": cls._normalize_value(cls._get(row, "CodiceStep")),
            "ordine": cls._normalize_value(cls._get(row, "Ordine")),
            "stato_step": cls._normalize_value(cls._get(row, "StatoStep")),
        }

    @classmethod
    def _row_to_utente(cls, row: Any) -> dict[str, Any]:
        nome = cls._normalize_value(cls._get(row, "nome"))
        cognome = cls._normalize_value(cls._get(row, "cognome"))
        nome_visualizzato = " ".join(
            str(part).strip()
            for part in (nome, cognome)
            if str(part or "").strip()
        )
        username = cls._normalize_value(cls._get(row, "username"))

        return {
            "id_utente": cls._normalize_value(cls._get(row, "id_utente")),
            "nome_visualizzato": nome_visualizzato or username or "Utente",
            "email": cls._normalize_value(cls._get(row, "email")),
        }

    def ensure_schema(self) -> dict[str, Any]:
        """Crea la tabella regole e gli indici se assenti."""

        conn = self._open_access_connection()
        cursor = conn.cursor()
        table_created = False
        indexes_created: list[str] = []

        try:
            if not self.table_exists(cursor):
                cursor.execute(
                    """
                    CREATE TABLE T_RegoleAssegnazioneStep (
                        IDRegola AUTOINCREMENT PRIMARY KEY,
                        TipoProcedimento TEXT(100) NULL,
                        CodiceSottofase TEXT(50) NULL,
                        CodiceStep TEXT(50) NOT NULL,
                        RuoloRichiesto TEXT(50) NOT NULL,
                        IDUtente LONG NULL,
                        IDGruppo LONG NULL,
                        NomeVisualizzato TEXT(255) NULL,
                        Email TEXT(255) NULL,
                        Obbligatorio YESNO,
                        Attiva YESNO,
                        Priorita SHORT NULL,
                        DataCreazione DATETIME NULL,
                        DataModifica DATETIME NULL
                    )
                    """
                )
                table_created = True

            for index_name, field_name in (
                ("IX_T_RegoleAssegnazioneStep_Attiva", "Attiva"),
                ("IX_T_RegoleAssegnazioneStep_Tipo", "TipoProcedimento"),
                ("IX_T_RegoleAssegnazioneStep_Sottofase", "CodiceSottofase"),
                ("IX_T_RegoleAssegnazioneStep_Step", "CodiceStep"),
                ("IX_T_RegoleAssegnazioneStep_Priorita", "Priorita"),
            ):
                if not self.index_exists(cursor, index_name):
                    cursor.execute(
                        f"CREATE INDEX {index_name} "
                        f"ON {RULES_TABLE} ({field_name})"
                    )
                    indexes_created.append(index_name)

            conn.commit()
            return {
                "table_created": table_created,
                "indexes_created": indexes_created,
            }
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    def table_exists(self, cursor: Any) -> bool:
        tables = getattr(cursor, "tables", None)
        if tables is not None:
            try:
                rows = tables(table=RULES_TABLE)
                fetchone = getattr(rows, "fetchone", None)
                if fetchone is not None:
                    return fetchone() is not None
            except Exception:
                pass

        try:
            cursor.execute(f"SELECT TOP 1 * FROM {RULES_TABLE}")
            return True
        except Exception:
            return False

    def index_exists(self, cursor: Any, index_name: str) -> bool:
        statistics = getattr(cursor, "statistics", None)
        if statistics is None:
            return False

        try:
            rows = statistics(table=RULES_TABLE)
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

    def get_sottofase_context(self, id_sottofase: int) -> dict[str, Any] | None:
        """Restituisce dati minimi di sottofase, fase e procedimento."""

        query = """
            SELECT
                s.IDSottofase,
                s.CodiceSottofase,
                s.IDFase,
                f.IDProcedimento,
                p.TipologiaProcedimento
            FROM
                (T_ProcedimentoSottofasi AS s
                LEFT JOIN T_ProcedimentoFasi AS f ON s.IDFase = f.IDFase)
                LEFT JOIN T_Procedimenti AS p ON f.IDProcedimento = p.IDProcedimento
            WHERE s.IDSottofase = ?
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
                "codice_sottofase": self._normalize_value(
                    self._get(row, "CodiceSottofase")
                ),
                "id_fase": self._normalize_value(self._get(row, "IDFase")),
                "id_procedimento": self._normalize_value(
                    self._get(row, "IDProcedimento")
                ),
                "tipo_procedimento": self._normalize_value(
                    self._get(row, "TipologiaProcedimento")
                ),
            }
        finally:
            cursor.close()
            conn.close()

    def list_steps_by_sottofase(self, id_sottofase: int) -> list[dict[str, Any]]:
        query = """
            SELECT
                IDStepSottofase,
                IDSottofase,
                CodiceStep,
                Ordine,
                StatoStep
            FROM T_SottofaseStepOperativi
            WHERE IDSottofase = ?
            ORDER BY Ordine ASC, IDStepSottofase ASC
        """

        conn = self._open_access_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(query, (id_sottofase,))
            return [self._row_to_step(row) for row in cursor.fetchall()]
        finally:
            cursor.close()
            conn.close()

    def list_codici_step_presenti(self) -> list[str]:
        """Restituisce i codici step realmente presenti nella timeline."""

        query = """
            SELECT CodiceStep
            FROM T_SottofaseStepOperativi
            WHERE CodiceStep IS NOT NULL
            GROUP BY CodiceStep
            ORDER BY CodiceStep
        """

        conn = self._open_access_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(query)
            return [
                str(self._get(row, "CodiceStep") or "").strip().upper()
                for row in cursor.fetchall()
                if str(self._get(row, "CodiceStep") or "").strip()
            ]
        finally:
            cursor.close()
            conn.close()

    def list_utenti_attivi(self) -> list[dict[str, Any]]:
        """Restituisce utenti attivi disponibili per regole default."""

        query = """
            SELECT id_utente, username, nome, cognome, email
            FROM t_utenti
            WHERE attivo = ?
            ORDER BY id_utente ASC
        """

        conn = self._open_access_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(query, (True,))
            return [self._row_to_utente(row) for row in cursor.fetchall()]
        finally:
            cursor.close()
            conn.close()

    def exists_regola_default(
        self,
        *,
        codice_step: str,
        ruolo_richiesto: str,
        id_utente: int | None,
        id_gruppo: int | None,
        email: str | None,
    ) -> bool:
        """Evita duplicati per la regola default proposta."""

        query = """
            SELECT TOP 1 IDRegola
            FROM T_RegoleAssegnazioneStep
            WHERE CodiceStep = ?
              AND RuoloRichiesto = ?
              AND Attiva = ?
        """
        params: list[Any] = [codice_step, ruolo_richiesto, True]

        if id_utente:
            query += " AND IDUtente = ?"
            params.append(id_utente)
        elif id_gruppo:
            query += " AND IDGruppo = ?"
            params.append(id_gruppo)
        elif email:
            query += " AND Email = ?"
            params.append(email)
        else:
            return False

        conn = self._open_access_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(query, tuple(params))
            return cursor.fetchone() is not None
        finally:
            cursor.close()
            conn.close()

    def inserisci_regola_default(
        self,
        *,
        codice_step: str,
        ruolo_richiesto: str,
        id_utente: int | None,
        id_gruppo: int | None,
        nome_visualizzato: str | None,
        email: str | None,
        obbligatorio: bool,
        priorita: int,
        data_creazione: datetime,
    ) -> int:
        """Inserisce una regola default con commit/rollback."""

        query = """
            INSERT INTO T_RegoleAssegnazioneStep (
                TipoProcedimento,
                CodiceSottofase,
                CodiceStep,
                RuoloRichiesto,
                IDUtente,
                IDGruppo,
                NomeVisualizzato,
                Email,
                Obbligatorio,
                Attiva,
                Priorita,
                DataCreazione,
                DataModifica
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        conn = self._open_access_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                query,
                (
                    None,
                    None,
                    codice_step,
                    ruolo_richiesto,
                    id_utente,
                    id_gruppo,
                    nome_visualizzato,
                    email,
                    obbligatorio,
                    True,
                    priorita,
                    data_creazione,
                    data_creazione,
                ),
            )
            cursor.execute("SELECT @@IDENTITY AS IDRegola")
            row = cursor.fetchone()
            id_regola = self._identity_from_row(row, field_name="IDRegola")
            conn.commit()
            return id_regola
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    def list_regole_attive(
        self,
        *,
        tipo_procedimento: str | None,
        codice_sottofase: str | None,
    ) -> list[dict[str, Any]]:
        query = """
            SELECT
                IDRegola,
                TipoProcedimento,
                CodiceSottofase,
                CodiceStep,
                RuoloRichiesto,
                IDUtente,
                IDGruppo,
                NomeVisualizzato,
                Email,
                Obbligatorio,
                Attiva,
                Priorita,
                DataCreazione,
                DataModifica
            FROM T_RegoleAssegnazioneStep
            WHERE Attiva = ?
              AND (TipoProcedimento IS NULL OR TipoProcedimento = '' OR TipoProcedimento = ?)
              AND (CodiceSottofase IS NULL OR CodiceSottofase = '' OR CodiceSottofase = ?)
            ORDER BY Priorita ASC, IDRegola ASC
        """

        conn = self._open_access_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                query,
                (
                    True,
                    tipo_procedimento or "",
                    codice_sottofase or "",
                ),
            )
            return [self._row_to_rule(row) for row in cursor.fetchall()]
        finally:
            cursor.close()
            conn.close()

    def resolve_utenti_for_regola(self, regola: dict[str, Any]) -> list[dict[str, Any]]:
        """Espande IDUtente, IDGruppo o Email della regola in candidati."""

        utenti: list[dict[str, Any]] = []
        seen: set[tuple[str, str]] = set()

        def add(candidate: dict[str, Any] | None) -> None:
            if not candidate:
                return

            key = (
                str(candidate.get("id_utente") or ""),
                str(candidate.get("email") or "").strip().lower(),
            )
            if key in seen:
                return

            seen.add(key)
            utenti.append(candidate)

        id_utente = regola.get("id_utente")
        id_gruppo = regola.get("id_gruppo")

        if id_utente:
            add(self.get_utente_by_id(int(id_utente)))

        if id_gruppo:
            for utente in self.list_utenti_by_gruppo(int(id_gruppo)):
                add(utente)

        if not id_utente and not id_gruppo and regola.get("email"):
            add(
                {
                    "id_utente": None,
                    "nome_visualizzato": (
                        regola.get("nome_visualizzato")
                        or regola.get("email")
                        or "Partecipante"
                    ),
                    "email": regola.get("email"),
                }
            )

        return utenti

    def get_utente_by_id(self, id_utente: int) -> dict[str, Any] | None:
        query = """
            SELECT id_utente, username, nome, cognome, email
            FROM t_utenti
            WHERE id_utente = ? AND attivo = ?
        """

        conn = self._open_access_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(query, (id_utente, True))
            row = cursor.fetchone()
            return self._row_to_utente(row) if row else None
        finally:
            cursor.close()
            conn.close()

    def list_utenti_by_gruppo(self, id_gruppo: int) -> list[dict[str, Any]]:
        query = """
            SELECT u.id_utente, u.username, u.nome, u.cognome, u.email
            FROM r_gruppi_utenti AS gu
            INNER JOIN t_utenti AS u ON gu.id_utente = u.id_utente
            WHERE gu.id_gruppo = ?
              AND gu.attivo = ?
              AND u.attivo = ?
            ORDER BY u.cognome ASC, u.nome ASC, u.id_utente ASC
        """

        conn = self._open_access_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(query, (id_gruppo, True, True))
            return [self._row_to_utente(row) for row in cursor.fetchall()]
        finally:
            cursor.close()
            conn.close()

    def exists_partecipante(
        self,
        *,
        id_sottofase: int,
        id_step_operativo: int,
        id_utente: int | None,
        email: str | None,
        ruolo: str,
    ) -> bool:
        base = """
            SELECT TOP 1 IDPartecipante
            FROM T_SottofasePartecipanti
            WHERE IDSottofase = ?
              AND IDStepOperativo = ?
              AND Ruolo = ?
              AND Attivo = ?
        """
        params: list[Any] = [id_sottofase, id_step_operativo, ruolo, True]

        if id_utente:
            base += " AND IDUtente = ?"
            params.append(id_utente)
        elif email:
            base += " AND Email = ?"
            params.append(email)
        else:
            return False

        conn = self._open_access_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(base, tuple(params))
            return cursor.fetchone() is not None
        finally:
            cursor.close()
            conn.close()

    def inserisci_partecipante_assegnato(
        self,
        *,
        id_sottofase: int,
        id_step_operativo: int,
        id_utente: int | None,
        nome_visualizzato: str,
        email: str | None,
        ruolo: str,
        obbligatorio: bool,
        ordine: int | None,
        iniziali: str,
        data_creazione: datetime,
    ) -> int:
        """Inserisce un partecipante generato da regola con commit/rollback."""

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
                    id_utente,
                    nome_visualizzato,
                    email,
                    ruolo,
                    "ASSEGNATO",
                    obbligatorio,
                    ordine,
                    None,
                    iniziali,
                    data_creazione,
                    None,
                    "Assegnazione automatica da regola.",
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
    def _identity_from_row(row: Any, *, field_name: str = "IDPartecipante") -> int:
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
