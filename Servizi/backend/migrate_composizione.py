"""
migrate_composizione.py — Migrazione schema composizione postazioni
===================================================================
Eseguire UNA SOLA VOLTA sul DB Access prima di avviare il backend aggiornato.

Aggiunge a `postazioni`:
  - turni_multipli    BIT      (SOUR=True, SOR=False)
  - slot_funzionario  INTEGER  (SOUR=1, SOR=0)
  - slot_tas2         INTEGER  (SOUR=1, SOR=0)
  - slot_addetto      INTEGER  (SOUR=0, SOR=1)

Aggiunge a `presenze`:
  - fascia_oraria     VARCHAR(1)  ('U'=unico, 'M'=mattina, 'P'=pomeriggio)

Le presenze storiche (AIB 2025) mantengono fascia_oraria=NULL:
la UI la deriva automaticamente dagli orari.
"""

import os
import pyodbc

DB_PATH = os.environ.get("ACCESS_DB_PATH", r"C:\SoluzioniOperative\aib2026.accdb")
CONN_STR = f"Driver={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={DB_PATH};"

conn = pyodbc.connect(CONN_STR)
cur = conn.cursor()

# ── DDL: nuove colonne ────────────────────────────────────────────────────────
ddl_ops = [
    ("postazioni.turni_multipli",   "ALTER TABLE postazioni ADD COLUMN turni_multipli BIT"),
    ("postazioni.slot_funzionario", "ALTER TABLE postazioni ADD COLUMN slot_funzionario INTEGER"),
    ("postazioni.slot_tas2",        "ALTER TABLE postazioni ADD COLUMN slot_tas2 INTEGER"),
    ("postazioni.slot_addetto",     "ALTER TABLE postazioni ADD COLUMN slot_addetto INTEGER"),
    ("presenze.fascia_oraria",      "ALTER TABLE presenze ADD COLUMN fascia_oraria VARCHAR(1)"),
]

for label, ddl in ddl_ops:
    try:
        cur.execute(ddl)
        print(f"ADD COLUMN OK:     {label}")
    except Exception as ex:
        msg = str(ex)
        # HY000 = errore generico Access — colonna già esistente è il caso più comune
        print(f"ADD COLUMN SKIP:   {label} — {msg[:80]}")

conn.commit()
conn.close()

# ── DML: valorizzazione regole composizione ───────────────────────────────────
# Riapri connessione dopo commit DDL (requisito Access via pyodbc)
conn = pyodbc.connect(CONN_STR)
cur = conn.cursor()

updates = [
    ("SOR",
     "UPDATE postazioni SET turni_multipli=False, slot_funzionario=0, slot_tas2=0, slot_addetto=1 "
     "WHERE codice='SOR'"),
    ("SOUR",
     "UPDATE postazioni SET turni_multipli=True,  slot_funzionario=1, slot_tas2=1, slot_addetto=0 "
     "WHERE codice='SOUR'"),
]

for label, sql in updates:
    try:
        cur.execute(sql)
        print(f"UPDATE OK:         postazione {label}")
    except Exception as ex:
        print(f"UPDATE FAIL:       postazione {label} — {str(ex)[:80]}")

conn.commit()

# Verifica
rows = cur.execute(
    "SELECT codice, turni_multipli, slot_funzionario, slot_tas2, slot_addetto "
    "FROM postazioni ORDER BY codice"
).fetchall()
print("\nStato postazioni dopo migrazione:")
for r in rows:
    print(f"  {r[0]:10s}  turni_multipli={r[1]}  funz={r[2]}  tas2={r[3]}  add={r[4]}")

conn.close()
print("\nMigrazione completata.")
