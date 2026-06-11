"""
routers/utenti.py — Gestione utenti applicativi (solo Admin)
"""

from fastapi import APIRouter, Depends, HTTPException
from db.database import db
from auth import require_role, _hash_password

router = APIRouter(prefix="/utenti", tags=["Utenti"],
                   dependencies=[Depends(require_role("admin"))])


def _utente_out(row: dict) -> dict:
    """Rimuove l'hash password e denormalizza il nominativo collegato."""
    out = {k: v for k, v in row.items() if k != "password_hash"}
    if row.get("personale_id"):
        p = db.fetch_one("SELECT cognome, nome FROM personale WHERE id=?", (row["personale_id"],))
        out["nominativo"] = f"{p['cognome']} {p['nome']}" if p else None
    else:
        out["nominativo"] = None
    return out


@router.get("/")
def lista_utenti():
    rows = db.fetch_all("SELECT * FROM utenti ORDER BY username")
    return [_utente_out(r) for r in rows]


@router.post("/")
def crea_utente(body: dict):
    if not body.get("username") or not body.get("password"):
        raise HTTPException(422, "Username e password sono obbligatori")
    dup = db.fetch_one("SELECT id FROM utenti WHERE username=?", (body["username"],))
    if dup:
        raise HTTPException(409, f"Username '{body['username']}' già esistente")

    new_id = db.execute(
        """INSERT INTO utenti ([username],[password_hash],[ruolo],[personale_id],[comando_id],[attivo])
           VALUES (?,?,?,?,?,?)""",
        (body["username"], _hash_password(body["password"]),
         body.get("ruolo", "dipendente"), body.get("personale_id"),
         body.get("comando_id"), body.get("attivo", True))
    )
    return _utente_out(db.fetch_one("SELECT * FROM utenti WHERE id=?", (new_id,)))


@router.put("/{uid}")
def aggiorna_utente(uid: int, body: dict):
    row = db.fetch_one("SELECT * FROM utenti WHERE id=?", (uid,))
    if not row:
        raise HTTPException(404, "Utente non trovato")

    db.execute(
        "UPDATE utenti SET [ruolo]=?, [personale_id]=?, [comando_id]=?, [attivo]=? WHERE id=?",
        (body.get("ruolo", row["ruolo"]),
         body.get("personale_id", row.get("personale_id")),
         body.get("comando_id", row.get("comando_id")),
         body.get("attivo", row.get("attivo", True)),
         uid)
    )
    # Disattivazione → chiudi subito le sessioni aperte
    if body.get("attivo") is False:
        db.execute("DELETE FROM sessioni WHERE utente_id=?", (uid,))

    return _utente_out(db.fetch_one("SELECT * FROM utenti WHERE id=?", (uid,)))


@router.put("/{uid}/password")
def reset_password(uid: int, body: dict):
    """Reset password da parte dell'admin (senza conoscere la vecchia)."""
    if not body.get("password"):
        raise HTTPException(422, "Password obbligatoria")
    row = db.fetch_one("SELECT id FROM utenti WHERE id=?", (uid,))
    if not row:
        raise HTTPException(404, "Utente non trovato")
    db.execute(
        "UPDATE utenti SET password_hash=? WHERE id=?",
        (_hash_password(body["password"]), uid)
    )
    # Invalida le sessioni esistenti dell'utente
    db.execute("DELETE FROM sessioni WHERE utente_id=?", (uid,))
    return {"ok": True}
