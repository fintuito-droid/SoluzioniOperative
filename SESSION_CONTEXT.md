# SESSION_CONTEXT.md — Piattaforma SoluzioniOperative

## Cos'è

**SoluzioniOperative** è la piattaforma multi-modulo dei VVF — Direzione Regionale
Sicilia: un **frontend unico** con login unico e abilitazioni per modulo, più un
backend separato per ogni modulo.

Integrazione completata il **2026-06-12** (Fasi 0–5).

## Architettura

```text
Piattaforma\frontend      Vue 3.5.35 (PINNATO) + Vuetify 4.1.1 + Pinia + Vite 6 — porta 5173
ProtocolloMonitor\backend FastAPI + Access            — porta 8000
Servizi\backend           FastAPI + PostgreSQL 17 (db aib2026) — porta 8001  ← AUTH PROVIDER
                          (fallback legacy: DB_ENGINE=access → aib2026.accdb)
XR33\backend              FastAPI + SQLAlchemy + PostgreSQL 17 (xr33db) — porta 8002
```

Integrazioni ProtocolloMonitor: Flask Grisu :5000, helper "Apri con Word" :8020.

**Avvio di tutto**: doppio click su `Piattaforma\avvia.bat`.
Login sviluppo: `admin` / `admin123`.

## Autenticazione e abilitazioni

* **Auth provider = backend Servizi** (sessioni persistenti su DB, scadenza 12h).
  Login: `POST :8001/api/v1/auth/login` → bearer token; validazione `GET /auth/me`.
* Il token è salvato dal frontend in `localStorage` come `so_token` (utente: `so_user`).
* **Abilitazioni moduli**: tabella `utenti_moduli` in aib2026.accdb
  (colonna `codice_modulo`: `servizi` | `protocollo-monitor` | `xr33`).
  Gli **admin sono abilitati a tutto implicitamente** (nessun record).
  Gestione: Impostazioni → Utenti (checkbox moduli, chips in tabella).
* `login` e `/auth/me` restituiscono `moduli: [...]`; il guard del router blocca le
  rotte dei moduli non abilitati; la home mostra il lucchetto "Non abilitato".
* **ProtocolloMonitor e XR33 validano il token piattaforma per introspezione**
  (`GET :8001/api/v1/auth/me`, cache in-memory 60s):
  - PM: `backend/core/platform_auth.py`, dipendenza globale sul router; 403 se modulo non abilitato.
  - XR33: `backend/auth.py` riscritto; in più **mappa per username** sull'utente XR33
    (tabella Utente in PostgreSQL) → 403 "non censito" se assente. Il vecchio JWT
    locale di XR33 non è più accettato (endpoint /login legacy, inutilizzato).

## Frontend unico (Piattaforma\frontend)

* Base: copia del frontend Servizi (versioni pinnate, Pinia, store auth).
* `src/moduli.js` = catalogo moduli (nome, icona, rotta, `migrato`).
* `src/views/` = shell: LoginView, HomeView (launcher a tessere), LayoutView
  (drawer dinamico per modulo: meta.modulo della rotta).
* `src/modules/<modulo>/` = codice di ogni modulo:
  - `servizi/views/*` — 7 view, rotte `/servizi/...` (guard di ruolo invariati)
  - `protocollo-monitor/{views,components,services,mock,assets}` — rotte
    `/protocollo-monitor/protocolli[...]` e `/protocollo-monitor/procedimenti[...]`;
    auth header aggiunto a procedimentoApi.js e alle fetch dirette delle view
  - `xr33/views/ChecklistXR33View.vue` — rotta `/xr33`; usa `getToken()` piattaforma
* I frontend originali nei moduli (`Servizi\frontend`, `ProtocolloMonitor\frontend`,
  `XR33\frontend`) restano come **fallback legacy** finché la piattaforma non è
  consolidata; non riceveranno evoluzioni.

## Utenti attuali (aib2026)

| username | ruolo | moduli |
|---|---|---|
| admin (id 1) | admin | tutti (implicito) |
| admin (id 2) | admin | DISATTIVATO (duplicato storico) |
| Davì | responsabile | servizi |
| francesco | dipendente | xr33 (mappa sull'utente XR33 'francesco', comando Palermo) |

## Vincoli tecnici

Vedi `Servizi\SESSION_CONTEXT.md` per i vincoli Access/FastAPI/Vue (JOIN annidati,
parole riservate in [quadre], niente N+1, Query(None) espliciti, ecc.).
Valgono per tutta la piattaforma. Regole permanenti: niente Docker, niente
microservizi, nessuna nuova dipendenza senza autorizzazione, piano prima del codice.

## Prossimi passi

1. Evoluzioni designer report: immagini/loghi, export PDF calendario visuale.
2. Valutare estrazione dell'auth in servizio dedicato (oggi è nel backend Servizi).
3. Pulizia frontend legacy dei moduli quando la piattaforma è consolidata.
4. Valutare migrazione PostgreSQL anche per ProtocolloMonitor (oggi su Access).

## Task B completato (2026-06-12): Servizi su PostgreSQL

* `db/database.py`: PostgreSQLDatabase con traduzione runtime `[x]`→`"x"`, `?`→`%s`,
  `lastval()`; motore scelto da `DB_ENGINE` (default postgres, fallback access)
* `pg_schema.py`: schema con FK e indici; `pg_migrate_dati.py`: travaso con ID
  preservati, sequenze riallineate, ore_totali arrotondate (13/13 tabelle OK)
* Password: bcrypt con dual-hash — i vecchi SHA-256 vengono convertiti al primo
  login riuscito; nessun reset necessario
