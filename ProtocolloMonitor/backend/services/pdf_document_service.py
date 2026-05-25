"""Service applicativo preparatorio per il salvataggio PDF protocollo.

Il service coordina il salvataggio fisico dei PDF tramite
`DocumentStorageService`, ma non aggiorna il database e non viene ancora
collegato al flusso Grisu/Flask. Resta quindi un punto di integrazione pronto
per lo step successivo, senza cambiare il comportamento attuale.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from backend.core.logging import get_logger, log_error, log_event
from backend.services.document_storage_service import DocumentStorageService


class PdfDocumentService:
    """Coordina il salvataggio fisico PDF senza accedere al database.

    La classe riceve un `DocumentStorageService` opzionale per permettere ai
    test di usare `tmp_path` e per lasciare configurabile il FileServer reale.
    Questo mantiene separata la responsabilita di storage dalla futura
    responsabilita di aggiornare `T_Protocolli.PercorsoDocumentoProtocollato`.
    """

    def __init__(
        self,
        *,
        storage_service: DocumentStorageService | None = None,
        document_storage_service: DocumentStorageService | None = None,
        documento_repository: Any | None = None,
    ) -> None:
        selected_storage_service = storage_service or document_storage_service
        self.document_storage_service = (
            selected_storage_service or DocumentStorageService()
        )
        self.documento_repository = documento_repository
        self.logger = get_logger()

    def save_protocollo_pdf(
        self,
        pdf_bytes: bytes,
        modalita: Any,
        comando: Any,
        numero_protocollo: Any,
        data_protocollo: Any,
    ) -> Path:
        """Salva il PDF con `DocumentStorageService` e restituisce il path.

        Cosa fa:
        delega a `DocumentStorageService.save_pdf()` la creazione cartella, la
        generazione del nome standard e la scrittura fisica del file.

        Perche esiste:
        prepara un punto applicativo unico da collegare, in uno step futuro, al
        flusso di acquisizione PDF senza mettere logica di filesystem dentro
        endpoint, repository o codice legacy.

        Parametri:
        - `pdf_bytes`: contenuto binario del PDF;
        - `modalita`: valore protocollo usato per produrre E/U/X;
        - `comando`: comando mittente/destinatario da includere nel nome file;
        - `numero_protocollo`: numero protocollo da includere nel nome file;
        - `data_protocollo`: data usata per cartella `YYYY/MM` e suffisso data.

        Valori restituiti:
        path del file salvato, come `Path`.

        Rischi evitati:
        - nessun aggiornamento Access prematuro;
        - nessuna query diretta;
        - nessuna dipendenza da Flask o dal flusso Grisu;
        - nessun accesso al FileServer reale nei test se viene iniettato un
          `DocumentStorageService` configurato con `tmp_path`.
        """

        return self.document_storage_service.save_pdf(
            pdf_bytes,
            modalita,
            comando,
            numero_protocollo,
            data_protocollo,
        )

    def save_and_register_protocollo_pdf(
        self,
        id_protocollo: int,
        pdf_bytes: bytes,
        modalita: Any,
        comando: Any,
        numero_protocollo: Any,
        data_protocollo: Any,
    ) -> dict[str, Any]:
        """Salva il PDF e registra il path su `T_Protocolli`.

        Cosa fa:
        prima delega a `DocumentStorageService.save_pdf()` la scrittura fisica,
        poi delega a `DocumentoRepository.update_protocollo_pdf_path()` la
        registrazione del path nel campo Access gia esistente.

        Perche esiste:
        questo metodo e il primo collegamento completo lato backend tra storage
        fisico e database, ma resta isolato dal runtime Flask/Grisu e dagli
        endpoint pubblici. Lo step successivo potra chiamarlo dal flusso reale
        senza spostare logica filesystem dentro `server_protocollo.py`.

        Parametri:
        - `id_protocollo`: ID Access del protocollo da aggiornare;
        - `pdf_bytes`: contenuto binario del PDF;
        - `modalita`: valore usato per il prefisso E/U/X;
        - `comando`: comando da usare nel filename standard;
        - `numero_protocollo`: numero protocollo da usare nel filename;
        - `data_protocollo`: data usata per cartella e filename.

        Valori restituiti:
        dizionario applicativo con esito salvataggio, esito registrazione,
        identificativo protocollo, path e nome file. Se il DB non aggiorna
        alcun record, il PDF resta salvato e `registered` vale `False`.

        Rischi evitati:
        - nessun accesso diretto ad Access dal Service;
        - nessun download HTTP;
        - nessun parsing HTML;
        - nessun aggiornamento di campi diversi da
          `PercorsoDocumentoProtocollato`;
        - nessuna dipendenza dal runtime Flask o dall'estensione Grisu.
        """

        saved_path = self.save_protocollo_pdf(
            pdf_bytes,
            modalita,
            comando,
            numero_protocollo,
            data_protocollo,
        )
        path_for_database = str(saved_path)

        log_event(
            logger=self.logger,
            module="PROTOCOLLO_MONITOR",
            operation="pdf_document_save",
            entity_type="protocollo",
            entity_id=id_protocollo,
            status="ok",
            message="PDF salvato tramite PdfDocumentService.",
            file_path=path_for_database,
        )

        update_method = self._get_update_protocollo_pdf_path_method()

        if update_method is None:
            log_event(
                logger=self.logger,
                level="WARNING",
                module="PROTOCOLLO_MONITOR",
                operation="pdf_document_register",
                entity_type="protocollo",
                entity_id=id_protocollo,
                status="failed",
                message="Repository documento non disponibile per registrare il PDF.",
                file_path=path_for_database,
            )

            return self._build_result(
                saved=True,
                registered=False,
                id_protocollo=id_protocollo,
                saved_path=saved_path,
                error="DocumentoRepository non disponibile.",
            )

        try:
            registered = bool(
                update_method(
                    id_protocollo,
                    path_for_database,
                )
            )
        except Exception as error:
            log_error(
                logger=self.logger,
                module="PROTOCOLLO_MONITOR",
                operation="pdf_document_register",
                entity_type="protocollo",
                entity_id=id_protocollo,
                message="Errore durante la registrazione del path PDF.",
                error=error,
                file_path=path_for_database,
            )

            return self._build_result(
                saved=True,
                registered=False,
                id_protocollo=id_protocollo,
                saved_path=saved_path,
                error=str(error),
            )

        if not registered:
            log_event(
                logger=self.logger,
                level="WARNING",
                module="PROTOCOLLO_MONITOR",
                operation="pdf_document_register",
                entity_type="protocollo",
                entity_id=id_protocollo,
                status="not_found",
                message="Nessun protocollo aggiornato con il path PDF.",
                file_path=path_for_database,
            )

            return self._build_result(
                saved=True,
                registered=False,
                id_protocollo=id_protocollo,
                saved_path=saved_path,
                error="Protocollo non aggiornato.",
            )

        log_event(
            logger=self.logger,
            module="PROTOCOLLO_MONITOR",
            operation="pdf_document_register",
            entity_type="protocollo",
            entity_id=id_protocollo,
            status="ok",
            message="Path PDF registrato su T_Protocolli.",
            file_path=path_for_database,
        )

        return self._build_result(
            saved=True,
            registered=True,
            id_protocollo=id_protocollo,
            saved_path=saved_path,
        )

    def _get_update_protocollo_pdf_path_method(self) -> Any | None:
        """Restituisce il metodo repository dedicato alla registrazione path.

        Il repository puo essere iniettato nei test. Quando manca e il metodo
        completo di registrazione viene usato davvero, viene creato il
        `DocumentoRepository` Access-compatible senza aprire connessioni fino
        alla chiamata del metodo repository.
        """

        if self.documento_repository is None:
            from backend.repositories.documento_repository import DocumentoRepository

            self.documento_repository = DocumentoRepository()

        update_method = getattr(
            self.documento_repository,
            "update_protocollo_pdf_path",
            None,
        )

        if update_method is None:
            return None

        return update_method

    @staticmethod
    def _build_result(
        *,
        saved: bool,
        registered: bool,
        id_protocollo: int,
        saved_path: Path,
        error: str | None = None,
    ) -> dict[str, Any]:
        """Costruisce la risposta applicativa stabile del service.

        Tenere questa struttura in un solo punto rende piu semplice testare il
        metodo e mantenere invariato il contratto quando il flusso reale verra
        collegato a Flask o a FastAPI.
        """

        result: dict[str, Any] = {
            "saved": saved,
            "registered": registered,
            "id_protocollo": id_protocollo,
            "path": str(saved_path),
            "filename": saved_path.name,
        }

        if error is not None:
            result["error"] = error

        return result
