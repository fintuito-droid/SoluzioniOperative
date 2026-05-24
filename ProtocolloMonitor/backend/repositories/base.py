"""Base architetturale del Repository Pattern per ProtocolloMonitor.

SCOPO DEL FILE
==============
Questo file introduce la classe minima `BaseRepository`, cioe il punto di
partenza comune per i futuri repository concreti di ProtocolloMonitor.

Lo scopo non e spostare query, non e cambiare endpoint e non e modificare il
runtime attuale. Lo scopo e creare il contratto architetturale che permettera,
nelle attivita successive, di separare in modo ordinato:

- route FastAPI;
- logica applicativa dei Service;
- accesso dati dei Repository;
- compatibilita Access attuale;
- target PostgreSQL futuro.

RESPONSABILITA
==============
- Conservare riferimenti a configurazione e logger applicativo.
- Esporre un helper protetto per ottenere una connessione Access centralizzata.
- Definire metodi informativi sul provider dati attivo.
- Documentare i confini tra Repository, Service e API.
- Restare minimale: nessuna query, nessuna entita di dominio, nessun endpoint.

MOTIVAZIONE ARCHITETTURALE
==========================
ProtocolloMonitor e il primo modulo operativo della futura piattaforma multi
modulo Soluzioni Operative. Se l'accesso dati resta dentro le route o dentro
script isolati, la migrazione verso PostgreSQL, multiutente, audit e workflow
diventa fragile.

Il Repository Pattern serve a concentrare l'accesso ai dati in classi dedicate.
I Service useranno i Repository; le route useranno i Service; il frontend Vue
non dovra conoscere dettagli del database.

VINCOLI
=======
- Non modificare endpoint esistenti.
- Non modificare query Access esistenti.
- Non importare questo file nei runtime attuali durante questa attivita.
- Non implementare `ProtocolloRepository`.
- Non implementare `DocumentoRepository`.
- Non implementare Service Layer.
- Non aprire connessioni durante l'inizializzazione del repository.
- Non introdurre dipendenze pesanti.

COMPATIBILITA ACCESS
====================
Access resta il provider operativo corrente. `BaseRepository` espone
`get_access_connection()` come helper protetto, usando il modulo centralizzato
`backend/core/access_connection.py`.

Questo helper non esegue query: restituisce solo una connessione aperta quando
un futuro repository concreto decidera di usarlo. Il chiamante sara sempre
responsabile di chiudere la connessione.

PREPARAZIONE POSTGRESQL
=======================
PostgreSQL non viene implementato in questo file. La preparazione consiste nel
non vincolare il contratto dei futuri Service a `pyodbc` o ad Access.

Quando PostgreSQL diventera operativo, potranno esistere repository concreti
diversi, ad esempio:

- `AccessProtocolloRepository`;
- `PostgresProtocolloRepository`;
- una factory che sceglie il repository in base a `database_provider`.

PUNTI DI ATTENZIONE
===================
- Questa classe base non deve diventare un contenitore generico di logica.
- Le query devono stare nei repository concreti, non qui.
- Le regole di business devono stare nei Service, non qui.
- Le route FastAPI devono restare sottili e non aprire direttamente il DB.

NOTE FUTURA EVOLUZIONE
======================
- Aggiungere repository concreti read-only partendo da `ProtocolloRepository`.
- Introdurre logging strutturato attorno alle operazioni DB.
- Introdurre provider PostgreSQL senza rompere compatibilita Access.
- Collegare i repository ai Service solo dopo avere verificato parita di output.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from logging import Logger
from typing import Any

import pyodbc

from ..core.access_connection import get_access_connection
from ..core.config import AppConfig, get_config
from ..core.logging import get_logger


@dataclass
class BaseRepository:
    """Classe base minimale per i futuri repository del backend.

    Cosa fa:
    conserva configurazione e logger condivisi e offre piccoli helper comuni.
    Non esegue query e non conosce tabelle specifiche come `T_Protocolli` o
    `T_Documenti`.

    Perche esiste:
    ogni repository concreto avra bisogno degli stessi elementi di base:
    configurazione applicativa, logger strutturato e connessione al provider
    dati corrente. Centralizzare questi elementi evita duplicazioni e rende piu
    semplice sostituire Access con PostgreSQL in futuro.

    Parametri:
    - `config`: configurazione applicativa. Se non viene passata, viene letta
      da `get_config()`.
    - `logger`: logger strutturato. Se non viene passato, viene creato con
      `get_logger()`.

    Valori restituiti:
    la classe non restituisce valori direttamente; crea istanze riusabili dai
    futuri repository concreti.

    Rischi evitati:
    - hardcoding ripetuto del percorso Access;
    - repository concreti costruiti con formati diversi;
    - accoppiamento dei Service a dettagli `pyodbc`;
    - migrazione PostgreSQL piu costosa per mancanza di confini.

    Uso futuro nei Repository/Service:
    un futuro `ProtocolloRepository` erediterà da `BaseRepository`, usera
    `_open_access_connection()` nei metodi Access-specific e offrira metodi di
    dominio come `list_protocolli()` o `get_protocollo_detail()`. I Service
    chiameranno quei metodi, non `pyodbc` direttamente.
    """

    config: AppConfig = field(default_factory=get_config)
    logger: Logger = field(default_factory=get_logger)

    @property
    def provider_name(self) -> str:
        """Restituisce il nome normalizzato del provider dati configurato.

        Cosa fa:
        legge `database_provider` dalla configurazione e lo normalizza in
        minuscolo.

        Perche esiste:
        i repository concreti avranno bisogno di sapere se stanno lavorando in
        modalita Access o, in futuro, PostgreSQL. Esporre una property comune
        evita controlli ripetuti e potenzialmente incoerenti.

        Parametri:
        nessuno, usa `self.config`.

        Valori restituiti:
        - stringa normalizzata, ad esempio `access` o `postgresql`.

        Rischi evitati:
        - confronti case-sensitive;
        - duplicazione del parsing provider;
        - logica provider sparsa nei repository concreti.

        Uso futuro nei Repository/Service:
        i repository concreti potranno usare questa property per loggare il
        provider o validare che un metodo Access-specific non venga invocato in
        modalita PostgreSQL.
        """

        return self.config.database_provider.strip().lower()

    @property
    def is_access_provider(self) -> bool:
        """Indica se il repository sta usando Access come provider.

        Cosa fa:
        delega alla configurazione centralizzata il controllo del provider.

        Perche esiste:
        Access e il provider compatibile oggi. Rendere esplicita questa
        informazione aiuta i futuri repository concreti a mantenere comportamenti
        conservativi durante la migrazione.

        Parametri:
        nessuno.

        Valori restituiti:
        - `True` se il provider configurato e Access;
        - `False` negli altri casi.

        Rischi evitati:
        - usare accidentalmente connessioni Access in modalita PostgreSQL;
        - replicare controlli diversi in classi diverse.

        Uso futuro nei Repository/Service:
        i metodi Access-specific potranno controllare questa property prima di
        aprire una connessione.
        """

        return self.config.is_access_provider

    @property
    def is_postgres_provider(self) -> bool:
        """Indica se il provider configurato punta a PostgreSQL.

        Cosa fa:
        delega alla configurazione centralizzata il controllo del provider
        PostgreSQL.

        Perche esiste:
        PostgreSQL e il target definitivo, ma non e operativo in Step 1. Questa
        property consente di preparare il codice senza introdurre connessioni
        PostgreSQL reali.

        Parametri:
        nessuno.

        Valori restituiti:
        - `True` se il provider configurato e `postgres` o `postgresql`;
        - `False` negli altri casi.

        Rischi evitati:
        - confondere predisposizione architetturale con implementazione reale;
        - introdurre dipendenze PostgreSQL premature.

        Uso futuro nei Repository/Service:
        una factory potra usare questa property per scegliere repository Access
        o PostgreSQL.
        """

        return self.config.is_postgres_provider

    def _open_access_connection(self, **connect_options: Any) -> pyodbc.Connection:
        """Apre una connessione Access tramite il modulo centralizzato.

        Cosa fa:
        chiama `get_access_connection()` passando la configurazione del
        repository e restituisce una connessione `pyodbc` aperta.

        Perche esiste:
        questo helper evita che ogni repository concreto importi direttamente
        dettagli di connessione o ricostruisca la stringa ODBC. E un uso
        concettuale e controllato di `access_connection.py`.

        Parametri:
        - `connect_options`: opzioni keyword da inoltrare a `pyodbc.connect`.
          In Step 1 non vengono usate dai runtime esistenti; servono solo per
          flessibilita futura.

        Valori restituiti:
        - connessione `pyodbc.Connection` aperta.

        Rischi evitati:
        - duplicare apertura connessione nei repository concreti;
        - perdere compatibilita con il percorso Access centralizzato;
        - accoppiare i Service a `pyodbc`.

        Uso futuro nei Repository/Service:
        un repository concreto potra usare:

        ```python
        with self._open_access_connection() as conn:
            ...
        ```

        oppure chiudere esplicitamente la connessione, coerentemente con le
        esigenze di Access e con le pratiche gia presenti nel progetto.
        """

        if not self.is_access_provider:
            raise RuntimeError(
                "Tentativo di aprire una connessione Access con provider "
                f"configurato come {self.provider_name!r}."
            )

        return get_access_connection(self.config, **connect_options)
