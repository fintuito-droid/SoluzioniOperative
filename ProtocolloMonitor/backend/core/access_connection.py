"""Connessione Access centralizzata per ProtocolloMonitor.

SCOPO DEL FILE
==============
Questo file introduce un unico punto tecnico per aprire connessioni al database
Access attuale di ProtocolloMonitor.

L'obiettivo di questa attivita e creare la capacita centrale, non collegarla
ancora ai runtime esistenti. Le funzioni locali presenti in `backend/main.py`,
`Python/server_protocollo.py` e `Python/salva_access.py` restano operative fino
alla successiva attivita di integrazione controllata.

RESPONSABILITA
==============
- Leggere il percorso del database Access dalla configurazione centralizzata.
- Costruire la stringa di connessione ODBC nello stesso formato oggi usato.
- Restituire una connessione `pyodbc` aperta al chiamante.
- Mantenere il modulo privo di query SQL, logica HTTP, logica Flask/FastAPI e
  logica di dominio.

MOTIVAZIONE ARCHITETTURALE
==========================
ProtocolloMonitor e il primo modulo operativo della piattaforma multi modulo
Soluzioni Operative. La modernizzazione richiede che connessioni, repository,
service e API non conoscano direttamente percorsi locali o dettagli duplicati.

Centralizzare l'apertura connessione e un passaggio piccolo ma importante:
permette ai futuri Repository Access di dipendere da una sola funzione, mentre
la futura migrazione PostgreSQL potra introdurre un provider diverso senza
riscrivere ogni route o script.

VINCOLI
=======
- Non modificare endpoint esistenti.
- Non modificare query Access esistenti.
- Non modificare il runtime Flask legacy.
- Non modificare il runtime FastAPI.
- Non modificare frontend Vue 3 + Vuetify 4.
- Non modificare estensione Grisu o flusso di acquisizione.
- Non implementare repository.
- Non implementare PostgreSQL operativo.
- Non introdurre dipendenze nuove: `pyodbc` e gia usato dal progetto.

COMPATIBILITA ACCESS
====================
La stringa di connessione resta compatibile con l'implementazione corrente:

```text
DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=<percorso accdb>;
```

Il percorso predefinito viene letto da `backend/core/config.py`, che oggi
mantiene lo stesso valore operativo gia presente nei file legacy:

```text
G:\\ProtocolloMonitor.accdb
```

PREPARAZIONE POSTGRESQL
=======================
Questo modulo non apre connessioni PostgreSQL. La preparazione consiste nel
separare il concetto "dammi una connessione Access" dai futuri Repository.
Quando PostgreSQL diventera operativo, potra esistere un modulo parallelo o un
factory provider-aware senza cambiare il contratto dei Service.

PUNTI DI ATTENZIONE
===================
- La funzione restituisce una connessione aperta: il chiamante resta
  responsabile di commit, rollback e close.
- Nessun pooling viene introdotto: Access non e un DB server e il comportamento
  deve restare coerente con l'MVP attuale.
- Il modulo non viene ancora importato dai runtime esistenti, quindi non cambia
  il comportamento applicativo.

NOTE FUTURA EVOLUZIONE
======================
- I futuri Repository useranno questa funzione al posto delle funzioni locali
  duplicate.
- Un'attivita successiva potra aggiungere logging strutturato attorno
  all'apertura connessione.
- Un provider PostgreSQL futuro potra affiancare questo modulo senza rimuovere
  immediatamente la compatibilita Access.
"""

from __future__ import annotations

from typing import Any

import pyodbc

from .config import AppConfig, get_config


ACCESS_DRIVER = "Microsoft Access Driver (*.mdb, *.accdb)"


def build_access_connection_string(config: AppConfig | None = None) -> str:
    """Costruisce la stringa di connessione ODBC per Access.

    Cosa fa:
    legge `access_db_path` dalla configurazione centralizzata e compone la
    stringa ODBC nello stesso formato usato oggi nei file legacy.

    Perche esiste:
    separare la costruzione della stringa dalla chiamata `pyodbc.connect`
    permette ai futuri test e Repository di verificare la configurazione senza
    dover aprire realmente una connessione al database.

    Parametri:
    - `config`: configurazione applicativa opzionale. Se non viene passata,
      viene caricata con `get_config()`.

    Valori restituiti:
    - stringa ODBC compatibile con Microsoft Access.

    Rischi evitati:
    - duplicare il percorso Access in piu file;
    - cambiare accidentalmente il driver rispetto all'MVP attuale;
    - rendere piu difficile la migrazione futura verso provider diversi.

    Uso futuro nei Repository/Service:
    i Repository Access potranno usare questa funzione quando avranno bisogno
    di ispezionare o loggare il provider senza aprire subito una connessione.
    I Service non dovrebbero chiamarla direttamente: dovrebbero passare dai
    Repository.
    """

    active_config = config or get_config()

    return (
        rf"DRIVER={{{ACCESS_DRIVER}}};"
        rf"DBQ={active_config.access_db_path};"
    )


def get_access_connection(
    config: AppConfig | None = None,
    **connect_options: Any,
) -> pyodbc.Connection:
    """Apre e restituisce una connessione Access usando la config centrale.

    Cosa fa:
    compone la stringa ODBC Access tramite `build_access_connection_string` e
    apre una connessione con `pyodbc.connect`.

    Perche esiste:
    oggi il progetto apre connessioni Access in tre punti diversi. Questa
    funzione crea il punto centrale che potra essere adottato gradualmente,
    senza cambiare query, endpoint o runtime durante questa attivita.

    Parametri:
    - `config`: configurazione applicativa opzionale. Serve per test futuri o
      per ambienti in cui la config sia gia stata caricata dal chiamante.
    - `connect_options`: opzioni keyword opzionali da inoltrare a
      `pyodbc.connect`, ad esempio timeout futuri. Non vengono usate di default
      per mantenere il comportamento identico all'attuale.

    Valori restituiti:
    - una connessione `pyodbc.Connection` aperta.

    Rischi evitati:
    - hardcoding ripetuto del percorso `.accdb`;
    - differenze tra connessione FastAPI, Flask legacy e salvataggio Access;
    - accoppiamento dei futuri Repository al modulo di configurazione.

    Uso futuro nei Repository/Service:
    i Repository Access chiameranno questa funzione per ottenere una
    connessione. I Service useranno i Repository, non la connessione diretta.
    In questo modo lo stesso Service potra in futuro lavorare con un repository
    PostgreSQL senza conoscere `pyodbc`.
    """

    connection_string = build_access_connection_string(config)
    return pyodbc.connect(connection_string, **connect_options)
