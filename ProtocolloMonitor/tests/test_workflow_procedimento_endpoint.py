import pytest
from fastapi import HTTPException

from backend.api.routes.protocollo_monitor import (
    ProcedimentoFasePayload,
    ProcedimentoFaseStepNotePayload,
    ProcedimentoFaseStepPayload,
    ProcedimentoFaseStepProtocolloPayload,
    aggiorna_procedimento_fase,
    aggiorna_note_procedimento_fase_step_redigi,
    avvia_procedimento_fase_step_redigi,
    collega_protocollo_procedimento_fase_step_istanza,
    completa_procedimento_fase_step_redigi,
    configura_procedimento_fase_step_istanza_fine,
    configura_procedimento_fase_step_predefinito,
    crea_procedimento_fase,
    elimina_procedimento_fase_step_orizzontale,
    get_catalogo_sottofasi,
    get_procedimento_fase_dettaglio,
    get_procedimento_fase_sottofasi,
    get_procedimento_fase_step_orizzontali,
    get_procedimento_fasi,
    inizializza_procedimento_fase_step_orizzontali,
    inserisci_procedimento_fase_step_orizzontale_dopo,
)
from backend.services.workflow_procedimento_service import (
    WorkflowConfigurazioneBloccataError,
    WorkflowFaseNotFoundError,
    WorkflowFaseValidationError,
)


class FakeWorkflowProcedimentoService:
    def __init__(self, *, fase_detail=None, mode=None):
        self.fase_detail = fase_detail
        self.mode = mode

    def list_fasi_by_procedimento(self, id_procedimento):
        return [{"id_procedimento": id_procedimento, "id_fase": 1}]

    def get_fase_detail(self, id_fase):
        return self.fase_detail

    def list_sottofasi_by_fase(self, id_fase):
        return [{"id_fase": id_fase, "id_sottofase": 2}]

    def list_catalogo_sottofasi(self, attivo_only=True):
        return [{"codice_sottofase": "EMAIL", "attivo_only": attivo_only}]

    def crea_fase_procedimento(self, *, id_procedimento, payload):
        if self.mode == "validation":
            raise WorkflowFaseValidationError("Titolo fase obbligatorio.")
        if self.mode == "missing":
            raise WorkflowFaseNotFoundError()

        return {
            "id_procedimento": id_procedimento,
            "id_fase": 9,
            "titolo": payload.Titolo,
            "descrizione": payload.Descrizione,
        }

    def aggiorna_fase_procedimento(self, *, id_procedimento, id_fase, payload):
        if self.mode == "validation":
            raise WorkflowFaseValidationError("Titolo fase obbligatorio.")
        if self.mode == "missing":
            raise WorkflowFaseNotFoundError()

        return {
            "id_procedimento": id_procedimento,
            "id_fase": id_fase,
            "titolo": payload.Titolo,
            "descrizione": payload.Descrizione,
        }

    def list_step_orizzontali_fase(self, *, id_procedimento, id_fase):
        if self.mode == "missing":
            raise WorkflowFaseNotFoundError()
        return [
            {
                "id_procedimento": id_procedimento,
                "id_fase": id_fase,
                "codice_step": "REDIGI",
                "titolo_step": "Redigi",
                "ordine": 1,
                "stato_step": "NON_AVVIATO",
            }
        ]

    def inizializza_step_orizzontali_fase(self, *, id_procedimento, id_fase):
        if self.mode == "missing":
            raise WorkflowFaseNotFoundError()
        return {
            "id_fase": id_fase,
            "step_creati": ["REDIGI", "REVISIONA", "FIRMA", "PROTOCOLLA", "FINE"],
            "step_gia_presenti": [],
            "step": self.list_step_orizzontali_fase(
                id_procedimento=id_procedimento,
                id_fase=id_fase,
            ),
        }

    def configura_step_orizzontali_istanza_fine(self, *, id_procedimento, id_fase):
        if self.mode == "missing":
            raise WorkflowFaseNotFoundError()
        if self.mode == "blocked":
            raise WorkflowConfigurazioneBloccataError("Workflow bloccato.")
        return [
            {"id_fase": id_fase, "codice_step": "ISTANZA", "ordine": 1},
            {"id_fase": id_fase, "codice_step": "FINE", "ordine": 2},
        ]

    def configura_step_orizzontali_predefinito(self, *, id_procedimento, id_fase):
        if self.mode == "missing":
            raise WorkflowFaseNotFoundError()
        if self.mode == "blocked":
            raise WorkflowConfigurazioneBloccataError("Workflow bloccato.")
        return [
            {"id_fase": id_fase, "codice_step": "REDIGI", "ordine": 1},
            {"id_fase": id_fase, "codice_step": "REVISIONA", "ordine": 2},
            {"id_fase": id_fase, "codice_step": "FIRMA", "ordine": 3},
            {"id_fase": id_fase, "codice_step": "PROTOCOLLA", "ordine": 4},
            {"id_fase": id_fase, "codice_step": "FINE", "ordine": 5},
        ]

    def inserisci_step_orizzontale_dopo(
        self,
        *,
        id_procedimento,
        id_fase,
        id_step,
        payload,
    ):
        if self.mode == "missing":
            raise WorkflowFaseNotFoundError()
        if self.mode == "validation":
            raise WorkflowFaseValidationError("Titolo step obbligatorio.")
        return [
            {"id_fase": id_fase, "codice_step": "REDIGI", "ordine": 1},
            {"id_fase": id_fase, "codice_step": payload.codiceStep, "ordine": 2},
        ]

    def elimina_logicamente_step_orizzontale(
        self,
        *,
        id_procedimento,
        id_fase,
        id_step,
    ):
        if self.mode == "missing":
            raise WorkflowFaseNotFoundError()
        if self.mode == "validation":
            raise WorkflowFaseValidationError("Non eliminabile.")
        return [{"id_fase": id_fase, "codice_step": "FINE", "ordine": 1}]

    def collega_protocollo_step_istanza(
        self,
        *,
        id_procedimento,
        id_fase,
        id_step,
        payload,
    ):
        if self.mode == "missing":
            raise WorkflowFaseNotFoundError("Protocollo non trovato.")
        if self.mode == "validation":
            raise WorkflowFaseValidationError("Step non collegabile.")
        return [
            {
                "id_fase": id_fase,
                "id_step_orizzontale": id_step,
                "codice_step": "ISTANZA",
                "stato_step": "COMPLETATO",
                "id_protocollo_collegato": payload.idProtocollo,
            }
        ]

    def avvia_step_redigi(self, *, id_procedimento, id_fase, id_step):
        if self.mode == "missing":
            raise WorkflowFaseNotFoundError("Step non trovato.")
        if self.mode == "validation":
            raise WorkflowFaseValidationError("Transizione non valida.")
        return [{"id_fase": id_fase, "codice_step": "REDIGI", "stato_step": "IN_CORSO"}]

    def completa_step_redigi(self, *, id_procedimento, id_fase, id_step):
        if self.mode == "missing":
            raise WorkflowFaseNotFoundError("Step non trovato.")
        if self.mode == "validation":
            raise WorkflowFaseValidationError("Transizione non valida.")
        return [{"id_fase": id_fase, "codice_step": "REDIGI", "stato_step": "COMPLETATO"}]

    def aggiorna_note_step_redigi(
        self,
        *,
        id_procedimento,
        id_fase,
        id_step,
        payload,
    ):
        if self.mode == "missing":
            raise WorkflowFaseNotFoundError("Step non trovato.")
        if self.mode == "validation":
            raise WorkflowFaseValidationError("Step non valido.")
        return [
            {
                "id_fase": id_fase,
                "codice_step": "REDIGI",
                "note_operative": payload.noteOperative,
            }
        ]


def test_get_procedimento_fasi_returns_list():
    response = get_procedimento_fasi(
        10,
        workflow_service=FakeWorkflowProcedimentoService(),
    )

    assert response == [{"id_procedimento": 10, "id_fase": 1}]


def test_crea_procedimento_fase_returns_created_record():
    response = crea_procedimento_fase(
        10,
        ProcedimentoFasePayload(Titolo="Nuova fase", Descrizione="Desc"),
        workflow_service=FakeWorkflowProcedimentoService(),
    )

    assert response == {
        "id_procedimento": 10,
        "id_fase": 9,
        "titolo": "Nuova fase",
        "descrizione": "Desc",
    }


def test_crea_procedimento_fase_returns_400_without_title():
    with pytest.raises(HTTPException) as exc_info:
        crea_procedimento_fase(
            10,
            ProcedimentoFasePayload(Titolo=None),
            workflow_service=FakeWorkflowProcedimentoService(mode="validation"),
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Titolo fase obbligatorio."


def test_aggiorna_procedimento_fase_returns_updated_record():
    response = aggiorna_procedimento_fase(
        10,
        9,
        ProcedimentoFasePayload(Titolo="Titolo aggiornato"),
        workflow_service=FakeWorkflowProcedimentoService(),
    )

    assert response["id_procedimento"] == 10
    assert response["id_fase"] == 9
    assert response["titolo"] == "Titolo aggiornato"


def test_aggiorna_procedimento_fase_returns_404_when_missing():
    with pytest.raises(HTTPException) as exc_info:
        aggiorna_procedimento_fase(
            10,
            999,
            ProcedimentoFasePayload(Titolo="Titolo"),
            workflow_service=FakeWorkflowProcedimentoService(mode="missing"),
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Fase non trovata"


def test_get_procedimento_fase_dettaglio_returns_detail():
    response = get_procedimento_fase_dettaglio(
        1,
        workflow_service=FakeWorkflowProcedimentoService(
            fase_detail={"id_fase": 1}
        ),
    )

    assert response == {"id_fase": 1}


def test_get_procedimento_fase_dettaglio_returns_404_when_missing():
    with pytest.raises(HTTPException) as exc_info:
        get_procedimento_fase_dettaglio(
            999,
            workflow_service=FakeWorkflowProcedimentoService(fase_detail=None),
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Fase non trovata"


def test_get_procedimento_fase_sottofasi_returns_legacy_empty_or_list():
    response = get_procedimento_fase_sottofasi(
        1,
        workflow_service=FakeWorkflowProcedimentoService(
            fase_detail={"id_fase": 1}
        ),
    )

    assert response == [{"id_fase": 1, "id_sottofase": 2}]


def test_get_procedimento_fase_sottofasi_returns_404_when_fase_missing():
    with pytest.raises(HTTPException) as exc_info:
        get_procedimento_fase_sottofasi(
            999,
            workflow_service=FakeWorkflowProcedimentoService(fase_detail=None),
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Fase non trovata"


def test_get_step_orizzontali_returns_initialized_steps():
    response = get_procedimento_fase_step_orizzontali(
        10,
        9,
        workflow_service=FakeWorkflowProcedimentoService(),
    )

    assert response == [
        {
            "id_procedimento": 10,
            "id_fase": 9,
            "codice_step": "REDIGI",
            "titolo_step": "Redigi",
            "ordine": 1,
            "stato_step": "NON_AVVIATO",
        }
    ]


def test_get_step_orizzontali_returns_404_when_fase_missing():
    with pytest.raises(HTTPException) as exc_info:
        get_procedimento_fase_step_orizzontali(
            10,
            999,
            workflow_service=FakeWorkflowProcedimentoService(mode="missing"),
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Fase non trovata"


def test_inizializza_step_orizzontali_returns_report():
    response = inizializza_procedimento_fase_step_orizzontali(
        10,
        9,
        workflow_service=FakeWorkflowProcedimentoService(),
    )

    assert response["id_fase"] == 9
    assert response["step_creati"] == [
        "REDIGI",
        "REVISIONA",
        "FIRMA",
        "PROTOCOLLA",
        "FINE",
    ]


def test_configura_step_istanza_fine_returns_updated_steps():
    response = configura_procedimento_fase_step_istanza_fine(
        10,
        9,
        workflow_service=FakeWorkflowProcedimentoService(),
    )

    assert [step["codice_step"] for step in response] == ["ISTANZA", "FINE"]


def test_configura_step_istanza_fine_returns_409_when_workflow_blocked():
    with pytest.raises(HTTPException) as exc_info:
        configura_procedimento_fase_step_istanza_fine(
            10,
            9,
            workflow_service=FakeWorkflowProcedimentoService(mode="blocked"),
        )

    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == "Workflow bloccato."


def test_configura_step_predefinito_returns_updated_steps():
    response = configura_procedimento_fase_step_predefinito(
        10,
        9,
        workflow_service=FakeWorkflowProcedimentoService(),
    )

    assert [step["codice_step"] for step in response] == [
        "REDIGI",
        "REVISIONA",
        "FIRMA",
        "PROTOCOLLA",
        "FINE",
    ]


def test_inserisci_step_orizzontale_dopo_returns_updated_steps():
    response = inserisci_procedimento_fase_step_orizzontale_dopo(
        10,
        9,
        1,
        ProcedimentoFaseStepPayload(
            titoloStep="Mail",
            codiceStep="MAIL",
        ),
        workflow_service=FakeWorkflowProcedimentoService(),
    )

    assert response[1]["codice_step"] == "MAIL"


def test_elimina_step_orizzontale_returns_updated_steps():
    response = elimina_procedimento_fase_step_orizzontale(
        10,
        9,
        1,
        workflow_service=FakeWorkflowProcedimentoService(),
    )

    assert response == [{"id_fase": 9, "codice_step": "FINE", "ordine": 1}]


def test_collega_protocollo_step_istanza_returns_updated_steps():
    response = collega_protocollo_procedimento_fase_step_istanza(
        10,
        9,
        3,
        ProcedimentoFaseStepProtocolloPayload(idProtocollo=123),
        workflow_service=FakeWorkflowProcedimentoService(),
    )

    assert response[0]["codice_step"] == "ISTANZA"
    assert response[0]["stato_step"] == "COMPLETATO"
    assert response[0]["id_protocollo_collegato"] == 123


def test_collega_protocollo_step_istanza_returns_404_when_missing():
    with pytest.raises(HTTPException) as exc_info:
        collega_protocollo_procedimento_fase_step_istanza(
            10,
            9,
            3,
            ProcedimentoFaseStepProtocolloPayload(idProtocollo=999),
            workflow_service=FakeWorkflowProcedimentoService(mode="missing"),
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Protocollo non trovato."


def test_avvia_step_redigi_returns_updated_steps():
    response = avvia_procedimento_fase_step_redigi(
        10,
        9,
        1,
        workflow_service=FakeWorkflowProcedimentoService(),
    )

    assert response[0]["codice_step"] == "REDIGI"
    assert response[0]["stato_step"] == "IN_CORSO"


def test_completa_step_redigi_returns_updated_steps():
    response = completa_procedimento_fase_step_redigi(
        10,
        9,
        1,
        workflow_service=FakeWorkflowProcedimentoService(),
    )

    assert response[0]["codice_step"] == "REDIGI"
    assert response[0]["stato_step"] == "COMPLETATO"


def test_aggiorna_note_step_redigi_returns_updated_steps():
    response = aggiorna_note_procedimento_fase_step_redigi(
        10,
        9,
        1,
        ProcedimentoFaseStepNotePayload(noteOperative="Nota operativa"),
        workflow_service=FakeWorkflowProcedimentoService(),
    )

    assert response[0]["codice_step"] == "REDIGI"
    assert response[0]["note_operative"] == "Nota operativa"


def test_avvia_step_redigi_returns_400_when_transition_invalid():
    with pytest.raises(HTTPException) as exc_info:
        avvia_procedimento_fase_step_redigi(
            10,
            9,
            1,
            workflow_service=FakeWorkflowProcedimentoService(mode="validation"),
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Transizione non valida."


def test_get_catalogo_sottofasi_returns_active_catalog_by_default():
    response = get_catalogo_sottofasi(
        workflow_service=FakeWorkflowProcedimentoService(),
    )

    assert response == [{"codice_sottofase": "EMAIL", "attivo_only": True}]


def test_get_catalogo_sottofasi_can_return_all_catalog():
    response = get_catalogo_sottofasi(
        attivo_only=False,
        workflow_service=FakeWorkflowProcedimentoService(),
    )

    assert response == [{"codice_sottofase": "EMAIL", "attivo_only": False}]
