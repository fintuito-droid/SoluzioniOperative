"""Service per documenti principali e allegati della sottofase."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from backend.core.access_backup import create_access_backup


class SottofaseDocumentiValidationError(ValueError):
    """Errore di validazione del modello documentale sottofase."""


class SottofaseDocumentoPrincipaleGiaEsistenteError(SottofaseDocumentiValidationError):
    """La sottofase possiede gia un documento principale attivo."""


class SottofaseDocumentoPrincipaleNotFoundError(LookupError):
    """Documento principale attivo non presente per la sottofase."""


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
    ) -> None:
        self.sottofase_documenti_repository = sottofase_documenti_repository
        self.backup_factory = backup_factory

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
            "get_allegati",
            None,
        )
        if get_allegati is None:
            return []

        return get_allegati(self._validate_id(id_sottofase, "IDSottofase"))

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
