# ======================================================================================
# ProtocolloMonitor - Backend FastAPI
# ======================================================================================

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import subprocess
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

    from backend.core.dependency_container import DependencyContainer

    container = DependencyContainer()
    protocollo_service = container.get_protocollo_service()

    return protocollo_service.list_protocolli()


# ======================================================================================
# APERTURA PDF CON PROGRAMMA PREDEFINITO DI WINDOWS
# ======================================================================================

@app.get("/protocollo-monitor/protocolli/{id_protocollo}/apri-pdf")
def apri_pdf(id_protocollo: int):

    from backend.core.dependency_container import DependencyContainer

    container = DependencyContainer()
    documento_service = container.get_documento_service()
    percorso_pdf = documento_service.get_pdf_path(id_protocollo)

    if percorso_pdf is None:
        return {"errore": "Protocollo non trovato"}

    if not percorso_pdf or not os.path.exists(percorso_pdf):
        raise HTTPException(status_code=404, detail="PDF non trovato")

    subprocess.Popen(
        [
            "cmd",
            "/c",
            "start",
            "/max",
            "",
            percorso_pdf
        ],
        shell=True
    )

    return {"success": True}


# ======================================================================================
# DETTAGLIO PROTOCOLLO
# ======================================================================================

@app.get("/protocollo-monitor/protocolli/{id_protocollo}")
def get_protocollo_dettaglio(id_protocollo: int):

    from backend.core.dependency_container import DependencyContainer

    container = DependencyContainer()
    protocollo_service = container.get_protocollo_service()

    return protocollo_service.get_protocollo_detail(id_protocollo)


# ======================================================================================
# VISUALIZZAZIONE PDF INLINE NEL BROWSER
# ======================================================================================

@app.get("/protocollo-monitor/protocolli/{id_protocollo}/pdf")
def apri_pdf_protocollo(id_protocollo: int):

    from backend.core.dependency_container import DependencyContainer

    container = DependencyContainer()
    documento_service = container.get_documento_service()

    percorso_pdf = documento_service.get_pdf_path(id_protocollo)

    if percorso_pdf is None:
        return {"errore": "Protocollo non trovato"}

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
