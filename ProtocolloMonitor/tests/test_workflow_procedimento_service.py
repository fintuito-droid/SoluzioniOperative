from datetime import datetime

import pytest

from backend.services.workflow_procedimento_service import (
    WorkflowConfigurazioneBloccataError,
    WorkflowFaseNotFoundError,
    WorkflowFaseValidationError,
    WorkflowProcedimentoService,
)


FIXED_NOW = datetime(2026, 6, 1, 10, 36, 0)


class FakeWorkflowProcedimentoRepository:
    procedimento_exists_value = True

    def __init__(self):
        self.init_calls = []
        self.configura_istanza_fine_calls = []
        self.configura_predefinito_calls = []
        self.inserisci_step_calls = []
        self.elimina_step_calls = []
        self.collega_protocollo_calls = []
        self.has_step_avviati_value = False
        self.has_step_orizzontali_value = False

    def list_fasi_by_procedimento(self, id_procedimento):
        return [{"id_procedimento": id_procedimento, "id_fase": 1}]

    def get_fase_detail(self, id_fase):
        return {"id_fase": id_fase, "id_procedimento": id_fase}

    def procedimento_exists(self, id_procedimento):
        return self.procedimento_exists_value

    def crea_fase_procedimento(
        self,
        *,
        id_procedimento,
        titolo,
        descrizione,
        data_creazione,
    ):
        return {
            "id_procedimento": id_procedimento,
            "id_fase": 9,
            "titolo": titolo,
            "descrizione": descrizione,
            "data_creazione": data_creazione,
        }

    def aggiorna_fase_procedimento(
        self,
        *,
        id_procedimento,
        id_fase,
        titolo,
        descrizione,
        data_modifica,
    ):
        return {
            "id_procedimento": id_procedimento,
            "id_fase": id_fase,
            "titolo": titolo,
            "descrizione": descrizione,
            "data_modifica": data_modifica,
        }

    def inizializza_step_orizzontali_fase(self, *, id_fase, data_creazione):
        self.init_calls.append((id_fase, data_creazione))
        return {
            "id_fase": id_fase,
            "step_creati": ["REDIGI"],
            "step_gia_presenti": ["REVISIONA"],
            "step": [
                {
                    "id_fase": id_fase,
                    "codice_step": "REDIGI",
                    "titolo_step": "Redigi",
                    "ordine": 1,
                    "stato_step": "NON_AVVIATO",
                }
            ],
        }

    def list_step_orizzontali_by_fase(self, id_fase):
        return [
            {
                "id_fase": id_fase,
                "codice_step": "REDIGI",
                "titolo_step": "Redigi",
                "ordine": 1,
                "stato_step": "NON_AVVIATO",
            }
        ]

    def has_step_orizzontali_avviati(self, id_fase):
        return self.has_step_avviati_value

    def has_step_orizzontali_fase(self, id_fase):
        return self.has_step_orizzontali_value

    def configura_step_orizzontali_istanza_fine(self, *, id_fase, data_modifica):
        self.configura_istanza_fine_calls.append((id_fase, data_modifica))
        return [
            {"id_fase": id_fase, "codice_step": "ISTANZA", "ordine": 1},
            {"id_fase": id_fase, "codice_step": "FINE", "ordine": 2},
        ]

    def configura_step_orizzontali_predefinito(self, *, id_fase, data_modifica):
        self.configura_predefinito_calls.append((id_fase, data_modifica))
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
        id_fase,
        id_step,
        titolo_step,
        codice_step,
        data_creazione,
    ):
        self.inserisci_step_calls.append(
            (id_fase, id_step, titolo_step, codice_step, data_creazione)
        )
        return [
            {"id_fase": id_fase, "codice_step": "REDIGI", "ordine": 1},
            {"id_fase": id_fase, "codice_step": codice_step, "ordine": 2},
        ]

    def elimina_logicamente_step_orizzontale(
        self,
        *,
        id_fase,
        id_step,
        data_modifica,
    ):
        self.elimina_step_calls.append((id_fase, id_step, data_modifica))
        return [{"id_fase": id_fase, "codice_step": "FINE", "ordine": 1}]

    def collega_protocollo_step_istanza(
        self,
        *,
        id_procedimento,
        id_fase,
        id_step,
        id_protocollo,
        data_modifica,
    ):
        self.collega_protocollo_calls.append(
            (id_procedimento, id_fase, id_step, id_protocollo, data_modifica)
        )
        return [
            {
                "id_fase": id_fase,
                "id_step_orizzontale": id_step,
                "codice_step": "ISTANZA",
                "stato_step": "COMPLETATO",
                "id_protocollo_collegato": id_protocollo,
            }
        ]

    def list_sottofasi_by_fase(self, id_fase):
        return [{"id_fase": id_fase, "id_sottofase": 2}]

    def list_catalogo_sottofasi(self, attivo_only=True):
        return [{"codice_sottofase": "EMAIL", "attivo_only": attivo_only}]


class FailingWorkflowProcedimentoRepository:
    def list_fasi_by_procedimento(self, id_procedimento):
        raise RuntimeError("errore test")

    def get_fase_detail(self, id_fase):
        raise RuntimeError("errore test")

    def list_sottofasi_by_fase(self, id_fase):
        raise RuntimeError("errore test")

    def list_catalogo_sottofasi(self, attivo_only=True):
        raise RuntimeError("errore test")


def test_list_fasi_without_repository_returns_empty_list():
    service = WorkflowProcedimentoService()

    assert service.list_fasi_by_procedimento(1) == []


def test_list_fasi_delegates_to_repository():
    service = WorkflowProcedimentoService(
        workflow_procedimento_repository=FakeWorkflowProcedimentoRepository()
    )

    assert service.list_fasi_by_procedimento(10) == [
        {"id_procedimento": 10, "id_fase": 1}
    ]


def test_get_fase_detail_without_repository_returns_none():
    service = WorkflowProcedimentoService()

    assert service.get_fase_detail(1) is None


def test_get_fase_detail_delegates_to_repository():
    service = WorkflowProcedimentoService(
        workflow_procedimento_repository=FakeWorkflowProcedimentoRepository()
    )

    assert service.get_fase_detail(7) == {"id_fase": 7, "id_procedimento": 7}


def test_crea_fase_procedimento_validates_and_delegates():
    service = WorkflowProcedimentoService(
        workflow_procedimento_repository=FakeWorkflowProcedimentoRepository(),
        now_factory=lambda: FIXED_NOW,
    )

    result = service.crea_fase_procedimento(
        id_procedimento=10,
        payload={"Titolo": "Nuova fase", "Descrizione": "Descrizione"},
    )

    assert result == {
        "id_procedimento": 10,
        "id_fase": 9,
        "titolo": "Nuova fase",
        "descrizione": "Descrizione",
        "data_creazione": FIXED_NOW,
    }


def test_crea_fase_procedimento_requires_title():
    service = WorkflowProcedimentoService(
        workflow_procedimento_repository=FakeWorkflowProcedimentoRepository(),
        now_factory=lambda: FIXED_NOW,
    )

    with pytest.raises(WorkflowFaseValidationError):
        service.crea_fase_procedimento(
            id_procedimento=10,
            payload={"Titolo": " "},
        )


def test_crea_fase_procedimento_raises_when_procedimento_missing():
    repository = FakeWorkflowProcedimentoRepository()
    repository.procedimento_exists_value = False
    service = WorkflowProcedimentoService(
        workflow_procedimento_repository=repository,
        now_factory=lambda: FIXED_NOW,
    )

    with pytest.raises(WorkflowFaseNotFoundError):
        service.crea_fase_procedimento(
            id_procedimento=999,
            payload={"Titolo": "Nuova fase"},
        )


def test_aggiorna_fase_procedimento_validates_membership_and_delegates():
    service = WorkflowProcedimentoService(
        workflow_procedimento_repository=FakeWorkflowProcedimentoRepository(),
        now_factory=lambda: FIXED_NOW,
    )

    result = service.aggiorna_fase_procedimento(
        id_procedimento=7,
        id_fase=7,
        payload={"Titolo": "Titolo aggiornato", "Descrizione": "Nuova"},
    )

    assert result == {
        "id_procedimento": 7,
        "id_fase": 7,
        "titolo": "Titolo aggiornato",
        "descrizione": "Nuova",
        "data_modifica": FIXED_NOW,
    }


def test_aggiorna_fase_procedimento_raises_when_not_same_procedimento():
    service = WorkflowProcedimentoService(
        workflow_procedimento_repository=FakeWorkflowProcedimentoRepository(),
        now_factory=lambda: FIXED_NOW,
    )

    with pytest.raises(WorkflowFaseNotFoundError):
        service.aggiorna_fase_procedimento(
            id_procedimento=999,
            id_fase=7,
            payload={"Titolo": "Titolo aggiornato"},
        )


def test_inizializza_step_orizzontali_validates_phase_and_delegates():
    repository = FakeWorkflowProcedimentoRepository()
    service = WorkflowProcedimentoService(
        workflow_procedimento_repository=repository,
        now_factory=lambda: FIXED_NOW,
    )

    report = service.inizializza_step_orizzontali_fase(
        id_procedimento=7,
        id_fase=7,
    )

    assert report["id_fase"] == 7
    assert report["step"][0]["codice_step"] == "REDIGI"
    assert repository.init_calls == [(7, FIXED_NOW)]


def test_inizializza_step_orizzontali_raises_when_fase_not_in_procedimento():
    service = WorkflowProcedimentoService(
        workflow_procedimento_repository=FakeWorkflowProcedimentoRepository(),
        now_factory=lambda: FIXED_NOW,
    )

    with pytest.raises(WorkflowFaseNotFoundError):
        service.inizializza_step_orizzontali_fase(
            id_procedimento=999,
            id_fase=7,
        )


def test_list_step_orizzontali_initializes_by_default():
    repository = FakeWorkflowProcedimentoRepository()
    service = WorkflowProcedimentoService(
        workflow_procedimento_repository=repository,
        now_factory=lambda: FIXED_NOW,
    )

    steps = service.list_step_orizzontali_fase(
        id_procedimento=7,
        id_fase=7,
    )

    assert steps[0]["codice_step"] == "REDIGI"
    assert repository.init_calls == [(7, FIXED_NOW)]


def test_list_step_orizzontali_can_skip_initialization():
    repository = FakeWorkflowProcedimentoRepository()
    service = WorkflowProcedimentoService(
        workflow_procedimento_repository=repository,
        now_factory=lambda: FIXED_NOW,
    )

    steps = service.list_step_orizzontali_fase(
        id_procedimento=7,
        id_fase=7,
        inizializza=False,
    )

    assert steps[0]["codice_step"] == "REDIGI"
    assert repository.init_calls == []


def test_list_step_orizzontali_does_not_reinitialize_existing_inactive_history():
    repository = FakeWorkflowProcedimentoRepository()
    repository.has_step_orizzontali_value = True
    service = WorkflowProcedimentoService(
        workflow_procedimento_repository=repository,
        now_factory=lambda: FIXED_NOW,
    )

    steps = service.list_step_orizzontali_fase(
        id_procedimento=7,
        id_fase=7,
    )

    assert steps[0]["codice_step"] == "REDIGI"
    assert repository.init_calls == []


def test_configura_step_orizzontali_istanza_fine_validates_and_delegates():
    repository = FakeWorkflowProcedimentoRepository()
    backup_calls = []
    service = WorkflowProcedimentoService(
        workflow_procedimento_repository=repository,
        now_factory=lambda: FIXED_NOW,
        backup_factory=lambda: backup_calls.append("backup"),
    )

    steps = service.configura_step_orizzontali_istanza_fine(
        id_procedimento=7,
        id_fase=7,
    )

    assert [step["codice_step"] for step in steps] == ["ISTANZA", "FINE"]
    assert repository.configura_istanza_fine_calls == [(7, FIXED_NOW)]
    assert backup_calls == ["backup"]


def test_configura_step_orizzontali_istanza_fine_blocks_when_step_started():
    repository = FakeWorkflowProcedimentoRepository()
    repository.has_step_avviati_value = True
    backup_calls = []
    service = WorkflowProcedimentoService(
        workflow_procedimento_repository=repository,
        now_factory=lambda: FIXED_NOW,
        backup_factory=lambda: backup_calls.append("backup"),
    )

    with pytest.raises(WorkflowConfigurazioneBloccataError):
        service.configura_step_orizzontali_istanza_fine(
            id_procedimento=7,
            id_fase=7,
        )

    assert backup_calls == []
    assert repository.configura_istanza_fine_calls == []


def test_configura_step_orizzontali_predefinito_validates_and_delegates():
    repository = FakeWorkflowProcedimentoRepository()
    backup_calls = []
    service = WorkflowProcedimentoService(
        workflow_procedimento_repository=repository,
        now_factory=lambda: FIXED_NOW,
        backup_factory=lambda: backup_calls.append("backup"),
    )

    steps = service.configura_step_orizzontali_predefinito(
        id_procedimento=7,
        id_fase=7,
    )

    assert [step["codice_step"] for step in steps] == [
        "REDIGI",
        "REVISIONA",
        "FIRMA",
        "PROTOCOLLA",
        "FINE",
    ]
    assert repository.configura_predefinito_calls == [(7, FIXED_NOW)]
    assert backup_calls == ["backup"]


def test_inserisci_step_orizzontale_dopo_generates_code_when_missing():
    repository = FakeWorkflowProcedimentoRepository()
    backup_calls = []
    service = WorkflowProcedimentoService(
        workflow_procedimento_repository=repository,
        now_factory=lambda: FIXED_NOW,
        backup_factory=lambda: backup_calls.append("backup"),
    )

    steps = service.inserisci_step_orizzontale_dopo(
        id_procedimento=7,
        id_fase=7,
        id_step=1,
        payload={"titoloStep": "Nuovo controllo"},
    )

    assert steps[1]["codice_step"] == "NUOVO_CONTROLLO"
    assert repository.inserisci_step_calls == [
        (7, 1, "Nuovo controllo", "NUOVO_CONTROLLO", FIXED_NOW)
    ]
    assert backup_calls == ["backup"]


def test_inserisci_step_orizzontale_dopo_requires_title():
    service = WorkflowProcedimentoService(
        workflow_procedimento_repository=FakeWorkflowProcedimentoRepository(),
        now_factory=lambda: FIXED_NOW,
        backup_factory=lambda: None,
    )

    with pytest.raises(WorkflowFaseValidationError):
        service.inserisci_step_orizzontale_dopo(
            id_procedimento=7,
            id_fase=7,
            id_step=1,
            payload={"titoloStep": " "},
        )


def test_elimina_logicamente_step_orizzontale_delegates():
    repository = FakeWorkflowProcedimentoRepository()
    backup_calls = []
    service = WorkflowProcedimentoService(
        workflow_procedimento_repository=repository,
        now_factory=lambda: FIXED_NOW,
        backup_factory=lambda: backup_calls.append("backup"),
    )

    steps = service.elimina_logicamente_step_orizzontale(
        id_procedimento=7,
        id_fase=7,
        id_step=3,
    )

    assert steps == [{"id_fase": 7, "codice_step": "FINE", "ordine": 1}]
    assert repository.elimina_step_calls == [(7, 3, FIXED_NOW)]
    assert backup_calls == ["backup"]


def test_collega_protocollo_step_istanza_validates_and_delegates():
    repository = FakeWorkflowProcedimentoRepository()
    backup_calls = []
    service = WorkflowProcedimentoService(
        workflow_procedimento_repository=repository,
        now_factory=lambda: FIXED_NOW,
        backup_factory=lambda: backup_calls.append("backup"),
    )

    steps = service.collega_protocollo_step_istanza(
        id_procedimento=7,
        id_fase=7,
        id_step=3,
        payload={"idProtocollo": 123},
    )

    assert steps[0]["stato_step"] == "COMPLETATO"
    assert steps[0]["id_protocollo_collegato"] == 123
    assert repository.collega_protocollo_calls == [
        (7, 7, 3, 123, FIXED_NOW)
    ]
    assert backup_calls == ["backup"]


def test_collega_protocollo_step_istanza_requires_protocollo():
    service = WorkflowProcedimentoService(
        workflow_procedimento_repository=FakeWorkflowProcedimentoRepository(),
        now_factory=lambda: FIXED_NOW,
    )

    with pytest.raises(WorkflowFaseValidationError):
        service.collega_protocollo_step_istanza(
            id_procedimento=7,
            id_fase=7,
            id_step=3,
            payload={},
        )


def test_list_sottofasi_without_repository_returns_empty_list():
    service = WorkflowProcedimentoService()

    assert service.list_sottofasi_by_fase(1) == []


def test_list_sottofasi_delegates_to_repository():
    service = WorkflowProcedimentoService(
        workflow_procedimento_repository=FakeWorkflowProcedimentoRepository()
    )

    assert service.list_sottofasi_by_fase(3) == [
        {"id_fase": 3, "id_sottofase": 2}
    ]


def test_list_catalogo_without_repository_returns_empty_list():
    service = WorkflowProcedimentoService()

    assert service.list_catalogo_sottofasi() == []


def test_list_catalogo_delegates_to_repository_with_flag():
    service = WorkflowProcedimentoService(
        workflow_procedimento_repository=FakeWorkflowProcedimentoRepository()
    )

    assert service.list_catalogo_sottofasi(attivo_only=False) == [
        {"codice_sottofase": "EMAIL", "attivo_only": False}
    ]


def test_service_returns_safe_fallbacks_when_repository_fails():
    service = WorkflowProcedimentoService(
        workflow_procedimento_repository=FailingWorkflowProcedimentoRepository()
    )

    assert service.list_fasi_by_procedimento(1) == []
    assert service.get_fase_detail(1) is None
    assert service.list_sottofasi_by_fase(1) == []
    assert service.list_catalogo_sottofasi() == []
