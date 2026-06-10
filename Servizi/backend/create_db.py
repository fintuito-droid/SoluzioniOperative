"""Script one-shot: crea tabelle e seed nel DB Access."""
import pyodbc
import hashlib

def sha256(s):
    return hashlib.sha256(s.encode()).hexdigest()

conn = pyodbc.connect(
    r"Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=C:\SoluzioniOperative\aib2026.accdb;"
)
cur = conn.cursor()

ddls = [
    ("campagne_aib",
     "CREATE TABLE campagne_aib ([id] COUNTER PRIMARY KEY, [anno] INTEGER, "
     "[data_inizio] DATETIME, [data_fine] DATETIME, [descrizione] MEMO, [attiva] BIT)"),
    ("postazioni",
     "CREATE TABLE postazioni ([id] COUNTER PRIMARY KEY, [codice] VARCHAR(20), "
     "[nome] VARCHAR(100), [note] MEMO, [attiva] BIT)"),
    ("qualifiche",
     "CREATE TABLE qualifiche ([id] COUNTER PRIMARY KEY, [codice] VARCHAR(10), [descrizione] VARCHAR(100))"),
    ("comandi",
     "CREATE TABLE comandi ([id] COUNTER PRIMARY KEY, [codice] VARCHAR(20), [nome] VARCHAR(100), [attivo] BIT)"),
    ("personale",
     "CREATE TABLE personale ([id] COUNTER PRIMARY KEY, [matricola] VARCHAR(20), [qualifica_id] INTEGER, "
     "[cognome] VARCHAR(100), [nome] VARCHAR(100), [telefono] VARCHAR(20), [comando_id] INTEGER, "
     "[email] VARCHAR(150), [attivo] BIT, [note] MEMO)"),
    ("utenti",
     "CREATE TABLE utenti ([id] COUNTER PRIMARY KEY, [username] VARCHAR(50), "
     "[password_hash] VARCHAR(255), [ruolo] VARCHAR(20), [personale_id] INTEGER, "
     "[comando_id] INTEGER, [attivo] BIT, [ultimo_accesso] DATETIME)"),
    ("funzioni_servizio",
     "CREATE TABLE funzioni_servizio ([id] COUNTER PRIMARY KEY, [codice] VARCHAR(30), [descrizione] VARCHAR(100))"),
    ("presenze",
     "CREATE TABLE presenze ([id] COUNTER PRIMARY KEY, [campagna_id] INTEGER, "
     "[personale_id] INTEGER, [postazione_id] INTEGER, [funzione_id] INTEGER, "
     "[data_servizio] DATETIME, [orario_inizio] VARCHAR(5), [orario_fine] VARCHAR(5), "
     "[ore_totali] DOUBLE, [stato] VARCHAR(20), [note_consuntivo] MEMO, "
     "[creato_da] INTEGER, [creato_il] DATETIME, [modificato_il] DATETIME)"),
]

for name, ddl in ddls:
    try:
        cur.execute(ddl)
        print(f"OK: {name}")
    except Exception as ex:
        msg = str(ex)
        if "42S01" in msg:
            print(f"EXISTS: {name}")
        else:
            print(f"FAIL: {name} — {msg[:80]}")

conn.commit()
conn.close()

# Riapri connessione per i seed (Access richiede commit DDL prima di DML)
conn = pyodbc.connect(
    r"Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=C:\SoluzioniOperative\aib2026.accdb;"
)
cur = conn.cursor()

admin_hash = sha256("admin123")
seeds = [
    ("campagne_aib", "INSERT INTO campagne_aib ([anno],[data_inizio],[data_fine],[descrizione],[attiva]) VALUES (2026,{d '2026-06-15'},{d '2026-10-15'},'Campagna AIB 2026 Sicilia',True)"),
    ("comandi PA",   "INSERT INTO comandi ([codice],[nome],[attivo]) VALUES ('PALERMO','Comando Palermo',True)"),
    ("comandi DIR",  "INSERT INTO comandi ([codice],[nome],[attivo]) VALUES ('DIR-SIC','Direzione Sicilia',True)"),
    ("postazioni",   "INSERT INTO postazioni ([codice],[nome],[attiva]) VALUES ('SOUR','Sala Operativa Unificata Regionale',True)"),
    ("qualifica VF", "INSERT INTO qualifiche ([codice],[descrizione]) VALUES ('VF','Vigile del Fuoco')"),
    ("qualifica CS", "INSERT INTO qualifiche ([codice],[descrizione]) VALUES ('CS','Capo Squadra')"),
    ("funz ADDETTO", "INSERT INTO funzioni_servizio ([codice],[descrizione]) VALUES ('ADDETTO','Addetto')"),
    ("funz FUNZ",    "INSERT INTO funzioni_servizio ([codice],[descrizione]) VALUES ('FUNZIONARIO','Funzionario')"),
    ("utente admin", f"INSERT INTO utenti ([username],[password_hash],[ruolo],[attivo]) VALUES ('admin','{admin_hash}','admin',True)"),
]

for label, sql in seeds:
    try:
        cur.execute(sql)
        print(f"SEED OK: {label}")
    except Exception as ex:
        print(f"SEED SKIP: {label} — {str(ex)[:80]}")

conn.commit()
conn.close()
print("DB pronto.")
