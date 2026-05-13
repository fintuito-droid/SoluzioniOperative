# ======================================================================================
# ProtocolloMonitor - Backend FastAPI
# ======================================================================================

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

import pyodbc
import os
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
# ======================================================================================

DB_PATH = r"G:\ProtocolloMonitor.accdb"


# ======================================================================================
# CONNESSIONE ACCESS
# ======================================================================================

def get_connection():
    conn_str = (
        r"DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};"
        rf"DBQ={DB_PATH};"
    )

    return pyodbc.connect(conn_str)


# ======================================================================================
# NORMALIZZAZIONE VALORI JSON
# ======================================================================================

def normalizza_valore(value):
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

    conn = get_connection()
    cursor = conn.cursor()

    sql = """
        SELECT
            IDProtocollo,
            NumeroProtocollo,
            DataProtocollo,
            Oggetto,
            Modalita,
            ComandoMittente,
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
            "comando_mittente": normalizza_valore(row.ComandoMittente),
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


# ======================================================================================
# APERTURA PDF CON PROGRAMMA PREDEFINITO DI WINDOWS
# ======================================================================================

@app.get("/protocollo-monitor/protocolli/{id_protocollo}/apri-pdf")
def apri_pdf(id_protocollo: int):

    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT PercorsoDocumentoProtocollato
        FROM T_Protocolli
        WHERE IDProtocollo = ?
    """

    row = cursor.execute(query, (id_protocollo,)).fetchone()

    cursor.close()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Protocollo non trovato")

    percorso_pdf = row[0]

    if not percorso_pdf or not os.path.exists(percorso_pdf):
        raise HTTPException(status_code=404, detail="PDF non trovato")

    os.startfile(percorso_pdf)

    return {"success": True}


# ======================================================================================
# DETTAGLIO PROTOCOLLO
# ======================================================================================

@app.get("/protocollo-monitor/protocolli/{id_protocollo}")
def get_protocollo_dettaglio(id_protocollo: int):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM T_Protocolli
        WHERE IDProtocollo = ?
    """, id_protocollo)

    row = cursor.fetchone()

    if not row:
        cursor.close()
        conn.close()

        return {
            "protocollo": None,
            "assegnazioni": [],
            "destinatari": [],
            "firmatari": []
        }

    colonne = [column[0] for column in cursor.description]
    protocollo = dict(zip(colonne, row))

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

    cursor.close()
    conn.close()

    return {
        "protocollo": protocollo,
        "assegnazioni": assegnazioni,
        "destinatari": destinatari,
        "firmatari": firmatari
    }


# ======================================================================================
# VISUALIZZAZIONE PDF INLINE NEL BROWSER
# ======================================================================================

@app.get("/protocollo-monitor/protocolli/{id_protocollo}/pdf")
def apri_pdf_protocollo(id_protocollo: int):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT PercorsoDocumentoProtocollato
        FROM T_Protocolli
        WHERE IDProtocollo = ?
    """, (id_protocollo,))

    row = cur.fetchone()

    cur.close()
    conn.close()

    if not row:
        return {"errore": "Protocollo non trovato"}

    percorso_pdf = row.PercorsoDocumentoProtocollato

    if not percorso_pdf:
        return {"errore": "PDF non disponibile"}

    if not os.path.exists(percorso_pdf):
        return {"errore": "File PDF non trovato"}

    return FileResponse(
        percorso_pdf,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'inline; filename="{os.path.basename(percorso_pdf)}"'
        }
    )