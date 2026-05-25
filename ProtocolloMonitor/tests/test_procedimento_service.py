from backend.services.procedimento_service import ProcedimentoService


class FakeProcedimentoRepository:
    def list_procedimenti(self):
        return [{"id_procedimento": 1}]

    def get_procedimento_detail(self, id_procedimento):
        return {"id_procedimento": id_procedimento}

    def list_protocolli_collegati(self, id_procedimento):
        return [{"id_procedimento": id_procedimento, "id_protocollo": 123}]

    def count_protocolli_collegati(self, id_procedimento):
        return 2


class FailingProcedimentoRepository:
    def list_procedimenti(self):
        raise RuntimeError("errore test")

    def get_procedimento_detail(self, id_procedimento):
        raise RuntimeError("errore test")

    def list_protocolli_collegati(self, id_procedimento):
        raise RuntimeError("errore test")

    def count_protocolli_collegati(self, id_procedimento):
        raise RuntimeError("errore test")


def test_list_procedimenti_without_repository_returns_empty_list():
    service = ProcedimentoService()

    assert service.list_procedimenti() == []


def test_list_procedimenti_delegates_to_repository():
    service = ProcedimentoService(
        procedimento_repository=FakeProcedimentoRepository()
    )

    assert service.list_procedimenti() == [{"id_procedimento": 1}]


def test_get_procedimento_detail_without_repository_returns_none():
    service = ProcedimentoService()

    assert service.get_procedimento_detail(1) is None


def test_get_procedimento_detail_delegates_to_repository():
    service = ProcedimentoService(
        procedimento_repository=FakeProcedimentoRepository()
    )

    assert service.get_procedimento_detail(7) == {"id_procedimento": 7}


def test_list_protocolli_collegati_without_repository_returns_empty_list():
    service = ProcedimentoService()

    assert service.list_protocolli_collegati(1) == []


def test_list_protocolli_collegati_delegates_to_repository():
    service = ProcedimentoService(
        procedimento_repository=FakeProcedimentoRepository()
    )

    assert service.list_protocolli_collegati(1) == [
        {"id_procedimento": 1, "id_protocollo": 123}
    ]


def test_count_protocolli_collegati_without_repository_returns_zero():
    service = ProcedimentoService()

    assert service.count_protocolli_collegati(1) == 0


def test_count_protocolli_collegati_delegates_to_repository():
    service = ProcedimentoService(
        procedimento_repository=FakeProcedimentoRepository()
    )

    assert service.count_protocolli_collegati(1) == 2


def test_service_returns_safe_fallbacks_when_repository_fails():
    service = ProcedimentoService(
        procedimento_repository=FailingProcedimentoRepository()
    )

    assert service.list_procedimenti() == []
    assert service.get_procedimento_detail(1) is None
    assert service.list_protocolli_collegati(1) == []
    assert service.count_protocolli_collegati(1) == 0
