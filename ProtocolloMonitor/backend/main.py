# ======================================================================================
# ProtocolloMonitor - Backend FastAPI
# STEP 9.5
#
# SCOPO:
# Esporre tramite API web i protocolli già acquisiti da Vigilia/Grisù
# e salvati nella tabella Access T_Protocolli.
#
# ARCHITETTURA:
# Vue.js + Vuetify
#        ↓
# FastAPI
#        ↓
# Access ora / PostgreSQL domani
# ======================================================================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pyodbc
from datetime import datetime, date


# ======================================================================================
# CONFIGURAZIONE APPLICAZIONE FASTAPI
# ======================================================================================

app = FastAPI(
    title="ProtocolloMonitor API",
    version="0.1.0"
)


# ======================================================================================
# CORS
#
# Serve per permettere al frontend Vue, che gira su localhost:5173,
# di chiamare il backend FastAPI, che gira su localhost:8000.
# ======================================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ======================================================================================
# PERCORSO DATABASE ACCESS
#
# ATTENZIONE:
# Qui devi mettere il percorso reale del tuo ProtocolloMonitor.accdb.
#
# Se stai usando il percorso che avevamo memorizzato:
# D:\OneDrive\FunTecVVF\Sviluppo\SoluzioniOperative\BackEnd_Access\ProtocolloMonitor.accdb
#
# lascia così.
# ======================================================================================

DB_PATH = r"G:\ProtocolloMonitor.accdb"


# ======================================================================================
# FUNZIONE DI CONNESSIONE ACCESS
# ======================================================================================

def get_connection():
    """
    Apre una connessione ODBC verso il database Access.

    Nota:
    - Su Windows deve essere installato il driver Microsoft Access ODBC.
    - Il driver normalmente si chiama:
      Microsoft Access Driver (*.mdb, *.accdb)
    """

    conn_str = (
        r"DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};"
        rf"DBQ={DB_PATH};"
    )

    return pyodbc.connect(conn_str)


# ======================================================================================
# FUNZIONE DI CONVERSIONE DATE
# ======================================================================================

def normalizza_valore(value):
    """
    Converte i valori letti da Access in valori compatibili JSON.

    FastAPI restituisce JSON al frontend.
    Alcuni tipi Python, come datetime/date, vanno convertiti in stringhe.
    """

    if isinstance(value, datetime):
        return value.strftime("%d/%m/%Y %H:%M")

    if isinstance(value, date):
        return value.strftime("%d/%m/%Y")

    return value


# ======================================================================================
# ROTTA TEST
# ======================================================================================

@app.get("/")
def home():
    return {
        "app": "ProtocolloMonitor API",
        "status": "ok"
    }


# ======================================================================================
# ROTTA PRINCIPALE: PROTOCOLLI ACQUISITI
# ======================================================================================

@app.get("/protocollo-monitor/protocolli")
def get_protocolli():
    """
    Restituisce l'elenco dei protocolli acquisiti da Vigilia.

    Questa rotta sarà chiamata da Vue nella pagina:
    ProtocolliAcquisitiView.vue
    """

    conn = get_connection()
    cursor = conn.cursor()

    sql = """
        SELECT
            IDProtocollo,
            NumeroProtocollo,
            DataProtocollo,
            Oggetto,
            Modalita,
            DaLavorare,
            dataScadenza,
            TipologiaDocumento,
            priorita,
            note_interne
        FROM
            T_Protocolli
        ORDER BY
            IDProtocollo DESC
    """

    cursor.execute(sql)

    records = []

    for row in cursor.fetchall():

        record = {
            "id_protocollo": normalizza_valore(row.IDProtocollo),
            "numero_protocollo": normalizza_valore(row.NumeroProtocollo),
            "data_protocollo": normalizza_valore(row.DataProtocollo),
            "oggetto": normalizza_valore(row.Oggetto),
            "modalita": normalizza_valore(row.Modalita),
            "da_lavorare": bool(row.DaLavorare) if row.DaLavorare is not None else False,
            "data_scadenza": normalizza_valore(row.dataScadenza),
            "tipologia_documento": normalizza_valore(row.TipologiaDocumento),
            "priorita": normalizza_valore(row.priorita) or "Normale",
            "stato_pratica": "NUOVA",
            "note_interne": normalizza_valore(row.note_interne) or ""
        }

        records.append(record)

    cursor.close()
    conn.close()

    return records

@app.get("/protocollo-monitor/protocolli/{id_protocollo}")
def get_protocollo_dettaglio(id_protocollo: int):

    conn = get_connection()
    cursor = conn.cursor()

    # -----------------------------
    # PROTOCOLLO PRINCIPALE
    # -----------------------------
    cursor.execute("""
        SELECT *
        FROM T_Protocolli
        WHERE IDProtocollo = ?
    """, id_protocollo)

    row = cursor.fetchone()

    if not row:
        conn.close()
        return {
            "protocollo": None,
            "assegnazioni": [],
            "destinatari": [],
            "firmatari": []
        }

    colonne = [column[0] for column in cursor.description]
    protocollo = dict(zip(colonne, row))

    # -----------------------------
    # ASSEGNAZIONI
    # -----------------------------
    cursor.execute("""
        SELECT *
        FROM T_ProtocolloAssegnazioni
        WHERE IDProtocollo = ?
    """, id_protocollo)

    colonne = [column[0] for column in cursor.description]
    assegnazioni = [
        dict(zip(colonne, r))
        for r in cursor.fetchall()
    ]

    # -----------------------------
    # DESTINATARI / MITTENTI
    # -----------------------------
    cursor.execute("""
        SELECT *
        FROM T_ProtocolloDestinatari
        WHERE IDProtocollo = ?
    """, id_protocollo)

    colonne = [column[0] for column in cursor.description]
    destinatari = [
        dict(zip(colonne, r))
        for r in cursor.fetchall()
    ]

    # -----------------------------
    # FIRMATARI
    # -----------------------------
    cursor.execute("""
        SELECT *
        FROM T_ProtocolloFirmatari
        WHERE IDProtocollo = ?
    """, id_protocollo)

    colonne = [column[0] for column in cursor.description]
    firmatari = [
        dict(zip(colonne, r))
        for r in cursor.fetchall()
    ]

    conn.close()

    return {
        "protocollo": protocollo,
        "assegnazioni": assegnazioni,
        "destinatari": destinatari,
        "firmatari": firmatari
    }