"""
auth.py — XR33 dentro la piattaforma SoluzioniOperative
=======================================================
XR33 non valida più un JWT proprio: il bearer token è quello della
piattaforma e viene verificato chiamando l'auth provider (backend
Servizi, porta 8001) su GET /auth/me, con cache breve in-memory.

L'identità di dominio resta la tabella Utente di XR33: il titolare del
token piattaforma viene mappato PER USERNAME su un Utente XR33 attivo.
Se non esiste, 403 (l'utente va censito in XR33 con lo stesso username).

Il vecchio /login con JWT locale resta nel main solo come legacy:
i token che emette non sono più accettati.
"""

import json
import time
import urllib.error
import urllib.request

from datetime import datetime, timedelta, timezone
from jose import jwt
from passlib.context import CryptContext
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from database import get_db
from models import Utente

SECRET_KEY = "XR33_SUPER_SECRET_KEY_CAMBIA_QUESTA"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 12

AUTH_ME_URL = "http://127.0.0.1:8001/api/v1/auth/me"
CODICE_MODULO = "xr33"
CACHE_TTL_SECONDI = 60.0

# token piattaforma -> (payload /auth/me, scadenza cache)
_cache: dict[str, tuple[dict, float]] = {}

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer_scheme = HTTPBearer()

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, password_hash: str) -> bool:
    return pwd_context.verify(plain_password, password_hash)

def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def _introspect(token: str) -> dict | None:
    """Chiede all'auth provider della piattaforma chi è il titolare del token."""
    req = urllib.request.Request(
        AUTH_ME_URL, headers={"Authorization": f"Bearer {token}"}
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError:
        return None        # 401: token scaduto o non valido
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Servizio di autenticazione della piattaforma non raggiungibile",
        )

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> Utente:
    token = credentials.credentials

    adesso = time.time()
    hit = _cache.get(token)
    if hit and hit[1] > adesso:
        info = hit[0]
    else:
        info = _introspect(token)
        if not info:
            _cache.pop(token, None)
            raise HTTPException(status_code=401, detail="Token non valido o scaduto")
        _cache[token] = (info, adesso + CACHE_TTL_SECONDI)

    if CODICE_MODULO not in info.get("moduli", []):
        raise HTTPException(status_code=403, detail="Modulo XR33 non abilitato per l'utente")

    user = (
        db.query(Utente)
        .filter(Utente.username == info["username"], Utente.attivo == True)
        .first()
    )
    if not user:
        raise HTTPException(
            status_code=403,
            detail="Utente non censito nel modulo XR33 (username piattaforma senza corrispondenza)",
        )

    return user