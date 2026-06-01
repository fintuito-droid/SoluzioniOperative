from datetime import datetime

import pytest

from backend.services.sottofase_partecipanti_service import (
    SottofasePartecipantiBackupError,
    SottofasePartecipantiDuplicateError,
    SottofasePartecipantiNotFoundError,
    SottofasePartecipantiService,
    SottofasePartecipantiValidationError,
    SottofasePartecipantiWriteError,
)


class FakeSottofaseDocumentaleService:
    def __init__(self, exists=True):
        self.exists = exists

    def get_sottofase_documentale(self, id_sottofase):
        if not self.exists:
            return None

        return {"id_sottofase": id_sottofase, "titolo": "Revisiona"}


class FakeRepository:
    def __init__(self, *, duplicate=False, fail_insert=False, steps=None):
        self.duplicate = duplicate
        self.fail_insert = fail_insert
        self.steps = steps or {}
        self.insert_payload = None

    def list_by_sottofase(self, id_sottofase):
        return []

    def list_by_step(self, *, id_sottofase, id_step_operativo):
        return []

    def exists_duplicate(self, *, id_sottofase, id_step_operativo, email, ruolo):
        return self.duplicate

    def get_step_operativo_by_id(self, id_step_operativo):
        return self.steps.get(id_step_operativo)

    def inserisci_partecipante(self, **kwargs):
        if self.fail_insert:
            raise RuntimeError("insert fallito")

        self.insert_payload = kwargs
        return 42

    def get_by_id(self, id_partecipante):
        return {
            "id_partecipante": id_partecipante,
            "nome_visualizzato": self.insert_payload["nome_visualizzato"],
            "iniziali": self.insert_payload["iniziali"],
        }


def test_get_participants_empty_list():
    service = SottofasePartecipantiService(
        partecipanti_repository=FakeRepository(),
        sottofase_documentale_service=FakeSottofaseDocumentaleService(),
    )

    assert service.list_partecipanti(7) == []


def test_create_valid_participant_with_backup_and_initials():
    backups = []
    repository = FakeRepository()
    service = SottofasePartecipantiService(
        partecipanti_repository=repository,
        sottofase_documentale_service=FakeSottofaseDocumentaleService(),
        backup_factory=lambda: backups.append("backup.accdb") or "backup.accdb",
        now_factory=lambda: datetime(2026, 6, 1, 10, 0, 0),
    )

    response = service.crea_partecipante(
        id_sottofase=7,
        payload={
            "nomeVisualizzato": "Mario Rossi",
            "email": "mario.rossi@example.it",
            "ruolo": "REVISORE",
            "statoPartecipante": "ASSEGNATO",
        },
    )

    assert response["success"] is True
    assert response["id_partecipante"] == 42
    assert backups == ["backup.accdb"]
    assert repository.insert_payload["iniziali"] == "MR"
    assert repository.insert_payload["id_step_operativo"] is None


def test_create_valid_step_participant():
    repository = FakeRepository(
        steps={
            12: {
                "id_step_operativo": 12,
                "id_sottofase": 7,
                "codice_step": "REVISIONA",
            }
        }
    )
    service = SottofasePartecipantiService(
        partecipanti_repository=repository,
        sottofase_documentale_service=FakeSottofaseDocumentaleService(),
        backup_factory=lambda: "backup.accdb",
    )

    response = service.crea_partecipante(
        id_sottofase=7,
        payload={
            "idStepOperativo": 12,
            "nomeVisualizzato": "Mario Rossi",
            "email": "mario.rossi@example.it",
            "ruolo": "REVISORE",
            "statoPartecipante": "ASSEGNATO",
        },
    )

    assert response["success"] is True
    assert repository.insert_payload["id_step_operativo"] == 12


def test_create_step_participant_rejects_missing_step():
    service = SottofasePartecipantiService(
        partecipanti_repository=FakeRepository(),
        sottofase_documentale_service=FakeSottofaseDocumentaleService(),
    )

    with pytest.raises(SottofasePartecipantiValidationError) as exc_info:
        service.crea_partecipante(
            id_sottofase=7,
            payload={
                "idStepOperativo": 999,
                "nomeVisualizzato": "Mario Rossi",
                "ruolo": "REVISORE",
                "statoPartecipante": "ASSEGNATO",
            },
        )

    assert "Step operativo non trovato" in str(exc_info.value)


def test_create_step_participant_rejects_step_from_other_sottofase():
    repository = FakeRepository(
        steps={
            12: {
                "id_step_operativo": 12,
                "id_sottofase": 99,
                "codice_step": "REVISIONA",
            }
        }
    )
    service = SottofasePartecipantiService(
        partecipanti_repository=repository,
        sottofase_documentale_service=FakeSottofaseDocumentaleService(),
    )

    with pytest.raises(SottofasePartecipantiValidationError) as exc_info:
        service.crea_partecipante(
            id_sottofase=7,
            payload={
                "idStepOperativo": 12,
                "nomeVisualizzato": "Mario Rossi",
                "ruolo": "REVISORE",
                "statoPartecipante": "ASSEGNATO",
            },
        )

    assert "non appartenente" in str(exc_info.value)


@pytest.mark.parametrize(
    ("codice_step", "ruolo"),
    [
        ("REVISIONA", "REVISORE"),
        ("FIRMA", "FIRMATARIO"),
        ("PROTOCOLLA", "PROTOCOLLATORE"),
    ],
)
def test_create_step_participant_accepts_coherent_role(codice_step, ruolo):
    repository = FakeRepository(
        steps={
            12: {
                "id_step_operativo": 12,
                "id_sottofase": 7,
                "codice_step": codice_step,
            }
        }
    )
    service = SottofasePartecipantiService(
        partecipanti_repository=repository,
        sottofase_documentale_service=FakeSottofaseDocumentaleService(),
        backup_factory=lambda: "backup.accdb",
    )

    response = service.crea_partecipante(
        id_sottofase=7,
        payload={
            "idStepOperativo": 12,
            "nomeVisualizzato": "Mario Rossi",
            "ruolo": ruolo,
            "statoPartecipante": "ASSEGNATO",
        },
    )

    assert response["success"] is True


def test_create_step_participant_rejects_incoherent_role():
    repository = FakeRepository(
        steps={
            12: {
                "id_step_operativo": 12,
                "id_sottofase": 7,
                "codice_step": "FIRMA",
            }
        }
    )
    service = SottofasePartecipantiService(
        partecipanti_repository=repository,
        sottofase_documentale_service=FakeSottofaseDocumentaleService(),
    )

    with pytest.raises(SottofasePartecipantiValidationError) as exc_info:
        service.crea_partecipante(
            id_sottofase=7,
            payload={
                "idStepOperativo": 12,
                "nomeVisualizzato": "Mario Rossi",
                "ruolo": "REVISORE",
                "statoPartecipante": "ASSEGNATO",
            },
        )

    assert "non coerente" in str(exc_info.value)


def test_create_participant_rejects_missing_name():
    service = SottofasePartecipantiService(
        partecipanti_repository=FakeRepository(),
        sottofase_documentale_service=FakeSottofaseDocumentaleService(),
    )

    with pytest.raises(SottofasePartecipantiValidationError) as exc_info:
        service.crea_partecipante(
            id_sottofase=7,
            payload={
                "nomeVisualizzato": " ",
                "ruolo": "REVISORE",
                "statoPartecipante": "ASSEGNATO",
            },
        )

    assert "nomeVisualizzato" in str(exc_info.value)


def test_create_participant_rejects_invalid_role():
    service = SottofasePartecipantiService(
        partecipanti_repository=FakeRepository(),
        sottofase_documentale_service=FakeSottofaseDocumentaleService(),
    )

    with pytest.raises(SottofasePartecipantiValidationError) as exc_info:
        service.crea_partecipante(
            id_sottofase=7,
            payload={
                "nomeVisualizzato": "Mario Rossi",
                "ruolo": "NON_VALIDO",
                "statoPartecipante": "ASSEGNATO",
            },
        )

    assert "Ruolo" in str(exc_info.value)


def test_create_participant_rejects_invalid_state():
    service = SottofasePartecipantiService(
        partecipanti_repository=FakeRepository(),
        sottofase_documentale_service=FakeSottofaseDocumentaleService(),
    )

    with pytest.raises(SottofasePartecipantiValidationError) as exc_info:
        service.crea_partecipante(
            id_sottofase=7,
            payload={
                "nomeVisualizzato": "Mario Rossi",
                "ruolo": "REVISORE",
                "statoPartecipante": "NON_VALIDO",
            },
        )

    assert "Stato" in str(exc_info.value)


def test_create_participant_rejects_duplicate_email_role():
    service = SottofasePartecipantiService(
        partecipanti_repository=FakeRepository(duplicate=True),
        sottofase_documentale_service=FakeSottofaseDocumentaleService(),
    )

    with pytest.raises(SottofasePartecipantiDuplicateError):
        service.crea_partecipante(
            id_sottofase=7,
            payload={
                "nomeVisualizzato": "Mario Rossi",
                "email": "mario.rossi@example.it",
                "ruolo": "REVISORE",
                "statoPartecipante": "ASSEGNATO",
            },
        )


def test_create_step_participant_rejects_duplicate_email_role_on_step():
    repository = FakeRepository(
        duplicate=True,
        steps={
            12: {
                "id_step_operativo": 12,
                "id_sottofase": 7,
                "codice_step": "REVISIONA",
            }
        },
    )
    service = SottofasePartecipantiService(
        partecipanti_repository=repository,
        sottofase_documentale_service=FakeSottofaseDocumentaleService(),
    )

    with pytest.raises(SottofasePartecipantiDuplicateError):
        service.crea_partecipante(
            id_sottofase=7,
            payload={
                "idStepOperativo": 12,
                "nomeVisualizzato": "Mario Rossi",
                "email": "mario.rossi@example.it",
                "ruolo": "REVISORE",
                "statoPartecipante": "ASSEGNATO",
            },
        )


def test_create_participant_requires_existing_sottofase():
    service = SottofasePartecipantiService(
        partecipanti_repository=FakeRepository(),
        sottofase_documentale_service=FakeSottofaseDocumentaleService(exists=False),
    )

    with pytest.raises(SottofasePartecipantiNotFoundError):
        service.crea_partecipante(
            id_sottofase=999,
            payload={
                "nomeVisualizzato": "Mario Rossi",
                "ruolo": "REVISORE",
                "statoPartecipante": "ASSEGNATO",
            },
        )


def test_create_participant_stops_when_backup_fails():
    service = SottofasePartecipantiService(
        partecipanti_repository=FakeRepository(),
        sottofase_documentale_service=FakeSottofaseDocumentaleService(),
        backup_factory=lambda: (_ for _ in ()).throw(RuntimeError("backup fallito")),
    )

    with pytest.raises(SottofasePartecipantiBackupError):
        service.crea_partecipante(
            id_sottofase=7,
            payload={
                "nomeVisualizzato": "Mario Rossi",
                "ruolo": "REVISORE",
                "statoPartecipante": "ASSEGNATO",
            },
        )


def test_create_participant_wraps_insert_error():
    service = SottofasePartecipantiService(
        partecipanti_repository=FakeRepository(fail_insert=True),
        sottofase_documentale_service=FakeSottofaseDocumentaleService(),
        backup_factory=lambda: "backup.accdb",
    )

    with pytest.raises(SottofasePartecipantiWriteError):
        service.crea_partecipante(
            id_sottofase=7,
            payload={
                "nomeVisualizzato": "Mario Rossi",
                "ruolo": "REVISORE",
                "statoPartecipante": "ASSEGNATO",
            },
        )
