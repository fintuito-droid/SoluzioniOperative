"""Contratti Pydantic per le future azioni workflow della sottofase.

Il modulo definisce solo il contratto dati che potra essere usato dal futuro
endpoint:

POST /protocollo-monitor/sottofasi/{id_sottofase}/workflow/azioni

In questo step il contratto non viene collegato ad alcuna scrittura reale. Non
apre connessioni Access, non modifica il database e non espone endpoint POST
operativi. Le mutazioni future dovranno essere implementate in uno step
dedicato, con repository separati e test di integrazione mirati.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


MAX_TESTO_OPERATORE_LENGTH = 1000


class SottofaseWorkflowAzione(str, Enum):
    """Azioni ammesse nel workflow guidato della sottofase.

    I valori sono intenzionalmente stabili e mai tradotti: saranno salvabili in
    Access oggi e in PostgreSQL domani senza dipendere dalle etichette UI.
    """

    AVVIA_REDAZIONE = "AVVIA_REDAZIONE"
    INVIA_REVISIONE = "INVIA_REVISIONE"
    SEGNA_FIRMATO = "SEGNA_FIRMATO"
    SEGNA_PROTOCOLLATO = "SEGNA_PROTOCOLLATO"
    CHIUDI_SOTTOFASE = "CHIUDI_SOTTOFASE"


AZIONI_WORKFLOW_SOTTOFASE_AMMESSE = tuple(
    azione.value for azione in SottofaseWorkflowAzione
)


class SottofaseWorkflowAzionePayload(BaseModel):
    """Payload futuro per avanzare il workflow operativo della sottofase.

    Campi:
    - azione: obbligatoria, deve appartenere alle azioni ammesse;
    - testoOperatore: opzionale, massimo 1000 caratteri;
    - utenteOperatore: opzionale, utile quando sara introdotto il contesto
      autenticato o un operatore esplicito.

    Il modello valida solo forma e limiti del payload. La coerenza della
    transizione rispetto al workflow corrente viene verificata dal service puro
    `sottofase_workflow_action_service`.
    """

    azione: SottofaseWorkflowAzione
    testoOperatore: str | None = Field(
        default=None,
        max_length=MAX_TESTO_OPERATORE_LENGTH,
    )
    utenteOperatore: str | None = None
