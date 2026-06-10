"""
main.py — FastAPI entry point — Modulo AIB 2026
================================================
Avvio: uvicorn main:app --reload --port 8000
Docs:  http://localhost:8000/docs
"""

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from db.database import db
from auth import login, logout, get_current_user
from models.models import UtenteLogin, TokenResponse, RuoloUtente
from routers import personale, presenze

app = FastAPI(
    title="SoluzioniOperative — Modulo AIB 2026",
    description="Gestione presenze servizi a pagamento campagna antincendio boschivo",
    version="1.0.0"
)

# ── CORS per Vue dev server ──────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:5175",
                   "http://localhost:5176", "http://localhost:5177", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Router ───────────────────────────────────────────────────────────────────
app.include_router(personale.router, prefix="/api/v1")
app.include_router(presenze.router,  prefix="/api/v1")


# ── Auth endpoints ───────────────────────────────────────────────────────────
@app.post("/api/v1/auth/login", response_model=TokenResponse)
def auth_login(credentials: UtenteLogin):
    result = login(credentials.username, credentials.password)
    if not result:
        from fastapi import HTTPException
        raise HTTPException(401, "Credenziali non valide")
    return result


@app.post("/api/v1/auth/logout")
def auth_logout(authorization: str = None, current_user: dict = Depends(get_current_user)):
    if authorization:
        token = authorization.removeprefix("Bearer ").strip()
        logout(token)
    return {"ok": True}


# ── Lookup endpoints (postazioni, funzioni, campagne) ────────────────────────
@app.get("/api/v1/lookup/postazioni")
def get_postazioni(current_user: dict = Depends(get_current_user)):
    return db.fetch_all("SELECT * FROM postazioni WHERE attiva=True ORDER BY codice")

@app.get("/api/v1/lookup/funzioni")
def get_funzioni(current_user: dict = Depends(get_current_user)):
    return db.fetch_all("SELECT * FROM funzioni_servizio ORDER BY codice")

@app.get("/api/v1/lookup/campagne")
def get_campagne(current_user: dict = Depends(get_current_user)):
    return db.fetch_all("SELECT * FROM campagne_aib ORDER BY anno DESC")

@app.get("/api/v1/lookup/qualifiche")
def get_qualifiche(current_user: dict = Depends(get_current_user)):
    return db.fetch_all("SELECT * FROM qualifiche ORDER BY codice")

@app.get("/api/v1/lookup/comandi")
def get_comandi(current_user: dict = Depends(get_current_user)):
    return db.fetch_all("SELECT * FROM comandi WHERE attivo=True ORDER BY codice")

@app.get("/api/v1/lookup/specialita")
def get_specialita(current_user: dict = Depends(get_current_user)):
    return db.fetch_all("SELECT * FROM specialita ORDER BY codice")

# ── Gestione postazioni (solo Admin) ─────────────────────────────────────────
@app.post("/api/v1/lookup/postazioni")
def crea_postazione(
    body: dict,
    current_user: dict = Depends(get_current_user)
):
    if current_user["ruolo"] != "admin":
        from fastapi import HTTPException
        raise HTTPException(403)
    new_id = db.execute(
        "INSERT INTO postazioni (codice, nome, note, attiva) VALUES (?,?,?,?)",
        (body["codice"], body["nome"], body.get("note"), True)
    )
    return db.fetch_one("SELECT * FROM postazioni WHERE id=?", (new_id,))

@app.put("/api/v1/lookup/postazioni/{pid}")
def aggiorna_postazione(
    pid: int,
    body: dict,
    current_user: dict = Depends(get_current_user)
):
    if current_user["ruolo"] != "admin":
        from fastapi import HTTPException
        raise HTTPException(403)
    db.execute(
        "UPDATE postazioni SET codice=?, nome=?, note=?, attiva=? WHERE id=?",
        (body["codice"], body["nome"], body.get("note"), body.get("attiva", True), pid)
    )
    return db.fetch_one("SELECT * FROM postazioni WHERE id=?", (pid,))


# ── Health check ─────────────────────────────────────────────────────────────
@app.get("/api/v1/health")
def health():
    return {"status": "ok", "db": "access", "modulo": "aib2026"}
