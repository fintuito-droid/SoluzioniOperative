from datetime import datetime

import pytest

from backend.core.access_backup import AccessBackupError, create_access_backup
from backend.core.config import AppConfig


def test_create_access_backup_copies_configured_database(tmp_path):
    source = tmp_path / "ProtocolloMonitor.accdb"
    source.write_bytes(b"database-test")
    config = AppConfig(access_db_path=str(source))

    backup_path = create_access_backup(
        config=config,
        timestamp=datetime(2026, 5, 27, 12, 0, 0),
    )

    assert backup_path.exists()
    assert backup_path.name == "ProtocolloMonitor_BACKUP_20260527_120000.accdb"
    assert backup_path.parent == tmp_path / "Backup"
    assert backup_path.read_bytes() == b"database-test"
    assert backup_path.stat().st_size == source.stat().st_size


def test_create_access_backup_rejects_missing_database(tmp_path):
    config = AppConfig(access_db_path=str(tmp_path / "missing.accdb"))

    with pytest.raises(AccessBackupError) as exc_info:
        create_access_backup(config=config)

    assert "Database Access configurato non trovato" in str(exc_info.value)


def test_create_access_backup_rejects_lock_file(tmp_path):
    source = tmp_path / "ProtocolloMonitor.accdb"
    source.write_bytes(b"database-test")
    source.with_suffix(".laccdb").write_bytes(b"lock")
    config = AppConfig(access_db_path=str(source))

    with pytest.raises(AccessBackupError) as exc_info:
        create_access_backup(config=config)

    assert "File lock Access presente" in str(exc_info.value)
    assert not (tmp_path / "Backup").exists()
