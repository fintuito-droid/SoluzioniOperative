from datetime import datetime
from pathlib import Path
import shutil

from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import Base, engine, get_db
from models import (
    Utente,
    Comando,
    Stazione,
    Checklist,
    ChecklistOperatore,
    ChecklistDettaglio,
)
from schemas import (
    LoginRequest,
    TokenResponse,
    UtenteOut,
    ComandoOut,
    StazioneOut,
    OperatoreOut,
    ChecklistCreate,
)
from auth import verify_password, create_access_token, get_current_user

Base.metadata.create_all(bind=engine)

app = FastAPI(title="XR33 API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_BASE = Path("uploads")
APP_NAME = "XR33"


def sanitize_filename_part(value: str) -> str:
    safe = "".join(c for c in value if c.isalnum() or c in ("_", "-", " "))
    return safe.strip().replace(" ", "_")


@app.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = (
        db.query(Utente)
        .filter(Utente.username == payload.username, Utente.attivo == True)
        .first()
    )

    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Credenziali non valide")

    token = create_access_token(user.id)
    return TokenResponse(access_token=token)


@app.get("/me", response_model=UtenteOut)
def me(current_user: Utente = Depends(get_current_user)):
    return current_user


@app.get("/me/comando", response_model=ComandoOut)
def my_command(
    current_user: Utente = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not current_user.comando_id:
        raise HTTPException(status_code=400, detail="Nessun comando associato all'utente")

    comando = db.query(Comando).filter(Comando.id == current_user.comando_id).first()

    if not comando:
        raise HTTPException(status_code=404, detail="Comando non trovato")

    return comando


@app.get("/stazioni", response_model=list[StazioneOut])
def get_stazioni(
    current_user: Utente = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not current_user.comando_id:
        raise HTTPException(status_code=400, detail="Utente senza comando associato")

    stazioni = (
        db.query(Stazione)
        .filter(
            Stazione.comando_id == current_user.comando_id,
            Stazione.tipo_app == APP_NAME,
            Stazione.attiva == True,
        )
        .order_by(Stazione.nome_stazione.asc())
        .all()
    )

    return stazioni


@app.get("/operatori", response_model=list[OperatoreOut])
def get_operatori(
    current_user: Utente = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not current_user.comando_id:
        raise HTTPException(status_code=400, detail="Utente senza comando associato")

    operatori = (
        db.query(Utente)
        .filter(
            Utente.comando_id == current_user.comando_id,
            Utente.attivo == True,
        )
        .order_by(Utente.username.asc())
        .all()
    )

    return operatori


@app.post("/upload-foto")
async def upload_foto(
    stazione_id: int = Form(...),
    tipo_controllo: str = Form(...),
    foto: UploadFile = File(...),
    current_user: Utente = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not current_user.comando_id:
        raise HTTPException(status_code=400, detail="Utente senza comando associato")

    stazione = (
        db.query(Stazione)
        .filter(
            Stazione.id == stazione_id,
            Stazione.comando_id == current_user.comando_id,
            Stazione.tipo_app == APP_NAME,
        )
        .first()
    )

    if not stazione:
        raise HTTPException(status_code=404, detail="Stazione non trovata")

    comando = db.query(Comando).filter(Comando.id == current_user.comando_id).first()

    if not comando:
        raise HTTPException(status_code=404, detail="Comando non trovato")

    ext = Path(foto.filename).suffix.lower() or ".jpg"
    if ext not in [".jpg", ".jpeg", ".png", ".webp"]:
        raise HTTPException(status_code=400, detail="Formato immagine non supportato")

    tipo_safe = sanitize_filename_part(tipo_controllo)
    now = datetime.now()
    data_str = now.strftime("%d%m%Y")
    ora_str = now.strftime("%H%M%S")

    filename = f"{current_user.id}_{tipo_safe}_{data_str}_{ora_str}{ext}"

    folder = (
        UPLOAD_BASE
        / APP_NAME
        / sanitize_filename_part(comando.nome)
        / sanitize_filename_part(stazione.nome_stazione)
    )
    folder.mkdir(parents=True, exist_ok=True)

    file_path = folder / filename
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(foto.file, buffer)

    relative_path = str(file_path).replace("\\", "/")

    return {
        "ok": True,
        "foto_path": relative_path,
        "filename": filename,
    }


@app.post("/checklist")
def create_checklist(
    payload: ChecklistCreate,
    current_user: Utente = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if payload.tipo_attivita not in ["Sopralluogo", "Manutenzione"]:
        raise HTTPException(status_code=400, detail="Tipo attività non valido")

    if not payload.operatori_ids:
        raise HTTPException(status_code=400, detail="Selezionare almeno un operatore")

    if len(payload.operatori_ids) > 3:
        raise HTTPException(status_code=400, detail="Massimo 3 operatori")

    if current_user.id not in payload.operatori_ids:
        raise HTTPException(
            status_code=400,
            detail="L'utente loggato deve essere incluso tra gli operatori",
        )

    stazione = (
        db.query(Stazione)
        .filter(
            Stazione.id == payload.stazione_id,
            Stazione.comando_id == current_user.comando_id,
            Stazione.tipo_app == APP_NAME,
        )
        .first()
    )

    if not stazione:
        raise HTTPException(status_code=404, detail="Stazione non trovata")

    operatori = (
        db.query(Utente)
        .filter(
            Utente.id.in_(payload.operatori_ids),
            Utente.comando_id == current_user.comando_id,
            Utente.attivo == True,
        )
        .all()
    )

    if len(operatori) != len(set(payload.operatori_ids)):
        raise HTTPException(status_code=400, detail="Uno o più operatori non validi")

    checklist = Checklist(
        app=APP_NAME,
        stazione_id=payload.stazione_id,
        comando_id=current_user.comando_id,
        utente_creatore_id=current_user.id,
        tipo_attivita=payload.tipo_attivita,
        note_generali=payload.note_generali,
    )
    db.add(checklist)
    db.commit()
    db.refresh(checklist)

    for op_id in set(payload.operatori_ids):
        db.add(ChecklistOperatore(checklist_id=checklist.id, utente_id=op_id))

    for controllo in payload.controlli:
        db.add(
            ChecklistDettaglio(
                checklist_id=checklist.id,
                tipo_controllo=controllo.tipo_controllo,
                esito=controllo.esito,
                note=controllo.note,
                foto_path=controllo.foto_path,
            )
        )

    db.commit()

    return {
        "ok": True,
        "checklist_id": checklist.id,
    }