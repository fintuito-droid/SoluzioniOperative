"""Router FastAPI per gli endpoint del modulo ProtocolloMonitor."""

from __future__ import annotations

import subprocess
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse


router = APIRouter()


def get_protocollo_service() -> Any:
    """Dipendenza FastAPI per ottenere `ProtocolloService`."""

    from backend.core.dependency_container import DependencyContainer

    return DependencyContainer().get_protocollo_service()


def get_documento_service() -> Any:
    """Dipendenza FastAPI per ottenere `DocumentoService`."""

    from backend.core.dependency_container import DependencyContainer

    return DependencyContainer().get_documento_service()


def get_metadata_service() -> Any:
    """Dipendenza FastAPI per ottenere `MetadataService`."""

    from backend.core.dependency_container import DependencyContainer

    return DependencyContainer().get_metadata_service()


def _resolve_pdf_path_or_404(id_protocollo: int, documento_service: Any):
    """Recupera e risolve il path PDF, sollevando 404 coerenti.

    La funzione mantiene separati i casi:
    - protocollo inesistente;
    - protocollo presente ma senza PDF;
    - path presente in Access ma file fisico mancante/non valido.
    """

    percorso_pdf = documento_service.get_pdf_path(id_protocollo)

    if percorso_pdf is None:
        raise HTTPException(status_code=404, detail="Protocollo non trovato")

    if not percorso_pdf:
        raise HTTPException(status_code=404, detail="PDF non disponibile")

    from backend.services.document_path_service import resolve_document_path

    resolved_pdf_path = resolve_document_path(percorso_pdf)

    if resolved_pdf_path is None:
        raise HTTPException(
            status_code=404,
            detail="File PDF non trovato",
        )

    return resolved_pdf_path


# ======================================================================================
# ROTTA PRINCIPALE: PROTOCOLLI ACQUISITI
# ======================================================================================

@router.get("/protocollo-monitor/protocolli")
def get_protocolli(protocollo_service: Any = Depends(get_protocollo_service)):
    return protocollo_service.list_protocolli()


# ======================================================================================
# APERTURA PDF CON PROGRAMMA PREDEFINITO DI WINDOWS
# ======================================================================================

@router.get("/protocollo-monitor/protocolli/{id_protocollo}/apri-pdf")
def apri_pdf(
    id_protocollo: int,
    documento_service: Any = Depends(get_documento_service),
):

    resolved_pdf_path = _resolve_pdf_path_or_404(id_protocollo, documento_service)

    subprocess.Popen(
        [
            "cmd",
            "/c",
            "start",
            "/max",
            "",
            str(resolved_pdf_path)
        ],
        shell=True
    )

    return {"success": True}


# ======================================================================================
# DETTAGLIO PROTOCOLLO
# ======================================================================================

@router.get("/protocollo-monitor/protocolli/{id_protocollo}")
def get_protocollo_dettaglio(
    id_protocollo: int,
    protocollo_service: Any = Depends(get_protocollo_service),
):
    return protocollo_service.get_protocollo_detail(id_protocollo)


# ======================================================================================
# METADATI PROTOCOLLO
# ======================================================================================

@router.get("/protocollo-monitor/protocolli/{id_protocollo}/metadata")
def get_protocollo_metadata(
    id_protocollo: int,
    metadata_service: Any = Depends(get_metadata_service),
):
    metadata = metadata_service.get_metadata(id_protocollo)

    if metadata is None:
        raise HTTPException(status_code=404, detail="Protocollo non trovato")

    return metadata


# ======================================================================================
# VISUALIZZAZIONE PDF INLINE NEL BROWSER
# ======================================================================================

@router.get("/protocollo-monitor/protocolli/{id_protocollo}/pdf")
def apri_pdf_protocollo(
    id_protocollo: int,
    documento_service: Any = Depends(get_documento_service),
):

    resolved_pdf_path = _resolve_pdf_path_or_404(id_protocollo, documento_service)

    return FileResponse(
        str(resolved_pdf_path),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'inline; filename="{resolved_pdf_path.name}"'
        }
    )
