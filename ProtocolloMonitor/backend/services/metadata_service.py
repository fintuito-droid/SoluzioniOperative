"""Service Layer minimo per metadati e tag.

Questo modulo introduce `MetadataService` come predisposizione read-only per la
futura gestione di metadati e tag nella piattaforma Soluzioni Operative.

Il service non viene collegato al runtime, non esegue query dirette, non crea
schema e non modifica il database Access. In futuro potra orchestrare repository
Access o PostgreSQL mantenendo stabile il contratto applicativo.
"""

from __future__ import annotations

from typing import Any


class MetadataService:
    """Service minimale e prudente per metadati/tag futuri.

    Il service accetta un `metadata_repository` opzionale. Quando il repository
    non e disponibile, restituisce fallback sicuri. Questo permette di
    predisporre il Service Layer senza attivare funzionalita non ancora
    supportate dallo schema Access.

    PostgreSQL futuro:
    quando saranno disponibili tabelle dedicate a metadati e tag, questo
    service potra restare il punto stabile usato dagli endpoint, delegando a un
    repository PostgreSQL senza cambiare il frontend.
    """

    def __init__(self, *, metadata_repository: Any | None = None) -> None:
        self.metadata_repository = metadata_repository

    def feature_enabled(self) -> bool:
        """Indica se la feature metadati/tag e disponibile.

        Delega a `metadata_repository.metadata_feature_available()` quando il
        repository e presente. In assenza del repository, o se il repository
        segnala feature non disponibile, restituisce `False`.
        """

        if self.metadata_repository is None:
            return False

        return bool(self.metadata_repository.metadata_feature_available())

    def get_metadata(
        self,
        entity_type: str,
        entity_id: int | str,
    ) -> list[dict[str, Any]]:
        """Restituisce i metadati associati a un'entita.

        Valida prudentemente il riferimento entita. Se la feature non e attiva
        restituisce lista vuota. Non esegue query dirette: la lettura reale,
        quando esistera, restera responsabilita del repository.
        """

        self.validate_entity(entity_type, entity_id)

        if not self.feature_enabled():
            return []

        return self.metadata_repository.list_metadata_for_entity(
            entity_type,
            entity_id,
        )

    def get_tags(
        self,
        entity_type: str,
        entity_id: int | str,
    ) -> list[dict[str, Any]]:
        """Restituisce i tag associati a un'entita.

        Oggi la feature e solo predisposta, quindi il fallback normale e `[]`.
        In futuro il metodo potra delegare a repository PostgreSQL con tabelle
        molti-a-molti tra entita e tag.
        """

        self.validate_entity(entity_type, entity_id)

        if not self.feature_enabled():
            return []

        return self.metadata_repository.list_tags_for_entity(
            entity_type,
            entity_id,
        )

    def validate_entity(self, entity_type: str, entity_id: int | str) -> bool:
        """Valida in modo prudente tipo entita e identificativo.

        La validazione non interroga il database e non verifica l'esistenza
        reale dell'entita. Controlla solo che i valori siano presenti e
        semanticamente utilizzabili come riferimento futuro.

        Restituisce `True` se il riferimento e valido; solleva `ValueError` se
        manca `entity_type` o `entity_id`.
        """

        normalized_entity_type = str(entity_type or "").strip()
        normalized_entity_id = str(entity_id or "").strip()

        if not normalized_entity_type:
            raise ValueError("entity_type e obbligatorio.")

        if not normalized_entity_id:
            raise ValueError("entity_id e obbligatorio.")

        return True
