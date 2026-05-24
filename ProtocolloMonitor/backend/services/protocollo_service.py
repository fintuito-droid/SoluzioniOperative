"""Service Layer minimo per ProtocolloMonitor.

Questo modulo introduce `ProtocolloService` come primo punto di ingresso della
logica applicativa sopra i repository, ma non lo collega ancora al runtime.

Il service e volutamente prudente:

- non modifica dati;
- non crea tabelle;
- non cambia endpoint;
- non accede direttamente al database;
- non assume che i repository siano sempre presenti;
- restituisce valori sicuri quando una dipendenza non e disponibile.

In uno step successivo le route FastAPI potranno chiamare questo service al
posto dei repository o delle query inline. Per ora il file e solo preparatorio
e non altera il comportamento di ProtocolloMonitor.
"""

from __future__ import annotations

from typing import Any


class ProtocolloService:
    """Service applicativo minimale e read-only per protocolli.

    Il service riceve repository opzionali dall'esterno. Questa scelta evita di
    creare dipendenze rigide e permette, nei prossimi step, di sostituire
    repository Access con repository PostgreSQL senza cambiare le route.

    Parametri:
    - `protocollo_repository`: repository per dati protocollo, se disponibile.
    - `documento_repository`: repository per dati documento/PDF, se disponibile.
    - `metadata_repository`: repository per metadati/tag futuri, se disponibile.

    Nota importante:
    questa classe non viene ancora importata da `backend/main.py`; quindi non
    cambia endpoint, query, formato dati o runtime.
    """

    def __init__(
        self,
        *,
        protocollo_repository: Any | None = None,
        documento_repository: Any | None = None,
        metadata_repository: Any | None = None,
    ) -> None:
        self.protocollo_repository = protocollo_repository
        self.documento_repository = documento_repository
        self.metadata_repository = metadata_repository

    def get_protocollo_detail(self, id_protocollo: int) -> dict[str, Any]:
        """Restituisce il dettaglio protocollo delegando al repository.

        Se `protocollo_repository` non e disponibile, restituisce la struttura
        sicura gia usata dal backend quando un protocollo non viene trovato.
        Non modifica dati e non apre connessioni direttamente.
        """

        if self.protocollo_repository is None:
            return {
                "protocollo": None,
                "assegnazioni": [],
                "destinatari": [],
                "firmatari": [],
            }

        return self.protocollo_repository.get_protocollo_detail(id_protocollo)

    def get_pdf_path(self, id_protocollo: int) -> str | None:
        """Restituisce il percorso PDF delegando ai repository disponibili.

        La priorita va a `documento_repository`, per preparare il futuro dominio
        documentale. Se non disponibile, usa `protocollo_repository` come
        fallback, per compatibilita con il repository protocollo gia creato.
        Se nessun repository e disponibile, restituisce `None`.
        """

        if self.documento_repository is not None:
            return self.documento_repository.get_pdf_path_by_protocollo_id(
                id_protocollo
            )

        if self.protocollo_repository is not None:
            return self.protocollo_repository.get_pdf_path(id_protocollo)

        return None

    def metadata_available(self) -> bool:
        """Indica se metadati/tag sono disponibili tramite repository.

        Oggi la feature metadati e solo predisposta. Se il repository non e
        presente, o se segnala feature non disponibile, il service restituisce
        `False` in modo conservativo.
        """

        if self.metadata_repository is None:
            return False

        return bool(self.metadata_repository.metadata_feature_available())
