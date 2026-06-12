"""
migrate_moduli.py
=================
Crea la tabella `utenti_moduli` per le abilitazioni ai moduli della
piattaforma SoluzioniOperative (un record per utente/modulo abilitato).

Gli admin NON hanno record: sono abilitati a tutti i moduli implicitamente.
Seed iniziale: gli utenti attivi non-admin vengono abilitati a 'servizi'
(sono nati come utenti del modulo Servizi).

Nota nomi: 'codice_modulo' e non 'modulo' per stare lontani dalla parola
riservata Access MODULE. Schema PG-compatibile (COUNTER -> SERIAL).

  python migrate_moduli.py
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

    if "utenti_moduli" not in tables:
        cur.execute(
            "CREATE TABLE utenti_moduli ("
            "  [id]            COUNTER PRIMARY KEY, "
            "  [utente_id]     INTEGER NOT NULL, "
            "  [codice_modulo] VARCHAR(50) NOT NULL"
            ")"
        )
        conn.commit()
        print("Tabella 'utenti_moduli' creata.")

        # Dopo DDL: riapertura connessione prima del DML (vincolo Access)
        conn.close()
        conn = pyodbc.connect(CONN_STR)
        cur  = conn.cursor()

        # Seed: utenti attivi non-admin -> abilitati a 'servizi'
        cur.execute("SELECT id, username FROM utenti WHERE attivo=True AND ruolo<>'admin'")
        utenti = cur.fetchall()
        for u in utenti:
            cur.execute(
                "INSERT INTO utenti_moduli ([utente_id],[codice_modulo]) VALUES (?,?)",
                (u.id, "servizi")
            )
            print(f"  abilitato 'servizi' per utente {u.username} (id={u.id})")
        conn.commit()
    else:
        print("Tabella 'utenti_moduli' già esistente — skip.")

    conn.close()
    print("Migrazione completata.")


if __name__ == "__main__":
    run()
