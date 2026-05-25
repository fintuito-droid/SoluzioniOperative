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
        id_protocollo_or_entity_type: int | str,
        entity_id: int | str | None = None,
    ) -> dict[str, Any] | list[dict[str, Any]] | None:
        """Restituisce metadati protocollo o metadati generici futuri.

        Uso nuovo:
        `get_metadata(id_protocollo)` restituisce un dizionario con i metadati
        del protocollo oppure `None` se non trovato.

        Uso legacy/preparatorio:
        `get_metadata(entity_type, entity_id)` mantiene il comportamento
        placeholder per metadati generici futuri e restituisce una lista.
        """

        if entity_id is not None:
            self.validate_entity(id_protocollo_or_entity_type, entity_id)

            if not self.feature_enabled():
                return []

            return self.metadata_repository.list_metadata_for_entity(
                id_protocollo_or_entity_type,
                entity_id,
            )

        if self.metadata_repository is None:
            return None

        get_metadata_by_protocollo_id = getattr(
            self.metadata_repository,
            "get_metadata_by_protocollo_id",
            None,
        )

        if get_metadata_by_protocollo_id is None:
            return None

        metadata = get_metadata_by_protocollo_id(id_protocollo_or_entity_type)

        if metadata is None:
            return None

        return self._add_pdf_availability(metadata)

    def _add_pdf_availability(self, metadata: dict[str, Any]) -> dict[str, Any]:
        """Aggiunge `pdf_disponibile` ai metadati protocollo.

        Cosa fa:
        legge il path `percorso_documento_protocollato`, lo passa al resolver
        centralizzato dei documenti e aggiunge un booleano al dizionario.

        Perche esiste:
        il repository deve restare limitato alla lettura dei dati Access. La
        disponibilita fisica del PDF e invece una regola applicativa: dipende
        dal filesystem e dalla normalizzazione sicura introdotta con
        `DocumentPathService`.

        Parametri:
        - `metadata`: dizionario restituito dal repository.

        Valori restituiti:
        lo stesso contenuto logico dei metadati, arricchito con
        `pdf_disponibile`.

        Rischi evitati:
        - accesso filesystem nel repository;
        - duplicazione della risoluzione path nell'endpoint;
        - esposizione al frontend di uno stato ambiguo quando il path esiste in
          Access ma il file non e raggiungibile.
        """

        from backend.services import document_path_service

        enriched_metadata = dict(metadata)
        pdf_path = enriched_metadata.get("percorso_documento_protocollato")
        enriched_metadata["pdf_disponibile"] = (
            document_path_service.resolve_document_path(pdf_path) is not None
        )

        return enriched_metadata

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
