-- ============================================================
-- SCRIPT CREAZIONE TABELLE ACCESS — AIB 2026
-- SoluzioniOperative · Vigili del Fuoco
-- ============================================================
-- Struttura identica allo schema PostgreSQL finale.
-- I tipi Access sono mappati ai tipi Postgres equivalenti
-- nei commenti a fianco — migrazione 1:1 senza trasformazioni.
--
-- Eseguire in ordine: prima le tabelle lookup,
-- poi quelle con FK.
-- ============================================================


-- ── 1. CAMPAGNE_AIB ─────────────────────────────────────────
-- PG: id SERIAL, anno INT, date DATE, descrizione TEXT
CREATE TABLE campagne_aib (
    id          AUTOINCREMENT PRIMARY KEY,   -- PG: SERIAL
    anno        INTEGER NOT NULL,            -- PG: INT
    data_inizio DATETIME NOT NULL,           -- PG: DATE
    data_fine   DATETIME NOT NULL,           -- PG: DATE
    descrizione MEMO,                        -- PG: TEXT
    attiva      YESNO DEFAULT TRUE           -- PG: BOOLEAN
);
-- Seed iniziale AIB 2026
-- INSERT INTO campagne_aib (anno, data_inizio, data_fine, descrizione, attiva)
-- VALUES (2026, #06/15/2026#, #10/15/2026#, 'Campagna AIB 2026 Sicilia', True);


-- ── 2. POSTAZIONI ───────────────────────────────────────────
-- PG: id SERIAL, codice VARCHAR(20) UNIQUE, nome VARCHAR(100), attiva BOOL
CREATE TABLE postazioni (
    id      AUTOINCREMENT PRIMARY KEY,       -- PG: SERIAL
    codice  TEXT(20) NOT NULL,               -- PG: VARCHAR(20) UNIQUE NOT NULL
    nome    TEXT(100) NOT NULL,              -- PG: VARCHAR(100)
    note    MEMO,                            -- PG: TEXT
    attiva  YESNO DEFAULT TRUE              -- PG: BOOLEAN
);
-- Seed dalle postazioni 2025
-- INSERT INTO postazioni (codice, nome, attiva) VALUES
--   ('SOUR', 'Sala Operativa Unificata Regionale', True),
--   ('SOR', 'Sala Operativa Regionale', True),
--   ('COMANDO PA', 'Comando Provinciale Palermo', True);


-- ── 3. QUALIFICHE ───────────────────────────────────────────
-- Lookup per normalizzare le qualifiche (erano stringhe libere in Access 2025)
-- PG: id SERIAL, codice VARCHAR(10) UNIQUE, descrizione VARCHAR(100)
CREATE TABLE qualifiche (
    id          AUTOINCREMENT PRIMARY KEY,   -- PG: SERIAL
    codice      TEXT(10) NOT NULL,           -- PG: VARCHAR(10) UNIQUE NOT NULL
    descrizione TEXT(100)                    -- PG: VARCHAR(100)
);
-- Seed dalle qualifiche distinte presenti nel DB 2025
-- (CS, CSE, D, DCS, DS, DV, EDCS, IA, IAE, CR, VC, VCSC, VE, VESC, VF, VIG)


-- ── 4. COMANDI ──────────────────────────────────────────────
-- Lookup comandi provinciali/regionali
-- PG: id SERIAL, codice VARCHAR(20) UNIQUE, nome VARCHAR(100), attivo BOOL
CREATE TABLE comandi (
    id      AUTOINCREMENT PRIMARY KEY,       -- PG: SERIAL
    codice  TEXT(20) NOT NULL,               -- PG: VARCHAR(20) UNIQUE NOT NULL
    nome    TEXT(100) NOT NULL,              -- PG: VARCHAR(100)
    attivo  YESNO DEFAULT TRUE              -- PG: BOOLEAN
);
-- Seed: PALERMO, MESSINA, CALTANISSETTA, ENNA, DIR-SIC


-- ── 5. PERSONALE ────────────────────────────────────────────
-- Anagrafica dipendenti. Identica alla tabella Access originale
-- con aggiunte: qualifica_id (FK), comando_id (FK), attivo, matricola
-- PG: tipi identici salvo AUTOINCREMENT→SERIAL, YESNO→BOOLEAN
CREATE TABLE personale (
    id              AUTOINCREMENT PRIMARY KEY,   -- PG: SERIAL
    matricola       TEXT(20),                    -- PG: VARCHAR(20) — per futuro CAS/JWT
    qualifica_id    INTEGER,                     -- PG: INT FK → qualifiche.id
    cognome         TEXT(100) NOT NULL,          -- PG: VARCHAR(100)
    nome            TEXT(100) NOT NULL,          -- PG: VARCHAR(100)
    telefono        TEXT(20),                    -- PG: VARCHAR(20) — era Double in Access 2025!
    comando_id      INTEGER,                     -- PG: INT FK → comandi.id
    email           TEXT(150),                   -- PG: VARCHAR(150) — per notifiche future
    attivo          YESNO DEFAULT TRUE,          -- PG: BOOLEAN
    note            MEMO                         -- PG: TEXT
);
-- Nota: qualifica e comando sono anche mantenuti come testo (campo calcolato / vista)
-- per semplicità in Access. In Postgres si useranno JOIN.


-- ── 6. UTENTI ───────────────────────────────────────────────
-- Gestione accessi al modulo (auth semplice, sostituibile con CAS/JWT)
-- PG: tipi identici
CREATE TABLE utenti (
    id              AUTOINCREMENT PRIMARY KEY,   -- PG: SERIAL
    username        TEXT(50) NOT NULL,           -- PG: VARCHAR(50) UNIQUE NOT NULL
    password_hash   TEXT(255) NOT NULL,          -- PG: VARCHAR(255) — bcrypt hash
    ruolo           TEXT(20) NOT NULL,           -- PG: VARCHAR(20) — 'admin'|'responsabile'|'dipendente'
    personale_id    INTEGER,                     -- PG: INT FK → personale.id (nullable per admin puri)
    comando_id      INTEGER,                     -- PG: INT FK → comandi.id (scope responsabile)
    attivo          YESNO DEFAULT TRUE,          -- PG: BOOLEAN
    ultimo_accesso  DATETIME                     -- PG: TIMESTAMP
);


-- ── 7. FUNZIONI_SERVIZIO ────────────────────────────────────
-- Lookup ruoli/funzioni nei servizi AIB (erano stringhe libere)
-- PG: id SERIAL, codice VARCHAR(30) UNIQUE, descrizione VARCHAR(100)
CREATE TABLE funzioni_servizio (
    id          AUTOINCREMENT PRIMARY KEY,   -- PG: SERIAL
    codice      TEXT(30) NOT NULL,           -- PG: VARCHAR(30) UNIQUE NOT NULL
    descrizione TEXT(100)                    -- PG: VARCHAR(100)
);
-- Seed dal DB 2025: ADDETTO, AUTISTA DOS, FUNZIONARIO, TAS 2


-- ── 8. PRESENZE ─────────────────────────────────────────────
-- Tabella principale. Ogni riga = un turno (programmato o consuntivato).
-- Aggiunta colonna stato per gestire il flusso pianificazione→consuntivo.
-- PG: tipi identici salvo AUTOINCREMENT→SERIAL, YESNO→BOOLEAN, MEMO→TEXT
CREATE TABLE presenze (
    id              AUTOINCREMENT PRIMARY KEY,   -- PG: SERIAL
    campagna_id     INTEGER NOT NULL,            -- PG: INT FK → campagne_aib.id
    personale_id    INTEGER NOT NULL,            -- PG: INT FK → personale.id
    postazione_id   INTEGER NOT NULL,            -- PG: INT FK → postazioni.id
    funzione_id     INTEGER NOT NULL,            -- PG: INT FK → funzioni_servizio.id
    data_servizio   DATETIME NOT NULL,           -- PG: DATE
    orario_inizio   TEXT(5) NOT NULL,            -- PG: TIME — es. "08:00"
    orario_fine     TEXT(5) NOT NULL,            -- PG: TIME — es. "20:00"
    ore_totali      DOUBLE,                      -- PG: NUMERIC(4,1) — calcolato o inserito
    stato           TEXT(20) DEFAULT 'programmato', -- PG: VARCHAR(20)
                                                 -- valori: programmato | confermato | modificato | assente
    note_consuntivo MEMO,                        -- PG: TEXT — variazioni rispetto al programmato
    creato_da       INTEGER,                     -- PG: INT FK → utenti.id
    creato_il       DATETIME DEFAULT NOW(),      -- PG: TIMESTAMP DEFAULT NOW()
    modificato_il   DATETIME                     -- PG: TIMESTAMP
);

-- ── INDICI consigliati (Access supporta indici su singolo campo) ──────────
-- CREATE INDEX idx_presenze_personale ON presenze (personale_id);
-- CREATE INDEX idx_presenze_data ON presenze (data_servizio);
-- CREATE INDEX idx_presenze_campagna ON presenze (campagna_id);
-- CREATE INDEX idx_presenze_stato ON presenze (stato);

-- ============================================================
-- NOTE MIGRAZIONE → PostgreSQL
-- ============================================================
-- 1. AUTOINCREMENT → SERIAL (o BIGSERIAL per sicurezza)
-- 2. YESNO → BOOLEAN
-- 3. MEMO → TEXT
-- 4. DATETIME → DATE o TIMESTAMP a seconda del campo
-- 5. TEXT(n) → VARCHAR(n)
-- 6. DOUBLE → NUMERIC(4,1)
-- 7. DEFAULT NOW() → DEFAULT NOW() (identico)
-- 8. Aggiungere vincoli FOREIGN KEY espliciti (Access li gestisce
--    solo tramite relazioni grafiche, non SQL)
-- 9. Aggiungere UNIQUE constraints sui codici lookup
-- ============================================================
