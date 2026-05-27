"""Validazione pura delle future azioni workflow sottofase.

Questo service non accede al database, non usa repository e non esegue alcuna
scrittura. Riceve:

- il workflow corrente gia letto dall'endpoint read-only `/workflow`;
- il payload azione validabile tramite Pydantic.

Lo scopo e preparare il contratto tecnico dello Step 30L-10. Nello step
successivo, quando saranno autorizzate scritture reali, qui andra agganciato un
service applicativo che potra aggiornare in modo controllato:

- `T_ProcedimentoSottofasi.StepCorrente`;
- `T_ProcedimentoSottofasi.TestoOperatore`;
- `T_ProcedimentoSottofasi.DataUltimaAzione`;
- eventuali record in `T_SottofaseStepOperativi`;
- eventuale storico/audit dell'azione.

Fino ad allora questo modulo resta side-effect free: nessun INSERT, nessun
UPDATE, nessun DELETE.
"""

from __future__ import annotations

from typing import Any, Mapping

from pydantic import ValidationError

from backend.schemas.sottofase_workflow import (
    SottofaseWorkflowAzione,
    SottofaseWorkflowAzionePayload,
)


class WorkflowActionValidationError(ValueError):
    """Errore controllato per payload o transizioni workflow non validi."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


STEP_ORDER = {
    "REDIGI": 1,
    "REVISIONA": 2,
    "FIRMA": 3,
    "PROTOCOLLA": 4,
    "FINE": 5,
}


ACTION_TRANSITIONS = {
    SottofaseWorkflowAzione.AVVIA_REDAZIONE: {
        "step_atteso": "REDIGI",
        "step_destinazione": "REVISIONA",
        "messaggio": "Redazione validata: prossimo step Revisione.",
    },
    SottofaseWorkflowAzione.INVIA_REVISIONE: {
        "step_atteso": "REVISIONA",
        "step_destinazione": "FIRMA",
        "messaggio": "Revisione validata: prossimo step Firma.",
    },
    SottofaseWorkflowAzione.SEGNA_FIRMATO: {
        "step_atteso": "FIRMA",
        "step_destinazione": "PROTOCOLLA",
        "messaggio": "Firma validata: prossimo step Protocolla.",
    },
    SottofaseWorkflowAzione.SEGNA_PROTOCOLLATO: {
        "step_atteso": "PROTOCOLLA",
        "step_destinazione": "FINE",
        "messaggio": "Protocollazione validata: prossimo step Fine.",
    },
    SottofaseWorkflowAzione.CHIUDI_SOTTOFASE: {
        "step_atteso": "FINE",
        "step_destinazione": "FINE",
        "messaggio": "Chiusura sottofase validata.",
    },
}


def validate_sottofase_workflow_action(
    workflow_corrente: Mapping[str, Any] | None,
    payload: SottofaseWorkflowAzionePayload | Mapping[str, Any],
) -> dict[str, Any]:
    """Valida una futura azione workflow senza produrre effetti collaterali.

    Parametri:
    - workflow_corrente: risposta gia calcolata dal workflow read-only della
      sottofase;
    - payload: modello Pydantic o dizionario con azione, testoOperatore e
      utenteOperatore.

    Restituisce un dizionario applicativo stabile:
    {
      "valida": true,
      "azione": "...",
      "stepDestinazione": "...",
      "messaggio": "..."
    }

    In caso di payload o transizione non validi solleva
    `WorkflowActionValidationError` con messaggio leggibile dalla futura API.
    """

    normalized_payload = _normalize_payload(payload)
    steps = _extract_workflow_steps(workflow_corrente)

    if not steps:
        raise WorkflowActionValidationError("Workflow corrente non disponibile.")

    if _workflow_is_completed(workflow_corrente, steps):
        raise WorkflowActionValidationError("Workflow gia completato.")

    transition = ACTION_TRANSITIONS[normalized_payload.azione]
    expected_step = transition["step_atteso"]
    destination_step = transition["step_destinazione"]
    active_step = _get_active_step(steps)

    if active_step is None:
        raise WorkflowActionValidationError(
            "Workflow corrente privo di step attivo."
        )

    active_code = active_step.get("codice")

    if (
        normalized_payload.azione == SottofaseWorkflowAzione.CHIUDI_SOTTOFASE
        and not _is_step_completed(steps, "PROTOCOLLA")
    ):
        raise WorkflowActionValidationError(
            "Non e possibile chiudere la sottofase prima della protocollazione."
        )

    _validate_step_sequence(
        steps=steps,
        active_code=active_code,
        expected_step=expected_step,
    )

    return {
        "valida": True,
        "azione": normalized_payload.azione.value,
        "stepDestinazione": destination_step,
        "messaggio": transition["messaggio"],
    }


def _normalize_payload(
    payload: SottofaseWorkflowAzionePayload | Mapping[str, Any],
) -> SottofaseWorkflowAzionePayload:
    """Converte il payload in modello Pydantic o produce errore controllato."""

    if isinstance(payload, SottofaseWorkflowAzionePayload):
        return payload

    try:
        return SottofaseWorkflowAzionePayload(**dict(payload))
    except ValidationError as exc:
        raise WorkflowActionValidationError(_message_from_validation_error(exc))
    except (TypeError, ValueError):
        raise WorkflowActionValidationError("Payload azione non valido.")


def _message_from_validation_error(exc: ValidationError) -> str:
    """Trasforma errori Pydantic in messaggi stabili per la futura API."""

    errors = exc.errors()
    first_error = errors[0] if errors else {}
    location = tuple(first_error.get("loc", ()))

    if "azione" in location:
        error_type = str(first_error.get("type", ""))
        if "missing" in error_type:
            return "Azione obbligatoria."
        return "Azione non ammessa."

    if "testoOperatore" in location:
        return "testoOperatore supera il limite massimo di 1000 caratteri."

    return "Payload azione non valido."


def _extract_workflow_steps(
    workflow_corrente: Mapping[str, Any] | None,
) -> list[dict[str, Any]]:
    """Estrae e ordina gli step dalla risposta read-only del workflow."""

    if not workflow_corrente:
        return []

    raw_steps = workflow_corrente.get("workflow") or []

    if not isinstance(raw_steps, list):
        return []

    return sorted(
        [step for step in raw_steps if isinstance(step, Mapping)],
        key=lambda step: int(step.get("ordine") or STEP_ORDER.get(step.get("codice"), 0)),
    )


def _workflow_is_completed(
    workflow_corrente: Mapping[str, Any] | None,
    steps: list[Mapping[str, Any]],
) -> bool:
    """Determina se il workflow risulta gia concluso."""

    percentuale = 0

    if workflow_corrente:
        try:
            percentuale = int(workflow_corrente.get("percentualeAvanzamento") or 0)
        except (TypeError, ValueError):
            percentuale = 0

    return percentuale >= 100 or all(bool(step.get("completato")) for step in steps)


def _get_active_step(steps: list[Mapping[str, Any]]) -> Mapping[str, Any] | None:
    """Restituisce lo step attivo calcolato dal workflow read-only."""

    for step in steps:
        if step.get("attivo"):
            return step

    return None


def _is_step_completed(
    steps: list[Mapping[str, Any]],
    step_code: str,
) -> bool:
    """Verifica se uno step del workflow corrente risulta completato."""

    for step in steps:
        if step.get("codice") == step_code:
            return bool(step.get("completato"))

    return False


def _validate_step_sequence(
    *,
    steps: list[Mapping[str, Any]],
    active_code: str | None,
    expected_step: str,
) -> None:
    """Impedisce salti in avanti, ritorni indietro e azioni non coerenti."""

    active_order = STEP_ORDER.get(active_code or "")
    expected_order = STEP_ORDER.get(expected_step)

    if active_order is None or expected_order is None:
        raise WorkflowActionValidationError(
            "Workflow corrente non riconosciuto."
        )

    if _is_step_completed(steps, expected_step) and active_order > expected_order:
        raise WorkflowActionValidationError(
            "Non e possibile tornare indietro nel workflow."
        )

    if active_order < expected_order:
        raise WorkflowActionValidationError(
            "Non e possibile saltare step del workflow."
        )

    if active_order > expected_order:
        raise WorkflowActionValidationError(
            "Azione non coerente con lo step attivo corrente."
        )

    if active_code != expected_step:
        raise WorkflowActionValidationError(
            "Azione non coerente con lo step attivo corrente."
        )
