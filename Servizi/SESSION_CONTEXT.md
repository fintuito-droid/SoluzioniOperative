# SESSION_CONTEXT.md

## Progetto

**Modulo AIB 2026** — applicazione web per la gestione delle presenze nei servizi a pagamento della Campagna Antincendio Boschivo (AIB) del Corpo Nazionale dei Vigili del Fuoco - Direzione Regionale Sicilia.

Il progetto fa parte dell'ecosistema **SoluzioniOperative**.

Repository:

```text
C:\Users\fintu\Documents\GitHub\SoluzioniOperative\Servizi
```

---

# Obiettivo del progetto

Realizzare una piattaforma web moderna per la pianificazione, gestione e consuntivazione dei servizi AIB.

Obiettivi principali:

* Pianificazione turni
* Gestione presenze
* Gestione personale
* Calcolo monte ore
* Reportistica
* Gestione campagne annuali
* Futura integrazione con SoluzioniOperative

---

# Architettura

## Frontend

Tecnologie:

* Vue 3
* Vuetify **4.1.1** (latest stable — NON 3.x)
* Pinia
* Vue Router
* Vite 6

Percorso:

```text
Servizi/frontend
```

Avvio:

```bash
cd Servizi/frontend
npm run dev
```

URL:

```text
http://localhost:5173
```

---

## Backend

Tecnologie:

* Python 3.10
* FastAPI
* Uvicorn

Percorso:

```text
Servizi/backend
```

Avvio:

```bash
cd Servizi/backend
python -m uvicorn main:app --port 8000
```

Swagger:

```text
http://localhost:8000/docs
```

---

## Database

Tecnologia:

* Microsoft Access (.accdb)
* pyodbc + driver ODBC "Microsoft Access Driver (*.mdb, *.accdb)"

Percorso:

```text
C:\SoluzioniOperative\aib2026.accdb
```

Configurabile tramite variabile d'ambiente `ACCESS_DB_PATH`.

Predisposto per futura migrazione PostgreSQL (tutti i tipi SQL commentati nel file `schema_access.sql`).

---

# Struttura funzionale

## Implementato

### Login

Stato: COMPLETATO

Funzionalità:

* autenticazione token bearer in-memory
* ruoli: admin, responsabile, dipendente
* guard router per ruolo

Credenziali sviluppo:

```text
username: admin
password: admin123
```

---

### Presenze

Stato: COMPLETATO

Funzionalità:

* elenco turni con tabella
* filtri: postazione, stato, data dal/al
* inserimento nuovo turno (solo admin/responsabile)
* consuntivazione turno (solo admin/responsabile)
* eliminazione (solo admin)
* badge colorato per stato: programmato (blu), confermato (verde), modificato (arancio), assente (rosso)

---

### Monte Ore

Stato: COMPLETATO

Funzionalità:

* aggregazione ore per dipendente
* filtri: campagna, dal (mese), al (mese), funzione, comando
* selezione campagna imposta automaticamente il range mesi
* KPI reattivi ai filtri: dipendenti coinvolti, ore totali, turni totali, media ore/dip.
* dettaglio presenze per dipendente (dialog)
* export CSV
* ordine colonne: Qualifica | Cognome | Nome | Turni | Ore tot. | Per funzione

---

### Calendario

Stato: DA SVILUPPARE (placeholder)

Funzionalità previste:

* vista mensile
* click sul giorno per aggiungere/modificare turno
* colori per stato
* filtri postazione e funzione

---

### Anagrafica

Stato: DA SVILUPPARE (placeholder)

Funzionalità previste:

* CRUD personale
* filtri comando e qualifica
* attivazione/disattivazione dipendente

---

### Impostazioni

Stato: DA SVILUPPARE (placeholder)

Funzionalità previste:

* gestione campagne
* gestione utenti
* gestione postazioni

---

# Tabelle principali

* `campagne_aib`
* `postazioni`
* `qualifiche`
* `comandi`
* `personale`
* `utenti`
* `funzioni_servizio`
* `presenze`

---

# Dati attualmente caricati

## Campagna AIB 2025

* id = 3
* 69 dipendenti
* 266 presenze (fonte: `PresenzeSour - Copia.accdb`)
* Lookup caricati: 4 funzioni, 3 postazioni, 5 comandi, 16 qualifiche

Stato:

```text
attiva = False
```

---

## Campagna AIB 2026

* id = 1

Stato:

```text
attiva = True
```

Pronta per la pianificazione. Nessuna presenza ancora inserita.

---

# Decisioni progettuali

## Database

Decisione: Access adesso, PostgreSQL successivamente.

Motivazione: velocità di sviluppo e compatibilità con l'ambiente operativo VVF.

La classe `AccessDatabase` in `db/database.py` implementa l'interfaccia `BaseDatabase`.
Migrare a PostgreSQL = scrivere `PostgreSQLDatabase` e sostituire il singleton `db`. Nessun'altra modifica necessaria.

---

## Autenticazione

Decisione: token bearer in-memory (dizionario Python).

Motivazione: semplicità nella fase iniziale.

Punto di sostituzione documentato in `auth.py`. Prevista futura sostituzione con JWT, CAS o SSO senza modificare il resto dell'applicazione.

Conseguenza: i token vengono persi al riavvio del backend — gli utenti devono ri-loginare.

---

## Filtri Monte Ore

Decisione: filtri funzione e comando lato client.

Motivazione: dataset attuale ridotto (< 300 presenze).

Da rivalutare con dataset superiori — in quel caso spostare i filtri come parametri API.

---

## Orari

Decisione: formato `HH:MM`, memorizzati come `VARCHAR(5)`.

Motivazione: Access non ha tipo TIME nativo.

Il backend normalizza automaticamente in input (`8:00` → `08:00`) tramite validator Pydantic in `models.py`.

---

# Vincoli tecnici

## Access — JOIN multipli annidati ⚠️ CRITICO

I LEFT JOIN multipli in Access via ODBC **devono** usare la sintassi annidata con parentesi.
La sintassi SQL standard (flat) genera errore ODBC 500.

**Sintassi corretta (obbligatoria):**

```sql
FROM ((((presenze pr
LEFT JOIN personale     pe ON pe.id = pr.personale_id)
LEFT JOIN qualifiche    q  ON q.id  = pe.qualifica_id)
LEFT JOIN postazioni    po ON po.id = pr.postazione_id)
LEFT JOIN funzioni_servizio f ON f.id = pr.funzione_id)
```

**Sintassi errata (causa errore):**

```sql
FROM presenze pr
LEFT JOIN personale pe ON pe.id = pr.personale_id
LEFT JOIN qualifiche q ON q.id = pe.qualifica_id
...
```

---

## Access ODBC — limitazioni DDL e DML

* Tipi DDL: usare `COUNTER`, `BIT`, `VARCHAR` (non `AUTOINCREMENT`, `YESNO`, `TEXT`)
* Nomi colonna riservati (es. `nome`, `note`) vanno racchiusi in `[parentesi quadre]`
* No `DEFAULT` nelle istruzioni `CREATE TABLE` via ODBC
* No `RETURNING` — usare `SELECT @@IDENTITY` dopo INSERT per ottenere il nuovo id
* No `NOW()` nelle query DML via pyodbc — valorizzare i timestamp lato Python
* Dopo DDL occorre fare `commit` e riaprire la connessione prima di eseguire DML sulle nuove tabelle

---

## FastAPI — chiamate interne tra route

Quando una route chiama direttamente un'altra funzione di route (es. `monte_ore` chiama `lista_presenze`), tutti i parametri con default `Query(None)` devono essere passati esplicitamente come `None`.
Altrimenti il default `Query(None)` è un oggetto `FieldInfo` truthy che viene passato al DB causando errore `Invalid parameter type`.

---

## Vuetify

Versione installata: **4.1.1**. Non usare import da `vuetify/labs/` (es. `VCalendar` è già stabile nei `components`).

---

## CORS

Il backend accetta richieste da:

* `http://localhost:5173`
* `http://localhost:5174`
* `http://localhost:3000`

---

# Regole permanenti

Queste regole devono essere sempre rispettate.

1. Non modificare il database senza autorizzazione.
2. Non introdurre Docker.
3. Non introdurre microservizi.
4. Non introdurre nuove dipendenze senza autorizzazione.
5. Mostrare sempre il piano prima di modificare il codice.
6. Per modifiche che coinvolgono più di 3 file chiedere conferma.
7. Non eseguire refactoring non richiesti.
8. Mantenere compatibilità futura PostgreSQL.
9. Preferire modifiche incrementali.
10. Non eliminare codice senza motivazione esplicita.

---

# Problemi aperti

1. `CalendarioView.vue` non implementata.
2. `AnagraficaView.vue` non implementata.
3. `ImpostazioniView.vue` non implementata.
4. Orari non uniformi nel DB (alcuni record hanno `8:00` invece di `08:00`).
5. Valori `ore_totali` con floating point impreciso (es. `6.000000000000002`) — il modello arrotonda in output ma il DB non è stato corretto.
6. Sessioni non persistenti — token persi al riavvio backend.
7. Titolo "AIB 2026" hardcoded nel nav drawer (`LayoutView.vue`).
8. File di debug `test_query.py` da eliminare.

---

# Stato Git

Branch corrente:

```text
main
```

Aggiornare questa sezione al termine di ogni sessione.

Ultimo commit significativo:

```text
DA AGGIORNARE
```

---

# Storico sessioni

## 2026-06-10

Attività completate:

* Setup progetto completo da zero (DB, frontend scaffold, backend)
* Aggiornamento Vuetify 3.x → 4.1.1
* Fix alias `@` in vite.config.js
* Creati componenti `PresenzaForm.vue` e `ConsuntivoForm.vue`
* Creati placeholder `CalendarioView`, `AnagraficaView`, `ImpostazioniView`
* Fix JOIN annidati Access (bug critico)
* Fix validazione Pydantic orari e date
* Fix chiamata interna `monte_ore` → `lista_presenze` (parametri Query)
* Migrazione dati AIB 2025 (69 dipendenti, 266 presenze)
* Pulizia duplicati in `funzioni_servizio`, `postazioni`, `comandi`
* Implementazione filtri Monte Ore: funzione, comando, range mese, auto-set da campagna
* KPI Monte Ore reattivi ai filtri
* Ordine colonne Monte Ore: Qualifica | Cognome | Nome

---

# Session Summary

Data aggiornamento:

```text
DA AGGIORNARE
```

Attività completate:

```text
DA AGGIORNARE
```

Attività in corso:

```text
DA AGGIORNARE
```

Prossimo task:

```text
Sviluppo CalendarioView — vista mensile per pianificazione presenze
```

---

# Prossimi passi

Priorità alta:

1. `CalendarioView` — vista mensile, click su giorno, inserimento/modifica turno, colori stato, filtri
2. `AnagraficaView` — CRUD personale, filtri comando/qualifica

Priorità media:

3. `ImpostazioniView` — gestione campagne, utenti, postazioni
4. Persistenza sessioni (JWT o sessionStorage)

Priorità bassa:

5. Pulizia file debug (`test_query.py`, `create_db.py`)
6. Normalizzazione orari nel DB (`8:00` → `08:00`)

---

# Prompt di ripartenza

Leggi interamente questo documento prima di fare qualsiasi cosa.

Assumilo come stato ufficiale del progetto.

Prima di proporre modifiche:

1. Riassumi ciò che hai compreso.
2. Individua il task successivo.
3. Presenta un piano di lavoro.
4. Attendi conferma.

Non modificare file senza autorizzazione esplicita.

**Contesto tecnico critico da tenere sempre presente:**

* I LEFT JOIN multipli in Access **devono** essere annidati con parentesi (vedi sezione Vincoli).
* Quando una route FastAPI chiama un'altra funzione di route, passare **tutti** i parametri esplicitamente come `None`.
* Vuetify è alla versione **4.1.1** — non usare import da `vuetify/labs/`.
