from backend.services.workflow_procedimento_service import (
    WorkflowProcedimentoService,
)


class FakeWorkflowProcedimentoRepository:
    def list_fasi_by_procedimento(self, id_procedimento):
        return [{"id_procedimento": id_procedimento, "id_fase": 1}]

    def get_fase_detail(self, id_fase):
        return {"id_fase": id_fase}

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

    assert service.get_fase_detail(7) == {"id_fase": 7}


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
