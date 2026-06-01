from datetime import datetime

import pytest

from backend.services.sottofase_assegnazioni_service import (
    SottofaseAssegnazioniNotFoundError,
    SottofaseAssegnazioniService,
)


class FakeRepository:
    def __init__(
        self,
        *,
        context=None,
        steps=None,
        regole=None,
        utenti_by_rule=None,
        existing=None,
    ):
        self.context = context
        self.steps = steps or []
        self.regole = regole or []
        self.utenti_by_rule = utenti_by_rule or {}
        self.existing = existing or set()
        self.inserted = []

    def get_sottofase_context(self, id_sottofase):
        return self.context

    def list_steps_by_sottofase(self, id_sottofase):
        return self.steps

    def list_regole_attive(self, *, tipo_procedimento, codice_sottofase):
        return [regola for regola in self.regole if regola.get("attiva", True)]

    def resolve_utenti_for_regola(self, regola):
        return self.utenti_by_rule.get(regola["id_regola"], [])

    def exists_partecipante(
        self,
        *,
        id_sottofase,
        id_step_operativo,
        id_utente,
        email,
        ruolo,
    ):
        key = (id_sottofase, id_step_operativo, id_utente, email, ruolo)
        return key in self.existing

    def inserisci_partecipante_assegnato(self, **kwargs):
        self.inserted.append(kwargs)
        self.existing.add(
            (
                kwargs["id_sottofase"],
                kwargs["id_step_operativo"],
                kwargs["id_utente"],
                kwargs["email"],
                kwargs["ruolo"],
            )
        )
        return 100 + len(self.inserted)


def _service(repository, backups=None):
    if backups is None:
        backups = []

    return SottofaseAssegnazioniService(
        assegnazioni_repository=repository,
        backup_factory=lambda: backups.append("backup.accdb") or "backup.accdb",
        now_factory=lambda: datetime(2026, 6, 1, 14, 0, 0),
    )


def _context():
    return {
        "id_sottofase": 7,
        "codice_sottofase": "DOCUMENTALE",
        "tipo_procedimento": "SCIA",
    }


def _step():
    return {
        "id_step_operativo": 12,
        "id_sottofase": 7,
        "codice_step": "REVISIONA",
        "ordine": 1,
    }


def _regola(**overrides):
    regola = {
        "id_regola": 1,
        "codice_step": "REVISIONA",
        "ruolo_richiesto": "REVISORE",
        "obbligatorio": True,
        "attiva": True,
    }
    regola.update(overrides)
    return regola


def test_applies_active_rules_and_creates_participants():
    backups = []
    repository = FakeRepository(
        context=_context(),
        steps=[_step()],
        regole=[_regola()],
        utenti_by_rule={
            1: [
                {
                    "id_utente": 5,
                    "nome_visualizzato": "Mario Rossi",
                    "email": "mario.rossi@example.it",
                }
            ]
        },
    )
    service = _service(repository, backups)

    report = service.applica_regole_assegnazione_sottofase(7)

    assert report["regole_valutate"] == 1
    assert len(report["partecipanti_creati"]) == 1
    assert repository.inserted[0]["ruolo"] == "REVISORE"
    assert backups == ["backup.accdb"]


def test_inactive_rules_are_ignored():
    repository = FakeRepository(
        context=_context(),
        steps=[_step()],
        regole=[_regola(attiva=False)],
    )
    service = _service(repository)

    report = service.applica_regole_assegnazione_sottofase(7)

    assert report["regole_valutate"] == 0
    assert report["partecipanti_creati"] == []


def test_avoids_duplicates_and_is_idempotent():
    backups = []
    repository = FakeRepository(
        context=_context(),
        steps=[_step()],
        regole=[_regola()],
        utenti_by_rule={
            1: [
                {
                    "id_utente": 5,
                    "nome_visualizzato": "Mario Rossi",
                    "email": "mario.rossi@example.it",
                }
            ]
        },
    )
    service = _service(repository, backups)

    first = service.applica_regole_assegnazione_sottofase(7)
    second = service.applica_regole_assegnazione_sottofase(7)

    assert len(first["partecipanti_creati"]) == 1
    assert second["partecipanti_creati"] == []
    assert len(second["partecipanti_gia_presenti"]) == 1
    assert len(repository.inserted) == 1


def test_sets_optional_participant_flag():
    repository = FakeRepository(
        context=_context(),
        steps=[_step()],
        regole=[_regola(obbligatorio=False)],
        utenti_by_rule={
            1: [
                {
                    "id_utente": None,
                    "nome_visualizzato": "Osservatore",
                    "email": "osservatore@example.it",
                }
            ]
        },
    )
    service = _service(repository)

    service.applica_regole_assegnazione_sottofase(7)

    assert repository.inserted[0]["obbligatorio"] is False


def test_reports_rule_without_users():
    repository = FakeRepository(
        context=_context(),
        steps=[_step()],
        regole=[_regola()],
        utenti_by_rule={1: []},
    )
    service = _service(repository)

    report = service.applica_regole_assegnazione_sottofase(7)

    assert report["partecipanti_creati"] == []
    assert report["regole_senza_utenti"][0]["id_regola"] == 1


def test_requires_existing_sottofase():
    service = _service(FakeRepository(context=None))

    with pytest.raises(SottofaseAssegnazioniNotFoundError):
        service.applica_regole_assegnazione_sottofase(999)
