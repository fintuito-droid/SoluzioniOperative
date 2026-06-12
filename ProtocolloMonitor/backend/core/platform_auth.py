"""
platform_auth.py — Validazione del token piattaforma SoluzioniOperative
=======================================================================
ProtocolloMonitor non ha utenti propri: delega la verifica del bearer token
all'auth provider della piattaforma (backend Servizi, porta 8001) chiamando
GET /auth/me. Una cache in-memory con TTL breve evita una chiamata HTTP
per ogni richiesta.

Richiede inoltre che l'utente sia abilitato al modulo 'protocollo-monitor'
(tabella utenti_moduli; gli admin sono abilitati a tutto).

Uso in main.py:
    app.include_router(router, dependencies=[Depends(get_current_user)])
"""

import json
import time
import urllib.error
import urllib.request

from fastapi import HTTPException, Request

AUTH_ME_URL = "http://127.0.0.1:8001/api/v1/auth/me"
CODICE_MODULO = "protocollo-monitor"
CACHE_TTL_SECONDI = 60.0

# token -> (user_dict, scadenza_cache)
_cache: dict[str, tuple[dict, float]] = {}


def _introspect(token: str) -> dict | None:
    """Chiede all'auth provider chi è il titolare del token. None se non valido."""
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
            503, "Servizio di autenticazione della piattaforma non raggiungibile"
        )


def get_current_user(request: Request) -> dict:
    auth_header = request.headers.get("authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header.removeprefix("Bearer ").strip()
    else:
        # Fallback per URL diretti (es. risorse aperte fuori da fetch)
        token = request.query_params.get("token", "")

    if not token:
        raise HTTPException(401, "Token mancante")

    adesso = time.time()
    hit = _cache.get(token)
    if hit and hit[1] > adesso:
        return hit[0]

    user = _introspect(token)
    if not user:
        _cache.pop(token, None)
        raise HTTPException(401, "Token non valido o scaduto")

    if CODICE_MODULO not in user.get("moduli", []):
        raise HTTPException(403, "Modulo ProtocolloMonitor non abilitato per l'utente")

    _cache[token] = (user, adesso + CACHE_TTL_SECONDI)
    return user
