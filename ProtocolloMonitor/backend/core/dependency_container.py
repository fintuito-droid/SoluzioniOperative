"""Dependency container minimale per ProtocolloMonitor.

Questo modulo prepara un punto unico di composizione per Repository e Service,
ma non viene ancora collegato al runtime esistente.

Il container e intenzionalmente piccolo e prudente:

- non modifica endpoint;
- non apre query direttamente;
- non crea schema;
- non cambia database;
- non introduce dipendenze obbligatorie nei runtime FastAPI/Flask;
- inizializza le dipendenze in modo lazy solo quando richieste.

In futuro potra diventare il punto in cui scegliere repository Access o
PostgreSQL in base alla configurazione centralizzata.
"""

from __future__ import annotations

from typing import Any


class DependencyContainer:
    """Container preparatorio per Service Layer e Repository Pattern.

    Il container costruisce repository e service solo alla prima richiesta.
    Questa scelta permette di introdurre la composizione architetturale senza
    effetti collaterali all'import del modulo.

    PostgreSQL futuro:
    quando PostgreSQL diventera operativo, questo container potra scegliere tra
    repository Access e repository PostgreSQL senza cambiare le route FastAPI.
    """

    def __init__(self) -> None:
        self._protocollo_repository: Any | None = None
        self._documento_repository: Any | None = None
        self._metadata_repository: Any | None = None
        self._procedimento_repository: Any | None = None

        self._protocollo_service: Any | None = None
        self._documento_service: Any | None = None
        self._metadata_service: Any | None = None
        self._procedimento_service: Any | None = None

    def _get_protocollo_repository(self) -> Any:
        """Restituisce il repository protocolli, creandolo lazy.

        Il metodo resta privato per evitare che il runtime inizi a dipendere
        direttamente dai repository. Gli endpoint futuri dovrebbero usare i
        service pubblici del container.
        """

        if self._protocollo_repository is None:
            from ..repositories.protocollo_repository import ProtocolloRepository

            self._protocollo_repository = ProtocolloRepository()

        return self._protocollo_repository

    def _get_documento_repository(self) -> Any:
        """Restituisce il repository documenti, creandolo lazy."""

        if self._documento_repository is None:
            from ..repositories.documento_repository import DocumentoRepository

            self._documento_repository = DocumentoRepository()

        return self._documento_repository

    def _get_metadata_repository(self) -> Any:
        """Restituisce il repository metadati, creandolo lazy."""

        if self._metadata_repository is None:
            from ..repositories.metadata_repository import MetadataRepository

            self._metadata_repository = MetadataRepository()

        return self._metadata_repository

    def _get_procedimento_repository(self) -> Any:
        """Restituisce il repository procedimenti, creandolo lazy."""

        if self._procedimento_repository is None:
            from ..repositories.procedimento_repository import ProcedimentoRepository

            self._procedimento_repository = ProcedimentoRepository()

        return self._procedimento_repository

    def get_protocollo_service(self) -> Any:
        """Restituisce `ProtocolloService` con repository opzionali collegati.

        Il service e creato solo alla prima richiesta. Non viene integrato nelle
        route in questa attivita, quindi il comportamento runtime resta
        invariato.
        """

        if self._protocollo_service is None:
            from ..services.protocollo_service import ProtocolloService

            self._protocollo_service = ProtocolloService(
                protocollo_repository=self._get_protocollo_repository(),
                documento_repository=self._get_documento_repository(),
                metadata_repository=self._get_metadata_repository(),
            )

        return self._protocollo_service

    def get_documento_service(self) -> Any:
        """Restituisce `DocumentoService` con repository opzionali collegati."""

        if self._documento_service is None:
            from ..services.documento_service import DocumentoService

            self._documento_service = DocumentoService(
                documento_repository=self._get_documento_repository(),
                metadata_repository=self._get_metadata_repository(),
            )

        return self._documento_service

    def get_metadata_service(self) -> Any:
        """Restituisce `MetadataService` con repository opzionale collegato."""

        if self._metadata_service is None:
            from ..services.metadata_service import MetadataService

            self._metadata_service = MetadataService(
                metadata_repository=self._get_metadata_repository(),
            )

        return self._metadata_service

    def get_procedimento_service(self) -> Any:
        """Restituisce `ProcedimentoService` con repository read-only collegato."""

        if self._procedimento_service is None:
            from ..services.procedimento_service import ProcedimentoService

            self._procedimento_service = ProcedimentoService(
                procedimento_repository=self._get_procedimento_repository(),
            )

        return self._procedimento_service


def create_container() -> DependencyContainer:
    """Crea un nuovo container applicativo.

    La factory mantiene esplicito il ciclo di vita del container senza
    introdurre singleton globali. Le route FastAPI possono dipendere da questa
    funzione e, in futuro, sostituirla con una gestione request-scoped piu
    ricca senza cambiare gli endpoint.
    """

    return DependencyContainer()
