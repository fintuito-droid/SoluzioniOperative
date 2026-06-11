"""
migrate_orari.py
================
Normalizza gli orari nelle presenze esistenti: `8:00` -> `08:00`.
Idempotente: rilancia senza effetti collaterali.

  python migrate_orari.py
"""

import pyodbc
import os

DB_PATH = os.getenv("ACCESS_DB_PATH", r"C:\SoluzioniOperative\aib2026.accdb")
CONN_STR = (
    r"DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};"
    f"DBQ={DB_PATH};"
)


def normalizza(orario):
    """'8:00' -> '08:00'; valori già corretti o nulli restano invariati."""
    if not orario or ":" not in orario:
        return orario
    h, m = orario.split(":", 1)
    return f"{int(h):02d}:{m[:2]}"


def run():
    conn = pyodbc.connect(CONN_STR)
    cur  = conn.cursor()

    rows = cur.execute(
        "SELECT id, orario_inizio, orario_fine FROM presenze"
    ).fetchall()

    aggiornate = 0
    for r in rows:
        ni = normalizza(r.orario_inizio)
        nf = normalizza(r.orario_fine)
        if ni != r.orario_inizio or nf != r.orario_fine:
            cur.execute(
                "UPDATE presenze SET orario_inizio=?, orario_fine=? WHERE id=?",
                (ni, nf, r.id)
            )
            aggiornate += 1

    conn.commit()
    conn.close()
    print(f"Presenze esaminate: {len(rows)} — normalizzate: {aggiornate}")
    print("Migrazione completata.")


if __name__ == "__main__":
    run()
