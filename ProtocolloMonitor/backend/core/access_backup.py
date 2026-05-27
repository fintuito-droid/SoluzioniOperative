"""Backup prudente del database Access prima delle scritture controllate.

Il modulo serve agli endpoint che introducono scritture reali su Access. Prima
di qualunque `UPDATE` o `INSERT`, il chiamante deve creare una copia del file
`.accdb` configurato in `backend.core.config`.

Questo modulo non modifica schema, non apre Access e non esegue query. Copia
solo il file database configurato, verifica che il backup esista e controlla la
dimensione per ridurre il rischio di procedere con una copia corrotta.
"""

from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path

from .config import AppConfig, get_config


class AccessBackupError(RuntimeError):
    """Errore controllato quando il backup Access non e sicuro."""


def create_access_backup(
    *,
    config: AppConfig | None = None,
    timestamp: datetime | None = None,
) -> Path:
    """Crea e verifica una copia del database Access configurato.

    La funzione e volutamente autonoma: viene chiamata prima della transazione
    di scrittura, cosi un fallimento del backup blocca qualunque modifica reale.

    Validazioni:
    - il file sorgente deve esistere;
    - non deve essere presente un lock `.laccdb`;
    - la cartella `Backup` viene creata se assente;
    - il backup deve esistere;
    - il backup deve avere dimensione maggiore di zero;
    - la dimensione deve coincidere con quella del sorgente.
    """

    active_config = config or get_config()
    source_path = Path(active_config.access_db_path)

    if not source_path.exists():
        raise AccessBackupError(
            f"Database Access configurato non trovato: {source_path}"
        )

    lock_path = source_path.with_suffix(".laccdb")

    if lock_path.exists():
        raise AccessBackupError(
            f"File lock Access presente, backup non sicuro: {lock_path}"
        )

    backup_dir = source_path.parent / "Backup"
    backup_dir.mkdir(parents=True, exist_ok=True)

    backup_timestamp = (timestamp or datetime.now()).strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / (
        f"{source_path.stem}_BACKUP_{backup_timestamp}{source_path.suffix}"
    )

    shutil.copy2(source_path, backup_path)

    if not backup_path.exists():
        raise AccessBackupError(f"Backup Access non creato: {backup_path}")

    source_size = source_path.stat().st_size
    backup_size = backup_path.stat().st_size

    if backup_size <= 0:
        raise AccessBackupError(f"Backup Access vuoto: {backup_path}")

    if source_size != backup_size:
        raise AccessBackupError(
            "Dimensione backup Access diversa dal sorgente: "
            f"origine={source_size}, backup={backup_size}"
        )

    return backup_path
