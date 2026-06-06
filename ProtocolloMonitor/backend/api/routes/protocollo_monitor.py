"""Router FastAPI per gli endpoint del modulo ProtocolloMonitor."""

from __future__ import annotations

from email.parser import BytesParser
from email.policy import default as email_policy
import mimetypes
import subprocess
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from backend.core.dependency_container import DependencyContainer, create_container
from backend.schemas.sottofase_partecipanti import SottofasePartecipantePayload
from backend.schemas.sottofase_workflow import SottofaseWorkflowAzionePayload
from backend.services.procedimento_service import (
    ProcedimentoNotFoundError,
    ProcedimentoProtocolloLinkAlreadyExistsError,
    ProtocolloNotFoundError,
)
from backend.services.workflow_procedimento_service import (
    WorkflowConfigurazioneBloccataError,
    WorkflowFaseNotFoundError,
    WorkflowFaseValidationError,
)
from backend.services.sottofase_workflow_action_service import (
    WorkflowActionValidationError,
)
from backend.services.sottofase_workflow_command_service import (
    SottofaseWorkflowBackupError,
    SottofaseWorkflowNotFoundError,
    SottofaseWorkflowWriteError,
)
from backend.services.sottofase_document_upload_service import (
    MAX_DOCX_SIZE_BYTES,
    SottofaseDocumentUploadBackupError,
    SottofaseDocumentUploadNotFoundError,
    SottofaseDocumentUploadTooLargeError,
    SottofaseDocumentUploadValidationError,
    SottofaseDocumentUploadWriteError,
)
from backend.services.sottofase_documenti_service import (
    SottofaseDocumentiValidationError,
)
from backend.services.sottofase_partecipanti_service import (
    SottofasePartecipantiBackupError,
    SottofasePartecipantiDuplicateError,
    SottofasePartecipantiNotFoundError,
    SottofasePartecipantiValidationError,
    SottofasePartecipantiWriteError,
)
from backend.services.sottofase_assegnazioni_service import (
    SottofaseAssegnazioniBackupError,
    SottofaseAssegnazioniNotFoundError,
    SottofaseAssegnazioniWriteError,
)


router = APIRouter()


class ProtocolloProcedimentoLinkPayload(BaseModel):
    """Payload opzionale per collegare protocollo e procedimento."""

    RuoloProtocollo: str | None = "COLLEGATO"
    Principale: bool = False
    NoteCollegamento: str | None = None


class ProcedimentoCreatePayload(BaseModel):
    """Payload minimo per creare un nuovo procedimento."""

    CodiceProcedimento: str | None = Field(default=None, max_length=50)
    Titolo: str | None = Field(default=None, max_length=255)
    Descrizione: str | None = None
    AziendaSoggetto: str | None = Field(default=None, max_length=255)
    ComandoCompetenza: str | None = Field(default=None, max_length=50)
    SettoreCompetenza: str | None = Field(default=None, max_length=100)
    TipologiaProcedimento: str | None = Field(default=None, max_length=100)
    Priorita: str | None = Field(default=None, max_length=50)
    DataScadenza: str | None = None
    NoteInterne: str | None = None


class ProcedimentoFasePayload(BaseModel):
    """Payload per creare o modificare una fase verticale."""

    Titolo: str | None = Field(default=None, max_length=255)
    Descrizione: str | None = None


class ProcedimentoFaseStepPayload(BaseModel):
    """Payload minimo per inserire uno step orizzontale."""

    titoloStep: str | None = Field(default=None, max_length=255)
    codiceStep: str | None = Field(default=None, max_length=50)


class ProcedimentoFaseStepProtocolloPayload(BaseModel):
    """Payload per collegare un protocollo a uno step orizzontale."""

    idProtocollo: int


class ProcedimentoFaseStepNotePayload(BaseModel):
    """Payload per salvare le note operative di uno step orizzontale."""

    noteOperative: str | None = None


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


def get_sottofase_documenti_service(
    container: DependencyContainer = Depends(get_container),
) -> Any:
    """Dipendenza FastAPI per documenti principali/allegati sottofase."""

    return container.get_sottofase_documenti_service()


def get_sottofase_workflow_service(
    container: DependencyContainer = Depends(get_container),
) -> Any:
    """Dipendenza FastAPI per ottenere `SottofaseWorkflowService`."""

    return container.get_sottofase_workflow_service()


def get_sottofase_workflow_command_service(
    container: DependencyContainer = Depends(get_container),
) -> Any:
    """Dipendenza FastAPI per ottenere il command service workflow."""

    return container.get_sottofase_workflow_command_service()


def get_sottofase_document_upload_service(
    container: DependencyContainer = Depends(get_container),
) -> Any:
    """Dipendenza FastAPI per ottenere il service upload documenti Word."""

    return container.get_sottofase_document_upload_service()


def get_sottofase_partecipanti_service(
    container: DependencyContainer = Depends(get_container),
) -> Any:
    """Dipendenza FastAPI per ottenere il service partecipanti sottofase."""

    return container.get_sottofase_partecipanti_service()


def get_sottofase_assegnazioni_service(
    container: DependencyContainer = Depends(get_container),
) -> Any:
    """Dipendenza FastAPI per ottenere il service assegnazioni sottofase."""

    return container.get_sottofase_assegnazioni_service()


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


def _parse_multipart_form_data(
    *,
    content_type: str,
    body: bytes,
) -> dict[str, Any]:
    """Parsing multipart minimale con standard library.

    L'ambiente corrente non include `python-multipart`; usare `UploadFile`,
    `File` o `Form` farebbe fallire l'import della route. Questa funzione
    mantiene il contratto `multipart/form-data` senza introdurre dipendenze
    nuove. Il parsing resta circoscritto al caso richiesto: un campo file e un
    campo testuale `utenteOperatore`.
    """

    if "multipart/form-data" not in content_type.lower():
        raise HTTPException(
            status_code=400,
            detail="Richiesta non valida: usare multipart/form-data",
        )

    message_bytes = (
        f"Content-Type: {content_type}\r\nMIME-Version: 1.0\r\n\r\n".encode(
            "utf-8"
        )
        + body
    )
    message = BytesParser(policy=email_policy).parsebytes(message_bytes)

    if not message.is_multipart():
        raise HTTPException(
            status_code=400,
            detail="Payload multipart non valido",
        )

    fields: dict[str, Any] = {}

    for part in message.iter_parts():
        if part.get_content_disposition() != "form-data":
            continue

        name = part.get_param("name", header="content-disposition")

        if not name:
            continue

        filename = part.get_filename()
        payload = part.get_payload(decode=True) or b""

        if filename is not None:
            fields[name] = {
                "filename": filename,
                "content": payload,
                "content_type": part.get_content_type(),
            }
        else:
            charset = part.get_content_charset() or "utf-8"
            fields[name] = payload.decode(charset, errors="replace")

    return fields


async def _read_documento_word_upload_request(
    request: Request,
) -> dict[str, Any]:
    """Legge file `.docx` e utente operatore dal multipart request."""

    content_length = request.headers.get("content-length")

    if content_length:
        try:
            if int(content_length) > MAX_DOCX_SIZE_BYTES + 1024 * 1024:
                raise HTTPException(
                    status_code=413,
                    detail="File troppo grande: limite massimo 50 MB",
                )
        except ValueError:
            pass

    fields = _parse_multipart_form_data(
        content_type=request.headers.get("content-type", ""),
        body=await request.body(),
    )
    file_part = fields.get("file")

    if not isinstance(file_part, dict):
        raise HTTPException(status_code=400, detail="File Word mancante")

    return {
        "file_bytes": file_part.get("content") or b"",
        "filename": file_part.get("filename") or "",
        "utente_operatore": fields.get("utenteOperatore"),
    }


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


@router.post("/protocollo-monitor/procedimenti", status_code=201)
def crea_procedimento(
    payload: ProcedimentoCreatePayload,
    procedimento_service: Any = Depends(get_procedimento_service),
):
    try:
        return procedimento_service.crea_procedimento(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


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


@router.post("/protocollo-monitor/procedimenti/{id_procedimento}/fasi", status_code=201)
def crea_procedimento_fase(
    id_procedimento: int,
    payload: ProcedimentoFasePayload,
    workflow_service: Any = Depends(get_workflow_procedimento_service),
):
    try:
        return workflow_service.crea_fase_procedimento(
            id_procedimento=id_procedimento,
            payload=payload,
        )
    except WorkflowFaseNotFoundError:
        raise HTTPException(status_code=404, detail="Procedimento non trovato")
    except WorkflowFaseValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.put("/protocollo-monitor/procedimenti/{id_procedimento}/fasi/{id_fase}")
def aggiorna_procedimento_fase(
    id_procedimento: int,
    id_fase: int,
    payload: ProcedimentoFasePayload,
    workflow_service: Any = Depends(get_workflow_procedimento_service),
):
    try:
        return workflow_service.aggiorna_fase_procedimento(
            id_procedimento=id_procedimento,
            id_fase=id_fase,
            payload=payload,
        )
    except WorkflowFaseNotFoundError:
        raise HTTPException(status_code=404, detail="Fase non trovata")
    except WorkflowFaseValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


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


@router.get(
    "/protocollo-monitor/procedimenti/{id_procedimento}/fasi/{id_fase}/"
    "step-orizzontali"
)
def get_procedimento_fase_step_orizzontali(
    id_procedimento: int,
    id_fase: int,
    workflow_service: Any = Depends(get_workflow_procedimento_service),
):
    try:
        return workflow_service.list_step_orizzontali_fase(
            id_procedimento=id_procedimento,
            id_fase=id_fase,
        )
    except WorkflowFaseNotFoundError:
        raise HTTPException(status_code=404, detail="Fase non trovata")


@router.post(
    "/protocollo-monitor/procedimenti/{id_procedimento}/fasi/{id_fase}/"
    "step-orizzontali/inizializza"
)
def inizializza_procedimento_fase_step_orizzontali(
    id_procedimento: int,
    id_fase: int,
    workflow_service: Any = Depends(get_workflow_procedimento_service),
):
    try:
        return workflow_service.inizializza_step_orizzontali_fase(
            id_procedimento=id_procedimento,
            id_fase=id_fase,
        )
    except WorkflowFaseNotFoundError:
        raise HTTPException(status_code=404, detail="Fase non trovata")


@router.post(
    "/protocollo-monitor/procedimenti/{id_procedimento}/fasi/{id_fase}/"
    "step-orizzontali/configura-istanza-fine"
)
def configura_procedimento_fase_step_istanza_fine(
    id_procedimento: int,
    id_fase: int,
    workflow_service: Any = Depends(get_workflow_procedimento_service),
):
    try:
        return workflow_service.configura_step_orizzontali_istanza_fine(
            id_procedimento=id_procedimento,
            id_fase=id_fase,
        )
    except WorkflowFaseNotFoundError:
        raise HTTPException(status_code=404, detail="Fase non trovata")
    except WorkflowConfigurazioneBloccataError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    except WorkflowFaseValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post(
    "/protocollo-monitor/procedimenti/{id_procedimento}/fasi/{id_fase}/"
    "step-orizzontali/configura-predefinito"
)
def configura_procedimento_fase_step_predefinito(
    id_procedimento: int,
    id_fase: int,
    workflow_service: Any = Depends(get_workflow_procedimento_service),
):
    try:
        return workflow_service.configura_step_orizzontali_predefinito(
            id_procedimento=id_procedimento,
            id_fase=id_fase,
        )
    except WorkflowFaseNotFoundError:
        raise HTTPException(status_code=404, detail="Fase non trovata")
    except WorkflowConfigurazioneBloccataError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    except WorkflowFaseValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post(
    "/protocollo-monitor/procedimenti/{id_procedimento}/fasi/{id_fase}/"
    "step-orizzontali/{id_step}/inserisci-dopo"
)
def inserisci_procedimento_fase_step_orizzontale_dopo(
    id_procedimento: int,
    id_fase: int,
    id_step: int,
    payload: ProcedimentoFaseStepPayload,
    workflow_service: Any = Depends(get_workflow_procedimento_service),
):
    try:
        return workflow_service.inserisci_step_orizzontale_dopo(
            id_procedimento=id_procedimento,
            id_fase=id_fase,
            id_step=id_step,
            payload=payload,
        )
    except WorkflowFaseNotFoundError:
        raise HTTPException(status_code=404, detail="Fase o step non trovato")
    except WorkflowFaseValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.delete(
    "/protocollo-monitor/procedimenti/{id_procedimento}/fasi/{id_fase}/"
    "step-orizzontali/{id_step}"
)
def elimina_procedimento_fase_step_orizzontale(
    id_procedimento: int,
    id_fase: int,
    id_step: int,
    workflow_service: Any = Depends(get_workflow_procedimento_service),
):
    try:
        return workflow_service.elimina_logicamente_step_orizzontale(
            id_procedimento=id_procedimento,
            id_fase=id_fase,
            id_step=id_step,
        )
    except WorkflowFaseNotFoundError:
        raise HTTPException(status_code=404, detail="Fase o step non trovato")
    except WorkflowFaseValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post(
    "/protocollo-monitor/procedimenti/{id_procedimento}/fasi/{id_fase}/"
    "step-orizzontali/{id_step}/collega-protocollo"
)
def collega_protocollo_procedimento_fase_step_istanza(
    id_procedimento: int,
    id_fase: int,
    id_step: int,
    payload: ProcedimentoFaseStepProtocolloPayload,
    workflow_service: Any = Depends(get_workflow_procedimento_service),
):
    try:
        return workflow_service.collega_protocollo_step_istanza(
            id_procedimento=id_procedimento,
            id_fase=id_fase,
            id_step=id_step,
            payload=payload,
        )
    except WorkflowFaseNotFoundError as exc:
        detail = str(exc) or "Fase, step o protocollo non trovato"
        raise HTTPException(status_code=404, detail=detail)
    except WorkflowFaseValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post(
    "/protocollo-monitor/procedimenti/{id_procedimento}/fasi/{id_fase}/"
    "step-orizzontali/{id_step}/avvia"
)
def avvia_procedimento_fase_step_redigi(
    id_procedimento: int,
    id_fase: int,
    id_step: int,
    workflow_service: Any = Depends(get_workflow_procedimento_service),
):
    try:
        return workflow_service.avvia_step_redigi(
            id_procedimento=id_procedimento,
            id_fase=id_fase,
            id_step=id_step,
        )
    except WorkflowFaseNotFoundError as exc:
        detail = str(exc) or "Fase o step non trovato"
        raise HTTPException(status_code=404, detail=detail)
    except WorkflowFaseValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post(
    "/protocollo-monitor/procedimenti/{id_procedimento}/fasi/{id_fase}/"
    "step-orizzontali/{id_step}/completa"
)
def completa_procedimento_fase_step_redigi(
    id_procedimento: int,
    id_fase: int,
    id_step: int,
    workflow_service: Any = Depends(get_workflow_procedimento_service),
):
    try:
        return workflow_service.completa_step_redigi(
            id_procedimento=id_procedimento,
            id_fase=id_fase,
            id_step=id_step,
        )
    except WorkflowFaseNotFoundError as exc:
        detail = str(exc) or "Fase o step non trovato"
        raise HTTPException(status_code=404, detail=detail)
    except WorkflowFaseValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.put(
    "/protocollo-monitor/procedimenti/{id_procedimento}/fasi/{id_fase}/"
    "step-orizzontali/{id_step}/note-operative"
)
def aggiorna_note_procedimento_fase_step_redigi(
    id_procedimento: int,
    id_fase: int,
    id_step: int,
    payload: ProcedimentoFaseStepNotePayload,
    workflow_service: Any = Depends(get_workflow_procedimento_service),
):
    try:
        return workflow_service.aggiorna_note_step_redigi(
            id_procedimento=id_procedimento,
            id_fase=id_fase,
            id_step=id_step,
            payload=payload,
        )
    except WorkflowFaseNotFoundError as exc:
        detail = str(exc) or "Fase o step non trovato"
        raise HTTPException(status_code=404, detail=detail)
    except WorkflowFaseValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


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
    documenti_service: Any = Depends(get_sottofase_documenti_service),
):
    sottofase = sottofase_service.get_sottofase_documentale(id_sottofase)

    if sottofase is None:
        raise HTTPException(status_code=404, detail="Sottofase non trovata")

    try:
        return documenti_service.get_documenti_sottofase(id_sottofase)
    except SottofaseDocumentiValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/protocollo-monitor/sottofasi/{id_sottofase}/documento-principale")
def get_sottofase_documento_principale(
    id_sottofase: int,
    sottofase_service: Any = Depends(get_sottofase_documentale_service),
    documenti_service: Any = Depends(get_sottofase_documenti_service),
):
    sottofase = sottofase_service.get_sottofase_documentale(id_sottofase)

    if sottofase is None:
        raise HTTPException(status_code=404, detail="Sottofase non trovata")

    try:
        return documenti_service.get_documento_principale(id_sottofase)
    except SottofaseDocumentiValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/protocollo-monitor/sottofasi/{id_sottofase}/allegati")
def get_sottofase_allegati(
    id_sottofase: int,
    sottofase_service: Any = Depends(get_sottofase_documentale_service),
    documenti_service: Any = Depends(get_sottofase_documenti_service),
):
    sottofase = sottofase_service.get_sottofase_documentale(id_sottofase)

    if sottofase is None:
        raise HTTPException(status_code=404, detail="Sottofase non trovata")

    try:
        return documenti_service.get_allegati(id_sottofase)
    except SottofaseDocumentiValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/protocollo-monitor/sottofasi/{id_sottofase}/documenti", status_code=201)
async def carica_documento_word_sottofase(
    id_sottofase: int,
    request: Request,
    upload_service: Any = Depends(get_sottofase_document_upload_service),
):
    """Collega una nuova versione Word alla sottofase in REDIGI/REVISIONA."""

    upload_data = await _read_documento_word_upload_request(request)

    try:
        return upload_service.collega_documento_word(
            id_sottofase=id_sottofase,
            file_bytes=upload_data["file_bytes"],
            original_filename=upload_data["filename"],
            utente_operatore=upload_data["utente_operatore"],
        )
    except SottofaseDocumentUploadNotFoundError:
        raise HTTPException(status_code=404, detail="Sottofase non trovata")
    except SottofaseDocumentUploadTooLargeError as exc:
        raise HTTPException(status_code=413, detail=str(exc))
    except SottofaseDocumentUploadValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except SottofaseDocumentUploadBackupError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    except SottofaseDocumentUploadWriteError as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/protocollo-monitor/sottofasi/{id_sottofase}/step-operativi")
def get_sottofase_step_operativi(
    id_sottofase: int,
    sottofase_service: Any = Depends(get_sottofase_documentale_service),
):
    sottofase = sottofase_service.get_sottofase_documentale(id_sottofase)

    if sottofase is None:
        raise HTTPException(status_code=404, detail="Sottofase non trovata")

    return sottofase_service.list_step_operativi_by_sottofase(id_sottofase)


@router.get("/protocollo-monitor/sottofasi/{id_sottofase}/partecipanti")
def get_sottofase_partecipanti(
    id_sottofase: int,
    partecipanti_service: Any = Depends(get_sottofase_partecipanti_service),
):
    try:
        return partecipanti_service.list_partecipanti(id_sottofase)
    except SottofasePartecipantiNotFoundError:
        raise HTTPException(status_code=404, detail="Sottofase non trovata")


@router.post(
    "/protocollo-monitor/sottofasi/{id_sottofase}/partecipanti",
    status_code=201,
)
def crea_sottofase_partecipante(
    id_sottofase: int,
    payload: SottofasePartecipantePayload,
    partecipanti_service: Any = Depends(get_sottofase_partecipanti_service),
):
    try:
        return partecipanti_service.crea_partecipante(
            id_sottofase=id_sottofase,
            payload=payload,
        )
    except SottofasePartecipantiNotFoundError:
        raise HTTPException(status_code=404, detail="Sottofase non trovata")
    except SottofasePartecipantiDuplicateError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    except SottofasePartecipantiValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except SottofasePartecipantiBackupError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    except SottofasePartecipantiWriteError as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get(
    "/protocollo-monitor/sottofasi/{id_sottofase}/step-operativi/{id_step}/partecipanti"
)
def get_sottofase_step_partecipanti(
    id_sottofase: int,
    id_step: int,
    partecipanti_service: Any = Depends(get_sottofase_partecipanti_service),
):
    try:
        return partecipanti_service.list_partecipanti_by_step(
            id_sottofase=id_sottofase,
            id_step_operativo=id_step,
        )
    except SottofasePartecipantiNotFoundError:
        raise HTTPException(status_code=404, detail="Sottofase non trovata")
    except SottofasePartecipantiValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post(
    "/protocollo-monitor/sottofasi/{id_sottofase}/step/{id_step}/"
    "partecipanti/{id_partecipante}/completa"
)
def completa_sottofase_step_partecipante(
    id_sottofase: int,
    id_step: int,
    id_partecipante: int,
    partecipanti_service: Any = Depends(get_sottofase_partecipanti_service),
):
    try:
        return partecipanti_service.completa_partecipante_step(
            id_sottofase=id_sottofase,
            id_step_operativo=id_step,
            id_partecipante=id_partecipante,
        )
    except SottofasePartecipantiNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except SottofasePartecipantiValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except SottofasePartecipantiBackupError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    except SottofasePartecipantiWriteError as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post(
    "/protocollo-monitor/sottofasi/{id_sottofase}/assegnazioni/applica-regole"
)
def applica_regole_assegnazione_sottofase(
    id_sottofase: int,
    assegnazioni_service: Any = Depends(get_sottofase_assegnazioni_service),
):
    try:
        return assegnazioni_service.applica_regole_assegnazione_sottofase(
            id_sottofase,
        )
    except SottofaseAssegnazioniNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except SottofaseAssegnazioniBackupError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    except SottofaseAssegnazioniWriteError as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/protocollo-monitor/assegnazioni/popola-regole-default")
def popola_regole_assegnazione_default(
    assegnazioni_service: Any = Depends(get_sottofase_assegnazioni_service),
):
    try:
        return assegnazioni_service.popola_regole_assegnazione_default()
    except SottofaseAssegnazioniBackupError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    except SottofaseAssegnazioniWriteError as exc:
        raise HTTPException(status_code=500, detail=str(exc))


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


@router.get("/protocollo-monitor/sottofase-documenti/{id_documento}/scarica")
def scarica_sottofase_documento(
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
        filename=resolved_document_path.name,
        headers={
            "Content-Disposition": (
                f'attachment; filename="{resolved_document_path.name}"'
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


@router.post("/protocollo-monitor/sottofasi/{id_sottofase}/workflow/azioni")
def esegui_azione_workflow_sottofase(
    id_sottofase: int,
    payload: SottofaseWorkflowAzionePayload,
    command_service: Any = Depends(get_sottofase_workflow_command_service),
):
    try:
        return command_service.esegui_azione_workflow_sottofase(
            id_sottofase=id_sottofase,
            payload=payload,
        )
    except SottofaseWorkflowNotFoundError:
        raise HTTPException(status_code=404, detail="Sottofase non trovata")
    except WorkflowActionValidationError as exc:
        raise HTTPException(status_code=400, detail=exc.message)
    except SottofaseWorkflowBackupError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    except SottofaseWorkflowWriteError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
