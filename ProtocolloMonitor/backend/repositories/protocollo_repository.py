"""Repository read-only Access-compatible per i protocolli.

SCOPO DEL FILE
==============
Questo file introduce `ProtocolloRepository`, il primo repository concreto
read-only per ProtocolloMonitor.

Il repository replica le query di lettura oggi presenti in `backend/main.py`,
ma NON viene ancora collegato alle route FastAPI. Questo permette di preparare
il Repository Pattern senza modificare endpoint, query originali, formato dati
atteso dal frontend o comportamento runtime.

RESPONSABILITA
==============
- Leggere l'elenco dei protocolli acquisiti.
- Leggere il dettaglio di un protocollo e delle sue tabelle figlie.
- Leggere il percorso del PDF protocollato.
- Mantenere la compatibilita con Access.
- Conservare la forma dati oggi attesa da `backend/main.py` e dal frontend.

MOTIVAZIONE ARCHITETTURALE
==========================
Oggi le route FastAPI aprono connessioni, eseguono query e trasformano dati
direttamente. Questo funziona per un MVP, ma rende fragile la crescita verso
Service Layer, PostgreSQL, audit, workflow e multiutente.

Il repository concentra l'accesso dati in una classe separata. In uno step
successivo le route potranno chiamare un Service, il Service potra chiamare
questo repository, e il frontend non dovra cambiare.

VINCOLI
=======
- Non modificare `backend/main.py`.
- Non modificare endpoint.
- Non modificare query originali dentro `backend/main.py`.
- Non modificare frontend Vue 3 + Vuetify 4.
- Non modificare Flask legacy.
- Non modificare estensione Grisu.
- Non implementare Service Layer.
- Non implementare PostgreSQL operativo.
- Non cambiare formato date, boolean, path o nomi campi.

COMPATIBILITA ACCESS
====================
Il repository eredita da `BaseRepository` e apre connessioni Access usando
solo `_open_access_connection()`, che a sua volta usa il modulo centralizzato
`backend/core/access_connection.py`.

Le query sono scritte per restare equivalenti a quelle oggi presenti in
`backend/main.py`. Il dettaglio usa ancora `SELECT *` per le tabelle di
dettaglio perche la route attuale restituisce dizionari basati su tutte le
colonne disponibili nel cursore.

PREPARAZIONE POSTGRESQL
=======================
Questo file non apre connessioni PostgreSQL. La preparazione consiste nel
delimitare le query Access in un repository concreto. Quando PostgreSQL sara
operativo, si potra introdurre un repository parallelo con query esplicite,
tipi nativi, paginazione e contratti schema-driven.

PUNTI DI ATTENZIONE
===================
- `SELECT *` resta solo dove serve a preservare il comportamento attuale.
- I metodi sono read-only: non eseguono INSERT, UPDATE o DELETE.
- Il repository non valida permessi: questo sara responsabilita del futuro
  Service Layer e del futuro Security Context.
- Il repository non viene ancora importato da runtime.

NOTE FUTURA EVOLUZIONE
======================
- Sostituire progressivamente `SELECT *` con colonne esplicite quando saranno
  definiti schema API stabili.
- Introdurre paginazione e filtri server-side per l'elenco protocolli.
- Spostare normalizzazione date/boolean in schema o mapper dedicati.
- Affiancare un `PostgresProtocolloRepository` quando PostgreSQL diventera il
  provider operativo.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from .base import BaseRepository


class ProtocolloRepository(BaseRepository):
    """Repository read-only per dati protocollo su Access.

    Cosa fa:
    espone metodi di lettura che rispecchiano le query oggi eseguite da
    `backend/main.py`.

    Perche esiste:
    prepara il passaggio da route monolitiche a Repository Pattern senza
    cambiare runtime. Il repository sara collegato solo in un'attivita futura,
    dopo avere verificato parita di output.

    Parametri:
    eredita `config` e `logger` da `BaseRepository`.

    Valori restituiti:
    ogni metodo restituisce dizionari/lista di dizionari compatibili con la
    forma dati attuale.

    Rischi evitati:
    - cambiare endpoint prima di avere una base testabile;
    - duplicare ulteriormente apertura connessione;
    - introdurre PostgreSQL operativo prima che il dominio sia stabile.

    Uso futuro nei Service:
    un futuro `ProtocolloService` chiamera questi metodi e applichera regole
    applicative, permessi, logging operativo e mapping schema.
    """

    @staticmethod
    def _normalize_json_value(value: Any) -> Any:
        """Normalizza valori data come fa oggi `backend/main.py`.

        Cosa fa:
        converte `datetime` in `dd/mm/YYYY HH:MM` e `date` in `dd/mm/YYYY`.
        Gli altri valori vengono restituiti invariati.

        Perche esiste:
        l'elenco protocolli oggi restituisce date gia formattate. Cambiare
        formato sarebbe una regressione per il frontend. Questa funzione replica
        la logica `normalizza_valore` di `backend/main.py`.

        Parametri:
        - `value`: valore letto da Access.

        Valori restituiti:
        - valore normalizzato secondo il formato attuale.

        Rischi evitati:
        - cambiare formato date durante l'introduzione del repository;
        - rompere filtri o visualizzazione frontend;
        - mescolare normalizzazioni diverse tra route e repository.

        Uso futuro nei Repository/Service:
        in uno step successivo questa normalizzazione potra essere spostata in
        schema Pydantic o mapper dedicati, preparando date ISO per PostgreSQL.
        """

        if isinstance(value, datetime):
            return value.strftime("%d/%m/%Y %H:%M")

        if isinstance(value, date):
            return value.strftime("%d/%m/%Y")

        return value

    @staticmethod
    def _row_to_dict(cursor: Any, row: Any) -> dict[str, Any]:
        """Converte una riga pyodbc in dizionario basato su cursor.description.

        Cosa fa:
        legge i nomi colonna dal cursore e li associa ai valori della riga.

        Perche esiste:
        `backend/main.py` usa questa tecnica nel dettaglio protocollo. Replicare
        il comportamento preserva la forma dati delle route attuali.

        Parametri:
        - `cursor`: cursore pyodbc dopo una query;
        - `row`: riga restituita da `fetchone` o `fetchall`.

        Valori restituiti:
        - dizionario `{nome_colonna: valore}`.

        Rischi evitati:
        - perdere colonne non ancora modellate;
        - cambiare maiuscole/minuscole dei campi Access;
        - anticipare schema espliciti prima della relativa attivita.

        Uso futuro nei Repository/Service:
        da sostituire gradualmente con mapper espliciti quando saranno definiti
        schema stabili e PostgreSQL-friendly.
        """

        columns = [column[0] for column in cursor.description]
        return dict(zip(columns, row))

    def list_protocolli(self) -> list[dict[str, Any]]:
        """Restituisce l'elenco protocolli con forma dati attuale.

        Cosa fa:
        esegue la stessa query della route `/protocollo-monitor/protocolli` e
        costruisce record con chiavi snake_case gia attese dal frontend.

        Perche esiste:
        prepara lo spostamento della lettura protocolli fuori dalla route
        FastAPI, mantenendo output equivalente.

        Parametri:
        nessuno.

        Valori restituiti:
        - lista di dizionari con campi:
          `id_protocollo`, `numero_protocollo`, `data_protocollo`, `oggetto`,
          `modalita`, `comando_mittente`, `da_lavorare`, `data_scadenza`,
          `tipologia_documento`, `priorita`, `stato_pratica`, `note_interne`.

        Rischi evitati:
        - cambio involontario dei nomi campo frontend;
        - cambio formato date;
        - perdita dei default `Normale`, `NUOVA` e stringa vuota note.

        Uso futuro nei Repository/Service:
        il futuro `ProtocolloService` potra chiamare questo metodo e aggiungere
        paginazione, filtri server-side o permessi senza toccare SQL nella route.
        """

        sql = """
            SELECT
                IDProtocollo,
                NumeroProtocollo,
                DataProtocollo,
                Oggetto,
                Modalita,
                ComandoMittente,
                DaLavorare,
                dataScadenza,
                TipologiaDocumento,
                priorita,
                note_interne
            FROM
                T_Protocolli
            ORDER BY
                IDProtocollo DESC
        """

        conn = self._open_access_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(sql)

            records: list[dict[str, Any]] = []

            for row in cursor.fetchall():
                record = {
                    "id_protocollo": self._normalize_json_value(row.IDProtocollo),
                    "numero_protocollo": self._normalize_json_value(row.NumeroProtocollo),
                    "data_protocollo": self._normalize_json_value(row.DataProtocollo),
                    "oggetto": self._normalize_json_value(row.Oggetto),
                    "modalita": self._normalize_json_value(row.Modalita),
                    "comando_mittente": self._normalize_json_value(row.ComandoMittente),
                    "da_lavorare": (
                        bool(row.DaLavorare)
                        if row.DaLavorare is not None
                        else False
                    ),
                    "data_scadenza": self._normalize_json_value(row.dataScadenza),
                    "tipologia_documento": self._normalize_json_value(
                        row.TipologiaDocumento
                    ),
                    "priorita": self._normalize_json_value(row.priorita) or "Normale",
                    "stato_pratica": "NUOVA",
                    "note_interne": self._normalize_json_value(row.note_interne) or "",
                }

                records.append(record)

            return records

        finally:
            cursor.close()
            conn.close()

    def get_pdf_path(self, id_protocollo: int) -> str | None:
        """Restituisce il percorso PDF protocollato per un protocollo.

        Cosa fa:
        esegue la stessa query usata oggi dagli endpoint `apri-pdf` e `pdf` per
        leggere `PercorsoDocumentoProtocollato`.

        Perche esiste:
        il percorso documento e un dato di persistenza, quindi deve vivere nel
        repository e non nella route quando avverra l'integrazione.

        Parametri:
        - `id_protocollo`: identificativo Access del protocollo.

        Valori restituiti:
        - stringa percorso PDF se trovata;
        - `None` se il protocollo non esiste o il campo e vuoto.

        Rischi evitati:
        - duplicare la query PDF in piu endpoint futuri;
        - cambiare il path salvato in Access;
        - introdurre storage astratto prima dell'attivita dedicata.

        Uso futuro nei Repository/Service:
        un futuro `DocumentoService` potra chiamare questo metodo o un
        `DocumentoRepository` dedicato per validare esistenza file e permessi.
        """

        query = """
            SELECT PercorsoDocumentoProtocollato
            FROM T_Protocolli
            WHERE IDProtocollo = ?
        """

        conn = self._open_access_connection()
        cursor = conn.cursor()

        try:
            row = cursor.execute(query, (id_protocollo,)).fetchone()

            if not row:
                return None

            return row.PercorsoDocumentoProtocollato

        finally:
            cursor.close()
            conn.close()

    def get_protocollo_detail(self, id_protocollo: int) -> dict[str, Any]:
        """Restituisce dettaglio protocollo e tabelle figlie.

        Cosa fa:
        replica la query di dettaglio oggi presente in `backend/main.py`,
        includendo protocollo, assegnazioni, destinatari e firmatari.

        Perche esiste:
        prepara la separazione tra route e accesso dati senza alterare la
        risposta attuale. La route corrente restituisce tutte le colonne di
        Access tramite `SELECT *`; qui manteniamo la stessa semantica per non
        introdurre regressioni.

        Parametri:
        - `id_protocollo`: identificativo Access del protocollo.

        Valori restituiti:
        - dizionario con chiavi `protocollo`, `assegnazioni`, `destinatari`,
          `firmatari`;
        - se il protocollo non esiste, `protocollo` e `None` e le liste sono
          vuote, come accade oggi.

        Rischi evitati:
        - perdere colonne usate da viste o sviluppi futuri;
        - cambiare formato della route dettaglio;
        - anticipare schema Pydantic non ancora introdotti.

        Uso futuro nei Repository/Service:
        il futuro `ProtocolloService` potra chiamare questo metodo e aggiungere
        controlli permessi, audit e mapping schema prima di restituire dati alla
        route.
        """

        conn = self._open_access_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                SELECT *
                FROM T_Protocolli
                WHERE IDProtocollo = ?
                """,
                id_protocollo,
            )

            row = cursor.fetchone()

            if not row:
                return {
                    "protocollo": None,
                    "assegnazioni": [],
                    "destinatari": [],
                    "firmatari": [],
                }

            protocollo = self._row_to_dict(cursor, row)

            cursor.execute(
                """
                SELECT *
                FROM T_ProtocolloAssegnazioni
                WHERE IDProtocollo = ?
                """,
                id_protocollo,
            )
            assegnazioni = [
                self._row_to_dict(cursor, detail_row)
                for detail_row in cursor.fetchall()
            ]

            cursor.execute(
                """
                SELECT *
                FROM T_ProtocolloDestinatari
                WHERE IDProtocollo = ?
                """,
                id_protocollo,
            )
            destinatari = [
                self._row_to_dict(cursor, detail_row)
                for detail_row in cursor.fetchall()
            ]

            cursor.execute(
                """
                SELECT *
                FROM T_ProtocolloFirmatari
                WHERE IDProtocollo = ?
                """,
                id_protocollo,
            )
            firmatari = [
                self._row_to_dict(cursor, detail_row)
                for detail_row in cursor.fetchall()
            ]

            return {
                "protocollo": protocollo,
                "assegnazioni": assegnazioni,
                "destinatari": destinatari,
                "firmatari": firmatari,
            }

        finally:
            cursor.close()
            conn.close()
