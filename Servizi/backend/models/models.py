"""
models.py — Modelli Pydantic condivisi
=======================================
Questi modelli sono indipendenti dal DB.
Usati sia per la validazione degli input API
che per la serializzazione degli output.
Nessuna modifica necessaria alla migrazione.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import date, datetime
from enum import Enum


# ── Enum di dominio ──────────────────────────────────────────────────────────

class RuoloUtente(str, Enum):
    admin        = "admin"
    responsabile = "responsabile"
    dipendente   = "dipendente"

class StatoPresenza(str, Enum):
    programmato = "programmato"
    confermato  = "confermato"
    modificato  = "modificato"
    assente     = "assente"


# ── Lookup: Postazione ───────────────────────────────────────────────────────

class PostazioneBase(BaseModel):
    codice: str = Field(..., max_length=20)
    nome:   str = Field(..., max_length=100)
    note:   Optional[str] = None
    attiva: bool = True

class PostazioneCreate(PostazioneBase):
    pass

class Postazione(PostazioneBase):
    id:               int
    turni_multipli:   Optional[bool] = None
    slot_funzionario: Optional[int]  = None
    slot_tas2:        Optional[int]  = None
    slot_addetto:     Optional[int]  = None
    class Config:
        from_attributes = True


# ── Lookup: Campagna AIB ─────────────────────────────────────────────────────

class CampagnaBase(BaseModel):
    anno:        int
    data_inizio: date
    data_fine:   date
    descrizione: Optional[str] = None
    attiva:      bool = True

class CampagnaCreate(CampagnaBase):
    pass

class Campagna(CampagnaBase):
    id: int
    class Config:
        from_attributes = True


# ── Lookup: Funzione servizio ────────────────────────────────────────────────

class FunzioneBase(BaseModel):
    codice:      str = Field(..., max_length=30)
    descrizione: Optional[str] = None

class FunzioneCreate(FunzioneBase):
    pass

class Funzione(FunzioneBase):
    id: int
    class Config:
        from_attributes = True


# ── Specialità ───────────────────────────────────────────────────────────────

class Specialita(BaseModel):
    id:          int
    codice:      str
    descrizione: Optional[str] = None
    class Config:
        from_attributes = True


# ── Personale ────────────────────────────────────────────────────────────────

class PersonaleBase(BaseModel):
    matricola:    Optional[str] = Field(None, max_length=20)
    qualifica_id: Optional[int] = None
    cognome:      str = Field(..., max_length=100)
    nome:         str = Field(..., max_length=100)
    telefono:     Optional[str] = Field(None, max_length=20)
    comando_id:   Optional[int] = None
    email:        Optional[str] = Field(None, max_length=150)
    attivo:       bool = True
    note:         Optional[str] = None

class PersonaleCreate(PersonaleBase):
    pass

class PersonaleUpdate(BaseModel):
    """Solo i campi che un utente può modificare sulla propria anagrafica."""
    telefono: Optional[str] = Field(None, max_length=20)
    email:    Optional[str] = Field(None, max_length=150)
    note:     Optional[str] = None

class PersonaleAdminUpdate(PersonaleBase):
    """Aggiornamento completo, solo per Admin/Responsabile."""
    pass

class Personale(PersonaleBase):
    id:             int
    qualifica_cod:  Optional[str] = None
    comando_cod:    Optional[str] = None
    specialita:     list[Specialita] = []
    class Config:
        from_attributes = True


# ── Utente ───────────────────────────────────────────────────────────────────

class UtenteBase(BaseModel):
    username:    str = Field(..., max_length=50)
    ruolo:       RuoloUtente
    personale_id: Optional[int] = None
    comando_id:  Optional[int] = None
    attivo:      bool = True

class UtenteCreate(UtenteBase):
    password: str  # plain text in input, hashato prima del salvataggio

class Utente(UtenteBase):
    id:            int
    ultimo_accesso: Optional[datetime] = None
    class Config:
        from_attributes = True

class UtenteLogin(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type:   str = "bearer"
    ruolo:        RuoloUtente
    personale_id: Optional[int]
    username:     str
    moduli:       list[str] = []


# ── Presenze ─────────────────────────────────────────────────────────────────

class PresenzaBase(BaseModel):
    campagna_id:   int
    personale_id:  int
    postazione_id: int
    funzione_id:   int
    data_servizio: date
    orario_inizio: str
    orario_fine:   str
    ore_totali:    Optional[float] = None
    note_consuntivo: Optional[str] = None
    fascia_oraria: Optional[str]  = Field(None, max_length=1)  # U M P

    @field_validator("data_servizio", mode="before")
    @classmethod
    def coerce_date(cls, v):
        if isinstance(v, datetime):
            return v.date()
        return v

    @field_validator("orario_inizio", "orario_fine", mode="before")
    @classmethod
    def normalizza_orario(cls, v):
        if v is None:
            return "00:00"
        s = str(v).strip()
        if ":" in s:
            h, m = s.split(":", 1)
            return f"{int(h):02d}:{m[:2]}"
        return s

    @field_validator("ore_totali", mode="before")
    @classmethod
    def arrotonda_ore(cls, v):
        if v is None:
            return v
        return round(float(v), 1)

class PresenzaCreate(PresenzaBase):
    """Crea un turno in stato 'programmato'."""
    pass

class PresenzaConsuntivo(BaseModel):
    """Conferma o modifica un turno programmato."""
    orario_inizio:   Optional[str] = None
    orario_fine:     Optional[str] = None
    ore_totali:      Optional[float] = None
    stato:           StatoPresenza = StatoPresenza.confermato
    note_consuntivo: Optional[str] = None

class Presenza(PresenzaBase):
    id:           int
    stato:        StatoPresenza
    creato_da:    Optional[int]
    creato_il:    Optional[datetime]
    modificato_il: Optional[datetime]
    # Campi denormalizzati per il frontend (da JOIN nelle query)
    cognome:      Optional[str] = None
    nome_dip:     Optional[str] = None
    qualifica:    Optional[str] = None
    postazione:   Optional[str] = None
    funzione:     Optional[str] = None
    postazione_id: Optional[int] = None  # ridondante ma utile al frontend per filtri
    funzione_id:   Optional[int] = None
    class Config:
        from_attributes = True


# ── Monte ore (aggregazione) ─────────────────────────────────────────────────

class MonteOrePersonale(BaseModel):
    personale_id:  int
    cognome:       str
    nome:          str
    qualifica:     Optional[str]
    comando:       Optional[str]
    comando_id:    Optional[int] = None
    ore_totali:    float
    turni_totali:  int
    ore_per_funzione: dict[str, float] = {}  # {"FUNZIONARIO": 36.0, "TAS 2": 12.0}


# ── Filtri query presenze ────────────────────────────────────────────────────

class FiltroPresenze(BaseModel):
    campagna_id:   Optional[int] = None
    personale_id:  Optional[int] = None
    postazione_id: Optional[int] = None
    funzione_id:   Optional[int] = None
    data_da:       Optional[date] = None
    data_a:        Optional[date] = None
    stato:         Optional[StatoPresenza] = None
    comando_id:    Optional[int] = None
