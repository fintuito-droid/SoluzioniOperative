"""Repository read-only Access-compatible per i procedimenti.

SCOPO DEL FILE
==============
Questo file introduce `ProcedimentoRepository`, il repository dedicato alla
nuova entita `Procedimento` di ProtocolloMonitor.

RESPONSABILITA
==============
- Leggere l'elenco dei procedimenti.
- Leggere il dettaglio di un procedimento per ID.
- Leggere i protocolli collegati a un procedimento.
- Contare i protocolli collegati.
- Restare rigorosamente read-only.

MOTIVAZIONE ARCHITETTURALE
==========================
Il procedimento diventa il contenitore logico-operativo che collega protocolli,
documenti, scadenze, priorita e futuri tag/metadati. Isolare subito le letture
in un repository evita di reintrodurre query SQL nelle route FastAPI e prepara
la futura migrazione PostgreSQL.

VINCOLI
=======
- Nessuna modifica allo schema Access.
- Nessuna scrittura su database.
- Nessuna route FastAPI.
- Nessuna dipendenza dal frontend.
- Nessuna assunzione su tag o metadati non ancora modellati.

COMPATIBILITA ACCESS
====================
Il repository usa `BaseRepository._open_access_connection()`, quindi eredita la
connessione Access centralizzata gia introdotta nel backend.

PREPARAZIONE POSTGRESQL
=======================
Le chiavi restituite sono snake_case e i metodi sono separati per responsabilita
applicativa. In futuro un repository PostgreSQL potra implementare lo stesso
contratto senza cambiare il Service Layer.

PUNTI DI ATTENZIONE
===================
- `T_Procedimenti` e `T_ProcedimentoProtocolli` sono nuove tabelle Access.
- Il repository non crea, modifica o cancella record.
- Le relazioni fisiche non vengono forzate qui: il repository legge soltanto.

NOTE FUTURA EVOLUZIONE
======================
- Introdurre paginazione e filtri server-side.
- Collegare tag/metadati quando saranno presenti tabelle dedicate.
- Aggiungere repository PostgreSQL parallelo quando il provider definitivo sara
  operativo.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

import pyodbc

from .base import BaseRepository


class ProcedimentoRepository(BaseRepository):
    """Repository read-only per la nuova entita Procedimento.

    Il repository espone solo metodi di lettura e mantiene separato l'accesso
    dati dalle future regole applicative del `ProcedimentoService`.
    """

    @staticmethod
    def _normalize_value(value: Any) -> Any:
        """Normalizza valori Access in forme JSON/PostgreSQL-friendly.

        Date e datetime vengono convertite in ISO string, mentre gli altri
        valori restano invariati. Il procedimento non ha ancora endpoint
        pubblici, quindi possiamo adottare da subito un formato piu vicino a
        PostgreSQL senza rompere frontend esistente.
        """

        if isinstance(value, datetime):
            return value.isoformat(sep=" ")

        if isinstance(value, date):
            return value.isoformat()

        return value

    @staticmethod
    def _get(row: Any, name: str, default: Any = None) -> Any:
        """Legge un campo da una riga pyodbc o da fake row nei test."""

        if row is None:
            return default

        if isinstance(row, dict):
            return row.get(name, default)

        return getattr(row, name, default)

    def _procedimento_row_to_dict(self, row: Any) -> dict[str, Any]:
        """Converte una riga procedimento in dizionario snake_case."""

        return {
            "id_procedimento": self._normalize_value(
                self._get(row, "IDProcedimento")
            ),
            "codice_procedimento": self._normalize_value(
                self._get(row, "CodiceProcedimento")
            ),
            "titolo": self._normalize_value(self._get(row, "Titolo")),
            "descrizione": self._normalize_value(self._get(row, "Descrizione")),
            "azienda_soggetto": self._normalize_value(
                self._get(row, "AziendaSoggetto")
            ),
            "comando_competenza": self._normalize_value(
                self._get(row, "ComandoCompetenza")
            ),
            "settore_competenza": self._normalize_value(
                self._get(row, "SettoreCompetenza")
            ),
            "tipologia_procedimento": self._normalize_value(
                self._get(row, "TipologiaProcedimento")
            ),
            "stato_procedimento": self._normalize_value(
                self._get(row, "StatoProcedimento")
            ),
            "priorita": self._normalize_value(self._get(row, "Priorita")),
            "data_apertura": self._normalize_value(self._get(row, "DataApertura")),
            "data_ultimo_aggiornamento": self._normalize_value(
                self._get(row, "DataUltimoAggiornamento")
            ),
            "data_scadenza": self._normalize_value(self._get(row, "DataScadenza")),
            "data_chiusura": self._normalize_value(self._get(row, "DataChiusura")),
            "note_interne": self._normalize_value(self._get(row, "NoteInterne")),
            "attivo": bool(self._get(row, "Attivo"))
            if self._get(row, "Attivo") is not None
            else False,
            "data_creazione": self._normalize_value(self._get(row, "DataCreazione")),
            "data_modifica": self._normalize_value(self._get(row, "DataModifica")),
            "protocolli_collegati": int(self._get(row, "ProtocolliCollegati", 0) or 0),
        }

    def _protocollo_collegato_row_to_dict(self, row: Any) -> dict[str, Any]:
        """Converte una riga di collegamento procedimento/protocollo."""

        return {
            "id_procedimento_protocollo": self._normalize_value(
                self._get(row, "IDProcedimentoProtocollo")
            ),
            "id_procedimento": self._normalize_value(
                self._get(row, "IDProcedimento")
            ),
            "id_protocollo": self._normalize_value(self._get(row, "IDProtocollo")),
            "ruolo_protocollo": self._normalize_value(
                self._get(row, "RuoloProtocollo")
            ),
            "principale": bool(self._get(row, "Principale"))
            if self._get(row, "Principale") is not None
            else False,
            "data_collegamento": self._normalize_value(
                self._get(row, "DataCollegamento")
            ),
            "note_collegamento": self._normalize_value(
                self._get(row, "NoteCollegamento")
            ),
            "numero_protocollo": self._normalize_value(
                self._get(row, "NumeroProtocollo")
            ),
            "data_protocollo": self._normalize_value(self._get(row, "DataProtocollo")),
            "oggetto": self._normalize_value(self._get(row, "Oggetto")),
            "modalita": self._normalize_value(self._get(row, "Modalita")),
            "comando_mittente": self._normalize_value(
                self._get(row, "ComandoMittente")
            ),
            "tipologia_documento": self._normalize_value(
                self._get(row, "TipologiaDocumento")
            ),
            "percorso_documento_protocollato": self._normalize_value(
                self._get(row, "PercorsoDocumentoProtocollato")
            ),
        }

    def _procedimento_collegato_row_to_dict(self, row: Any) -> dict[str, Any]:
        """Converte una riga procedimento collegata a un protocollo."""

        procedimento = self._procedimento_row_to_dict(row)
        procedimento.update(
            {
                "id_procedimento_protocollo": self._normalize_value(
                    self._get(row, "IDProcedimentoProtocollo")
                ),
                "id_protocollo": self._normalize_value(
                    self._get(row, "IDProtocollo")
                ),
                "ruolo_protocollo": self._normalize_value(
                    self._get(row, "RuoloProtocollo")
                ),
                "principale": bool(self._get(row, "Principale"))
                if self._get(row, "Principale") is not None
                else False,
                "data_collegamento": self._normalize_value(
                    self._get(row, "DataCollegamento")
                ),
                "note_collegamento": self._normalize_value(
                    self._get(row, "NoteCollegamento")
                ),
            }
        )

        return procedimento

    def _link_row_to_dict(self, row: Any) -> dict[str, Any]:
        """Converte una riga della tabella ponte in dizionario."""

        return {
            "id_procedimento_protocollo": self._normalize_value(
                self._get(row, "IDProcedimentoProtocollo")
            ),
            "id_procedimento": self._normalize_value(
                self._get(row, "IDProcedimento")
            ),
            "id_protocollo": self._normalize_value(self._get(row, "IDProtocollo")),
            "ruolo_protocollo": self._normalize_value(
                self._get(row, "RuoloProtocollo")
            ),
            "principale": bool(self._get(row, "Principale"))
            if self._get(row, "Principale") is not None
            else False,
            "data_collegamento": self._normalize_value(
                self._get(row, "DataCollegamento")
            ),
            "note_collegamento": self._normalize_value(
                self._get(row, "NoteCollegamento")
            ),
        }

    def list_procedimenti(self) -> list[dict[str, Any]]:
        """Legge l'elenco procedimenti con conteggio protocolli collegati."""

        query = """
            SELECT
                p.IDProcedimento,
                p.CodiceProcedimento,
                p.Titolo,
                p.Descrizione,
                p.AziendaSoggetto,
                p.ComandoCompetenza,
                p.SettoreCompetenza,
                p.TipologiaProcedimento,
                p.StatoProcedimento,
                p.Priorita,
                p.DataApertura,
                p.DataUltimoAggiornamento,
                p.DataScadenza,
                p.DataChiusura,
                p.NoteInterne,
                p.Attivo,
                p.DataCreazione,
                p.DataModifica,
                (
                    SELECT COUNT(*)
                    FROM T_ProcedimentoProtocolli AS pp
                    WHERE pp.IDProcedimento = p.IDProcedimento
                ) AS ProtocolliCollegati
            FROM T_Procedimenti AS p
            ORDER BY p.IDProcedimento DESC
        """

        conn = self._open_access_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(query)
            return [
                self._procedimento_row_to_dict(row)
                for row in cursor.fetchall()
            ]
        finally:
            cursor.close()
            conn.close()

    def get_procedimento_detail(self, id_procedimento: int) -> dict[str, Any] | None:
        """Legge un procedimento per ID.

        Restituisce `None` se il procedimento non esiste. La gestione HTTP 404
        verra decisa solo quando sara introdotta una route FastAPI dedicata.
        """

        query = """
            SELECT
                p.IDProcedimento,
                p.CodiceProcedimento,
                p.Titolo,
                p.Descrizione,
                p.AziendaSoggetto,
                p.ComandoCompetenza,
                p.SettoreCompetenza,
                p.TipologiaProcedimento,
                p.StatoProcedimento,
                p.Priorita,
                p.DataApertura,
                p.DataUltimoAggiornamento,
                p.DataScadenza,
                p.DataChiusura,
                p.NoteInterne,
                p.Attivo,
                p.DataCreazione,
                p.DataModifica,
                (
                    SELECT COUNT(*)
                    FROM T_ProcedimentoProtocolli AS pp
                    WHERE pp.IDProcedimento = p.IDProcedimento
                ) AS ProtocolliCollegati
            FROM T_Procedimenti AS p
            WHERE p.IDProcedimento = ?
        """

        conn = self._open_access_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(query, (id_procedimento,))
            row = cursor.fetchone()

            if not row:
                return None

            return self._procedimento_row_to_dict(row)
        finally:
            cursor.close()
            conn.close()

    def list_protocolli_collegati(
        self,
        id_procedimento: int,
    ) -> list[dict[str, Any]]:
        """Legge i protocolli collegati a un procedimento."""

        query = """
            SELECT
                pp.IDProcedimentoProtocollo,
                pp.IDProcedimento,
                pp.IDProtocollo,
                pp.RuoloProtocollo,
                pp.Principale,
                pp.DataCollegamento,
                pp.NoteCollegamento,
                pr.NumeroProtocollo,
                pr.DataProtocollo,
                pr.Oggetto,
                pr.Modalita,
                pr.ComandoMittente,
                pr.TipologiaDocumento,
                pr.PercorsoDocumentoProtocollato
            FROM
                T_ProcedimentoProtocolli AS pp
                INNER JOIN T_Protocolli AS pr
                    ON pp.IDProtocollo = pr.IDProtocollo
            WHERE
                pp.IDProcedimento = ?
            ORDER BY
                pp.Principale DESC,
                pp.DataCollegamento DESC,
                pp.IDProcedimentoProtocollo DESC
        """

        conn = self._open_access_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(query, (id_procedimento,))
            return [
                self._protocollo_collegato_row_to_dict(row)
                for row in cursor.fetchall()
            ]
        finally:
            cursor.close()
            conn.close()

    def count_protocolli_collegati(self, id_procedimento: int) -> int:
        """Conta i protocolli collegati a un procedimento."""

        query = """
            SELECT COUNT(*) AS Totale
            FROM T_ProcedimentoProtocolli
            WHERE IDProcedimento = ?
        """

        conn = self._open_access_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(query, (id_procedimento,))
            row = cursor.fetchone()

            if not row:
                return 0

            return int(self._get(row, "Totale", 0) or 0)
        finally:
            cursor.close()
            conn.close()

    def crea_procedimento(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Inserisce un procedimento principale e restituisce il record creato."""

        insert_query = """
            INSERT INTO T_Procedimenti (
                CodiceProcedimento,
                Titolo,
                Descrizione,
                AziendaSoggetto,
                ComandoCompetenza,
                SettoreCompetenza,
                TipologiaProcedimento,
                StatoProcedimento,
                Priorita,
                DataApertura,
                DataUltimoAggiornamento,
                DataScadenza,
                DataChiusura,
                NoteInterne,
                Attivo,
                DataCreazione,
                DataModifica
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        conn = self._open_access_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                insert_query,
                (
                    payload.get("CodiceProcedimento"),
                    payload.get("Titolo"),
                    payload.get("Descrizione"),
                    payload.get("AziendaSoggetto"),
                    payload.get("ComandoCompetenza"),
                    payload.get("SettoreCompetenza"),
                    payload.get("TipologiaProcedimento"),
                    payload.get("StatoProcedimento"),
                    payload.get("Priorita"),
                    payload.get("DataApertura"),
                    payload.get("DataUltimoAggiornamento"),
                    payload.get("DataScadenza"),
                    payload.get("DataChiusura"),
                    payload.get("NoteInterne"),
                    bool(payload.get("Attivo", True)),
                    payload.get("DataCreazione"),
                    payload.get("DataModifica"),
                ),
            )
            cursor.execute("SELECT @@IDENTITY AS IDProcedimento")
            row = cursor.fetchone()
            id_procedimento = self._identity_from_row(
                row,
                field_name="IDProcedimento",
            )
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

        created = self.get_procedimento_detail(id_procedimento)
        if created is None:
            raise RuntimeError("Procedimento creato ma non rileggibile.")

        return created

    @staticmethod
    def _identity_from_row(row: Any, *, field_name: str = "IDProcedimento") -> int:
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

    def list_procedimenti_by_protocollo_id(
        self,
        id_protocollo: int,
    ) -> list[dict[str, Any]]:
        """Legge i procedimenti collegati a un protocollo."""

        query = """
            SELECT
                pp.IDProcedimentoProtocollo,
                pp.IDProcedimento,
                pp.IDProtocollo,
                pp.RuoloProtocollo,
                pp.Principale,
                pp.DataCollegamento,
                pp.NoteCollegamento,
                p.CodiceProcedimento,
                p.Titolo,
                p.Descrizione,
                p.AziendaSoggetto,
                p.ComandoCompetenza,
                p.SettoreCompetenza,
                p.TipologiaProcedimento,
                p.StatoProcedimento,
                p.Priorita,
                p.DataApertura,
                p.DataUltimoAggiornamento,
                p.DataScadenza,
                p.DataChiusura,
                p.NoteInterne,
                p.Attivo,
                p.DataCreazione,
                p.DataModifica,
                (
                    SELECT COUNT(*)
                    FROM T_ProcedimentoProtocolli AS pp_count
                    WHERE pp_count.IDProcedimento = p.IDProcedimento
                ) AS ProtocolliCollegati
            FROM
                T_ProcedimentoProtocolli AS pp
                INNER JOIN T_Procedimenti AS p
                    ON pp.IDProcedimento = p.IDProcedimento
            WHERE
                pp.IDProtocollo = ?
            ORDER BY
                pp.Principale DESC,
                pp.DataCollegamento DESC,
                pp.IDProcedimentoProtocollo DESC
        """

        conn = self._open_access_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(query, (id_protocollo,))
            return [
                self._procedimento_collegato_row_to_dict(row)
                for row in cursor.fetchall()
            ]
        finally:
            cursor.close()
            conn.close()

    def protocollo_exists(self, id_protocollo: int) -> bool:
        """Verifica se un protocollo esiste in `T_Protocolli`."""

        query = """
            SELECT COUNT(*) AS Totale
            FROM T_Protocolli
            WHERE IDProtocollo = ?
        """

        conn = self._open_access_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(query, (id_protocollo,))
            row = cursor.fetchone()
            return int(self._get(row, "Totale", 0) or 0) > 0
        finally:
            cursor.close()
            conn.close()

    def procedimento_exists(self, id_procedimento: int) -> bool:
        """Verifica se un procedimento esiste in `T_Procedimenti`."""

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

    def procedimento_protocollo_link_exists(
        self,
        id_protocollo: int,
        id_procedimento: int,
    ) -> bool:
        """Verifica se il collegamento procedimento/protocollo esiste gia."""

        query = """
            SELECT COUNT(*) AS Totale
            FROM T_ProcedimentoProtocolli
            WHERE IDProcedimento = ? AND IDProtocollo = ?
        """

        conn = self._open_access_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(query, (id_procedimento, id_protocollo))
            row = cursor.fetchone()
            return int(self._get(row, "Totale", 0) or 0) > 0
        finally:
            cursor.close()
            conn.close()

    def link_protocollo_to_procedimento(
        self,
        *,
        id_protocollo: int,
        id_procedimento: int,
        ruolo_protocollo: str,
        principale: bool,
        note_collegamento: str | None,
    ) -> dict[str, Any] | None:
        """Crea il collegamento nella tabella ponte.

        Il metodo aggiorna solo `T_ProcedimentoProtocolli`. Non modifica
        `T_Protocolli` e non modifica `T_Procedimenti`. Se il vincolo univoco
        del database intercetta un duplicato, restituisce `None` lasciando al
        service la traduzione in `409 Conflict`.
        """

        insert_query = """
            INSERT INTO T_ProcedimentoProtocolli (
                IDProcedimento,
                IDProtocollo,
                RuoloProtocollo,
                Principale,
                DataCollegamento,
                NoteCollegamento
            ) VALUES (?, ?, ?, ?, ?, ?)
        """

        select_query = """
            SELECT TOP 1
                IDProcedimentoProtocollo,
                IDProcedimento,
                IDProtocollo,
                RuoloProtocollo,
                Principale,
                DataCollegamento,
                NoteCollegamento
            FROM T_ProcedimentoProtocolli
            WHERE IDProcedimento = ? AND IDProtocollo = ?
            ORDER BY IDProcedimentoProtocollo DESC
        """

        conn = self._open_access_connection()
        cursor = conn.cursor()

        try:
            try:
                cursor.execute(
                    insert_query,
                    (
                        id_procedimento,
                        id_protocollo,
                        ruolo_protocollo,
                        bool(principale),
                        datetime.now(),
                        note_collegamento,
                    ),
                )
                conn.commit()
            except pyodbc.IntegrityError:
                return None

            cursor.execute(select_query, (id_procedimento, id_protocollo))
            row = cursor.fetchone()

            if not row:
                return None

            return self._link_row_to_dict(row)
        finally:
            cursor.close()
            conn.close()
