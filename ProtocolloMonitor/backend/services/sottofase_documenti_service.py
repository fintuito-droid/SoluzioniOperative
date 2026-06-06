"""Service per documenti principali e allegati della sottofase."""

from __future__ import annotations

import hashlib
import mimetypes
import re
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from backend.core.access_backup import create_access_backup


MAX_ALLEGATO_FILE_SIZE_BYTES = 25 * 1024 * 1024
ALLOWED_ALLEGATO_EXTENSIONS = {
    ".pdf",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
    ".ppt",
    ".pptx",
    ".jpg",
    ".jpeg",
    ".png",
    ".txt",
}


class SottofaseDocumentiValidationError(ValueError):
    """Errore di validazione del modello documentale sottofase."""


class SottofaseDocumentoPrincipaleGiaEsistenteError(SottofaseDocumentiValidationError):
    """La sottofase possiede gia un documento principale attivo."""


class SottofaseDocumentoPrincipaleNotFoundError(LookupError):
    """Documento principale attivo non presente per la sottofase."""


class SottofaseProtocolloAllegatoGiaEsistenteError(SottofaseDocumentiValidationError):
    """Protocollo gia collegato come allegato alla sottofase."""


class SottofaseProtocolloAllegatoNotFoundError(LookupError):
    """Protocollo da collegare come allegato non trovato."""


class SottofaseAllegatoFileTooLargeError(SottofaseDocumentiValidationError):
    """File allegato superiore al limite ammesso."""


class SottofaseAllegatoFileWriteError(RuntimeError):
    """Errore durante salvataggio file o registrazione allegato."""


class SottofaseAllegatoNotFoundError(LookupError):
    """Allegato non trovato o non appartenente alla sottofase."""


class SottofaseAllegatoEliminazioneError(SottofaseDocumentiValidationError):
    """Allegato non eliminabile logicamente."""


class SottofaseAllegatoRipristinoError(SottofaseDocumentiValidationError):
    """Allegato non ripristinabile."""


class SottofaseDocumentiService:
    """Regole applicative del modello documentale unificato."""

    RUOLI_AMMESSI = {"PRINCIPALE", "ALLEGATO"}
    TIPI_ORIGINE_AMMESSI = {"PROTOCOLLO", "FILE", "GENERATO"}
    STATI_DOCUMENTO_AMMESSI = {
        "BOZZA",
        "IN_REVISIONE",
        "APPROVATO",
        "FIRMATO",
        "PROTOCOLLATO",
        "ARCHIVIATO",
    }
    TIPI_DOCUMENTO_AMMESSI = {
        "NOTA",
        "RELAZIONE",
        "VERBALE",
        "RICHIESTA",
        "PARERE",
        "ALTRO",
    }

    def __init__(
        self,
        *,
        sottofase_documenti_repository: Any | None = None,
        backup_factory: Any = create_access_backup,
        storage_root: Path | str | None = None,
        now_factory: Any = datetime.now,
    ) -> None:
        self.sottofase_documenti_repository = sottofase_documenti_repository
        self.backup_factory = backup_factory
        self.storage_root = Path(storage_root) if storage_root else self._default_storage_root()
        self.now_factory = now_factory

    def get_documenti_sottofase(self, id_sottofase: int) -> list[dict[str, Any]]:
        if self.sottofase_documenti_repository is None:
            return []

        get_documenti = getattr(
            self.sottofase_documenti_repository,
            "get_documenti_sottofase",
            None,
        )
        if get_documenti is None:
            return []

        return get_documenti(self._validate_id(id_sottofase, "IDSottofase"))

    def get_documento_principale(
        self,
        id_sottofase: int,
    ) -> dict[str, Any] | None:
        if self.sottofase_documenti_repository is None:
            return None

        get_principale = getattr(
            self.sottofase_documenti_repository,
            "get_documento_principale",
            None,
        )
        if get_principale is None:
            return None

        return get_principale(self._validate_id(id_sottofase, "IDSottofase"))

    def exists_documento_principale(self, id_sottofase: int) -> bool:
        if self.sottofase_documenti_repository is None:
            return False

        exists = getattr(
            self.sottofase_documenti_repository,
            "exists_documento_principale",
            None,
        ) or getattr(
            self.sottofase_documenti_repository,
            "exists_documento_principale_attivo",
            None,
        )
        if exists is None:
            return False

        return bool(exists(self._validate_id(id_sottofase, "IDSottofase")))

    def create_documento_principale(
        self,
        id_sottofase: int,
    ) -> dict[str, Any]:
        if self.sottofase_documenti_repository is None:
            raise SottofaseDocumentiValidationError(
                "Repository documenti sottofase non configurato."
            )

        id_sottofase_normalizzato = self._validate_id(id_sottofase, "IDSottofase")
        if self.exists_documento_principale(id_sottofase_normalizzato):
            raise SottofaseDocumentoPrincipaleGiaEsistenteError(
                "Esiste gia un documento PRINCIPALE attivo per la sottofase."
            )

        now = datetime.now()
        self.backup_factory()

        create_principale = getattr(
            self.sottofase_documenti_repository,
            "create_documento_principale",
            None,
        )
        if create_principale is not None:
            return create_principale(
                id_sottofase=id_sottofase_normalizzato,
                data_creazione=now,
            )

        return self.sottofase_documenti_repository.create_documento(
            {
                "IDSottofase": id_sottofase_normalizzato,
                "RuoloDocumento": "PRINCIPALE",
                "TipoOrigine": "GENERATO",
                "TitoloDocumento": "Nuovo Documento",
                "StatoDocumento": "BOZZA",
                "VersioneDocumento": 1,
                "Attivo": True,
                "DataCreazione": now,
                "DataModifica": now,
                "DataCollegamento": now,
            }
        )

    def update_documento_principale_metadati(
        self,
        id_sottofase: int,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        if self.sottofase_documenti_repository is None:
            raise SottofaseDocumentiValidationError(
                "Repository documenti sottofase non configurato."
            )

        id_sottofase_normalizzato = self._validate_id(id_sottofase, "IDSottofase")
        dati = self._normalizza_payload_metadati(payload)
        self._valida_metadati_documento_principale(dati)

        self.backup_factory()
        update_metadati = getattr(
            self.sottofase_documenti_repository,
            "update_documento_principale_metadati",
            None,
        )
        if update_metadati is None:
            raise SottofaseDocumentiValidationError(
                "Aggiornamento metadati non disponibile."
            )

        updated = update_metadati(
            id_sottofase=id_sottofase_normalizzato,
            titolo_documento=dati["TitoloDocumento"],
            descrizione_documento=dati.get("DescrizioneDocumento"),
            stato_documento=dati["StatoDocumento"],
            tipo_documento=dati["TipoDocumento"],
            data_modifica=datetime.now(),
        )

        if updated is None:
            raise SottofaseDocumentoPrincipaleNotFoundError(
                "Documento principale non trovato."
            )

        return updated

    def get_allegati(self, id_sottofase: int) -> list[dict[str, Any]]:
        if self.sottofase_documenti_repository is None:
            return []

        get_allegati = getattr(
            self.sottofase_documenti_repository,
            "get_allegati_sottofase",
            None,
        ) or getattr(
            self.sottofase_documenti_repository,
            "get_allegati",
            None,
        )
        if get_allegati is None:
            return []

        return get_allegati(self._validate_id(id_sottofase, "IDSottofase"))

    def get_allegati_eliminati(self, id_sottofase: int) -> dict[str, Any]:
        if self.sottofase_documenti_repository is None:
            return {"items": []}

        get_eliminati = getattr(
            self.sottofase_documenti_repository,
            "get_allegati_eliminati",
            None,
        )
        if get_eliminati is None:
            return {"items": []}

        items = get_eliminati(self._validate_id(id_sottofase, "IDSottofase"))
        return {"items": items}

    def exists_protocollo_allegato(
        self,
        *,
        id_sottofase: int,
        id_protocollo: int,
    ) -> bool:
        if self.sottofase_documenti_repository is None:
            return False

        exists = getattr(
            self.sottofase_documenti_repository,
            "exists_protocollo_allegato",
            None,
        )
        if exists is None:
            return False

        return bool(
            exists(
                id_sottofase=self._validate_id(id_sottofase, "IDSottofase"),
                id_protocollo=self._validate_id(id_protocollo, "IDProtocollo"),
            )
        )

    def add_protocollo_come_allegato(
        self,
        id_sottofase: int,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        if self.sottofase_documenti_repository is None:
            raise SottofaseDocumentiValidationError(
                "Repository documenti sottofase non configurato."
            )

        id_sottofase_normalizzato = self._validate_id(id_sottofase, "IDSottofase")
        id_protocollo = self._validate_id(
            self._pick(payload, "idProtocollo", "IDProtocollo", "id_protocollo"),
            "IDProtocollo",
        )

        if self.exists_protocollo_allegato(
            id_sottofase=id_sottofase_normalizzato,
            id_protocollo=id_protocollo,
        ):
            raise SottofaseProtocolloAllegatoGiaEsistenteError(
                "Protocollo gia collegato alla sottofase."
            )

        get_protocollo = getattr(
            self.sottofase_documenti_repository,
            "get_protocollo_per_allegato",
            None,
        )
        if get_protocollo is None:
            raise SottofaseDocumentiValidationError(
                "Lettura protocollo non disponibile."
            )

        protocollo = get_protocollo(id_protocollo)
        if protocollo is None:
            raise SottofaseProtocolloAllegatoNotFoundError(
                "Protocollo non trovato."
            )

        add_protocollo = getattr(
            self.sottofase_documenti_repository,
            "add_protocollo_come_allegato",
            None,
        )
        if add_protocollo is None:
            raise SottofaseDocumentiValidationError(
                "Collegamento allegato protocollo non disponibile."
            )

        self.backup_factory()
        return add_protocollo(
            id_sottofase=id_sottofase_normalizzato,
            id_protocollo=id_protocollo,
            protocollo=protocollo,
            data_creazione=self.now_factory(),
        )

    def upload_file_allegato(
        self,
        *,
        id_sottofase: int,
        file_bytes: bytes,
        original_filename: str,
        content_type: str | None = None,
    ) -> dict[str, Any]:
        if self.sottofase_documenti_repository is None:
            raise SottofaseDocumentiValidationError(
                "Repository documenti sottofase non configurato."
            )

        id_sottofase_normalizzato = self._validate_id(id_sottofase, "IDSottofase")
        filename_originale = self._validate_allegato_file(
            file_bytes=file_bytes,
            original_filename=original_filename,
        )
        estensione = Path(filename_originale).suffix.lower()
        safe_filename = self._safe_filename(filename_originale)
        saved_filename = f"{uuid4().hex}_{safe_filename}"
        target_dir = (
            self.storage_root
            / "sottofasi"
            / str(id_sottofase_normalizzato)
            / "allegati"
        )
        target_path = (target_dir / saved_filename).resolve()
        storage_root = self.storage_root.resolve()

        if not self._is_relative_to(target_path, storage_root):
            raise SottofaseDocumentiValidationError("Percorso allegato non valido.")

        now = self.now_factory()
        mime_type = content_type or mimetypes.guess_type(filename_originale)[0]
        if not mime_type:
            mime_type = "application/octet-stream"
        hash_file = hashlib.sha256(file_bytes).hexdigest()
        titolo_documento = Path(filename_originale).stem
        saved_path: Path | None = None

        try:
            target_dir.mkdir(parents=True, exist_ok=True)
            target_path.write_bytes(file_bytes)
            saved_path = target_path
            self.backup_factory()

            create_allegato = getattr(
                self.sottofase_documenti_repository,
                "create_allegato_file",
                None,
            )
            if create_allegato is None:
                raise SottofaseDocumentiValidationError(
                    "Creazione allegato file non disponibile."
                )

            return create_allegato(
                {
                    "IDSottofase": id_sottofase_normalizzato,
                    "TitoloDocumento": titolo_documento,
                    "NomeFile": filename_originale,
                    "Estensione": estensione,
                    "PercorsoDocumento": str(target_path),
                    "MimeType": mime_type,
                    "DimensioneBytes": len(file_bytes),
                    "HashFile": hash_file,
                    "VersioneDocumento": 1,
                    "StatoDocumento": "CARICATO",
                    "TipoDocumento": estensione.lstrip(".").upper(),
                    "Ordine": self._next_ordine_allegato(id_sottofase_normalizzato),
                    "DataCollegamento": now,
                    "DataCreazione": now,
                    "DataModifica": now,
                }
            )
        except (
            SottofaseDocumentiValidationError,
            SottofaseAllegatoFileTooLargeError,
        ):
            self._remove_saved_file(saved_path)
            raise
        except Exception as exc:
            self._remove_saved_file(saved_path)
            raise SottofaseAllegatoFileWriteError(
                f"Upload allegato non riuscito: {exc}"
            )

    def create_documento(self, payload: dict[str, Any]) -> dict[str, Any]:
        if self.sottofase_documenti_repository is None:
            raise SottofaseDocumentiValidationError(
                "Repository documenti sottofase non configurato."
            )

        dati = self._normalizza_payload_creazione(payload)
        self._valida_documento(dati)

        if (
            dati["RuoloDocumento"] == "PRINCIPALE"
            and dati.get("Attivo", True)
            and self.sottofase_documenti_repository.exists_documento_principale_attivo(
                dati["IDSottofase"]
            )
        ):
            raise SottofaseDocumentoPrincipaleGiaEsistenteError(
                "Esiste gia un documento PRINCIPALE attivo per la sottofase."
            )

        self.backup_factory()
        return self.sottofase_documenti_repository.create_documento(dati)

    def update_documento(
        self,
        id_documento_sottofase: int,
        payload: dict[str, Any],
    ) -> dict[str, Any] | None:
        if self.sottofase_documenti_repository is None:
            raise SottofaseDocumentiValidationError(
                "Repository documenti sottofase non configurato."
            )

        id_documento = self._validate_id(
            id_documento_sottofase,
            "IDDocumentoSottofase",
        )
        dati = self._normalizza_payload_update(payload)
        self._valida_documento(dati, parziale=True)

        if dati.get("RuoloDocumento") == "PRINCIPALE" and dati.get("Attivo", True):
            documento_corrente = self.sottofase_documenti_repository.get_documento_by_id(
                id_documento
            )
            if documento_corrente is None and "IDSottofase" not in dati:
                raise SottofaseDocumentiValidationError("Documento non trovato.")

            id_sottofase = dati.get("IDSottofase") or documento_corrente.get(
                "id_sottofase"
            )

            if self.sottofase_documenti_repository.exists_documento_principale_attivo(
                id_sottofase,
                exclude_id_documento=id_documento,
            ):
                raise SottofaseDocumentoPrincipaleGiaEsistenteError(
                    "Esiste gia un documento PRINCIPALE attivo per la sottofase."
                )

        self.backup_factory()
        return self.sottofase_documenti_repository.update_documento(id_documento, dati)

    def disattiva_documento(
        self,
        id_documento_sottofase: int,
    ) -> dict[str, Any] | None:
        if self.sottofase_documenti_repository is None:
            raise SottofaseDocumentiValidationError(
                "Repository documenti sottofase non configurato."
            )

        id_documento = self._validate_id(
            id_documento_sottofase,
            "IDDocumentoSottofase",
        )
        self.backup_factory()
        return self.sottofase_documenti_repository.disattiva_documento(id_documento)

    def elimina_logicamente_allegato(
        self,
        *,
        id_sottofase: int,
        id_documento: int,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Elimina logicamente un allegato senza cancellare record o file."""

        if self.sottofase_documenti_repository is None:
            raise SottofaseDocumentiValidationError(
                "Repository documenti sottofase non configurato."
            )

        elimina_allegato = getattr(
            self.sottofase_documenti_repository,
            "elimina_logicamente_allegato",
            None,
        )
        if elimina_allegato is None:
            raise SottofaseDocumentiValidationError(
                "Eliminazione logica allegato non disponibile."
            )

        id_sottofase_normalizzato = self._validate_id(id_sottofase, "IDSottofase")
        id_documento_normalizzato = self._validate_id(
            id_documento,
            "IDDocumentoSottofase",
        )
        dati = payload or {}
        motivo = self._text_or_none(
            self._pick(
                dati,
                "motivoEliminazione",
                "MotivoEliminazione",
                "motivo_eliminazione",
            )
        ) or "Eliminazione logica allegato"
        utente = self._text_or_none(
            self._pick(
                dati,
                "utenteEliminazione",
                "UtenteEliminazione",
                "utente_eliminazione",
            )
        ) or "operatore"

        self.backup_factory()
        result = elimina_allegato(
            id_sottofase_normalizzato,
            id_documento_normalizzato,
            motivo,
            utente,
            data_eliminazione=self.now_factory(),
        )

        if result.get("success"):
            return {
                "success": True,
                "message": "Allegato eliminato logicamente",
                "idDocumento": id_documento_normalizzato,
                "documento": result.get("documento"),
            }

        reason = result.get("reason")
        message = result.get("message") or "Allegato non eliminabile."

        if reason == "not_found":
            raise SottofaseAllegatoNotFoundError(message)

        if reason == "not_allegato":
            raise SottofaseAllegatoEliminazioneError(
                "Il documento indicato non e un allegato."
            )

        if reason == "already_deleted":
            raise SottofaseAllegatoEliminazioneError("Allegato gia eliminato.")

        raise SottofaseAllegatoEliminazioneError(message)

    def ripristina_allegato(
        self,
        *,
        id_sottofase: int,
        id_documento: int,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Ripristina un allegato eliminato logicamente."""

        if self.sottofase_documenti_repository is None:
            raise SottofaseDocumentiValidationError(
                "Repository documenti sottofase non configurato."
            )

        ripristina = getattr(
            self.sottofase_documenti_repository,
            "ripristina_allegato",
            None,
        )
        if ripristina is None:
            raise SottofaseDocumentiValidationError(
                "Ripristino allegato non disponibile."
            )

        id_sottofase_normalizzato = self._validate_id(id_sottofase, "IDSottofase")
        id_documento_normalizzato = self._validate_id(
            id_documento,
            "IDDocumentoSottofase",
        )
        dati = payload or {}
        utente = self._text_or_none(
            self._pick(
                dati,
                "utenteRipristino",
                "UtenteRipristino",
                "utente_ripristino",
            )
        ) or "operatore"

        self.backup_factory()
        result = ripristina(
            id_sottofase_normalizzato,
            id_documento_normalizzato,
            utente,
            data_ripristino=self.now_factory(),
        )

        if result.get("success"):
            return {
                "success": True,
                "message": "Allegato ripristinato",
                "idDocumento": id_documento_normalizzato,
                "documento": result.get("documento"),
            }

        reason = result.get("reason")
        message = result.get("message") or "Allegato non ripristinabile."

        if reason == "not_found":
            raise SottofaseAllegatoNotFoundError(message)

        if reason == "not_allegato":
            raise SottofaseAllegatoRipristinoError(
                "Il documento indicato non e un allegato."
            )

        if reason == "not_deleted":
            raise SottofaseAllegatoRipristinoError("Allegato non eliminato.")

        raise SottofaseAllegatoRipristinoError(message)

    def _normalizza_payload_creazione(self, payload: dict[str, Any]) -> dict[str, Any]:
        now = datetime.now()
        id_sottofase = self._validate_id(
            self._pick(payload, "IDSottofase", "id_sottofase", "idSottofase"),
            "IDSottofase",
        )

        dati = {
            "IDSottofase": id_sottofase,
            "RuoloDocumento": self._upper(
                self._pick(payload, "RuoloDocumento", "ruolo_documento"),
                default="ALLEGATO",
            ),
            "TipoOrigine": self._upper(
                self._pick(payload, "TipoOrigine", "tipo_origine"),
                default="FILE",
            ),
            "TitoloDocumento": self._text_or_none(
                self._pick(payload, "TitoloDocumento", "titolo_documento")
            ),
            "DescrizioneDocumento": self._text_or_none(
                self._pick(payload, "DescrizioneDocumento", "descrizione_documento")
            ),
            "TipoDocumento": self._text_or_none(
                self._pick(payload, "TipoDocumento", "tipo_documento")
            ),
            "NomeFile": self._text_or_none(self._pick(payload, "NomeFile", "nome_file")),
            "Estensione": self._text_or_none(
                self._pick(payload, "Estensione", "estensione")
            ),
            "PercorsoDocumento": self._text_or_none(
                self._pick(payload, "PercorsoDocumento", "percorso_documento")
            ),
            "IDProtocolloCollegato": self._pick(
                payload,
                "IDProtocolloCollegato",
                "id_protocollo_collegato",
            ),
            "MimeType": self._text_or_none(self._pick(payload, "MimeType", "mime_type")),
            "DimensioneBytes": self._pick(
                payload,
                "DimensioneBytes",
                "dimensione_bytes",
            ),
            "HashFile": self._text_or_none(self._pick(payload, "HashFile", "hash_file")),
            "VersioneDocumento": self._pick(
                payload,
                "VersioneDocumento",
                "versione_documento",
            )
            or 1,
            "StatoDocumento": self._upper(
                self._pick(payload, "StatoDocumento", "stato_documento"),
                default="ATTIVO",
            ),
            "Ordine": self._pick(payload, "Ordine", "ordine"),
            "DataCollegamento": self._pick(payload, "DataCollegamento")
            or self._pick(payload, "data_collegamento")
            or now,
            "UtenteCollegamento": self._text_or_none(
                self._pick(payload, "UtenteCollegamento", "utente_collegamento")
            ),
            "Attivo": bool(self._pick(payload, "Attivo", "attivo", default=True)),
            "DataCreazione": self._pick(payload, "DataCreazione") or now,
            "DataModifica": self._pick(payload, "DataModifica") or now,
        }

        if not dati["TitoloDocumento"]:
            dati["TitoloDocumento"] = dati["NomeFile"]

        return dati

    def _normalizza_payload_update(self, payload: dict[str, Any]) -> dict[str, Any]:
        field_map = {
            "IDSottofase": ("IDSottofase", "id_sottofase", "idSottofase"),
            "RuoloDocumento": ("RuoloDocumento", "ruolo_documento"),
            "TipoOrigine": ("TipoOrigine", "tipo_origine"),
            "TitoloDocumento": ("TitoloDocumento", "titolo_documento"),
            "DescrizioneDocumento": (
                "DescrizioneDocumento",
                "descrizione_documento",
            ),
            "TipoDocumento": ("TipoDocumento", "tipo_documento"),
            "NomeFile": ("NomeFile", "nome_file"),
            "Estensione": ("Estensione", "estensione"),
            "PercorsoDocumento": ("PercorsoDocumento", "percorso_documento"),
            "IDProtocolloCollegato": (
                "IDProtocolloCollegato",
                "id_protocollo_collegato",
            ),
            "MimeType": ("MimeType", "mime_type"),
            "DimensioneBytes": ("DimensioneBytes", "dimensione_bytes"),
            "HashFile": ("HashFile", "hash_file"),
            "VersioneDocumento": ("VersioneDocumento", "versione_documento"),
            "StatoDocumento": ("StatoDocumento", "stato_documento"),
            "Ordine": ("Ordine", "ordine"),
            "DataCollegamento": ("DataCollegamento", "data_collegamento"),
            "UtenteCollegamento": ("UtenteCollegamento", "utente_collegamento"),
            "Attivo": ("Attivo", "attivo"),
            "DataModifica": ("DataModifica", "data_modifica"),
        }
        dati: dict[str, Any] = {}

        for target, aliases in field_map.items():
            value = self._pick(payload, *aliases)
            if value is None and not any(alias in payload for alias in aliases):
                continue
            dati[target] = value

        if "IDSottofase" in dati:
            dati["IDSottofase"] = self._validate_id(dati["IDSottofase"], "IDSottofase")
        if "RuoloDocumento" in dati:
            dati["RuoloDocumento"] = self._upper(
                dati["RuoloDocumento"],
                default="ALLEGATO",
            )
        if "TipoOrigine" in dati:
            dati["TipoOrigine"] = self._upper(dati["TipoOrigine"], default="FILE")
        if "StatoDocumento" in dati:
            dati["StatoDocumento"] = self._upper(
                dati["StatoDocumento"],
                default="ATTIVO",
            )

        for text_field in (
            "TitoloDocumento",
            "DescrizioneDocumento",
            "TipoDocumento",
            "NomeFile",
            "Estensione",
            "PercorsoDocumento",
            "MimeType",
            "HashFile",
            "UtenteCollegamento",
        ):
            if text_field in dati:
                dati[text_field] = self._text_or_none(dati[text_field])

        return dati

    def _normalizza_payload_metadati(self, payload: dict[str, Any]) -> dict[str, Any]:
        return {
            "TitoloDocumento": self._text_or_none(
                self._pick(payload, "TitoloDocumento", "titoloDocumento")
            ),
            "DescrizioneDocumento": self._text_or_none(
                self._pick(
                    payload,
                    "DescrizioneDocumento",
                    "descrizioneDocumento",
                )
            ),
            "StatoDocumento": self._upper(
                self._pick(payload, "StatoDocumento", "statoDocumento"),
                default="BOZZA",
            ),
            "TipoDocumento": self._upper(
                self._pick(payload, "TipoDocumento", "tipoDocumento"),
                default="ALTRO",
            ),
        }

    def _valida_metadati_documento_principale(
        self,
        dati: dict[str, Any],
    ) -> None:
        if not dati.get("TitoloDocumento"):
            raise SottofaseDocumentiValidationError("Titolo documento obbligatorio.")

        stato_documento = dati.get("StatoDocumento")
        if stato_documento not in self.STATI_DOCUMENTO_AMMESSI:
            raise SottofaseDocumentiValidationError(
                f"StatoDocumento non valido: {stato_documento}"
            )

        tipo_documento = dati.get("TipoDocumento")
        if tipo_documento not in self.TIPI_DOCUMENTO_AMMESSI:
            raise SottofaseDocumentiValidationError(
                f"TipoDocumento non valido: {tipo_documento}"
            )

    def _next_ordine_allegato(self, id_sottofase: int) -> int:
        get_next = getattr(
            self.sottofase_documenti_repository,
            "get_next_ordine_allegato",
            None,
        )
        if get_next is None:
            return 1
        return int(get_next(id_sottofase))

    @staticmethod
    def _validate_allegato_file(
        *,
        file_bytes: bytes,
        original_filename: str,
    ) -> str:
        if not file_bytes:
            raise SottofaseDocumentiValidationError("File allegato mancante.")

        filename = Path(str(original_filename or "")).name.strip()
        if not filename:
            raise SottofaseDocumentiValidationError("Nome file allegato mancante.")

        extension = Path(filename).suffix.lower()
        if extension not in ALLOWED_ALLEGATO_EXTENSIONS:
            raise SottofaseDocumentiValidationError(
                "Formato file non ammesso per gli allegati."
            )

        if len(file_bytes) > MAX_ALLEGATO_FILE_SIZE_BYTES:
            raise SottofaseAllegatoFileTooLargeError(
                "File troppo grande: limite massimo 25 MB."
            )

        return filename

    @staticmethod
    def _safe_filename(filename: str) -> str:
        name = Path(filename).name
        cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", name).strip("._")
        return cleaned or f"allegato{Path(filename).suffix.lower()}"

    @staticmethod
    def _is_relative_to(path: Path, parent: Path) -> bool:
        try:
            path.relative_to(parent)
            return True
        except ValueError:
            return False

    @staticmethod
    def _remove_saved_file(saved_path: Path | None) -> None:
        if saved_path is None or not saved_path.exists():
            return

        try:
            saved_path.unlink()
        except OSError:
            pass

    @staticmethod
    def _default_storage_root() -> Path:
        return Path(__file__).resolve().parents[2] / "storage"

    def _valida_documento(
        self,
        dati: dict[str, Any],
        *,
        parziale: bool = False,
    ) -> None:
        ruolo = dati.get("RuoloDocumento")
        tipo_origine = dati.get("TipoOrigine")

        if ruolo is not None and ruolo not in self.RUOLI_AMMESSI:
            raise SottofaseDocumentiValidationError(
                f"RuoloDocumento non valido: {ruolo}"
            )

        if tipo_origine is not None and tipo_origine not in self.TIPI_ORIGINE_AMMESSI:
            raise SottofaseDocumentiValidationError(
                f"TipoOrigine non valido: {tipo_origine}"
            )

        if not parziale or tipo_origine == "PROTOCOLLO":
            if tipo_origine == "PROTOCOLLO" and not dati.get("IDProtocolloCollegato"):
                raise SottofaseDocumentiValidationError(
                    "IDProtocolloCollegato obbligatorio per TipoOrigine PROTOCOLLO."
                )

    @staticmethod
    def _validate_id(value: Any, field_name: str) -> int:
        try:
            normalized = int(value)
        except (TypeError, ValueError):
            raise SottofaseDocumentiValidationError(f"{field_name} non valido.")

        if normalized <= 0:
            raise SottofaseDocumentiValidationError(f"{field_name} non valido.")

        return normalized

    @staticmethod
    def _pick(payload: dict[str, Any], *keys: str, default: Any = None) -> Any:
        for key in keys:
            if key in payload:
                return payload[key]
        return default

    @staticmethod
    def _upper(value: Any, *, default: str) -> str:
        text = str(value or default).strip().upper()
        return text or default

    @staticmethod
    def _text_or_none(value: Any) -> str | None:
        if value is None:
            return None
        text = str(value).strip()
        return text or None
