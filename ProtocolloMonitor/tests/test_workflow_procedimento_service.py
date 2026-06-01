from datetime import datetime

import pytest

from backend.services.workflow_procedimento_service import (
    WorkflowFaseNotFoundError,
    WorkflowFaseValidationError,
    WorkflowSottofaseNotFoundError,
    WorkflowSottofaseValidationError,
    WorkflowProcedimentoService,
)


FIXED_NOW = datetime(2026, 6, 1, 10, 36, 0)


class FakeWorkflowProcedimentoRepository:
    procedimento_exists_value = True

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

    def list_sottofasi_by_fase(self, id_fase):
        return [{"id_fase": id_fase, "id_sottofase": 2}]

    def get_sottofase_detail(self, id_sottofase):
        return {"id_sottofase": id_sottofase, "id_fase": id_sottofase}

    def crea_sottofase_fase(
        self,
        *,
        id_fase,
        codice_sottofase,
        titolo,
        descrizione,
        responsabile,
        data_scadenza,
        data_creazione,
    ):
        return {
            "id_fase": id_fase,
            "id_sottofase": 12,
            "codice_sottofase": codice_sottofase,
            "titolo": titolo,
            "descrizione": descrizione,
            "responsabile": responsabile,
            "data_scadenza": data_scadenza,
            "data_creazione": data_creazione,
        }

    def aggiorna_sottofase_fase(
        self,
        *,
        id_fase,
        id_sottofase,
        codice_sottofase,
        titolo,
        descrizione,
        responsabile,
        data_scadenza,
        data_modifica,
    ):
        return {
            "id_fase": id_fase,
            "id_sottofase": id_sottofase,
            "codice_sottofase": codice_sottofase,
            "titolo": titolo,
            "descrizione": descrizione,
            "responsabile": responsabile,
            "data_scadenza": data_scadenza,
            "data_modifica": data_modifica,
        }

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


def test_crea_sottofase_fase_validates_and_delegates():
    service = WorkflowProcedimentoService(
        workflow_procedimento_repository=FakeWorkflowProcedimentoRepository(),
        now_factory=lambda: FIXED_NOW,
    )

    result = service.crea_sottofase_fase(
        id_procedimento=7,
        id_fase=7,
        payload={"Titolo": "Sottofase", "Descrizione": "Desc"},
    )

    assert result["id_sottofase"] == 12
    assert result["codice_sottofase"] == "SF-20260601-103600"
    assert result["titolo"] == "Sottofase"
    assert result["descrizione"] == "Desc"
    assert result["data_creazione"] == FIXED_NOW


def test_crea_sottofase_fase_uses_manual_code():
    service = WorkflowProcedimentoService(
        workflow_procedimento_repository=FakeWorkflowProcedimentoRepository(),
        now_factory=lambda: FIXED_NOW,
    )

    result = service.crea_sottofase_fase(
        id_procedimento=7,
        id_fase=7,
        payload={"Titolo": "Sottofase", "CodiceSottofase": "SF-MANUALE"},
    )

    assert result["codice_sottofase"] == "SF-MANUALE"


def test_crea_sottofase_fase_requires_title():
    service = WorkflowProcedimentoService(
        workflow_procedimento_repository=FakeWorkflowProcedimentoRepository(),
        now_factory=lambda: FIXED_NOW,
    )

    with pytest.raises(WorkflowSottofaseValidationError):
        service.crea_sottofase_fase(
            id_procedimento=7,
            id_fase=7,
            payload={"Titolo": " "},
        )


def test_crea_sottofase_fase_raises_when_fase_not_in_procedimento():
    service = WorkflowProcedimentoService(
        workflow_procedimento_repository=FakeWorkflowProcedimentoRepository(),
        now_factory=lambda: FIXED_NOW,
    )

    with pytest.raises(WorkflowSottofaseNotFoundError):
        service.crea_sottofase_fase(
            id_procedimento=999,
            id_fase=7,
            payload={"Titolo": "Sottofase"},
        )


def test_aggiorna_sottofase_fase_validates_membership_and_delegates():
    service = WorkflowProcedimentoService(
        workflow_procedimento_repository=FakeWorkflowProcedimentoRepository(),
        now_factory=lambda: FIXED_NOW,
    )

    result = service.aggiorna_sottofase_fase(
        id_procedimento=7,
        id_fase=7,
        id_sottofase=7,
        payload={
            "Titolo": "Sottofase aggiornata",
            "CodiceSottofase": "SF-UPD",
            "Descrizione": "Nuova",
        },
    )

    assert result["id_sottofase"] == 7
    assert result["codice_sottofase"] == "SF-UPD"
    assert result["titolo"] == "Sottofase aggiornata"
    assert result["descrizione"] == "Nuova"
    assert result["data_modifica"] == FIXED_NOW


def test_aggiorna_sottofase_fase_raises_when_not_same_fase():
    service = WorkflowProcedimentoService(
        workflow_procedimento_repository=FakeWorkflowProcedimentoRepository(),
        now_factory=lambda: FIXED_NOW,
    )

    with pytest.raises(WorkflowSottofaseNotFoundError):
        service.aggiorna_sottofase_fase(
            id_procedimento=7,
            id_fase=7,
            id_sottofase=8,
            payload={"Titolo": "Sottofase"},
        )


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
