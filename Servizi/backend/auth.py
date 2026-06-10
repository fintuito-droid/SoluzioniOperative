"""
auth.py — Autenticazione semplice, pronta per CAS/JWT
======================================================
FASE 1: Token statico per sviluppo/test.
FASE 2: Sostituire _decode_token() con CAS ticket validation o JWT decode.
        Il resto dell'applicazione non cambia.

Il contratto pubblico di questo modulo è:
  - get_current_user(token) → Utente
  - require_role(*ruoli) → dependency FastAPI
"""

import hashlib
import secrets
from typing import Optional
from fastapi import Header, HTTPException, status, Depends
from db.database import db
from models.models import Utente, RuoloUtente


# ── Token store in-memory (solo per sviluppo/Access) ────────────────────────
# In produzione con JWT questo dizionario non esiste più.
_active_tokens: dict[str, dict] = {}


def _hash_password(password: str) -> str:
    """SHA-256 semplice per Access. In produzione: bcrypt."""
    return hashlib.sha256(password.encode()).hexdigest()


def _generate_token() -> str:
    return secrets.token_hex(32)


def login(username: str, password: str) -> Optional[dict]:
    """
    Verifica credenziali e ritorna token + info utente.
    MIGRAZIONE: sostituire il corpo con CAS ticket validation o OAuth2.
    """
    pw_hash = _hash_password(password)
    row = db.fetch_one(
        "SELECT * FROM utenti WHERE username=? AND password_hash=? AND attivo=True",
        (username, pw_hash)
    )
    if not row:
        return None

    token = _generate_token()
    _active_tokens[token] = {
        "id":           row["id"],
        "username":     row["username"],
        "ruolo":        row["ruolo"],
        "personale_id": row.get("personale_id"),
        "comando_id":   row.get("comando_id"),
    }

    # Aggiorna ultimo_accesso
    db.execute(
        "UPDATE utenti SET ultimo_accesso=NOW() WHERE id=?",
        (row["id"],)
    )

    return {
        "access_token": token,
        "token_type":   "bearer",
        "ruolo":        row["ruolo"],
        "personale_id": row.get("personale_id"),
        "username":     row["username"],
    }


def logout(token: str) -> None:
    _active_tokens.pop(token, None)


def _decode_token(token: str) -> Optional[dict]:
    """
    PUNTO DI SOSTITUZIONE PER CAS/JWT.
    Oggi: lookup in dizionario in-memory.
    Domani: return jwt.decode(token, SECRET, algorithms=["HS256"])
            oppure: return cas_client.validate_ticket(token)
    """
    return _active_tokens.get(token)


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
