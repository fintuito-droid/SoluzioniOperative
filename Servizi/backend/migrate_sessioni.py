"""
migrate_sessioni.py
===================
Crea la tabella `sessioni` per la persistenza dei token di login.
I login sopravvivono ai riavvii del backend; ogni token ha una scadenza.

  python migrate_sessioni.py
"""

import pyodbc
import os

DB_PATH = os.getenv("ACCESS_DB_PATH", r"C:\SoluzioniOperative\aib2026.accdb")
CONN_STR = (
    r"DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};"
    f"DBQ={DB_PATH};"
)


def run():
    conn = pyodbc.connect(CONN_STR)
    cur  = conn.cursor()

    tables = [r.table_name for r in cur.tables(tableType="TABLE")]

    if "sessioni" not in tables:
        cur.execute(
            "CREATE TABLE sessioni ("
            "  [id]        COUNTER PRIMARY KEY, "
            "  [token]     VARCHAR(64) NOT NULL, "
            "  [utente_id] INTEGER NOT NULL, "
            "  [scadenza]  DATETIME NOT NULL, "
            "  [creato_il] DATETIME"
            ")"
        )
        conn.commit()
        print("Tabella 'sessioni' creata.")
    else:
        print("Tabella 'sessioni' già esistente — skip.")

    conn.close()
    print("Migrazione completata.")


if __name__ == "__main__":
    run()
