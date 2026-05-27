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


def test_workflow_marks_revisione_active_when_first_document_exists():
    service = SottofaseWorkflowService(
        sottofase_documentale_service=FakeSottofaseDocumentaleService(
            quadro={
                "step_corrente": "REDIGI",
                "ha_documento_collegato": True,
                "id_documento_corrente": 10,
                "versione_documento": 1,
                "documento_corrente": {
                    "id_documento_sottofase": 10,
                    "versione_documento": 1,
                    "data_collegamento": "2026-05-27 10:00:00",
                    "utente_collegamento": "Operatore test",
                },
                "documenti": [
                    {"id_documento_sottofase": 10, "versione_documento": 1}
                ],
                "step_operativi": [],
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
