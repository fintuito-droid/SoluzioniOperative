"""
auth.py — Autenticazione con sessioni persistenti su DB
========================================================
I token sono salvati nella tabella `sessioni` con scadenza:
sopravvivono ai riavvii del backend. Una cache in-memory evita
una query Access per ogni richiesta.

MIGRAZIONE FUTURA (login unico piattaforma): sostituire _decode_token()
con JWT decode o CAS ticket validation. Il resto non cambia.

Contratto pubblico:
  - login(username, password) → dict token/utente
  - logout(token)
  - get_current_user(authorization) → dependency FastAPI
  - require_role(*ruoli) → dependency factory
  - cambia_password(utente_id, vecchia, nuova) → bool
"""

import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Header, HTTPException, status, Depends
from db.database import db
from models.models import RuoloUtente

# Durata sessione
SESSIONE_ORE = 12

# Moduli della piattaforma SoluzioniOperative.
# Gli admin sono abilitati a tutti; gli altri utenti solo a quelli
# presenti in utenti_moduli (tabella creata da migrate_moduli.py).
MODULI_PIATTAFORMA = ["servizi", "protocollo-monitor", "xr33"]

# Cache token → (user_dict, scadenza). Evita query DB a ogni richiesta;
# la verità resta sul DB (sopravvive ai riavvii).
_token_cache: dict[str, tuple[dict, datetime]] = {}


def _hash_password(password: str) -> str:
    """SHA-256 semplice per Access. In produzione: bcrypt."""
    return hashlib.sha256(password.encode()).hexdigest()


def _generate_token() -> str:
    return secrets.token_hex(32)


def moduli_utente(utente_id: int, ruolo: str) -> list[str]:
    """Codici dei moduli abilitati per l'utente. Admin: tutti."""
    if ruolo == "admin":
        return list(MODULI_PIATTAFORMA)
    rows = db.fetch_all(
        "SELECT codice_modulo FROM utenti_moduli WHERE utente_id=?", (utente_id,)
    )
    return [r["codice_modulo"] for r in rows]


def _user_dict(row: dict) -> dict:
    return {
        "id":           row["id"],
        "username":     row["username"],
        "ruolo":        row["ruolo"],
        "personale_id": row.get("personale_id"),
        "comando_id":   row.get("comando_id"),
        "moduli":       moduli_utente(row["id"], row["ruolo"]),
    }


def invalida_cache_utente(utente_id: int) -> None:
    """Rimuove dalla cache i token dell'utente: alla prossima richiesta
    il dict utente viene ricaricato dal DB (ruolo/moduli aggiornati),
    senza chiudere le sessioni."""
    for tok in [t for t, (u, _) in _token_cache.items() if u["id"] == utente_id]:
        _token_cache.pop(tok, None)


def login(username: str, password: str) -> Optional[dict]:
    pw_hash = _hash_password(password)
    row = db.fetch_one(
        "SELECT * FROM utenti WHERE username=? AND password_hash=? AND attivo=True",
        (username, pw_hash)
    )
    if not row:
        return None

    token    = _generate_token()
    adesso   = datetime.now()
    scadenza = adesso + timedelta(hours=SESSIONE_ORE)

    db.execute(
        "INSERT INTO sessioni ([token],[utente_id],[scadenza],[creato_il]) VALUES (?,?,?,?)",
        (token, row["id"], scadenza, adesso)
    )
    # Pulizia opportunistica delle sessioni scadute
    db.execute("DELETE FROM sessioni WHERE scadenza < ?", (adesso,))

    db.execute("UPDATE utenti SET ultimo_accesso=? WHERE id=?", (adesso, row["id"]))

    user = _user_dict(row)
    _token_cache[token] = (user, scadenza)

    return {
        "access_token": token,
        "token_type":   "bearer",
        "ruolo":        row["ruolo"],
        "personale_id": row.get("personale_id"),
        "username":     row["username"],
        "moduli":       user["moduli"],
    }


def logout(token: str) -> None:
    _token_cache.pop(token, None)
    db.execute("DELETE FROM sessioni WHERE token=?", (token,))


def cambia_password(utente_id: int, vecchia: str, nuova: str) -> bool:
    """Cambia la password verificando quella attuale. True se riuscito."""
    row = db.fetch_one(
        "SELECT id FROM utenti WHERE id=? AND password_hash=?",
        (utente_id, _hash_password(vecchia))
    )
    if not row:
        return False
    db.execute(
        "UPDATE utenti SET password_hash=? WHERE id=?",
        (_hash_password(nuova), utente_id)
    )
    return True


def _decode_token(token: str) -> Optional[dict]:
    """
    PUNTO DI SOSTITUZIONE PER JWT/CAS (login unico piattaforma).
    Oggi: cache in-memory con fallback su tabella sessioni.
    """
    adesso = datetime.now()

    cached = _token_cache.get(token)
    if cached:
        user, scadenza = cached
        if scadenza > adesso:
            return user
        _token_cache.pop(token, None)
        return None

    # Cache miss (es. dopo riavvio backend): verifica su DB
    sess = db.fetch_one("SELECT * FROM sessioni WHERE token=?", (token,))
    if not sess:
        return None
    scadenza = sess["scadenza"]
    if isinstance(scadenza, str):
        scadenza = datetime.fromisoformat(scadenza)
    if scadenza <= adesso:
        db.execute("DELETE FROM sessioni WHERE token=?", (token,))
        return None

    row = db.fetch_one("SELECT * FROM utenti WHERE id=? AND attivo=True", (sess["utente_id"],))
    if not row:
        return None

    user = _user_dict(row)
    _token_cache[token] = (user, scadenza)
    return user


# ── FastAPI Dependencies ─────────────────────────────────────────────────────

def get_current_user(authorization: str = Header(...)) -> dict:
    """
    Dependency FastAPI. Estrae e valida il token dall'header Authorization.
    Header atteso: "Bearer <token>"
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token mancante o formato errato"
        )
    token = authorization.removeprefix("Bearer ").strip()
    user = _decode_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token non valido o scaduto"
        )
    return user


def require_role(*ruoli: RuoloUtente):
    """
    Dependency factory. Uso:
      @router.get("/...", dependencies=[Depends(require_role("admin"))])
    """
    def _check(current_user: dict = Depends(get_current_user)):
        if current_user["ruolo"] not in ruoli:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Accesso riservato a: {', '.join(ruoli)}"
            )
        return current_user
    return _check


def require_self_or_role(personale_id: int, *ruoli: RuoloUtente):
    """
    Permette accesso se l'utente è il dipendente stesso O ha uno dei ruoli.
    """
    def _check(current_user: dict = Depends(get_current_user)):
        is_self  = current_user.get("personale_id") == personale_id
        has_role = current_user["ruolo"] in ruoli
        if not (is_self or has_role):
            raise HTTPException(status_code=403, detail="Accesso non autorizzato")
        return current_user
    return _check
