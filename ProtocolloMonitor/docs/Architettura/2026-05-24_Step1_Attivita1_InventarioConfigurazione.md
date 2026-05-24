# Step 1 - Attivita 1 - Inventario configurazione

Questo documento registra i valori di configurazione individuati nella base
attuale di ProtocolloMonitor prima dell'introduzione della configurazione
centralizzata.

L'obiettivo di questa attivita non e cambiare il comportamento applicativo.
L'obiettivo e rendere esplicito dove oggi vivono i valori operativi, cosi che
le attivita successive possano spostarli gradualmente in un unico punto senza
regressioni su Access, FastAPI, Flask legacy, estensione Chrome e frontend Vue.

## Principi di compatibilita

- ProtocolloMonitor resta il primo modulo operativo della piattaforma Soluzioni
  Operative.
- Access resta il database operativo corrente.
- PostgreSQL resta il target definitivo.
- FastAPI resta il backend applicativo da consolidare.
- Flask resta temporaneamente presente fino a una migrazione controllata.
- Vue 3 e Vuetify 4 restano lo stack frontend.
- I valori sotto elencati non devono essere modificati durante Step 1, Attivita
  1 e 2: devono solo essere censiti e resi disponibili come default nella nuova
  configurazione centralizzata.

## Database Access

Valore operativo attuale:

```text
G:\ProtocolloMonitor.accdb
```

Punti in cui il percorso e oggi dichiarato direttamente:

- `backend/main.py`
- `Python/server_protocollo.py`
- `Python/salva_access.py`

Nota architetturale:
questo valore dovra diventare `access_db_path` nella configurazione
centralizzata. In futuro, quando PostgreSQL diventera il database definitivo,
il codice applicativo non dovra piu dipendere direttamente dal percorso Access:
dovra dipendere da un repository compatibile con il provider configurato.

## Storage documentale

Valore operativo attuale:

```text
C:\Users\fintu\Documents\GitHub\SoluzioniOperative\ProtocolloMonitor\backend\FileServer
```

Punti in cui il percorso e oggi dichiarato direttamente:

- `Python/server_protocollo.py`

Nota architetturale:
questo valore dovra diventare `file_storage_root`. Lo storage fisico non deve
diventare una regola di dominio: il database e i service devono ragionare su
documenti e metadati, mentre il filesystem deve essere incapsulato da uno
storage service sostituibile.

## Backend FastAPI

Valori operativi attuali:

```text
host: 127.0.0.1
port: 8000
base url: http://127.0.0.1:8000
```

Punti in cui sono usati:

- `avvia_protocollo_monitor.bat`
- `tempCodeRunnerFile.bat`
- `frontend/src/views/protocollo-monitor/ProtocolliAcquisitiView.vue`
- `frontend/src/views/protocollo-monitor/NotaProtocolloView.vue`
- `frontend/src/views/protocollo-monitor/ProtocolloDettaglioView.vue`

Nota architetturale:
in Step 1 il frontend non viene modificato. Il valore viene solo censito e
preparato come default per una futura configurazione frontend/API client.

## Server Flask legacy

Valori operativi attuali:

```text
host: 127.0.0.1
port: 5000
base url: http://127.0.0.1:5000
```

Punti in cui sono usati:

- `Python/server_protocollo.py`
- `Estensione/content-script.js`
- `Estensione/background.js`
- `Estensione/manifest.json`
- `avvia_protocollo_monitor.bat`
- `tempCodeRunnerFile.bat`

Nota architetturale:
Flask resta compatibile nella fase iniziale. La futura eliminazione di Flask
andra valutata nello Step 2, quando gli endpoint di acquisizione potranno
essere spostati su FastAPI con parita funzionale.

## Frontend Vue

Valori operativi attuali:

```text
host sviluppo: localhost / 127.0.0.1
port: 5173
```

Punti in cui sono usati:

- `backend/main.py`, nella configurazione CORS FastAPI
- `avvia_protocollo_monitor.bat`
- `tempCodeRunnerFile.bat`

Nota architetturale:
Vue 3 e Vuetify 4 restano vincoli tecnici. La futura introduzione di Pinia e
di un API client centralizzato dovra usare questi valori senza hardcoding nei
componenti.

## CORS

Origini attualmente autorizzate in FastAPI:

```text
http://localhost:5173
http://127.0.0.1:5173
```

Punto in cui sono dichiarate:

- `backend/main.py`

Nota architetturale:
questo elenco dovra diventare `cors_origins`. In futuro, per ambienti diversi
da sviluppo locale, le origini dovranno essere configurate per ambiente e non
inserite direttamente nel codice.

## Modulo applicativo

Codice modulo usato nelle liste di contesto:

```text
PROTOCOLLO_MONITOR
```

Punti in cui compare:

- `Python/server_protocollo.py`

Nota architetturale:
questo valore dovra diventare `module_code`. Serve a preparare Soluzioni
Operative come piattaforma multi modulo, evitando che ProtocolloMonitor sia
trattato come applicazione monolitica isolata.

## Utente operativo locale

Valore attuale:

```text
ID_UTENTE_CORRENTE = 1
```

Punto in cui e dichiarato:

- `Python/salva_access.py`

Nota architetturale:
questo valore e un placeholder per la futura autenticazione. Nello Step 1 deve
restare compatibile; negli step successivi dovra confluire in un security
context capace di rappresentare utente, ruoli, permessi e modulo corrente.

## PostgreSQL target

PostgreSQL non e ancora collegato al runtime attuale.

La configurazione centralizzata dovra comunque prevedere:

- `database_provider`
- `postgres_dsn`
- `postgres_schema`

Nota architetturale:
questi valori devono esistere come predisposizione, ma il provider di default
deve restare `access` per evitare regressioni.

## Feature flags iniziali

Feature flags da prevedere come default conservativi:

- `enable_audit`
- `enable_metadata`
- `enable_health_details`
- `enable_new_repository_layer`
- `enable_postgres_mode`

Nota architetturale:
i flag non devono attivare nuove funzionalita in questa fase. Servono solo a
preparare introduzioni progressive e rollback semplici durante la
modernizzazione.
