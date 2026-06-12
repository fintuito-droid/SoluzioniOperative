# SESSION_CONTEXT.md

## Progetto

**Modulo Servizi (AIB 2026)** — applicazione web per la gestione delle presenze nei servizi a pagamento della Campagna Antincendio Boschivo (AIB) del Corpo Nazionale dei Vigili del Fuoco - Direzione Regionale Sicilia.

Il modulo fa parte della piattaforma **SoluzioniOperative**. Dal **2026-06-12** la piattaforma ha un **frontend unico** (`Piattaforma\frontend`, porta 5173) con login unico e abilitazioni per modulo: il backend Servizi è l'**auth provider** della piattaforma e le view del modulo vivono in `Piattaforma\frontend\src\modules\servizi\`. Vedi `SESSION_CONTEXT.md` alla radice del repo per l'architettura piattaforma. Il frontend in `Servizi\frontend` resta come fallback legacy.

Repository:

```text
C:\Users\fintu\Documents\GitHub\SoluzioniOperative\Servizi
```

---

# Architettura

## Frontend

* Vue **3.5.35** (versione PINNATA esatta in package.json — non aggiornare)
* Vuetify **4.1.1** (no import da `vuetify/labs/`)
* Pinia, Vue Router, Vite 6

Avvio rapido della piattaforma intera: doppio click su `Piattaforma\avvia.bat`.
Avvio del solo modulo (frontend legacy): `Servizi\avvia.bat`.

URL: `http://localhost:5173` — Login sviluppo: `admin` / `admin123`

## Backend

* Python 3.10, FastAPI, Uvicorn — **porta 8001** (la 8000 è di ProtocolloMonitor)

```bash
cd Servizi/backend
uvicorn main:app --reload --port 8001
```

Swagger: `http://localhost:8001/docs`

## Database

* **PostgreSQL 17, database `aib2026`** (default dal 2026-06-12) — connessione via
  env `DATABASE_URL` (default `postgresql://postgres:1234@localhost:5432/aib2026`)
* Fallback legacy: `DB_ENGINE=access` → `C:\SoluzioniOperative\aib2026.accdb`
  (override percorso con `ACCESS_DB_PATH`); il file Access NON viene più aggiornato
* Le query del backend restano scritte in dialetto Access-compatibile
  (`[quadre]`, `?`): è `PostgreSQLDatabase` a tradurle a runtime
* Script: `pg_schema.py` (schema con FK e indici, idempotente),
  `pg_migrate_dati.py` (travaso da Access, `--reset` per ricopiare)

---

# Stato funzionale

## COMPLETATO

### Login e sessioni
* Token bearer **persistiti su DB** (tabella `sessioni`, scadenza 12h) — i login sopravvivono ai riavvii del backend; cache in-memory per le performance
* `GET /auth/me` per ripristino sessione al refresh (F5): utente salvato in localStorage e validato all'avvio app
* Cambio password utente (`POST /auth/cambia-password`, voce nel menu laterale)
* Ruoli: admin, responsabile, dipendente; guard router per ruolo

### Matrice permessi ruoli
* **admin**: tutto, inclusi Report (sezione riservata solo admin), Impostazioni, Utenti
* **responsabile**: pianifica/consuntiva presenze del proprio comando, Anagrafica
* **dipendente**: SOLA VISUALIZZAZIONE totale (nessuna scrittura dati; unica eccezione: cambio della propria password)

### Calendario (CalendarioView)
* Vista mensile per postazione (tendina Postazione obbligatoria, un calendario per postazione)
* Cella giorno: cornice colorata che riempie tutta la cella (blu=programmato, verde=confermato, arancio=modificato, rosso=assente); righe `HH:MM -- HH:MM | nome | nome`; header Funzionario|TAS (SOUR) o Addetto (SOR)
* Numero giorno: corsivo grassetto blu; rosso se domenica o festivo nazionale
* Click su giorno vuoto → dialog composizione (regole da DB: SOR=1 addetto 08-20; SOUR=funzionario+TAS2, turno unico o doppio M/P)
* Click su giorno valorizzato → dialog dettaglio con elimina singolo turno e "Modifica composizione" (pre-carica i dati esistenti; al salvataggio elimina e ricrea)
* Personale nei dropdown ordinato per monte ore crescente NELLA postazione selezionata
* Navigazione mese con frecce tastiera ← →

### Presenze (PresenzeView)
* Tabella con filtri, consuntivazione, eliminazione (dialog di conferma, non confirm() nativo)
* Selezione multipla righe programmate + conferma massiva

### Monte Ore (MonteOreView)
* Aggregazione per dipendente, filtri campagna/mesi/funzione/comando, KPI, export CSV
* Barra colorata proporzionale sulla colonna ore (verde=norma, arancio >1.2x media, rosso >1.5x media)

### Anagrafica (AnagraficaView)
* CRUD personale completo con ricerca e filtro comando
* Gestione specialità multiple per dipendente (checkbox: TAS 1/2, NBCR 1/2, SAPR, DOS, USAR L/M/H)

### Impostazioni (ImpostazioniView) — 4 tab
* **Campagne**: crea/modifica, una sola attiva alla volta
* **Postazioni**: CRUD + regole composizione (slot_funzionario, slot_tas2, slot_addetto, turni_multipli)
* **Specialità**: CRUD, eliminazione bloccata se assegnata (409)
* **Utenti**: CRUD, ruolo, collegamento a dipendente, reset password (invalida sessioni), disattivazione (chiude sessioni)

### Hardening
* Validazioni server: data turno dentro periodo campagna (422); sovrapposizione fasce U/M/P stessa persona/giorno (409); batch validato tutto prima di scrivere
* Exception handler globale: i 500 rispondono sempre JSON `{detail}` con header CORS
* Audit log scritture in `backend/logs/operazioni.log` (utente, metodo, path, esito)

### Report (ReportView + ReportDesignerView) — Fase 3
* **Report Designer drag & drop** (`/report/designer/:id`, admin+responsabili, zero dipendenze frontend):
  canvas A4 in scala, bande intestazione/piè con elementi liberi (testo, campo dinamico,
  linea, riquadro, data, n. pagina), pannello proprietà (mm, font, B/I, colore, allineamento),
  gestione colonne tabella (ordine, etichette, larghezze), stile tabella, anteprima PDF reale
* Modello report = JSON in tabella `report_templates` (3 predefiniti: presenze, monte ore, riepilogo)
* `GET /report/pdf/{id}` render reportlab paginato; `POST /report/anteprima`; CRUD modelli
* `GET /report/excel/{sorgente}` — 3 export Excel layout fisso (openpyxl)
* Campi dinamici bande: {sottotitolo} {campagna} {postazione} {periodo} {utente}
* **Librerie autorizzate e installate**: reportlab 4.5.1, openpyxl 3.1.5

## TUTTE LE FASI DEL PIANO COMPLETATE (1–5)

---

# Tabelle DB

`campagne_aib`, `postazioni` (+ slot_funzionario, slot_tas2, slot_addetto, turni_multipli), `qualifiche`, `comandi`, `personale`, `specialita`, `personale_specialita`, `utenti`, `sessioni`, `utenti_moduli` (abilitazioni piattaforma, colonna `codice_modulo`), `funzioni_servizio`, `presenze` (+ fascia_oraria U/M/P), `report_templates` (definizione JSON in Memo)

Migrazioni eseguite (script in backend/): `migrate_composizione.py`, `migrate_specialita.py`, `migrate_sessioni.py`, `migrate_orari.py` (35 orari normalizzati), `migrate_report.py`, `migrate_moduli.py` (utenti_moduli). Tutte idempotenti.

Dati: campagna AIB 2025 (id=3, storica, 69 dipendenti, ~278 presenze), campagna AIB 2026 (id=1, attiva, periodo 2026-06-15 → 2026-10-15).

**Relazioni/FK assenti in Access** — verranno aggiunte alla migrazione PostgreSQL.

---

# Vincoli tecnici Access ⚠️ CRITICI

1. **JOIN multipli annidati con parentesi** obbligatori:
   ```sql
   FROM ((((presenze pr
   LEFT JOIN personale pe ON pe.id = pr.personale_id)
   LEFT JOIN qualifiche q ON q.id = pe.qualifica_id) ... )
   ```
2. **Parole riservate** come nomi colonna → `[parentesi quadre]`. Caso reale: `note` (personale, postazioni) causava 500 negli UPDATE. **Per nuove colonne usare nomi non riservati** (es. `annotazioni`).
3. No `RETURNING` → `SELECT @@IDENTITY`; no `DEFAULT` in CREATE TABLE; tipi `COUNTER`/`BIT`/`VARCHAR`
4. Timestamp DML valorizzati da Python (`datetime.now()`)
5. Dopo DDL: commit + riapertura connessione prima del DML
6. **MAI query-per-riga (N+1)**: ogni roundtrip ODBC costa ~1s. Caricare lookup in mappe e abbinare in Python (caso reale: lista_personale passata da 3 min a <1s)

## FastAPI
* Route che chiama un'altra funzione di route: passare TUTTI i parametri `Query(None)` esplicitamente come `None`
* Endpoint con path fissi (es. `/batch`) PRIMA delle route parametriche (`/{id}`)

## CORS
Origini ammesse: localhost 5173-5177 e 3000 (lista `ALLOWED_ORIGINS` in main.py)

## Frontend
* Personale e lookup in cache nello store Pinia, caricati una volta al login in parallelo; `store.caricaPersonale(force)` per refresh
* Pattern feedback: snackbar; dialog Vuetify per conferme distruttive

---

# Regole permanenti

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

1. Postazione "COMANDO PALERMO" (id 3): verificata il 2026-06-12 — ha 3 presenze confermate della campagna storica 2025 (Giordano Maurizio) e nessuna regola di composizione. **Decisione utente: lasciarla com'è** (non disattivare, non eliminare).
2. `create_db.py` e i `migrate_*.py` sono ormai documentazione storica dello schema Access: eliminabili quando il fallback Access verrà dismesso.

## Risolti

* Admin duplicato: utente id 2 (mai usato, zero sessioni) disattivato il 2026-06-12; l'admin operativo è id 1
* `backend/requirements.txt` creato (+ psycopg2-binary, passlib, bcrypt dal Task B)
* `ore_totali` floating point: valori arrotondati a 2 decimali nel travaso PostgreSQL
* Password SHA-256 → **bcrypt** con verifica dual-hash e upgrade trasparente al primo login

---

# Stato Git

Branch: `main` — push su https://github.com/fintuito-droid/SoluzioniOperative

Commit principali:
* `61675dc` AIB-2026 Modulo Servizi — primo commit
* `ee58992` Impostazioni, conferma massiva, fix performance e parole riservate (Fasi 2+4)
* `48ada9e` Sessioni persistenti, gestione utenti e hardening (Fasi 1+5)

---

# Storico sessioni

## 2026-06-10
Setup completo da zero; fix JOIN annidati; migrazione dati 2025; Monte Ore con filtri e KPI.

## 2026-06-11 / 06-12
* CalendarioView completa (composizione guidata SOR/SOUR, fasce U/M/P, stati colorati, festivi, modifica composizione)
* Regole composizione postazioni su DB (slot_*) + campo `fascia_oraria` presenze
* Specialità personale (tabelle + CRUD + form anagrafica)
* AnagraficaView e ImpostazioniView complete; conferma massiva presenze
* Fix critici: parola riservata `note` (500 al salvataggio), N+1 lista_personale (3 min → <1s), cache personale nello store
* Sessioni persistenti su DB, /auth/me, CRUD utenti, cambio password
* Validazioni server (campagna, sovrapposizioni), exception handler globale, audit log
* Branding piattaforma SoluzioniOperative; avvia.bat; Vue pinnato 3.5.35
* Regole personale calendario: solo comando DIR-SIC; funzionario = qualifica IA/IAE/DCS/DS/DV; addetti = non funzionari (SOR); slot TAS = specialità TAS 2
* Date in formato italiano dd/mm/yyyy ovunque (`utils/format.js`)
* **Fase 3**: Report Designer drag & drop + render PDF (reportlab) + export Excel (openpyxl)
* Restrizioni ruoli: Report solo admin; dipendente in sola visualizzazione totale
* Pulizia (Task A): requirements.txt backend; admin duplicato id 2 disattivato; COMANDO PALERMO analizzata (3 presenze storiche 2025) e lasciata invariata per decisione utente

## 2026-06-12 — Integrazione piattaforma (Fasi 0–5 completate)

* Backend spostato sulla **porta 8001**; frontend unico `Piattaforma\frontend` (5173)
* Login unico: il backend Servizi è l'auth provider della piattaforma; `login` e `/auth/me` restituiscono `moduli`
* Tabella `utenti_moduli` + abilitazioni nel CRUD utenti (admin = tutti impliciti; cache token invalidata al cambio senza chiudere le sessioni)
* View del modulo sotto `Piattaforma\frontend\src\modules\servizi\` con rotte `/servizi/...`
* ProtocolloMonitor (8000) e XR33 (8002) integrati: validano il token piattaforma per introspezione su /auth/me; XR33 mappa per username sulla propria tabella utenti PostgreSQL
* Tab Utenti: checkbox moduli + colonna chips; tessere home con lucchetto; guard router per modulo

## 2026-06-12 — Task B: migrazione PostgreSQL completata

* `PostgreSQLDatabase` in db/database.py (traduzione `[x]`→`"x"`, `?`→`%s`, lastval); default `DB_ENGINE=postgres`, fallback access
* `pg_schema.py`: 13 tabelle con FK e indici (assenti in Access); `pg_migrate_dati.py`: travaso 13/13 OK, ID e sequenze preservati, ore_totali ripulite
* bcrypt dual-hash in auth.py: hash legacy SHA-256 riconosciuti e convertiti al primo login
* Verifica su PG: login, presenze (lettura+scrittura+consuntivo+delete), monte ore, utenti/moduli, PDF reportlab

---

# Prossimi passi

1. Evoluzioni designer: immagini/loghi nei report, export PDF del calendario mensile visuale

---

# Prompt di ripartenza

Leggi interamente questo documento prima di fare qualsiasi cosa. Assumilo come stato ufficiale del progetto.

Prima di proporre modifiche:
1. Riassumi ciò che hai compreso.
2. Individua il task successivo.
3. Presenta un piano di lavoro.
4. Attendi conferma.

Non modificare file senza autorizzazione esplicita.

**Contesto tecnico critico:** JOIN Access annidati con parentesi; parole riservate in `[quadre]`; niente query N+1 (mappe in Python); parametri `Query(None)` espliciti nelle chiamate interne tra route; Vue pinnato 3.5.35; Vuetify 4.1.1 senza `labs/`.
