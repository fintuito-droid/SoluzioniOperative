from pydantic import BaseModel
from typing import List, Optional

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UtenteOut(BaseModel):
    id: int
    username: str
    ruolo: str
    comando_id: Optional[int] = None

    class Config:
        from_attributes = True

class ComandoOut(BaseModel):
    id: int
    nome: str

    class Config:
        from_attributes = True

class StazioneOut(BaseModel):
    id: int
    nome_stazione: str

    class Config:
        from_attributes = True

class OperatoreOut(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True

class ControlloInput(BaseModel):
    tipo_controllo: str
    esito: Optional[str] = None
    note: Optional[str] = None
    foto_path: Optional[str] = None

class ChecklistCreate(BaseModel):
    stazione_id: int
    tipo_attivita: str
    note_generali: Optional[str] = None
    operatori_ids: List[int]
    controlli: List[ControlloInput]