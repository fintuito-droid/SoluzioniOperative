# Step 17 - Backend Layer con Endpoint Migrati

## 1. Obiettivo

Questo documento registra il passaggio dei principali endpoint di
ProtocolloMonitor da query SQL dirette dentro `backend/main.py` a un primo
Service Layer e Repository Layer.

La migrazione non cambia il database Access, non modifica il frontend e non
introduce PostgreSQL operativo. Lo scopo e separare progressivamente le
responsabilita, rendendo il backend piu leggibile, testabile e predisposto alla
futura piattaforma Soluzioni Operative multi modulo.

## 2. Endpoint migrati

- `GET /protocollo-monitor/protocolli`
- `GET /protocollo-monitor/protocolli/{id_protocollo}`
- `GET /protocollo-monitor/protocolli/{id_protocollo}/pdf`
- `GET /protocollo-monitor/protocolli/{id_protocollo}/apri-pdf`

## 3. Architettura attuale

```text
FastAPI Endpoint
  -> DependencyContainer
  -> ProtocolloService / DocumentoService
  -> ProtocolloRepository / DocumentoRepository
  -> Access
```

Il `DependencyContainer` viene istanziato localmente negli endpoint migrati.
I Service delegano ai Repository. I Repository accedono ad Access tramite il
layer di connessione centralizzato.

## 4. Stato di main.py

- Non contiene piu query SQL dirette principali per gli endpoint migrati.
- Mantiene solo logica endpoint e orchestrazione minima.
- Mantiene i controlli filesystem per i PDF tramite `os.path.exists`.
- Mantiene `subprocess.Popen` per l'endpoint `apri-pdf`.
- Mantiene `FileResponse` per la visualizzazione PDF inline.

## 5. Benefici ottenuti

- Separazione delle responsabilita tra endpoint, Service e Repository.
- Predisposizione alla futura migrazione PostgreSQL.
- `main.py` e piu pulito e meno accoppiato ad Access.
- Endpoint piu testabili perche la logica dati e isolata.
- Repository sostituibili in futuro senza cambiare il contratto degli endpoint.

## 6. Limiti ancora presenti

- `SELECT *` e ancora presente nel repository del dettaglio protocollo per
  preservare il formato JSON attuale.
- `os.path.exists` e ancora negli endpoint PDF.
- `subprocess.Popen` e ancora Windows-specific.
- `DependencyContainer` viene istanziato localmente negli endpoint.
- L'elenco protocolli non ha ancora paginazione.
- Non esiste ancora uno storage service dedicato.
- Metadati e tag sono ancora solo predisposti, non reali.

## 7. Prossimi passi consigliati

- Valutare import globale controllato del `DependencyContainer`.
- Introdurre `DocumentStorageService`.
- Introdurre test automatici minimi sugli endpoint migrati.
- Progettare `ProcedimentoService`.
- Progettare tag e metadati reali con schema compatibile PostgreSQL.
