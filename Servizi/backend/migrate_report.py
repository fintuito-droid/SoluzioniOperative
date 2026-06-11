"""
migrate_report.py
=================
Crea la tabella `report_templates` e inserisce 3 modelli predefiniti.
La definizione del report è JSON in campo Memo (LONGTEXT).

  python migrate_report.py
"""

import pyodbc
import os
import json

DB_PATH = os.getenv("ACCESS_DB_PATH", r"C:\SoluzioniOperative\aib2026.accdb")
CONN_STR = (
    r"DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};"
    f"DBQ={DB_PATH};"
)


def template_base(titolo, sorgente, colonne):
    """Modello di partenza: intestazione con titolo e linea, tabella, piè di pagina."""
    return {
        "pagina": {"formato": "A4", "orientamento": "portrait",
                   "margini": {"sx": 15, "dx": 15, "alto": 12, "basso": 12}},
        "intestazione": {
            "altezza": 28,
            "elementi": [
                {"tipo": "testo", "x": 0, "y": 2, "w": 180, "h": 8,
                 "testo": "SoluzioniOperative — Modulo Servizi AIB",
                 "font": {"size": 9, "bold": False, "italic": True, "colore": "#888888"},
                 "align": "left"},
                {"tipo": "testo", "x": 0, "y": 10, "w": 180, "h": 10,
                 "testo": titolo,
                 "font": {"size": 16, "bold": True, "italic": False, "colore": "#C0392B"},
                 "align": "left"},
                {"tipo": "campo", "x": 0, "y": 20, "w": 180, "h": 6, "campo": "sottotitolo",
                 "font": {"size": 9, "bold": False, "italic": False, "colore": "#444444"},
                 "align": "left"},
                {"tipo": "linea", "x": 0, "y": 27, "w": 180, "h": 0,
                 "font": {"colore": "#C0392B"}},
            ],
        },
        "pie": {
            "altezza": 12,
            "elementi": [
                {"tipo": "linea", "x": 0, "y": 1, "w": 180, "h": 0,
                 "font": {"colore": "#CCCCCC"}},
                {"tipo": "data", "x": 0, "y": 4, "w": 60, "h": 5,
                 "font": {"size": 8, "bold": False, "italic": False, "colore": "#888888"},
                 "align": "left"},
                {"tipo": "numpagina", "x": 120, "y": 4, "w": 60, "h": 5,
                 "font": {"size": 8, "bold": False, "italic": False, "colore": "#888888"},
                 "align": "right"},
            ],
        },
        "tabella": {
            "colonne": colonne,
            "stile": {"colore_header": "#C0392B", "testo_header": "#FFFFFF",
                      "zebra": True, "bordi": True, "font_size": 8},
        },
        "_sorgente": sorgente,
    }


MODELLI = [
    ("Presenze per postazione", "presenze", template_base(
        "Registro presenze", "presenze",
        [
            {"campo": "data_servizio", "etichetta": "Data",       "larghezza": 22, "align": "left",  "formato": "data"},
            {"campo": "nominativo",    "etichetta": "Dipendente", "larghezza": 48, "align": "left"},
            {"campo": "qualifica",     "etichetta": "Qual.",      "larghezza": 14, "align": "left"},
            {"campo": "funzione",      "etichetta": "Funzione",   "larghezza": 28, "align": "left"},
            {"campo": "orario_inizio", "etichetta": "Inizio",     "larghezza": 16, "align": "center"},
            {"campo": "orario_fine",   "etichetta": "Fine",       "larghezza": 16, "align": "center"},
            {"campo": "ore_totali",    "etichetta": "Ore",        "larghezza": 12, "align": "right"},
            {"campo": "stato",         "etichetta": "Stato",      "larghezza": 24, "align": "left"},
        ])),
    ("Monte ore per dipendente", "monte_ore", template_base(
        "Monte ore", "monte_ore",
        [
            {"campo": "cognome",      "etichetta": "Cognome",   "larghezza": 40, "align": "left"},
            {"campo": "nome",         "etichetta": "Nome",      "larghezza": 40, "align": "left"},
            {"campo": "qualifica",    "etichetta": "Qualifica", "larghezza": 22, "align": "left"},
            {"campo": "turni_totali", "etichetta": "Turni",     "larghezza": 18, "align": "right"},
            {"campo": "ore_totali",   "etichetta": "Ore totali","larghezza": 22, "align": "right"},
        ])),
    ("Riepilogo campagna", "riepilogo", template_base(
        "Riepilogo campagna", "riepilogo",
        [
            {"campo": "postazione",   "etichetta": "Postazione",   "larghezza": 60, "align": "left"},
            {"campo": "turni_totali", "etichetta": "Turni",        "larghezza": 30, "align": "right"},
            {"campo": "ore_totali",   "etichetta": "Ore totali",   "larghezza": 30, "align": "right"},
            {"campo": "dipendenti",   "etichetta": "Dipendenti",   "larghezza": 30, "align": "right"},
        ])),
]


def run():
    conn = pyodbc.connect(CONN_STR)
    cur  = conn.cursor()

    tables = [r.table_name for r in cur.tables(tableType="TABLE")]

    if "report_templates" not in tables:
        cur.execute(
            "CREATE TABLE report_templates ("
            "  [id]          COUNTER PRIMARY KEY, "
            "  [nome]        VARCHAR(100) NOT NULL, "
            "  [sorgente]    VARCHAR(20) NOT NULL, "
            "  [definizione] LONGTEXT, "
            "  [creato_da]   INTEGER, "
            "  [creato_il]   DATETIME, "
            "  [aggiornato_il] DATETIME"
            ")"
        )
        conn.commit()
        print("Tabella 'report_templates' creata.")
        conn.close()
        conn = pyodbc.connect(CONN_STR)
        cur  = conn.cursor()
    else:
        print("Tabella 'report_templates' già esistente — skip.")

    esistenti = [r[0] for r in cur.execute("SELECT nome FROM report_templates").fetchall()]
    from datetime import datetime
    inseriti = 0
    for nome, sorgente, definizione in MODELLI:
        if nome not in esistenti:
            cur.execute(
                "INSERT INTO report_templates ([nome],[sorgente],[definizione],[creato_il]) VALUES (?,?,?,?)",
                (nome, sorgente, json.dumps(definizione, ensure_ascii=False), datetime.now())
            )
            inseriti += 1
    conn.commit()
    conn.close()
    print(f"Modelli predefiniti inseriti: {inseriti}")
    print("Migrazione completata.")


if __name__ == "__main__":
    run()
