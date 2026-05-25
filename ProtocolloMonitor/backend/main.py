# ======================================================================================
# ProtocolloMonitor - Backend FastAPI
# ======================================================================================

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import subprocess
import os


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
# METADATI PROTOCOLLO
# ======================================================================================

@app.get("/protocollo-monitor/protocolli/{id_protocollo}/metadata")
def get_protocollo_metadata(id_protocollo: int):

    from backend.core.dependency_container import DependencyContainer

    container = DependencyContainer()
    metadata_service = container.get_metadata_service()

    metadata = metadata_service.get_metadata(id_protocollo)

    if metadata is None:
        raise HTTPException(status_code=404, detail="Protocollo non trovato")

    return metadata


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

    from backend.services.document_path_service import resolve_document_path

    resolved_pdf_path = resolve_document_path(percorso_pdf)

    if resolved_pdf_path is None:
        raise HTTPException(
            status_code=404,
            detail="File PDF non trovato",
        )

    return FileResponse(
        str(resolved_pdf_path),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'inline; filename="{resolved_pdf_path.name}"'
        }
    )
