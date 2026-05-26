import pytest

from backend.services.procedimento_service import (
    ProcedimentoNotFoundError,
    ProcedimentoProtocolloLinkAlreadyExistsError,
    ProcedimentoService,
    ProtocolloNotFoundError,
)


class FakeProcedimentoRepository:
    protocollo_exists_value = True
    procedimento_exists_value = True
    link_exists_value = False

    def list_procedimenti(self):
        return [{"id_procedimento": 1}]

    def get_procedimento_detail(self, id_procedimento):
        return {"id_procedimento": id_procedimento}

    def list_protocolli_collegati(self, id_procedimento):
        return [{"id_procedimento": id_procedimento, "id_protocollo": 123}]

    def count_protocolli_collegati(self, id_procedimento):
        return 2

    def list_procedimenti_by_protocollo_id(self, id_protocollo):
        return [{"id_protocollo": id_protocollo, "id_procedimento": 1}]

    def protocollo_exists(self, id_protocollo):
        return self.protocollo_exists_value

    def procedimento_exists(self, id_procedimento):
        return self.procedimento_exists_value

    def procedimento_protocollo_link_exists(self, id_protocollo, id_procedimento):
        return self.link_exists_value

    def link_protocollo_to_procedimento(
        self,
        *,
        id_protocollo,
        id_procedimento,
        ruolo_protocollo,
        principale,
        note_collegamento,
    ):
        return {
            "id_protocollo": id_protocollo,
            "id_procedimento": id_procedimento,
            "ruolo_protocollo": ruolo_protocollo,
            "principale": principale,
            "note_collegamento": note_collegamento,
        }


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


def test_list_procedimenti_by_protocollo_id_delegates_to_repository():
    service = ProcedimentoService(
        procedimento_repository=FakeProcedimentoRepository()
    )

    assert service.list_procedimenti_by_protocollo_id(123) == [
        {"id_protocollo": 123, "id_procedimento": 1}
    ]


def test_list_procedimenti_by_protocollo_id_raises_when_protocollo_missing():
    repository = FakeProcedimentoRepository()
    repository.protocollo_exists_value = False
    service = ProcedimentoService(procedimento_repository=repository)

    with pytest.raises(ProtocolloNotFoundError):
        service.list_procedimenti_by_protocollo_id(999)


def test_link_protocollo_to_procedimento_delegates_with_defaults():
    service = ProcedimentoService(
        procedimento_repository=FakeProcedimentoRepository()
    )

    result = service.link_protocollo_to_procedimento(
        id_protocollo=123,
        id_procedimento=1,
    )

    assert result["id_protocollo"] == 123
    assert result["id_procedimento"] == 1
    assert result["ruolo_protocollo"] == "COLLEGATO"
    assert result["principale"] is False
    assert result["note_collegamento"] is None


def test_link_protocollo_to_procedimento_raises_when_protocollo_missing():
    repository = FakeProcedimentoRepository()
    repository.protocollo_exists_value = False
    service = ProcedimentoService(procedimento_repository=repository)

    with pytest.raises(ProtocolloNotFoundError):
        service.link_protocollo_to_procedimento(
            id_protocollo=999,
            id_procedimento=1,
        )


def test_link_protocollo_to_procedimento_raises_when_procedimento_missing():
    repository = FakeProcedimentoRepository()
    repository.procedimento_exists_value = False
    service = ProcedimentoService(procedimento_repository=repository)

    with pytest.raises(ProcedimentoNotFoundError):
        service.link_protocollo_to_procedimento(
            id_protocollo=123,
            id_procedimento=999,
        )


def test_link_protocollo_to_procedimento_raises_when_link_already_exists():
    repository = FakeProcedimentoRepository()
    repository.link_exists_value = True
    service = ProcedimentoService(procedimento_repository=repository)

    with pytest.raises(ProcedimentoProtocolloLinkAlreadyExistsError):
        service.link_protocollo_to_procedimento(
            id_protocollo=123,
            id_procedimento=1,
        )
