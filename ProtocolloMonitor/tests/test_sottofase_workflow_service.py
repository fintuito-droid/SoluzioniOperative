from backend.services.sottofase_workflow_service import SottofaseWorkflowService


class FakeSottofaseDocumentaleService:
    def __init__(self, quadro=None, raises=False):
        self.quadro = quadro
        self.raises = raises

    def get_quadro_documentale(self, id_sottofase):
        if self.raises:
            raise RuntimeError("errore test")

        if self.quadro is None:
            return None

        return {**self.quadro, "id_sottofase": id_sottofase}


def test_workflow_without_documentale_service_returns_none():
    service = SottofaseWorkflowService()

    assert service.get_workflow(1) is None


def test_workflow_returns_none_when_documentale_summary_missing():
    service = SottofaseWorkflowService(
        sottofase_documentale_service=FakeSottofaseDocumentaleService(
            quadro=None
        )
    )

    assert service.get_workflow(1) is None


def test_workflow_uses_safe_fallback_when_documentale_service_fails():
    service = SottofaseWorkflowService(
        sottofase_documentale_service=FakeSottofaseDocumentaleService(
            raises=True
        )
    )

    assert service.get_workflow(1) is None


def test_workflow_marks_revisione_active_when_redigi_history_exists():
    service = SottofaseWorkflowService(
        sottofase_documentale_service=FakeSottofaseDocumentaleService(
            quadro={
                "step_corrente": "REVISIONA",
                "ha_documento_collegato": False,
                "id_documento_corrente": None,
                "documento_corrente": None,
                "documenti": [],
                "step_operativi": [
                    {
                        "codice_step": "REDIGI",
                        "stato_step": "COMPLETATO",
                        "data_completamento": "2026-05-27 10:00:00",
                        "utente_completamento": "Operatore test",
                    }
                ],
            }
        )
    )

    workflow = service.get_workflow(7)
    redigi = workflow["workflow"][0]
    revisiona = workflow["workflow"][1]

    assert workflow["stepCorrente"] == 2
    assert workflow["percentualeAvanzamento"] == 20
    assert redigi["codice"] == "REDIGI"
    assert redigi["completato"] is True
    assert redigi["attivo"] is False
    assert redigi["timestamp"] == "2026-05-27 10:00:00"
    assert redigi["operatore"] == "Operatore test"
    assert revisiona["codice"] == "REVISIONA"
    assert revisiona["completato"] is False
    assert revisiona["attivo"] is True


def test_workflow_marks_firma_active_without_current_document():
    service = SottofaseWorkflowService(
        sottofase_documentale_service=FakeSottofaseDocumentaleService(
            quadro={
                "step_corrente": "FIRMA",
                "ha_documento_collegato": False,
                "id_documento_corrente": None,
                "documento_corrente": None,
                "documenti": [],
                "step_operativi": [
                    {
                        "codice_step": "REDIGI",
                        "stato_step": "COMPLETATO",
                    },
                    {
                        "codice_step": "REVISIONA",
                        "stato_step": "COMPLETATO",
                    },
                ],
            }
        )
    )

    workflow = service.get_workflow(5)
    redigi = workflow["workflow"][0]
    revisiona = workflow["workflow"][1]
    firma = workflow["workflow"][2]

    assert workflow["stepCorrente"] == 3
    assert workflow["percentualeAvanzamento"] == 40
    assert workflow["documentoCorrenteMancante"] is True
    assert redigi["completato"] is True
    assert revisiona["completato"] is True
    assert firma["codice"] == "FIRMA"
    assert firma["completato"] is False
    assert firma["attivo"] is True


def test_workflow_marks_protocollo_active_from_step_corrente():
    service = SottofaseWorkflowService(
        sottofase_documentale_service=FakeSottofaseDocumentaleService(
            quadro={
                "step_corrente": "PROTOCOLLA",
                "ha_documento_collegato": False,
                "id_documento_corrente": None,
                "documento_corrente": None,
                "documenti": [],
                "step_operativi": [
                    {"codice_step": "FIRMA", "stato_step": "COMPLETATO"}
                ],
            }
        )
    )

    workflow = service.get_workflow(5)
    protocolla = workflow["workflow"][3]

    assert workflow["stepCorrente"] == 4
    assert workflow["percentualeAvanzamento"] == 60
    assert workflow["documentoCorrenteMancante"] is True
    assert protocolla["codice"] == "PROTOCOLLA"
    assert protocolla["completato"] is False
    assert protocolla["attivo"] is True


def test_workflow_marks_fine_active_from_step_corrente():
    service = SottofaseWorkflowService(
        sottofase_documentale_service=FakeSottofaseDocumentaleService(
            quadro={
                "step_corrente": "FINE",
                "stato_sottofase": "IN_CORSO",
                "ha_documento_collegato": False,
                "id_documento_corrente": None,
                "documento_corrente": None,
                "documenti": [],
                "step_operativi": [
                    {"codice_step": "PROTOCOLLA", "stato_step": "COMPLETATO"}
                ],
            }
        )
    )

    workflow = service.get_workflow(5)
    fine = workflow["workflow"][4]

    assert workflow["stepCorrente"] == 5
    assert workflow["percentualeAvanzamento"] == 80
    assert workflow["documentoCorrenteMancante"] is True
    assert fine["codice"] == "FINE"
    assert fine["completato"] is False
    assert fine["attivo"] is True


def test_workflow_marks_fine_completed_when_sottofase_completed():
    service = SottofaseWorkflowService(
        sottofase_documentale_service=FakeSottofaseDocumentaleService(
            quadro={
                "step_corrente": "FINE",
                "stato_sottofase": "COMPLETATA",
                "ha_documento_collegato": False,
                "id_documento_corrente": None,
                "documento_corrente": None,
                "documenti": [],
                "step_operativi": [
                    {"codice_step": "PROTOCOLLA", "stato_step": "COMPLETATO"}
                ],
            }
        )
    )

    workflow = service.get_workflow(5)
    fine = workflow["workflow"][4]

    assert workflow["percentualeAvanzamento"] == 100
    assert fine["completato"] is True
    assert fine["attivo"] is False


def test_workflow_uses_operational_steps_for_firma_and_protocolla():
    service = SottofaseWorkflowService(
        sottofase_documentale_service=FakeSottofaseDocumentaleService(
            quadro={
                "step_corrente": "FIRMA",
                "ha_documento_collegato": True,
                "id_documento_corrente": 15,
                "versione_documento": 2,
                "documento_corrente": {
                    "id_documento_sottofase": 15,
                    "versione_documento": 2,
                },
                "documenti": [
                    {"id_documento_sottofase": 15, "versione_documento": 2}
                ],
                "step_operativi": [
                    {
                        "codice_step": "FIRMA",
                        "stato_step": "COMPLETATO",
                        "data_completamento": "2026-05-27 11:00:00",
                        "utente_completamento": "Responsabile firma",
                    }
                ],
            }
        )
    )

    workflow = service.get_workflow(9)
    firma = workflow["workflow"][2]
    protocolla = workflow["workflow"][3]

    assert workflow["stepCorrente"] == 4
    assert workflow["percentualeAvanzamento"] == 60
    assert firma["codice"] == "FIRMA"
    assert firma["completato"] is True
    assert firma["attivo"] is False
    assert firma["timestamp"] == "2026-05-27 11:00:00"
    assert firma["operatore"] == "Responsabile firma"
    assert protocolla["codice"] == "PROTOCOLLA"
    assert protocolla["completato"] is False
    assert protocolla["attivo"] is True
