"""Router FastAPI per gli endpoint del modulo ProtocolloMonitor."""

from __future__ import annotations

import mimetypes
import subprocess
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from backend.core.dependency_container import DependencyContainer, create_container
from backend.services.procedimento_service import (
    ProcedimentoNotFoundError,
    ProcedimentoProtocolloLinkAlreadyExistsError,
    ProtocolloNotFoundError,
)


router = APIRouter()


class ProtocolloProcedimentoLinkPayload(BaseModel):
    """Payload opzionale per collegare protocollo e procedimento."""

    RuoloProtocollo: str | None = "COLLEGATO"
    Principale: bool = False
    NoteCollegamento: str | None = None


def get_container() -> DependencyContainer:
    """Dipendenza FastAPI per creare il container della richiesta."""

    return create_container()


def get_protocollo_service(
    container: DependencyContainer = Depends(get_container),
) -> Any:
    """Dipendenza FastAPI per ottenere `ProtocolloService`."""

    return container.get_protocollo_service()


def get_documento_service(
    container: DependencyContainer = Depends(get_container),
) -> Any:
    """Dipendenza FastAPI per ottenere `DocumentoService`."""

    return container.get_documento_service()


def get_metadata_service(
    container: DependencyContainer = Depends(get_container),
) -> Any:
    """Dipendenza FastAPI per ottenere `MetadataService`."""

    return container.get_metadata_service()


def get_procedimento_service(
    container: DependencyContainer = Depends(get_container),
) -> Any:
    """Dipendenza FastAPI per ottenere `ProcedimentoService`."""

    return container.get_procedimento_service()


def get_workflow_procedimento_service(
    container: DependencyContainer = Depends(get_container),
) -> Any:
    """Dipendenza FastAPI per ottenere `WorkflowProcedimentoService`."""

    return container.get_workflow_procedimento_service()


def get_sottofase_documentale_service(
    container: DependencyContainer = Depends(get_container),
) -> Any:
    """Dipendenza FastAPI per ottenere `SottofaseDocumentaleService`."""

    return container.get_sottofase_documentale_service()


def get_sottofase_workflow_service(
    container: DependencyContainer = Depends(get_container),
) -> Any:
    """Dipendenza FastAPI per ottenere `SottofaseWorkflowService`."""

    return container.get_sottofase_workflow_service()


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


def _resolve_sottofase_documento_path_or_404(
    id_documento: int,
    sottofase_service: Any,
):
    """Recupera un documento sottofase e risolve il path fisico.

    La funzione resta read-only: legge il record documentale, controlla il path
    e restituisce un file esistente. Non apre programmi locali, non scrive su
    Access e non modifica il filesystem.
    """

    try:
        documento = sottofase_service.get_documento_by_id(id_documento)

        if documento is None:
            raise HTTPException(status_code=404, detail="Documento non trovato")

        percorso_documento = documento.get("percorso_documento")

        if not percorso_documento:
            raise HTTPException(
                status_code=404,
                detail="Documento non disponibile",
            )

        from backend.services.document_path_service import resolve_document_path

        resolved_document_path = resolve_document_path(percorso_documento)

        if resolved_document_path is None:
            raise HTTPException(
                status_code=404,
                detail="File documento non trovato",
            )

        return documento, resolved_document_path
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Errore durante apertura documento",
        )


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
# PROCEDIMENTI COLLEGATI AL PROTOCOLLO
# ======================================================================================

@router.get("/protocollo-monitor/protocolli/{id_protocollo}/procedimenti")
def get_procedimenti_by_protocollo(
    id_protocollo: int,
    procedimento_service: Any = Depends(get_procedimento_service),
):
    try:
        return procedimento_service.list_procedimenti_by_protocollo_id(id_protocollo)
    except ProtocolloNotFoundError:
        raise HTTPException(status_code=404, detail="Protocollo non trovato")


@router.post(
    "/protocollo-monitor/protocolli/{id_protocollo}/procedimenti/{id_procedimento}",
    status_code=201,
)
def collega_protocollo_a_procedimento(
    id_protocollo: int,
    id_procedimento: int,
    payload: ProtocolloProcedimentoLinkPayload | None = None,
    procedimento_service: Any = Depends(get_procedimento_service),
):
    payload = payload or ProtocolloProcedimentoLinkPayload()

    try:
        return procedimento_service.link_protocollo_to_procedimento(
            id_protocollo=id_protocollo,
            id_procedimento=id_procedimento,
            ruolo_protocollo=payload.RuoloProtocollo,
            principale=payload.Principale,
            note_collegamento=payload.NoteCollegamento,
        )
    except ProtocolloNotFoundError:
        raise HTTPException(status_code=404, detail="Protocollo non trovato")
    except ProcedimentoNotFoundError:
        raise HTTPException(status_code=404, detail="Procedimento non trovato")
    except ProcedimentoProtocolloLinkAlreadyExistsError:
        raise HTTPException(
            status_code=409,
            detail="Protocollo gia collegato al procedimento",
        )


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


# ======================================================================================
# PROCEDIMENTI - ENDPOINT READ-ONLY
# ======================================================================================

@router.get("/protocollo-monitor/procedimenti")
def get_procedimenti(
    procedimento_service: Any = Depends(get_procedimento_service),
):
    return procedimento_service.list_procedimenti()


@router.get("/protocollo-monitor/procedimenti/{id_procedimento}")
def get_procedimento_dettaglio(
    id_procedimento: int,
    procedimento_service: Any = Depends(get_procedimento_service),
):
    procedimento = procedimento_service.get_procedimento_detail(id_procedimento)

    if procedimento is None:
        raise HTTPException(status_code=404, detail="Procedimento non trovato")

    return procedimento


@router.get("/protocollo-monitor/procedimenti/{id_procedimento}/protocolli")
def get_procedimento_protocolli(
    id_procedimento: int,
    procedimento_service: Any = Depends(get_procedimento_service),
):
    procedimento = procedimento_service.get_procedimento_detail(id_procedimento)

    if procedimento is None:
        raise HTTPException(status_code=404, detail="Procedimento non trovato")

    return procedimento_service.list_protocolli_collegati(id_procedimento)


@router.get("/protocollo-monitor/procedimenti/{id_procedimento}/protocolli/count")
def get_procedimento_protocolli_count(
    id_procedimento: int,
    procedimento_service: Any = Depends(get_procedimento_service),
):
    procedimento = procedimento_service.get_procedimento_detail(id_procedimento)

    if procedimento is None:
        raise HTTPException(status_code=404, detail="Procedimento non trovato")

    return {
        "id_procedimento": id_procedimento,
        "protocolli_collegati": procedimento_service.count_protocolli_collegati(
            id_procedimento
        ),
    }


# ======================================================================================
# WORKFLOW PROCEDIMENTO - ENDPOINT READ-ONLY
# ======================================================================================

@router.get("/protocollo-monitor/procedimenti/{id_procedimento}/fasi")
def get_procedimento_fasi(
    id_procedimento: int,
    workflow_service: Any = Depends(get_workflow_procedimento_service),
):
    return workflow_service.list_fasi_by_procedimento(id_procedimento)


@router.get("/protocollo-monitor/procedimenti/fasi/{id_fase}")
def get_procedimento_fase_dettaglio(
    id_fase: int,
    workflow_service: Any = Depends(get_workflow_procedimento_service),
):
    fase = workflow_service.get_fase_detail(id_fase)

    if fase is None:
        raise HTTPException(status_code=404, detail="Fase non trovata")

    return fase


@router.get("/protocollo-monitor/procedimenti/fasi/{id_fase}/sottofasi")
def get_procedimento_fase_sottofasi(
    id_fase: int,
    workflow_service: Any = Depends(get_workflow_procedimento_service),
):
    fase = workflow_service.get_fase_detail(id_fase)

    if fase is None:
        raise HTTPException(status_code=404, detail="Fase non trovata")

    return workflow_service.list_sottofasi_by_fase(id_fase)


@router.get("/protocollo-monitor/catalogo-sottofasi")
def get_catalogo_sottofasi(
    attivo_only: bool = True,
    workflow_service: Any = Depends(get_workflow_procedimento_service),
):
    return workflow_service.list_catalogo_sottofasi(attivo_only=attivo_only)


# ======================================================================================
# SOTTOFASE DOCUMENTALE - ENDPOINT READ-ONLY
# ======================================================================================

@router.get("/protocollo-monitor/sottofasi/{id_sottofase}/documentale")
def get_sottofase_documentale(
    id_sottofase: int,
    sottofase_service: Any = Depends(get_sottofase_documentale_service),
):
    quadro = sottofase_service.get_quadro_documentale(id_sottofase)

    if quadro is None:
        raise HTTPException(status_code=404, detail="Sottofase non trovata")

    return quadro


@router.get("/protocollo-monitor/sottofasi/{id_sottofase}/documenti")
def get_sottofase_documenti(
    id_sottofase: int,
    sottofase_service: Any = Depends(get_sottofase_documentale_service),
):
    sottofase = sottofase_service.get_sottofase_documentale(id_sottofase)

    if sottofase is None:
        raise HTTPException(status_code=404, detail="Sottofase non trovata")

    return sottofase_service.list_documenti_by_sottofase(id_sottofase)


@router.get("/protocollo-monitor/sottofasi/{id_sottofase}/step-operativi")
def get_sottofase_step_operativi(
    id_sottofase: int,
    sottofase_service: Any = Depends(get_sottofase_documentale_service),
):
    sottofase = sottofase_service.get_sottofase_documentale(id_sottofase)

    if sottofase is None:
        raise HTTPException(status_code=404, detail="Sottofase non trovata")

    return sottofase_service.list_step_operativi_by_sottofase(id_sottofase)


@router.get("/protocollo-monitor/sottofase-documenti/{id_documento}/apri")
def apri_sottofase_documento(
    id_documento: int,
    sottofase_service: Any = Depends(get_sottofase_documentale_service),
):
    documento, resolved_document_path = _resolve_sottofase_documento_path_or_404(
        id_documento,
        sottofase_service,
    )

    media_type = (
        documento.get("mime_type")
        or mimetypes.guess_type(str(resolved_document_path))[0]
        or "application/octet-stream"
    )

    return FileResponse(
        str(resolved_document_path),
        media_type=media_type,
        headers={
            "Content-Disposition": (
                f'inline; filename="{resolved_document_path.name}"'
            )
        },
    )


@router.get("/protocollo-monitor/sottofasi/{id_sottofase}/workflow")
def get_sottofase_workflow(
    id_sottofase: int,
    workflow_service: Any = Depends(get_sottofase_workflow_service),
):
    workflow = workflow_service.get_workflow(id_sottofase)

    if workflow is None:
        raise HTTPException(status_code=404, detail="Sottofase non trovata")

    return workflow
