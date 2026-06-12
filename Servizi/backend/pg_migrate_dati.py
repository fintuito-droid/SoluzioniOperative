"""
pg_migrate_dati.py — Travaso dati Access → PostgreSQL
======================================================
Copia tutte le tabelle dal DB Access (aib2026.accdb) al database PostgreSQL
`aib2026`, preservando gli ID originali e riallineando le sequenze.

- Ordine di copia rispettoso delle FOREIGN KEY
- `ore_totali` arrotondato a 2 decimali (ripulisce il floating point sporco)
- Sicurezza: se il PG di destinazione contiene già dati si ferma;
  rilanciare con --reset per svuotarlo e ricopiare da zero

  python pg_migrate_dati.py [--reset]
"""

import os
import sys
import pyodbc
import psycopg2

ACCESS_PATH = os.getenv("ACCESS_DB_PATH", r"C:\SoluzioniOperative\aib2026.accdb")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:1234@localhost:5432/aib2026")

# Ordine di copia: prima le tabelle referenziate, poi quelle che le puntano
TABELLE = [
    "qualifiche",
    "comandi",
    "campagne_aib",
    "postazioni",
    "specialita",
    "funzioni_servizio",
    "personale",
    "utenti",
    "personale_specialita",
    "presenze",
    "sessioni",
    "utenti_moduli",
    "report_templates",
]


def run(reset: bool = False):
    acc = pyodbc.connect(
        r"DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};"
        rf"DBQ={ACCESS_PATH};ReadOnly=1;"
    )
    pg = psycopg2.connect(DATABASE_URL)
    pg_cur = pg.cursor()

    # ── Sicurezza: destinazione vuota o reset esplicito ──────────────────────
    pg_cur.execute("SELECT COALESCE(SUM(n_live_tup),0) FROM pg_stat_user_tables")
    occupate = pg_cur.fetchone()[0]
    if occupate and not reset:
        print("Il database PostgreSQL contiene già dati. Rilanciare con --reset "
              "per svuotarlo e ricopiare tutto da Access.")
        sys.exit(1)
    if reset:
        pg_cur.execute(
            "TRUNCATE " + ", ".join(reversed(TABELLE)) + " RESTART IDENTITY CASCADE"
        )
        print("Tabelle PostgreSQL svuotate (--reset).")

    # ── Copia tabella per tabella ─────────────────────────────────────────────
    for tabella in TABELLE:
        acc_cur = acc.cursor()
        acc_cur.execute(f"SELECT * FROM {tabella}")
        colonne = [c[0].lower() for c in acc_cur.description]
        righe = acc_cur.fetchall()

        if not righe:
            print(f"{tabella:22} 0 righe")
            continue

        idx_ore = colonne.index("ore_totali") if "ore_totali" in colonne else None

        valori = []
        for r in righe:
            r = list(r)
            if idx_ore is not None and r[idx_ore] is not None:
                r[idx_ore] = round(float(r[idx_ore]), 2)
            valori.append(tuple(r))

        col_sql = ", ".join(f'"{c}"' for c in colonne)
        ph = ", ".join(["%s"] * len(colonne))
        pg_cur.executemany(
            f'INSERT INTO {tabella} ({col_sql}) VALUES ({ph})', valori
        )

        # Riallinea la sequenza dell'id al massimo valore copiato
        if "id" in colonne:
            pg_cur.execute(
                f"SELECT setval(pg_get_serial_sequence('{tabella}','id'), "
                f"(SELECT MAX(id) FROM {tabella}))"
            )

        print(f"{tabella:22} {len(valori)} righe copiate")

    pg.commit()

    # ── Verifica conteggi ─────────────────────────────────────────────────────
    print("\nVerifica conteggi Access vs PostgreSQL:")
    errori = 0
    for tabella in TABELLE:
        n_acc = acc.cursor().execute(f"SELECT COUNT(*) FROM {tabella}").fetchone()[0]
        pg_cur.execute(f"SELECT COUNT(*) FROM {tabella}")
        n_pg = pg_cur.fetchone()[0]
        esito = "OK" if n_acc == n_pg else "DIVERSO!"
        if n_acc != n_pg:
            errori += 1
        print(f"  {tabella:22} access={n_acc:5}  pg={n_pg:5}  {esito}")

    acc.close()
    pg.close()

    if errori:
        print(f"\nATTENZIONE: {errori} tabelle con conteggi diversi.")
        sys.exit(1)
    print("\nTravaso completato senza differenze.")


if __name__ == "__main__":
    run(reset="--reset" in sys.argv)
