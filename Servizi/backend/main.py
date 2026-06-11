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
    return {"status": "ok", "db": "access", "modulo": "aib2026"}
