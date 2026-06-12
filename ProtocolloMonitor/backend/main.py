# ======================================================================================
# ProtocolloMonitor - Backend FastAPI
# ======================================================================================

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes.protocollo_monitor import router as protocollo_monitor_router
from backend.core.platform_auth import get_current_user


# ======================================================================================
# CONFIGURAZIONE APPLICAZIONE FASTAPI
# ======================================================================================

app = FastAPI(
    title="ProtocolloMonitor API",
    version="0.1.0"
)


# ======================================================================================
# CORS
# ======================================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:5175",
        "http://127.0.0.1:5175",
        "http://localhost:5176",
        "http://127.0.0.1:5176",
        "http://localhost:5177",
        "http://127.0.0.1:5177",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Tutte le rotte del modulo richiedono il token piattaforma SoluzioniOperative
app.include_router(protocollo_monitor_router, dependencies=[Depends(get_current_user)])


# ======================================================================================
# ROTTA TEST
# ======================================================================================

@app.get("/")
def home():
    return {
        "app": "ProtocolloMonitor API",
        "status": "ok"
    }
