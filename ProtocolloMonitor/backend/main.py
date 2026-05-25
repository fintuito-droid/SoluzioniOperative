# ======================================================================================
# ProtocolloMonitor - Backend FastAPI
# ======================================================================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes.protocollo_monitor import router as protocollo_monitor_router


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
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(protocollo_monitor_router)


# ======================================================================================
# ROTTA TEST
# ======================================================================================

@app.get("/")
def home():
    return {
        "app": "ProtocolloMonitor API",
        "status": "ok"
    }
