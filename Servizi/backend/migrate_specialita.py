"""
migrate_specialita.py
=====================
Crea le tabelle `specialita` e `personale_specialita` nel DB Access.
Eseguire una sola volta prima di avviare il backend aggiornato.

  python migrate_specialita.py
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

    # ── 1. Tabella specialita ────────────────────────────────────────────────
    tables = [r.table_name for r in cur.tables(tableType="TABLE")]

    if "specialita" not in tables:
        cur.execute(
            "CREATE TABLE specialita ("
            "  [id]          COUNTER PRIMARY KEY, "
            "  [codice]      VARCHAR(30) NOT NULL, "
            "  [descrizione] VARCHAR(100)"
            ")"
        )
        conn.commit()
        print("Tabella 'specialita' creata.")
    else:
        print("Tabella 'specialita' già esistente — skip.")

    # ── 2. Tabella personale_specialita ──────────────────────────────────────
    if "personale_specialita" not in tables:
        cur.execute(
            "CREATE TABLE personale_specialita ("
            "  [id]           COUNTER PRIMARY KEY, "
            "  [personale_id] INTEGER NOT NULL, "
            "  [specialita_id] INTEGER NOT NULL"
            ")"
        )
        conn.commit()
        print("Tabella 'personale_specialita' creata.")
    else:
        print("Tabella 'personale_specialita' già esistente — skip.")

    # Riapre connessione per DDL commit (Access richiede)
    conn.close()
    conn = pyodbc.connect(CONN_STR)
    cur  = conn.cursor()

    # ── 3. Voci predefinite ──────────────────────────────────────────────────
    existing = [r[0] for r in cur.execute("SELECT codice FROM specialita").fetchall()]

    voci = [
        ("TAS 1",  "Tecnico Abilitato Specialista livello 1"),
        ("TAS 2",  "Tecnico Abilitato Specialista livello 2"),
        ("NBCR 1", "Nucleare Biologico Chimico Radiologico livello 1"),
        ("NBCR 2", "Nucleare Biologico Chimico Radiologico livello 2"),
        ("SAPR",   "Sistemi Aeromobili a Pilotaggio Remoto"),
        ("DOS",    "Direttore delle Operazioni di Spegnimento"),
        ("USAR L", "Urban Search and Rescue - Light"),
        ("USAR M", "Urban Search and Rescue - Medium"),
        ("USAR H", "Urban Search and Rescue - Heavy"),
    ]

    inseriti = 0
    for codice, descrizione in voci:
        if codice not in existing:
            cur.execute(
                "INSERT INTO specialita ([codice],[descrizione]) VALUES (?,?)",
                (codice, descrizione)
            )
            inseriti += 1

    conn.commit()
    conn.close()

    if inseriti:
        print(f"Inserite {inseriti} specialità predefinite.")
    else:
        print("Specialità predefinite già presenti — skip.")

    print("\nMigrazione completata.")


if __name__ == "__main__":
    run()
