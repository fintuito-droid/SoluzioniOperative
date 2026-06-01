"""Contratti Pydantic per i partecipanti di una sottofase."""

from __future__ import annotations

from enum import Enum
import re

from pydantic import BaseModel, Field, field_validator


class RuoloPartecipanteSottofase(str, Enum):
    """Ruoli ammessi per i partecipanti collegati a una sottofase."""

    OPERATORE = "OPERATORE"
    REVISORE = "REVISORE"
    FIRMATARIO = "FIRMATARIO"
    PROTOCOLLATORE = "PROTOCOLLATORE"
    APPROVATORE = "APPROVATORE"
    OSSERVATORE = "OSSERVATORE"


class StatoPartecipanteSottofase(str, Enum):
    """Stati iniziali ammessi per un partecipante sottofase."""

    ASSEGNATO = "ASSEGNATO"
    IN_ATTESA = "IN_ATTESA"
    IN_CORSO = "IN_CORSO"
    COMPLETATO = "COMPLETATO"
    RESPINTO = "RESPINTO"
    ANNULLATO = "ANNULLATO"


RUOLI_PARTECIPANTE_SOTTOFASE_AMMESSI = tuple(
    ruolo.value for ruolo in RuoloPartecipanteSottofase
)
STATI_PARTECIPANTE_SOTTOFASE_AMMESSI = tuple(
    stato.value for stato in StatoPartecipanteSottofase
)


_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class SottofasePartecipantePayload(BaseModel):
    """Payload per inserire un partecipante collegato a una sottofase."""

    idStepOperativo: int | None = None
    nomeVisualizzato: str = Field(..., min_length=1, max_length=255)
    email: str | None = Field(default=None, max_length=255)
    ruolo: RuoloPartecipanteSottofase
    statoPartecipante: StatoPartecipanteSottofase
    ordine: int | None = None
    coloreAvatar: str | None = Field(default=None, max_length=20)
    iniziali: str | None = Field(default=None, max_length=10)
    notePartecipante: str | None = None

    @field_validator("nomeVisualizzato")
    @classmethod
    def _nome_non_vuoto(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("nomeVisualizzato obbligatorio.")
        return normalized

    @field_validator("email")
    @classmethod
    def _email_forma_semplice(cls, value: str | None) -> str | None:
        if value is None:
            return None

        normalized = value.strip()
        if not normalized:
            return None

        if not _EMAIL_RE.match(normalized):
            raise ValueError("email non valida.")

        return normalized

    @field_validator("coloreAvatar")
    @classmethod
    def _colore_opzionale_non_vuoto(cls, value: str | None) -> str | None:
        if value is None:
            return None

        normalized = value.strip()
        return normalized or None

    @field_validator("iniziali")
    @classmethod
    def _iniziali_opzionali_normalizzate(cls, value: str | None) -> str | None:
        if value is None:
            return None

        normalized = value.strip().upper()
        return normalized or None
