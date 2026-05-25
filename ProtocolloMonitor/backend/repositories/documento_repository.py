"""Repository Access-compatible per documenti e PDF.

SCOPO DEL FILE
==============
Questo file introduce `DocumentoRepository`, un repository concreto dedicato
alla parte documentale/PDF di ProtocolloMonitor.

Il repository contiene letture conservative e un unico aggiornamento isolato
per registrare il path PDF in `T_Protocolli.PercorsoDocumentoProtocollato`.
La scrittura e volutamente piccola, parametrica e separata dal salvataggio
fisico del file.

RESPONSABILITA
==============
- Leggere il percorso PDF protocollato associato a un protocollo.
- Verificare, lato dato, se per un protocollo esiste un percorso PDF valorizzato.
- Leggere, quando disponibile, il record documentale da `T_Documenti`.
- Aggiornare solo `T_Protocolli.PercorsoDocumentoProtocollato` quando un PDF
  e stato salvato da un Service applicativo dedicato.
- Conservare compatibilita con Access e con la struttura attuale.
- Documentare il rapporto tra `T_Protocolli.PercorsoDocumentoProtocollato` e
  `T_Documenti.percorso_file`.

MOTIVAZIONE ARCHITETTURALE
==========================
Oggi gli endpoint PDF leggono il percorso direttamente da `T_Protocolli`.
In parallelo, il flusso di salvataggio in `Python/salva_access.py` popola anche
`T_Documenti`, che rappresenta il documento in modo piu vicino al target futuro
di piattaforma documentale.

Questo repository riconosce entrambe le realta:

- runtime attuale: percorso PDF letto da `T_Protocolli`;
- evoluzione futura: documento come entita propria, leggibile da `T_Documenti`.

VINCOLI
=======
- Non modificare `backend/main.py`.
- Non modificare endpoint.
- Non modificare query originali.
- Non salvare fisicamente PDF.
- Non modificare FileServer.
- Non modificare Flask legacy.
- Non modificare frontend Vue 3 + Vuetify 4.
- Non modificare estensione Grisu.
- Non implementare PostgreSQL operativo.

COMPATIBILITA ACCESS
====================
Il repository usa `BaseRepository` e quindi apre connessioni Access tramite il
modulo centralizzato `backend/core/access_connection.py`.

La maggior parte dei metodi e read-only. L'unica scrittura introdotta e
`update_protocollo_pdf_path`, che aggiorna esclusivamente il campo
`PercorsoDocumentoProtocollato` con query parametrica e commit esplicito.
Il repository non salva file e non effettua download.

PREPARAZIONE POSTGRESQL
=======================
PostgreSQL non viene usato in questo file. La preparazione consiste nel
separare il concetto di documento dal path fisico salvato oggi in Access.

In futuro il documento potra avere:

- chiave primaria PostgreSQL;
- riferimenti logici allo storage;
- metadati e tag;
- permessi utente/gruppo;
- collegamento a Procedimento;
- audit di visualizzazione/download.

PUNTI DI ATTENZIONE
===================
- `T_Documenti` non risulta usata dagli endpoint FastAPI attuali.
- Gli endpoint attuali leggono il PDF da `T_Protocolli.PercorsoDocumentoProtocollato`.
- Questo repository non verifica il filesystem: restituisce dati dal database.
  L'esistenza fisica del file sara responsabilita di un futuro storage/service.
- I nomi campo non vengono trasformati se non dove serve compatibilita con il
  metodo chiamante.

NOTE FUTURA EVOLUZIONE
======================
- Collegare questo repository a un futuro `DocumentoService`.
- Introdurre storage astratto per non esporre path fisici alle route.
- Spostare controlli `os.path.exists` fuori dagli endpoint.
- Modellare `T_Documenti` come tabella documentale principale nella migrazione
  PostgreSQL.
"""

from __future__ import annotations

from typing import Any

from .base import BaseRepository


class DocumentoRepository(BaseRepository):
    """Repository per informazioni documentali e registrazione path PDF.

    Cosa fa:
    espone letture conservative sui dati documento oggi disponibili in Access e
    una scrittura isolata per aggiornare il solo path PDF protocollato.

    Perche esiste:
    prepara una separazione pulita tra protocollo, documento e storage, senza
    mescolare salvataggio file e aggiornamento database.

    Parametri:
    eredita `config` e `logger` da `BaseRepository`.

    Valori restituiti:
    letture restituiscono dizionari o valori semplici; l'aggiornamento path
    restituisce `True` quando Access segnala almeno un record modificato.

    Rischi evitati:
    - cambiare il flusso PDF attuale;
    - confondere salvataggio file con accesso dati;
    - introdurre una struttura PostgreSQL prima della migrazione.

    Uso futuro nei Service:
    un futuro `DocumentoService` usera questo repository per recuperare dati,
    applicare permessi, controllare storage e restituire risposte agli endpoint.
    """

    @staticmethod
    def _row_to_dict(cursor: Any, row: Any) -> dict[str, Any]:
        """Converte una riga pyodbc in dizionario con nomi colonna Access.

        Cosa fa:
        legge `cursor.description` e associa ogni nome colonna al valore della
        riga corrente.

        Perche esiste:
        `T_Documenti` puo contenere colonne utili non ancora formalizzate in
        schema API. In questa fase read-only e prudente non perdere campi.

        Parametri:
        - `cursor`: cursore pyodbc dopo una query;
        - `row`: riga restituita da Access.

        Valori restituiti:
        - dizionario `{nome_colonna: valore}`.

        Rischi evitati:
        - cambiare nomi campo Access;
        - anticipare schema definitivi;
        - perdere metadati documentali gia presenti.

        Uso futuro nei Repository/Service:
        questo mapper potra essere sostituito da schema espliciti quando
        `T_Documenti` diventera il centro del modello documentale.
        """

        columns = [column[0] for column in cursor.description]
        return dict(zip(columns, row))

    def get_pdf_path_by_protocollo_id(self, id_protocollo: int) -> str | None:
        """Legge il percorso PDF protocollato associato a un protocollo.

        Cosa fa:
        esegue la stessa lettura oggi presente negli endpoint PDF di
        `backend/main.py`: legge `PercorsoDocumentoProtocollato` da
        `T_Protocolli`.

        Perche esiste:
        il runtime attuale usa questo campo come fonte del PDF. Spostarlo ora
        su `T_Documenti` cambierebbe il comportamento. Il repository mantiene
        compatibilita e prepara un futuro service documentale.

        Parametri:
        - `id_protocollo`: identificativo Access del protocollo.

        Valori restituiti:
        - percorso PDF come stringa, se presente;
        - `None` se il protocollo non esiste o il campo e vuoto.

        Rischi evitati:
        - cambiare fonte dati degli endpoint PDF;
        - alterare path fisici salvati in Access;
        - introdurre controlli filesystem nel repository.

        Uso futuro nei Service:
        `DocumentoService` potra usare questo metodo e poi delegare a uno
        storage service la verifica fisica del file.
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

    def document_exists_for_protocollo(self, id_protocollo: int) -> bool:
        """Indica se il protocollo ha un percorso PDF valorizzato nel DB.

        Cosa fa:
        usa `get_pdf_path_by_protocollo_id` e restituisce `True` quando il
        campo `PercorsoDocumentoProtocollato` contiene un valore non vuoto.

        Perche esiste:
        gli endpoint attuali distinguono tra protocollo non trovato, PDF non
        disponibile e file mancante. Questo metodo copre solo la parte dati:
        "esiste un riferimento al documento nel database?".

        Parametri:
        - `id_protocollo`: identificativo Access del protocollo.

        Valori restituiti:
        - `True` se il DB contiene un percorso;
        - `False` se il protocollo non esiste o il percorso e vuoto.

        Rischi evitati:
        - confondere esistenza logica DB con esistenza fisica file;
        - duplicare controlli su stringhe vuote nei futuri Service;
        - introdurre accesso filesystem nel repository.

        Uso futuro nei Service:
        un futuro `DocumentoService` potra combinare questo controllo con uno
        storage service per verificare anche `os.path.exists`.
        """

        pdf_path = self.get_pdf_path_by_protocollo_id(id_protocollo)
        return bool(pdf_path)

    def get_documento_by_protocollo_id(self, id_protocollo: int) -> dict[str, Any] | None:
        """Legge il record in `T_Documenti` collegabile al protocollo.

        Cosa fa:
        prova a recuperare il documento partendo dal percorso PDF salvato in
        `T_Protocolli.PercorsoDocumentoProtocollato` e cercando lo stesso valore
        in `T_Documenti.percorso_file`.

        Perche esiste:
        il runtime attuale non usa direttamente `T_Documenti` per servire PDF,
        ma `Python/salva_access.py` la popola durante l'acquisizione. Questo
        metodo crea un ponte read-only e conservativo verso la futura entita
        documento.

        Parametri:
        - `id_protocollo`: identificativo Access del protocollo.

        Valori restituiti:
        - dizionario con le colonne del record `T_Documenti`, se trovato;
        - `None` se il protocollo non ha path PDF o se `T_Documenti` non ha un
          record corrispondente.

        Rischi evitati:
        - assumere che `T_Documenti` sia sempre popolata;
        - cambiare gli endpoint attuali, che non dipendono da `T_Documenti`;
        - introdurre join non presenti nel runtime.

        Uso futuro nei Service:
        quando il dominio documento sara consolidato, il Service potra usare
        questo metodo come fallback iniziale e poi passare a chiavi esplicite o
        relazioni PostgreSQL.
        """

        pdf_path = self.get_pdf_path_by_protocollo_id(id_protocollo)

        if not pdf_path:
            return None

        query = """
            SELECT
                id_documento,
                tipo,
                comando_vigilia,
                numero_protocollo,
                data_protocollo,
                nome_file,
                percorso_file,
                chiave_univoca,
                data_acquisizione
            FROM T_Documenti
            WHERE percorso_file = ?
        """

        conn = self._open_access_connection()
        cursor = conn.cursor()

        try:
            row = cursor.execute(query, (pdf_path,)).fetchone()

            if not row:
                return None

            return self._row_to_dict(cursor, row)

        finally:
            cursor.close()
            conn.close()

    def update_protocollo_pdf_path(
        self,
        id_protocollo: int,
        percorso_documento_protocollato: str,
    ) -> bool:
        """Aggiorna il path PDF protocollato su `T_Protocolli`.

        Cosa fa:
        esegue un `UPDATE` parametrico sul solo campo
        `PercorsoDocumentoProtocollato`, filtrando per `IDProtocollo`.

        Perche esiste:
        Step 18 collega in modo controllato lo storage fisico del PDF alla
        registrazione del path nel database, ma mantiene separate le
        responsabilita: il Service salva il file, il Repository aggiorna Access.

        Parametri:
        - `id_protocollo`: identificativo reale Access del protocollo;
        - `percorso_documento_protocollato`: path da registrare nel campo gia
          esistente `T_Protocolli.PercorsoDocumentoProtocollato`.

        Valori restituiti:
        - `True` se Access segnala almeno un record aggiornato;
        - `False` se nessun record corrisponde all'ID indicato.

        Rischi evitati:
        - aggiornare campi diversi dal path PDF;
        - concatenare SQL manualmente;
        - mescolare logica di filesystem, download o parsing HTML nel repository;
        - introdurre modifiche allo schema Access.

        Uso futuro nei Service:
        `PdfDocumentService.save_and_register_protocollo_pdf` usera questo
        metodo dopo `DocumentStorageService.save_pdf`, e un repository
        PostgreSQL futuro potra offrire lo stesso contratto.
        """

        query = """
            UPDATE T_Protocolli
            SET PercorsoDocumentoProtocollato = ?
            WHERE IDProtocollo = ?
        """

        conn = self._open_access_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                query,
                (
                    percorso_documento_protocollato,
                    id_protocollo,
                ),
            )
            updated_rows = cursor.rowcount
            conn.commit()

            return bool(updated_rows and updated_rows > 0)

        finally:
            cursor.close()
            conn.close()
