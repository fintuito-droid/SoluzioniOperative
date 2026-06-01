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
        codici_step=None,
        utenti_attivi=None,
        existing_rules=None,
    ):
        self.context = context
        self.steps = steps or []
        self.regole = regole or []
        self.utenti_by_rule = utenti_by_rule or {}
        self.existing = existing or set()
        self.codici_step = codici_step or []
        self.utenti_attivi = utenti_attivi or []
        self.existing_rules = existing_rules or set()
        self.inserted = []
        self.inserted_rules = []

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

    def list_codici_step_presenti(self):
        return self.codici_step

    def list_utenti_attivi(self):
        return self.utenti_attivi

    def exists_regola_default(
        self,
        *,
        codice_step,
        ruolo_richiesto,
        id_utente,
        id_gruppo,
        email,
    ):
        key = (codice_step, ruolo_richiesto, id_utente, id_gruppo, email)
        return key in self.existing_rules

    def inserisci_regola_default(self, **kwargs):
        self.inserted_rules.append(kwargs)
        self.existing_rules.add(
            (
                kwargs["codice_step"],
                kwargs["ruolo_richiesto"],
                kwargs["id_utente"],
                kwargs["id_gruppo"],
                kwargs["email"],
            )
        )
        return 200 + len(self.inserted_rules)


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


def test_default_population_creates_rules_for_existing_supported_steps():
    backups = []
    repository = FakeRepository(
        codici_step=["FINE", "REDIGI", "REVISIONA"],
        utenti_attivi=[
            {
                "id_utente": 1,
                "nome_visualizzato": "Francesco Matranga",
                "email": "francesco@example.it",
            },
            {
                "id_utente": 2,
                "nome_visualizzato": "Claudio Pieri",
                "email": "claudio@example.it",
            },
        ],
    )
    service = _service(repository, backups)

    report = service.popola_regole_assegnazione_default()

    assert [item["codice_step"] for item in report["regole_create"]] == [
        "REDIGI",
        "REVISIONA",
    ]
    assert report["regole_saltate"][0]["codice_step"] == "FINE"
    assert repository.inserted_rules[0]["ruolo_richiesto"] == "OPERATORE"
    assert repository.inserted_rules[1]["ruolo_richiesto"] == "REVISORE"
    assert backups == ["backup.accdb"]


def test_default_population_is_idempotent():
    repository = FakeRepository(
        codici_step=["REDIGI"],
        utenti_attivi=[
            {
                "id_utente": 1,
                "nome_visualizzato": "Francesco Matranga",
                "email": "francesco@example.it",
            }
        ],
    )
    service = _service(repository)

    first = service.popola_regole_assegnazione_default()
    second = service.popola_regole_assegnazione_default()

    assert len(first["regole_create"]) == 1
    assert second["regole_create"] == []
    assert len(second["regole_gia_presenti"]) == 1
    assert len(repository.inserted_rules) == 1


def test_default_population_handles_missing_users_without_error():
    repository = FakeRepository(codici_step=["REDIGI"], utenti_attivi=[])
    service = _service(repository)

    report = service.popola_regole_assegnazione_default()

    assert report["regole_create"] == []
    assert report["regole_saltate"][0]["motivo"] == "Nessun utente attivo disponibile."


def test_default_population_uses_only_existing_step_codes():
    repository = FakeRepository(
        codici_step=["NON_ESISTE"],
        utenti_attivi=[
            {
                "id_utente": 1,
                "nome_visualizzato": "Francesco Matranga",
                "email": "francesco@example.it",
            }
        ],
    )
    service = _service(repository)

    report = service.popola_regole_assegnazione_default()

    assert report["regole_create"] == []
    assert report["regole_saltate"][0]["codice_step"] == "NON_ESISTE"
