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
        self._workflow_procedimento_repository: Any | None = None
        self._sottofase_documentale_repository: Any | None = None
        self._sottofase_workflow_action_repository: Any | None = None
        self._sottofase_document_upload_repository: Any | None = None
        self._sottofase_partecipanti_repository: Any | None = None

        self._protocollo_service: Any | None = None
        self._documento_service: Any | None = None
        self._metadata_service: Any | None = None
        self._procedimento_service: Any | None = None
        self._workflow_procedimento_service: Any | None = None
        self._sottofase_documentale_service: Any | None = None
        self._sottofase_workflow_service: Any | None = None
        self._sottofase_workflow_command_service: Any | None = None
        self._sottofase_document_upload_service: Any | None = None
        self._sottofase_partecipanti_service: Any | None = None

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

    def _get_workflow_procedimento_repository(self) -> Any:
        """Restituisce il repository workflow procedimento, creandolo lazy."""

        if self._workflow_procedimento_repository is None:
            from ..repositories.workflow_procedimento_repository import (
                WorkflowProcedimentoRepository,
            )

            self._workflow_procedimento_repository = WorkflowProcedimentoRepository()

        return self._workflow_procedimento_repository

    def _get_sottofase_documentale_repository(self) -> Any:
        """Restituisce il repository documentale sottofase, creandolo lazy."""

        if self._sottofase_documentale_repository is None:
            from ..repositories.sottofase_documentale_repository import (
                SottofaseDocumentaleRepository,
            )

            self._sottofase_documentale_repository = (
                SottofaseDocumentaleRepository()
            )

        return self._sottofase_documentale_repository

    def _get_sottofase_workflow_action_repository(self) -> Any:
        """Restituisce il repository di scrittura workflow sottofase."""

        if self._sottofase_workflow_action_repository is None:
            from ..repositories.sottofase_workflow_action_repository import (
                SottofaseWorkflowActionRepository,
            )

            self._sottofase_workflow_action_repository = (
                SottofaseWorkflowActionRepository()
            )

        return self._sottofase_workflow_action_repository

    def _get_sottofase_document_upload_repository(self) -> Any:
        """Restituisce il repository di scrittura documenti sottofase."""

        if self._sottofase_document_upload_repository is None:
            from ..repositories.sottofase_document_upload_repository import (
                SottofaseDocumentUploadRepository,
            )

            self._sottofase_document_upload_repository = (
                SottofaseDocumentUploadRepository()
            )

        return self._sottofase_document_upload_repository

    def _get_sottofase_partecipanti_repository(self) -> Any:
        """Restituisce il repository partecipanti sottofase."""

        if self._sottofase_partecipanti_repository is None:
            from ..repositories.sottofase_partecipanti_repository import (
                SottofasePartecipantiRepository,
            )

            self._sottofase_partecipanti_repository = (
                SottofasePartecipantiRepository()
            )

        return self._sottofase_partecipanti_repository

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

    def get_workflow_procedimento_service(self) -> Any:
        """Restituisce `WorkflowProcedimentoService` read-only collegato."""

        if self._workflow_procedimento_service is None:
            from ..services.workflow_procedimento_service import (
                WorkflowProcedimentoService,
            )

            self._workflow_procedimento_service = WorkflowProcedimentoService(
                workflow_procedimento_repository=(
                    self._get_workflow_procedimento_repository()
                ),
            )

        return self._workflow_procedimento_service

    def get_sottofase_documentale_service(self) -> Any:
        """Restituisce `SottofaseDocumentaleService` read-only collegato."""

        if self._sottofase_documentale_service is None:
            from ..services.sottofase_documentale_service import (
                SottofaseDocumentaleService,
            )

            self._sottofase_documentale_service = SottofaseDocumentaleService(
                sottofase_documentale_repository=(
                    self._get_sottofase_documentale_repository()
                ),
            )

        return self._sottofase_documentale_service

    def get_sottofase_workflow_service(self) -> Any:
        """Restituisce `SottofaseWorkflowService` read-only collegato."""

        if self._sottofase_workflow_service is None:
            from ..services.sottofase_workflow_service import (
                SottofaseWorkflowService,
            )

            self._sottofase_workflow_service = SottofaseWorkflowService(
                sottofase_documentale_service=(
                    self.get_sottofase_documentale_service()
                ),
            )

        return self._sottofase_workflow_service

    def get_sottofase_workflow_command_service(self) -> Any:
        """Restituisce il service di comando workflow sottofase."""

        if self._sottofase_workflow_command_service is None:
            from ..services.sottofase_workflow_command_service import (
                SottofaseWorkflowCommandService,
            )

            self._sottofase_workflow_command_service = (
                SottofaseWorkflowCommandService(
                    workflow_service=self.get_sottofase_workflow_service(),
                    workflow_action_repository=(
                        self._get_sottofase_workflow_action_repository()
                    ),
                )
            )

        return self._sottofase_workflow_command_service

    def get_sottofase_document_upload_service(self) -> Any:
        """Restituisce il service per upload documenti Word sottofase."""

        if self._sottofase_document_upload_service is None:
            from ..services.sottofase_document_upload_service import (
                SottofaseDocumentUploadService,
            )

            self._sottofase_document_upload_service = (
                SottofaseDocumentUploadService(
                    sottofase_documentale_service=(
                        self.get_sottofase_documentale_service()
                    ),
                    workflow_service=self.get_sottofase_workflow_service(),
                    document_upload_repository=(
                        self._get_sottofase_document_upload_repository()
                    ),
                )
            )

        return self._sottofase_document_upload_service

    def get_sottofase_partecipanti_service(self) -> Any:
        """Restituisce il service per partecipanti sottofase."""

        if self._sottofase_partecipanti_service is None:
            from ..services.sottofase_partecipanti_service import (
                SottofasePartecipantiService,
            )

            self._sottofase_partecipanti_service = SottofasePartecipantiService(
                partecipanti_repository=(
                    self._get_sottofase_partecipanti_repository()
                ),
                sottofase_documentale_service=self.get_sottofase_documentale_service(),
            )

        return self._sottofase_partecipanti_service


def create_container() -> DependencyContainer:
    """Crea un nuovo container applicativo.

    La factory mantiene esplicito il ciclo di vita del container senza
    introdurre singleton globali. Le route FastAPI possono dipendere da questa
    funzione e, in futuro, sostituirla con una gestione request-scoped piu
    ricca senza cambiare gli endpoint.
    """

    return DependencyContainer()
