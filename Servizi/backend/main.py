"""
main.py — FastAPI entry point — Modulo AIB 2026
================================================
Avvio: uvicorn main:app --reload --port 8001
Docs:  http://localhost:8001/docs
(porta 8001: la 8000 è del backend ProtocolloMonitor nella piattaforma)
"""

import logging
import os
from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from db.database import db
from auth import login, logout, get_current_user, cambia_password, _decode_token
from models.models import UtenteLogin, TokenResponse, RuoloUtente
from routers import personale, presenze, utenti, report

# ── Logging operazioni di scrittura ──────────────────────────────────────────
os.makedirs(os.path.join(os.path.dirname(__file__), "logs"), exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(__file__), "logs", "operazioni.log"), encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("aib")

app = FastAPI(
    title="SoluzioniOperative — Modulo AIB 2026",
    description="Gestione presenze servizi a pagamento campagna antincendio boschivo",
    version="1.0.0"
)

ALLOWED_ORIGINS = ["http://localhost:5173", "http://localhost:5174", "http://localhost:5175",
                   "http://localhost:5176", "http://localhost:5177", "http://localhost:3000"]


def _cors_headers(request: Request) -> dict:
    """Header CORS per le risposte generate fuori dal middleware (exception handler)."""
    origin = request.headers.get("origin", "")
    if origin in ALLOWED_ORIGINS:
        return {"Access-Control-Allow-Origin": origin, "Access-Control-Allow-Credentials": "true"}
    return {}


# ── Exception handler globale: mai 500 senza JSON leggibile ──────────────────
@app.exception_handler(Exception)
async def gestione_errori(request: Request, exc: Exception):
    logger.exception("Errore non gestito su %s %s: %s", request.method, request.url.path, exc)
    return JSONResponse(
        status_code=500,
        content={"detail": f"Errore interno del server ({type(exc).__name__}). Contattare l'amministratore."},
        headers=_cors_headers(request),
    )


# ── Audit: log delle operazioni di scrittura (chi, cosa, quando) ─────────────
@app.middleware("http")
async def audit_scritture(request: Request, call_next):
    response = await call_next(request)
    if request.method in ("POST", "PUT", "PATCH", "DELETE") and "/auth/login" not in request.url.path:
        username = "-"
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            user = _decode_token(auth_header.removeprefix("Bearer ").strip())
            if user:
                username = user["username"]
        logger.info("AUDIT  user=%s  %s %s  → %s",
                    username, request.method, request.url.path, response.status_code)
    return response

# ── CORS per Vue dev server ──────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Router ───────────────────────────────────────────────────────────────────
app.include_router(personale.router, prefix="/api/v1")
app.include_router(presenze.router,  prefix="/api/v1")
app.include_router(utenti.router,    prefix="/api/v1")
app.include_router(report.router,    prefix="/api/v1")


# ── Auth endpoints ───────────────────────────────────────────────────────────
@app.post("/api/v1/auth/login", response_model=TokenResponse)
def auth_login(credentials: UtenteLogin):
    result = login(credentials.username, credentials.password)
    if not result:
        from fastapi import HTTPException
        raise HTTPException(401, "Credenziali non valide")
    logger.info("AUDIT  login utente=%s", credentials.username)
    return result


@app.post("/api/v1/auth/logout")
def auth_logout(request: Request, current_user: dict = Depends(get_current_user)):
    auth_header = request.headers.get("authorization", "")
    if auth_header.startswith("Bearer "):
        logout(auth_header.removeprefix("Bearer ").strip())
    return {"ok": True}


@app.get("/api/v1/auth/me")
def auth_me(current_user: dict = Depends(get_current_user)):
    """Valida il token e restituisce l'utente corrente (ripristino sessione F5)."""
    return {
        "username":     current_user["username"],
        "ruolo":        current_user["ruolo"],
        "personale_id": current_user.get("personale_id"),
        "moduli":       current_user.get("moduli", []),
    }


@app.post("/api/v1/auth/cambia-password")
def auth_cambia_password(body: dict, current_user: dict = Depends(get_current_user)):
    from fastapi import HTTPException
    vecchia = body.get("vecchia_password", "")
    nuova   = body.get("nuova_password", "")
    if len(nuova) < 6:
        raise HTTPException(422, "La nuova password deve avere almeno 6 caratteri")
    if not cambia_password(current_user["id"], vecchia, nuova):
        raise HTTPException(401, "Password attuale non corretta")
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
def _require_admin(current_user: dict):
    if current_user["ruolo"] != "admin":
        from fastapi import HTTPException
        raise HTTPException(403, "Operazione riservata agli amministratori")


@app.post("/api/v1/lookup/postazioni")
def crea_postazione(
    body: dict,
    current_user: dict = Depends(get_current_user)
):
    _require_admin(current_user)
    new_id = db.execute(
        """INSERT INTO postazioni
           (codice, nome, [note], attiva, turni_multipli, slot_funzionario, slot_tas2, slot_addetto)
           VALUES (?,?,?,?,?,?,?,?)""",
        (body["codice"], body["nome"], body.get("note"), True,
         body.get("turni_multipli", False),
         body.get("slot_funzionario", 0),
         body.get("slot_tas2", 0),
         body.get("slot_addetto", 0))
    )
    return db.fetch_one("SELECT * FROM postazioni WHERE id=?", (new_id,))

@app.put("/api/v1/lookup/postazioni/{pid}")
def aggiorna_postazione(
    pid: int,
    body: dict,
    current_user: dict = Depends(get_current_user)
):
    _require_admin(current_user)
    db.execute(
        """UPDATE postazioni SET
           codice=?, nome=?, [note]=?, attiva=?,
           turni_multipli=?, slot_funzionario=?, slot_tas2=?, slot_addetto=?
           WHERE id=?""",
        (body["codice"], body["nome"], body.get("note"), body.get("attiva", True),
         body.get("turni_multipli", False),
         body.get("slot_funzionario", 0),
         body.get("slot_tas2", 0),
         body.get("slot_addetto", 0),
         pid)
    )
    return db.fetch_one("SELECT * FROM postazioni WHERE id=?", (pid,))


# ── Gestione campagne (solo Admin) ───────────────────────────────────────────
@app.post("/api/v1/lookup/campagne")
def crea_campagna(
    body: dict,
    current_user: dict = Depends(get_current_user)
):
    _require_admin(current_user)
    # Una sola campagna attiva: se la nuova è attiva, disattiva le altre
    if body.get("attiva", True):
        db.execute("UPDATE campagne_aib SET attiva=False")
    new_id = db.execute(
        "INSERT INTO campagne_aib (anno, data_inizio, data_fine, descrizione, attiva) VALUES (?,?,?,?,?)",
        (body["anno"], str(body["data_inizio"]), str(body["data_fine"]),
         body.get("descrizione"), body.get("attiva", True))
    )
    return db.fetch_one("SELECT * FROM campagne_aib WHERE id=?", (new_id,))

@app.put("/api/v1/lookup/campagne/{cid}")
def aggiorna_campagna(
    cid: int,
    body: dict,
    current_user: dict = Depends(get_current_user)
):
    _require_admin(current_user)
    if body.get("attiva"):
        db.execute("UPDATE campagne_aib SET attiva=False")
    db.execute(
        "UPDATE campagne_aib SET anno=?, data_inizio=?, data_fine=?, descrizione=?, attiva=? WHERE id=?",
        (body["anno"], str(body["data_inizio"]), str(body["data_fine"]),
         body.get("descrizione"), body.get("attiva", False), cid)
    )
    return db.fetch_one("SELECT * FROM campagne_aib WHERE id=?", (cid,))


# ── Gestione specialità (solo Admin) ─────────────────────────────────────────
@app.post("/api/v1/lookup/specialita")
def crea_specialita(
    body: dict,
    current_user: dict = Depends(get_current_user)
):
    _require_admin(current_user)
    new_id = db.execute(
        "INSERT INTO specialita ([codice],[descrizione]) VALUES (?,?)",
        (body["codice"], body.get("descrizione"))
    )
    return db.fetch_one("SELECT * FROM specialita WHERE id=?", (new_id,))

@app.put("/api/v1/lookup/specialita/{sid}")
def aggiorna_specialita(
    sid: int,
    body: dict,
    current_user: dict = Depends(get_current_user)
):
    _require_admin(current_user)
    db.execute(
        "UPDATE specialita SET [codice]=?, [descrizione]=? WHERE id=?",
        (body["codice"], body.get("descrizione"), sid)
    )
    return db.fetch_one("SELECT * FROM specialita WHERE id=?", (sid,))

@app.delete("/api/v1/lookup/specialita/{sid}")
def elimina_specialita(
    sid: int,
    current_user: dict = Depends(get_current_user)
):
    _require_admin(current_user)
    # Blocca eliminazione se assegnata a qualcuno
    in_uso = db.fetch_one(
        "SELECT COUNT(*) AS n FROM personale_specialita WHERE specialita_id=?", (sid,)
    )
    if in_uso and in_uso["n"] > 0:
        from fastapi import HTTPException
        raise HTTPException(409, f"Specialità assegnata a {in_uso['n']} dipendenti: rimuoverla prima dalle anagrafiche")
    db.execute("DELETE FROM specialita WHERE id=?", (sid,))
    return {"ok": True}


# ── Health check ─────────────────────────────────────────────────────────────
@app.get("/api/v1/health")
def health():
    from db.database import DB_ENGINE
    return {"status": "ok", "db": DB_ENGINE, "modulo": "aib2026"}
