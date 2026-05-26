from backend.services.sottofase_documentale_service import (
    SottofaseDocumentaleService,
)


class FakeSottofaseDocumentaleRepository:
    def get_sottofase_documentale(self, id_sottofase):
        return {
            "id_sottofase": id_sottofase,
            "step_corrente": "REDIGI",
            "id_documento_corrente": 10,
        }

    def get_documento_by_id(self, id_documento_sottofase):
        return {"id_documento_sottofase": id_documento_sottofase}

    def list_documenti_by_sottofase(self, id_sottofase):
        return [{"id_sottofase": id_sottofase, "id_documento_sottofase": 10}]

    def list_step_operativi_by_sottofase(self, id_sottofase):
        return [{"id_sottofase": id_sottofase, "codice_step": "REDIGI"}]


class FailingSottofaseDocumentaleRepository:
    def get_sottofase_documentale(self, id_sottofase):
        raise RuntimeError("errore test")

    def get_documento_by_id(self, id_documento_sottofase):
        raise RuntimeError("errore test")

    def list_documenti_by_sottofase(self, id_sottofase):
        raise RuntimeError("errore test")

    def list_step_operativi_by_sottofase(self, id_sottofase):
        raise RuntimeError("errore test")


def test_service_without_repository_returns_safe_fallbacks():
    service = SottofaseDocumentaleService()

    assert service.get_sottofase_documentale(1) is None
    assert service.list_documenti_by_sottofase(1) == []
    assert service.list_step_operativi_by_sottofase(1) == []
    assert service.get_quadro_documentale(1) is None


def test_service_delegates_to_repository():
    service = SottofaseDocumentaleService(
        sottofase_documentale_repository=FakeSottofaseDocumentaleRepository()
    )

    assert service.get_sottofase_documentale(1)["step_corrente"] == "REDIGI"
    assert service.list_documenti_by_sottofase(1) == [
        {"id_sottofase": 1, "id_documento_sottofase": 10}
    ]
    assert service.list_step_operativi_by_sottofase(1) == [
        {"id_sottofase": 1, "codice_step": "REDIGI"}
    ]


def test_get_quadro_documentale_composes_summary():
    service = SottofaseDocumentaleService(
        sottofase_documentale_repository=FakeSottofaseDocumentaleRepository()
    )

    summary = service.get_quadro_documentale(5)

    assert summary["id_sottofase"] == 5
    assert summary["step_corrente"] == "REDIGI"
    assert summary["documento_corrente"] == {"id_documento_sottofase": 10}
    assert summary["documenti"] == [
        {"id_sottofase": 5, "id_documento_sottofase": 10}
    ]
    assert summary["step_operativi"] == [
        {"id_sottofase": 5, "codice_step": "REDIGI"}
    ]


def test_service_returns_safe_fallbacks_when_repository_fails():
    service = SottofaseDocumentaleService(
        sottofase_documentale_repository=FailingSottofaseDocumentaleRepository()
    )

    assert service.get_sottofase_documentale(1) is None
    assert service.list_documenti_by_sottofase(1) == []
    assert service.list_step_operativi_by_sottofase(1) == []
    assert service.get_quadro_documentale(1) is None
