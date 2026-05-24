# Step 15 - Backend Layer Preparatorio

## 1. Obiettivo dello step

Lo Step 15 ha introdotto un primo backend layer preparatorio per
ProtocolloMonitor, composto da repository, service e dependency container.

Questi elementi sono stati creati per preparare una separazione piu ordinata
tra endpoint FastAPI, logica applicativa e accesso dati, ma non sono ancora
collegati al runtime esistente.

Il comportamento applicativo resta invariato: gli endpoint attuali continuano a
usare il codice gia presente in `backend/main.py`, il database Access resta
compatibile e non sono state introdotte integrazioni operative.

## 2. File introdotti

- `backend/repositories/metadata_repository.py`
- `backend/services/protocollo_service.py`
- `backend/services/documento_service.py`
- `backend/services/metadata_service.py`
- `backend/core/dependency_container.py`

## 3. Mappa logica

```text
Endpoint FastAPI
  -> Service Layer
  -> Repository Layer
  -> Access oggi / PostgreSQL domani
```

La mappa rappresenta il target architetturale, non lo stato runtime attuale.
Al momento gli endpoint FastAPI non usano ancora il Service Layer.

## 4. Responsabilita dei file

### metadata_repository.py

Repository minimale e read-only per predisporre la futura gestione di metadati
e tag. Non interroga tabelle reali e non modifica Access. Restituisce fallback
controllati finche la feature non sara progettata e collegata.

### protocollo_service.py

Service minimale e read-only per protocolli. Riceve repository opzionali e
delega a essi il recupero di dettaglio protocollo, percorso PDF e disponibilita
metadati. Non apre connessioni e non modifica dati.

### documento_service.py

Service minimale e read-only per la parte documentale. Prepara il punto in cui
in futuro saranno coordinate lettura documento, verifica esistenza logica e
metadati documentali.

### metadata_service.py

Service minimale e read-only per metadati e tag. Valida in modo prudente
`entity_type` e `entity_id`, delega al repository se disponibile e restituisce
fallback sicuri.

### dependency_container.py

Container minimale con inizializzazione lazy. Predispone la composizione di
repository e service senza integrarli negli endpoint. In futuro potra scegliere
implementazioni Access o PostgreSQL in base alla configurazione.

## 5. Cosa NON e stato fatto

- Nessuna modifica runtime.
- Nessuna modifica database.
- Nessuna integrazione endpoint.
- Nessuna modifica frontend.
- Nessuna modifica Grisu.
- Nessuna modifica a `backend/main.py`.
- Nessuna creazione di tabelle.
- Nessuna attivazione PostgreSQL operativa.

## 6. Rischi e limiti

- Il codice introdotto e preparatorio e non ancora usato dal runtime.
- I metadati non sono ancora reali: non esistono tabelle dedicate collegate.
- Il dependency container non e ancora integrato negli endpoint.
- PostgreSQL e solo predisposto a livello architetturale.
- Prima dell'integrazione sara necessario confrontare l'output dei repository
  con quello degli endpoint attuali.

## 7. Prossimi passi consigliati

- Eseguire un test controllato dei repository senza modificare gli endpoint.
- Integrare gradualmente il layer solo negli endpoint PDF/protocolli, quando i
  test di parita saranno completati.
- Introdurre in futuro `ProcedimentoService` per modellare la futura entita
  Procedimento.
- Introdurre in futuro tag e metadati reali con schema dedicato e compatibile
  con PostgreSQL.
