from backend.services.sottofase_documentale_service import (
    SottofaseAlreadyLinkedError,
    SottofaseAssociazioneNotFoundError,
    SottofaseDocumentaleService,
    SottofaseNotAssociableError,
    SottofaseStepAlreadyLinkedError,
    SottofaseStepFaseMismatchError,
    SottofaseStepNotFoundError,
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


_DEFAULT = object()


class FakeAssociazioneRepository:
    def __init__(
        self,
        *,
        step=_DEFAULT,
        sottofase=_DEFAULT,
        active_sottofase=None,
    ):
        self.step = step if step is not _DEFAULT else {
            "id_step_orizzontale": 10,
            "id_fase": 3,
            "attivo": True,
        }
        self.sottofase = sottofase if sottofase is not _DEFAULT else {
            "id_sottofase": 25,
            "id_fase": 3,
            "id_step_orizzontale": None,
            "stato_sottofase": "BOZZA",
            "attivo": True,
        }
        self.active_sottofase = active_sottofase
        self.associa_calls = []
        self.disponibili_calls = []
        self.disponibili = [
            {
                "id_sottofase": 25,
                "titolo": "Fascicolo documentale",
                "stato_sottofase": "BOZZA",
                "attivo": True,
                "ha_documenti": True,
                "documenti_count": 2,
            }
        ]

    def get_step_orizzontale_context(self, id_step_orizzontale):
        return self.step

    def get_sottofase_aggancio_context(self, id_sottofase):
        return self.sottofase

    def get_sottofase_attiva_by_step(self, id_step_orizzontale):
        return self.active_sottofase

    def associa_sottofase_a_step(self, **kwargs):
        self.associa_calls.append(kwargs)
        return {
            "success": True,
            "id_step_orizzontale": kwargs["id_step_orizzontale"],
            "id_sottofase": kwargs["id_sottofase"],
            "tipo_aggancio": "STEP",
            "sottofase_principale": True,
        }

    def list_sottofasi_disponibili_per_step(self, **kwargs):
        self.disponibili_calls.append(kwargs)
        return self.disponibili


class FakeAssegnazioniService:
    def __init__(self, *, raises=None):
        self.raises = raises
        self.calls = []
        self.created = False

    def applica_regole_assegnazione_sottofase(self, id_sottofase):
        self.calls.append(id_sottofase)

        if self.raises:
            raise self.raises

        if self.created:
            return {
                "success": True,
                "id_sottofase": id_sottofase,
                "partecipanti_creati": [],
                "partecipanti_gia_presenti": [{"id_sottofase": id_sottofase}],
            }

        self.created = True
        return {
            "success": True,
            "id_sottofase": id_sottofase,
            "partecipanti_creati": [{"id_sottofase": id_sottofase}],
            "partecipanti_gia_presenti": [],
        }


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
    assert service.get_documento_by_id(10) == {"id_documento_sottofase": 10}
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
    assert summary["assegnazioni_auto_report"] is None


def test_get_quadro_documentale_applies_assignment_rules_on_open():
    assegnazioni_service = FakeAssegnazioniService()
    service = SottofaseDocumentaleService(
        sottofase_documentale_repository=FakeSottofaseDocumentaleRepository(),
        sottofase_assegnazioni_service=assegnazioni_service,
    )

    summary = service.get_quadro_documentale(5)

    assert assegnazioni_service.calls == [5]
    assert summary["assegnazioni_auto_report"]["success"] is True
    assert summary["assegnazioni_auto_report"]["partecipanti_creati"] == [
        {"id_sottofase": 5}
    ]


def test_get_quadro_documentale_second_open_does_not_duplicate_assignments():
    assegnazioni_service = FakeAssegnazioniService()
    service = SottofaseDocumentaleService(
        sottofase_documentale_repository=FakeSottofaseDocumentaleRepository(),
        sottofase_assegnazioni_service=assegnazioni_service,
    )

    first = service.get_quadro_documentale(5)
    second = service.get_quadro_documentale(5)

    assert len(first["assegnazioni_auto_report"]["partecipanti_creati"]) == 1
    assert second["assegnazioni_auto_report"]["partecipanti_creati"] == []
    assert len(second["assegnazioni_auto_report"]["partecipanti_gia_presenti"]) == 1


def test_get_quadro_documentale_assignment_error_does_not_block_loading():
    service = SottofaseDocumentaleService(
        sottofase_documentale_repository=FakeSottofaseDocumentaleRepository(),
        sottofase_assegnazioni_service=FakeAssegnazioniService(
            raises=RuntimeError("regola non valida")
        ),
    )

    summary = service.get_quadro_documentale(5)

    assert summary["id_sottofase"] == 5
    assert summary["assegnazioni_auto_report"]["success"] is False
    assert summary["assegnazioni_auto_report"]["non_bloccante"] is True


def test_get_quadro_documentale_without_assignment_service_stays_loadable():
    service = SottofaseDocumentaleService(
        sottofase_documentale_repository=FakeSottofaseDocumentaleRepository(),
    )

    summary = service.get_quadro_documentale(5)

    assert summary["id_sottofase"] == 5
    assert summary["assegnazioni_auto_report"] is None


def test_service_returns_safe_fallbacks_when_repository_fails():
    service = SottofaseDocumentaleService(
        sottofase_documentale_repository=FailingSottofaseDocumentaleRepository()
    )

    assert service.get_sottofase_documentale(1) is None
    assert service.list_documenti_by_sottofase(1) == []
    assert service.list_step_operativi_by_sottofase(1) == []
    assert service.get_quadro_documentale(1) is None


def test_associa_sottofase_a_step_orizzontale_validates_and_delegates():
    repository = FakeAssociazioneRepository()
    service = SottofaseDocumentaleService(
        sottofase_documentale_repository=repository,
        now_factory=lambda: "2026-06-07 08:00:00",
    )

    result = service.associa_sottofase_a_step_orizzontale(
        id_fase=3,
        id_step_orizzontale=10,
        id_sottofase=25,
        utente="mario",
    )

    assert result == {
        "success": True,
        "id_step_orizzontale": 10,
        "id_sottofase": 25,
        "tipo_aggancio": "STEP",
        "sottofase_principale": True,
        "id_fase": 3,
    }
    assert repository.associa_calls == [
        {
            "id_sottofase": 25,
            "id_step_orizzontale": 10,
            "data_aggancio": "2026-06-07 08:00:00",
            "utente_aggancio": "mario",
        }
    ]


def test_associa_sottofase_a_step_orizzontale_uses_system_user_by_default():
    repository = FakeAssociazioneRepository()
    service = SottofaseDocumentaleService(
        sottofase_documentale_repository=repository,
        now_factory=lambda: "now",
    )

    service.associa_sottofase_a_step_orizzontale(
        id_fase=3,
        id_step_orizzontale=10,
        id_sottofase=25,
        utente="",
    )

    assert repository.associa_calls[0]["utente_aggancio"] == "system"


def test_associa_sottofase_a_step_orizzontale_blocks_missing_step():
    service = SottofaseDocumentaleService(
        sottofase_documentale_repository=FakeAssociazioneRepository(step=None)
    )

    try:
        service.associa_sottofase_a_step_orizzontale(
            id_fase=3,
            id_step_orizzontale=10,
            id_sottofase=25,
        )
    except SottofaseStepNotFoundError:
        pass
    else:
        raise AssertionError("Expected SottofaseStepNotFoundError")


def test_associa_sottofase_a_step_orizzontale_blocks_missing_sottofase():
    service = SottofaseDocumentaleService(
        sottofase_documentale_repository=FakeAssociazioneRepository(sottofase=None)
    )

    try:
        service.associa_sottofase_a_step_orizzontale(
            id_fase=3,
            id_step_orizzontale=10,
            id_sottofase=25,
        )
    except SottofaseAssociazioneNotFoundError:
        pass
    else:
        raise AssertionError("Expected SottofaseAssociazioneNotFoundError")


def test_associa_sottofase_a_step_orizzontale_blocks_step_fase_mismatch():
    service = SottofaseDocumentaleService(
        sottofase_documentale_repository=FakeAssociazioneRepository(
            step={"id_step_orizzontale": 10, "id_fase": 4, "attivo": True}
        )
    )

    try:
        service.associa_sottofase_a_step_orizzontale(
            id_fase=3,
            id_step_orizzontale=10,
            id_sottofase=25,
        )
    except SottofaseStepFaseMismatchError:
        pass
    else:
        raise AssertionError("Expected SottofaseStepFaseMismatchError")


def test_associa_sottofase_a_step_orizzontale_blocks_sottofase_fase_mismatch():
    service = SottofaseDocumentaleService(
        sottofase_documentale_repository=FakeAssociazioneRepository(
            sottofase={
                "id_sottofase": 25,
                "id_fase": 4,
                "id_step_orizzontale": None,
                "stato_sottofase": "BOZZA",
                "attivo": True,
            }
        )
    )

    try:
        service.associa_sottofase_a_step_orizzontale(
            id_fase=3,
            id_step_orizzontale=10,
            id_sottofase=25,
        )
    except SottofaseStepFaseMismatchError:
        pass
    else:
        raise AssertionError("Expected SottofaseStepFaseMismatchError")


def test_associa_sottofase_a_step_orizzontale_blocks_step_already_linked():
    service = SottofaseDocumentaleService(
        sottofase_documentale_repository=FakeAssociazioneRepository(
            active_sottofase={"id_sottofase": 99, "id_step_orizzontale": 10}
        )
    )

    try:
        service.associa_sottofase_a_step_orizzontale(
            id_fase=3,
            id_step_orizzontale=10,
            id_sottofase=25,
        )
    except SottofaseStepAlreadyLinkedError:
        pass
    else:
        raise AssertionError("Expected SottofaseStepAlreadyLinkedError")


def test_associa_sottofase_a_step_orizzontale_blocks_sottofase_linked_elsewhere():
    service = SottofaseDocumentaleService(
        sottofase_documentale_repository=FakeAssociazioneRepository(
            sottofase={
                "id_sottofase": 25,
                "id_fase": 3,
                "id_step_orizzontale": 99,
                "stato_sottofase": "BOZZA",
                "attivo": True,
            }
        )
    )

    try:
        service.associa_sottofase_a_step_orizzontale(
            id_fase=3,
            id_step_orizzontale=10,
            id_sottofase=25,
        )
    except SottofaseAlreadyLinkedError:
        pass
    else:
        raise AssertionError("Expected SottofaseAlreadyLinkedError")


def test_associa_sottofase_a_step_orizzontale_blocks_inactive_sottofase():
    service = SottofaseDocumentaleService(
        sottofase_documentale_repository=FakeAssociazioneRepository(
            sottofase={
                "id_sottofase": 25,
                "id_fase": 3,
                "id_step_orizzontale": None,
                "stato_sottofase": "BOZZA",
                "attivo": False,
            }
        )
    )

    try:
        service.associa_sottofase_a_step_orizzontale(
            id_fase=3,
            id_step_orizzontale=10,
            id_sottofase=25,
        )
    except SottofaseNotAssociableError:
        pass
    else:
        raise AssertionError("Expected SottofaseNotAssociableError")


def test_associa_sottofase_a_step_orizzontale_blocks_annullata_or_archiviata():
    for stato in ("ANNULLATA", "ARCHIVIATA"):
        service = SottofaseDocumentaleService(
            sottofase_documentale_repository=FakeAssociazioneRepository(
                sottofase={
                    "id_sottofase": 25,
                    "id_fase": 3,
                    "id_step_orizzontale": None,
                    "stato_sottofase": stato,
                    "attivo": True,
                }
            )
        )

        try:
            service.associa_sottofase_a_step_orizzontale(
                id_fase=3,
                id_step_orizzontale=10,
                id_sottofase=25,
            )
        except SottofaseNotAssociableError:
            pass
        else:
            raise AssertionError("Expected SottofaseNotAssociableError")


def test_list_sottofasi_disponibili_per_step_validates_step_and_delegates():
    repository = FakeAssociazioneRepository()
    service = SottofaseDocumentaleService(
        sottofase_documentale_repository=repository
    )

    result = service.list_sottofasi_disponibili_per_step(
        id_fase=3,
        id_step_orizzontale=10,
    )

    assert result == {
        "id_fase": 3,
        "id_step_orizzontale": 10,
        "items": repository.disponibili,
    }
    assert repository.disponibili_calls == [
        {"id_fase": 3, "id_step_orizzontale": 10}
    ]


def test_list_sottofasi_disponibili_per_step_blocks_missing_step():
    service = SottofaseDocumentaleService(
        sottofase_documentale_repository=FakeAssociazioneRepository(step=None)
    )

    try:
        service.list_sottofasi_disponibili_per_step(
            id_fase=3,
            id_step_orizzontale=10,
        )
    except SottofaseStepNotFoundError:
        pass
    else:
        raise AssertionError("Expected SottofaseStepNotFoundError")


def test_list_sottofasi_disponibili_per_step_blocks_step_fase_mismatch():
    service = SottofaseDocumentaleService(
        sottofase_documentale_repository=FakeAssociazioneRepository(
            step={"id_step_orizzontale": 10, "id_fase": 99, "attivo": True}
        )
    )

    try:
        service.list_sottofasi_disponibili_per_step(
            id_fase=3,
            id_step_orizzontale=10,
        )
    except SottofaseStepFaseMismatchError:
        pass
    else:
        raise AssertionError("Expected SottofaseStepFaseMismatchError")
