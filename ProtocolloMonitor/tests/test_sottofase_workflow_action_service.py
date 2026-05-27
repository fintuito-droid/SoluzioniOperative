import pytest

from backend.services.sottofase_workflow_action_service import (
    WorkflowActionValidationError,
    validate_sottofase_workflow_action,
)


def make_workflow(*, active_code="REDIGI", completed_codes=None, percentuale=0):
    completed_codes = set(completed_codes or [])
    steps = [
        ("REDIGI", 1),
        ("REVISIONA", 2),
        ("FIRMA", 3),
        ("PROTOCOLLA", 4),
        ("FINE", 5),
    ]

    return {
        "stepCorrente": next(
            ordine for codice, ordine in steps if codice == active_code
        ),
        "workflow": [
            {
                "codice": codice,
                "titolo": codice.title(),
                "ordine": ordine,
                "completato": codice in completed_codes,
                "attivo": codice == active_code,
            }
            for codice, ordine in steps
        ],
        "percentualeAvanzamento": percentuale,
    }


def test_valid_redigi_action_moves_to_revisione():
    result = validate_sottofase_workflow_action(
        make_workflow(active_code="REDIGI", completed_codes=[]),
        {
            "azione": "AVVIA_REDAZIONE",
            "testoOperatore": "Pronta per la revisione",
            "utenteOperatore": "Francesco Matranga",
        },
    )

    assert result == {
        "valida": True,
        "azione": "AVVIA_REDAZIONE",
        "stepDestinazione": "REVISIONA",
        "messaggio": "Redazione validata: prossimo step Revisione.",
    }


def test_unknown_action_is_rejected():
    with pytest.raises(WorkflowActionValidationError) as exc_info:
        validate_sottofase_workflow_action(
            make_workflow(active_code="REDIGI"),
            {"azione": "AZIONE_NON_AMMESSA"},
        )

    assert exc_info.value.message == "Azione non ammessa."


def test_missing_action_is_rejected():
    with pytest.raises(WorkflowActionValidationError) as exc_info:
        validate_sottofase_workflow_action(
            make_workflow(active_code="REDIGI"),
            {"testoOperatore": "Test senza azione"},
        )

    assert exc_info.value.message == "Azione obbligatoria."


def test_step_jump_is_rejected():
    with pytest.raises(WorkflowActionValidationError) as exc_info:
        validate_sottofase_workflow_action(
            make_workflow(active_code="REDIGI"),
            {"azione": "SEGNA_FIRMATO"},
        )

    assert exc_info.value.message == "Non e possibile saltare step del workflow."


def test_early_close_is_rejected_before_protocollo_completion():
    with pytest.raises(WorkflowActionValidationError) as exc_info:
        validate_sottofase_workflow_action(
            make_workflow(
                active_code="FINE",
                completed_codes={"REDIGI", "REVISIONA", "FIRMA"},
            ),
            {"azione": "CHIUDI_SOTTOFASE"},
        )

    assert (
        exc_info.value.message
        == "Non e possibile chiudere la sottofase prima della protocollazione."
    )


def test_long_operator_text_is_rejected():
    with pytest.raises(WorkflowActionValidationError) as exc_info:
        validate_sottofase_workflow_action(
            make_workflow(active_code="REDIGI"),
            {
                "azione": "AVVIA_REDAZIONE",
                "testoOperatore": "x" * 1001,
            },
        )

    assert (
        exc_info.value.message
        == "testoOperatore supera il limite massimo di 1000 caratteri."
    )


def test_completed_workflow_is_rejected():
    with pytest.raises(WorkflowActionValidationError) as exc_info:
        validate_sottofase_workflow_action(
            make_workflow(
                active_code="FINE",
                completed_codes={
                    "REDIGI",
                    "REVISIONA",
                    "FIRMA",
                    "PROTOCOLLA",
                    "FINE",
                },
                percentuale=100,
            ),
            {"azione": "CHIUDI_SOTTOFASE"},
        )

    assert exc_info.value.message == "Workflow gia completato."


def test_backward_action_is_rejected():
    with pytest.raises(WorkflowActionValidationError) as exc_info:
        validate_sottofase_workflow_action(
            make_workflow(
                active_code="FIRMA",
                completed_codes={"REDIGI", "REVISIONA"},
            ),
            {"azione": "AVVIA_REDAZIONE"},
        )

    assert exc_info.value.message == "Non e possibile tornare indietro nel workflow."


def test_firma_action_is_valid_without_current_document():
    result = validate_sottofase_workflow_action(
        make_workflow(
            active_code="FIRMA",
            completed_codes={"REDIGI", "REVISIONA"},
            percentuale=40,
        ),
        {"azione": "SEGNA_FIRMATO"},
    )

    assert result == {
        "valida": True,
        "azione": "SEGNA_FIRMATO",
        "stepDestinazione": "PROTOCOLLA",
        "messaggio": "Firma validata: prossimo step Protocolla.",
    }


def test_protocollo_action_is_valid_when_protocollo_is_active():
    result = validate_sottofase_workflow_action(
        make_workflow(
            active_code="PROTOCOLLA",
            completed_codes={"REDIGI", "REVISIONA", "FIRMA"},
            percentuale=60,
        ),
        {"azione": "SEGNA_PROTOCOLLATO"},
    )

    assert result == {
        "valida": True,
        "azione": "SEGNA_PROTOCOLLATO",
        "stepDestinazione": "FINE",
        "messaggio": "Protocollazione validata: prossimo step Fine.",
    }


def test_close_action_is_valid_when_fine_is_active_and_protocollo_completed():
    result = validate_sottofase_workflow_action(
        make_workflow(
            active_code="FINE",
            completed_codes={"REDIGI", "REVISIONA", "FIRMA", "PROTOCOLLA"},
            percentuale=80,
        ),
        {"azione": "CHIUDI_SOTTOFASE"},
    )

    assert result == {
        "valida": True,
        "azione": "CHIUDI_SOTTOFASE",
        "stepDestinazione": "FINE",
        "messaggio": "Chiusura sottofase validata.",
    }


def test_cannot_jump_from_firma_to_close():
    with pytest.raises(WorkflowActionValidationError) as exc_info:
        validate_sottofase_workflow_action(
            make_workflow(
                active_code="FIRMA",
                completed_codes={"REDIGI", "REVISIONA"},
                percentuale=40,
            ),
            {"azione": "CHIUDI_SOTTOFASE"},
        )

    assert exc_info.value.message == (
        "Non e possibile chiudere la sottofase prima della protocollazione."
    )
