"""Repository per fasi verticali e step orizzontali del procedimento.

Il modulo usa le tabelle Access del procedimento:

- `T_ProcedimentoFasi`
- `T_FaseStepOrizzontali`

Restano presenti alcune letture legacy del vecchio modello sottofase solo per
compatibilita difensiva; la creazione/modifica complessa delle sottofasi e stata
rimossa dal contratto del repository.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from .base import BaseRepository


class WorkflowProcedimentoRepository(BaseRepository):
    """Repository Access-compatible per leggere il workflow dei procedimenti."""

    STEP_ORIZZONTALI_DEFAULT = [
        ("REDIGI", "Redigi", 1),
        ("REVISIONA", "Revisiona", 2),
        ("FIRMA", "Firma", 3),
        ("PROTOCOLLA", "Protocolla", 4),
        ("FINE", "Fine", 5),
    ]

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

    def _step_orizzontale_row_to_dict(self, row: Any) -> dict[str, Any]:
        """Converte una riga `T_FaseStepOrizzontali` in dizionario snake_case."""

        return {
            "id_step_orizzontale": self._normalize_value(
                self._get(row, "IDStepOrizzontale")
            ),
            "id_fase": self._normalize_value(self._get(row, "IDFase")),
            "codice_step": self._normalize_value(self._get(row, "CodiceStep")),
            "titolo_step": self._normalize_value(self._get(row, "TitoloStep")),
            "ordine": self._normalize_value(self._get(row, "Ordine")),
            "stato_step": self._normalize_value(self._get(row, "StatoStep")),
            "data_avvio": self._normalize_value(self._get(row, "DataAvvio")),
            "data_completamento": self._normalize_value(
                self._get(row, "DataCompletamento")
            ),
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

    def list_step_orizzontali_by_fase(
        self,
        id_fase: int,
    ) -> list[dict[str, Any]]:
        """Legge gli step orizzontali fissi associati a una fase."""

        query = """
            SELECT
                IDStepOrizzontale,
                IDFase,
                CodiceStep,
                TitoloStep,
                Ordine,
                StatoStep,
                DataAvvio,
                DataCompletamento,
                Attivo,
                DataCreazione,
                DataModifica
            FROM T_FaseStepOrizzontali
            WHERE IDFase = ? AND Attivo = ?
            ORDER BY Ordine ASC, IDStepOrizzontale ASC
        """

        conn = self._open_access_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(query, (id_fase, True))
            return [
                self._step_orizzontale_row_to_dict(row)
                for row in cursor.fetchall()
            ]
        finally:
            cursor.close()
            conn.close()

    def inizializza_step_orizzontali_fase(
        self,
        *,
        id_fase: int,
        data_creazione: datetime,
    ) -> dict[str, Any]:
        """Crea i cinque step orizzontali fissi se non sono gia presenti."""

        conn = self._open_access_connection()
        cursor = conn.cursor()

        report = {
            "id_fase": id_fase,
            "step_creati": [],
            "step_gia_presenti": [],
        }

        try:
            cursor.execute(
                """
                SELECT CodiceStep
                FROM T_FaseStepOrizzontali
                WHERE IDFase = ? AND Attivo = ?
                """,
                (id_fase, True),
            )
            existing = {
                str(self._get(row, "CodiceStep") or "").upper()
                for row in cursor.fetchall()
            }

            for codice, titolo, ordine in self.STEP_ORIZZONTALI_DEFAULT:
                if codice in existing:
                    report["step_gia_presenti"].append(codice)
                    continue

                cursor.execute(
                    """
                    INSERT INTO T_FaseStepOrizzontali (
                        IDFase,
                        CodiceStep,
                        TitoloStep,
                        Ordine,
                        StatoStep,
                        DataAvvio,
                        DataCompletamento,
                        Attivo,
                        DataCreazione,
                        DataModifica
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        id_fase,
                        codice,
                        titolo,
                        ordine,
                        "NON_AVVIATO",
                        None,
                        None,
                        True,
                        data_creazione,
                        data_creazione,
                    ),
                )
                report["step_creati"].append(codice)

            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

        report["step"] = self.list_step_orizzontali_by_fase(id_fase)
        return report

    def configura_step_orizzontali_istanza_fine(
        self,
        *,
        id_fase: int,
        data_modifica: datetime,
    ) -> list[dict[str, Any]]:
        """Sostituisce logicamente gli step attivi con `Istanza -> Fine`."""

        conn = self._open_access_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                UPDATE T_FaseStepOrizzontali
                SET Attivo = ?,
                    DataModifica = ?
                WHERE IDFase = ? AND Attivo = ?
                """,
                (False, data_modifica, id_fase, True),
            )

            for codice, titolo, ordine in (
                ("ISTANZA", "Istanza", 1),
                ("FINE", "Fine", 2),
            ):
                self._insert_step_orizzontale(
                    cursor,
                    id_fase=id_fase,
                    codice_step=codice,
                    titolo_step=titolo,
                    ordine=ordine,
                    data_creazione=data_modifica,
                )

            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

        return self.list_step_orizzontali_by_fase(id_fase)

    def has_step_orizzontali_avviati(self, id_fase: int) -> bool:
        """Indica se esistono step attivi con stato diverso da NON_AVVIATO."""

        query = """
            SELECT COUNT(*) AS Totale
            FROM T_FaseStepOrizzontali
            WHERE IDFase = ?
                AND Attivo = ?
                AND (
                    StatoStep IS NULL
                    OR UCASE(StatoStep) <> ?
                )
        """

        conn = self._open_access_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(query, (id_fase, True, "NON_AVVIATO"))
            row = cursor.fetchone()
            return int(self._get(row, "Totale", 0) or 0) > 0
        finally:
            cursor.close()
            conn.close()

    def configura_step_orizzontali_predefinito(
        self,
        *,
        id_fase: int,
        data_modifica: datetime,
    ) -> list[dict[str, Any]]:
        """Sostituisce logicamente gli step attivi con il workflow standard."""

        conn = self._open_access_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                UPDATE T_FaseStepOrizzontali
                SET Attivo = ?,
                    DataModifica = ?
                WHERE IDFase = ? AND Attivo = ?
                """,
                (False, data_modifica, id_fase, True),
            )

            for codice, titolo, ordine in self.STEP_ORIZZONTALI_DEFAULT:
                self._insert_step_orizzontale(
                    cursor,
                    id_fase=id_fase,
                    codice_step=codice,
                    titolo_step=titolo,
                    ordine=ordine,
                    data_creazione=data_modifica,
                )

            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

        return self.list_step_orizzontali_by_fase(id_fase)

    def inserisci_step_orizzontale_dopo(
        self,
        *,
        id_fase: int,
        id_step: int,
        titolo_step: str,
        codice_step: str,
        data_creazione: datetime,
    ) -> list[dict[str, Any]]:
        """Inserisce uno step attivo subito dopo quello selezionato."""

        conn = self._open_access_connection()
        cursor = conn.cursor()

        try:
            step = self._get_step_orizzontale_attivo(
                cursor,
                id_fase=id_fase,
                id_step=id_step,
            )
            if step is None:
                raise ValueError("Step non trovato.")

            ordine_corrente = int(self._get(step, "Ordine") or 0)

            cursor.execute(
                """
                UPDATE T_FaseStepOrizzontali
                SET Ordine = Ordine + 1,
                    DataModifica = ?
                WHERE IDFase = ?
                    AND Attivo = ?
                    AND Ordine > ?
                """,
                (data_creazione, id_fase, True, ordine_corrente),
            )
            self._insert_step_orizzontale(
                cursor,
                id_fase=id_fase,
                codice_step=codice_step,
                titolo_step=titolo_step,
                ordine=ordine_corrente + 1,
                data_creazione=data_creazione,
            )
            self._rinumera_step_orizzontali_attivi(
                cursor,
                id_fase=id_fase,
                data_modifica=data_creazione,
            )

            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

        return self.list_step_orizzontali_by_fase(id_fase)

    def elimina_logicamente_step_orizzontale(
        self,
        *,
        id_fase: int,
        id_step: int,
        data_modifica: datetime,
    ) -> list[dict[str, Any]]:
        """Disattiva uno step e rinumera gli step attivi rimanenti."""

        conn = self._open_access_connection()
        cursor = conn.cursor()

        try:
            step = self._get_step_orizzontale_attivo(
                cursor,
                id_fase=id_fase,
                id_step=id_step,
            )
            if step is None:
                raise ValueError("Step non trovato.")

            cursor.execute(
                """
                SELECT COUNT(*) AS Totale
                FROM T_FaseStepOrizzontali
                WHERE IDFase = ? AND Attivo = ?
                """,
                (id_fase, True),
            )
            totale_row = cursor.fetchone()
            totale_attivi = int(self._get(totale_row, "Totale", 0) or 0)
            if totale_attivi <= 1:
                raise ValueError("Non e possibile eliminare l'unico step attivo.")

            stato_step = str(self._get(step, "StatoStep") or "").upper()
            if stato_step == "COMPLETATO":
                raise ValueError("Non e possibile eliminare uno step completato.")

            cursor.execute(
                """
                UPDATE T_FaseStepOrizzontali
                SET Attivo = ?,
                    DataModifica = ?
                WHERE IDStepOrizzontale = ?
                    AND IDFase = ?
                    AND Attivo = ?
                """,
                (False, data_modifica, id_step, id_fase, True),
            )
            self._rinumera_step_orizzontali_attivi(
                cursor,
                id_fase=id_fase,
                data_modifica=data_modifica,
            )

            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

        return self.list_step_orizzontali_by_fase(id_fase)

    def _get_step_orizzontale_attivo(
        self,
        cursor: Any,
        *,
        id_fase: int,
        id_step: int,
    ) -> Any | None:
        cursor.execute(
            """
            SELECT
                IDStepOrizzontale,
                IDFase,
                CodiceStep,
                TitoloStep,
                Ordine,
                StatoStep,
                Attivo
            FROM T_FaseStepOrizzontali
            WHERE IDStepOrizzontale = ?
                AND IDFase = ?
                AND Attivo = ?
            """,
            (id_step, id_fase, True),
        )
        return cursor.fetchone()

    def _insert_step_orizzontale(
        self,
        cursor: Any,
        *,
        id_fase: int,
        codice_step: str,
        titolo_step: str,
        ordine: int,
        data_creazione: datetime,
    ) -> None:
        cursor.execute(
            """
            INSERT INTO T_FaseStepOrizzontali (
                IDFase,
                CodiceStep,
                TitoloStep,
                Ordine,
                StatoStep,
                DataAvvio,
                DataCompletamento,
                Attivo,
                DataCreazione,
                DataModifica
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                id_fase,
                codice_step,
                titolo_step,
                ordine,
                "NON_AVVIATO",
                None,
                None,
                True,
                data_creazione,
                data_creazione,
            ),
        )

    def _rinumera_step_orizzontali_attivi(
        self,
        cursor: Any,
        *,
        id_fase: int,
        data_modifica: datetime,
    ) -> None:
        cursor.execute(
            """
            SELECT IDStepOrizzontale
            FROM T_FaseStepOrizzontali
            WHERE IDFase = ? AND Attivo = ?
            ORDER BY Ordine ASC, IDStepOrizzontale ASC
            """,
            (id_fase, True),
        )
        rows = cursor.fetchall()

        for ordine, row in enumerate(rows, start=1):
            cursor.execute(
                """
                UPDATE T_FaseStepOrizzontali
                SET Ordine = ?,
                    DataModifica = ?
                WHERE IDStepOrizzontale = ?
                    AND IDFase = ?
                """,
                (
                    ordine,
                    data_modifica,
                    self._get(row, "IDStepOrizzontale"),
                    id_fase,
                ),
            )

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

    @classmethod
    def codice_step_from_titolo(cls, titolo: str) -> str:
        normalized = "".join(
            char.upper() if char.isalnum() else "_"
            for char in str(titolo or "").strip()
        )
        parts = [part for part in normalized.split("_") if part]
        return "_".join(parts)[:50] or "STEP"

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
