"""Service Layer minimo per documenti ProtocolloMonitor.

Questo modulo introduce `DocumentoService` come predisposizione read-only sopra
il repository documentale, senza collegarlo al runtime esistente.

Il service non modifica dati, non crea query nuove, non cambia endpoint e non
tocca il database. Serve solo a preparare il punto in cui, in futuro, verranno
centralizzate regole applicative su documenti, PDF, metadati e storage.
"""

from __future__ import annotations

from typing import Any


class DocumentoService:
    """Service minimale e prudente per informazioni documentali.

    Il service riceve repository opzionali dall'esterno:

    - `documento_repository`: repository read-only per documento/PDF;
    - `metadata_repository`: repository placeholder per metadati/tag futuri.

    Se i repository non sono disponibili, i metodi restituiscono fallback
    sicuri. La classe non viene ancora usata da `backend/main.py`, quindi non
    cambia il comportamento applicativo attuale.
    """

    def __init__(
        self,
        *,
        documento_repository: Any | None = None,
        metadata_repository: Any | None = None,
    ) -> None:
        self.documento_repository = documento_repository
        self.metadata_repository = metadata_repository

    def get_documento(self, protocollo_id: int) -> dict[str, Any] | None:
        """Restituisce il documento collegato a un protocollo, se disponibile.

        Delega a `documento_repository.get_documento_by_protocollo_id` quando
        il repository e presente. In assenza del repository restituisce `None`.
        Non esegue query direttamente e non modifica dati.
        """

        if self.documento_repository is None:
            return None

        return self.documento_repository.get_documento_by_protocollo_id(
            protocollo_id
        )

    def document_exists(self, protocollo_id: int) -> bool:
        """Indica se esiste un riferimento documentale per il protocollo.

        Delega a `documento_repository.document_exists_for_protocollo` quando
        disponibile. In assenza del repository restituisce `False`.

        Questo metodo non verifica il filesystem e non modifica il database:
        resta una predisposizione per un futuro storage service.
        """

        if self.documento_repository is None:
            return False

        return bool(
            self.documento_repository.document_exists_for_protocollo(
                protocollo_id
            )
        )

    def get_document_metadata(self, protocollo_id: int) -> list[dict[str, Any]]:
        """Restituisce metadati documento futuri con fallback sicuro.

        Delega a `metadata_repository.list_metadata_for_entity` usando
        `entity_type="documento"` quando il repository e presente e la feature
        risulta disponibile. Oggi il repository metadati e un placeholder, quindi
        il comportamento sicuro atteso e una lista vuota.
        """

        if self.metadata_repository is None:
            return []

        if not self.metadata_repository.metadata_feature_available():
            return []

        return self.metadata_repository.list_metadata_for_entity(
            "documento",
            protocollo_id,
        )
