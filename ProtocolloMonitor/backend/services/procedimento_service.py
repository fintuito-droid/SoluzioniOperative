"""Service Layer read-only per l'entita Procedimento.

Il service introduce un punto applicativo sopra `ProcedimentoRepository`, senza
creare route FastAPI e senza modificare dati.

Responsabilita:
- esporre metodi read-only per procedimenti;
- delegare al repository quando disponibile;
- restituire fallback sicuri quando la dipendenza non e configurata;
- mantenere il backend pronto a PostgreSQL senza cambiare il runtime attuale.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any


class ProtocolloNotFoundError(Exception):
    """Errore applicativo per protocollo inesistente."""


class ProcedimentoNotFoundError(Exception):
    """Errore applicativo per procedimento inesistente."""


class ProcedimentoProtocolloLinkAlreadyExistsError(Exception):
    """Errore applicativo per collegamento gia presente."""


class ProcedimentoService:
    """Service minimale per procedimenti.

    Il service non apre connessioni, non esegue SQL e non modifica il database.
    Tutto l'accesso dati resta nel repository, cosi in futuro sara possibile
    sostituire Access con PostgreSQL mantenendo stabile il contratto.
    """

    def __init__(
        self,
        *,
        procedimento_repository: Any | None = None,
        now_factory: Any | None = None,
    ) -> None:
        self.procedimento_repository = procedimento_repository
        self.now_factory = now_factory or datetime.now

    def crea_procedimento(self, payload: Any) -> dict[str, Any]:
        """Valida e crea un procedimento principale senza workflow collegato."""

        if self.procedimento_repository is None:
            raise ValueError("Repository procedimento non configurato.")

        data = self._payload_to_dict(payload)
        titolo = str(data.get("Titolo") or "").strip()
        if not titolo:
            raise ValueError("Titolo obbligatorio.")

        now = self.now_factory()
        codice = str(data.get("CodiceProcedimento") or "").strip()
        if not codice:
            codice = now.strftime("PM-%Y%m%d-%H%M%S")

        priorita = str(data.get("Priorita") or "").strip() or "NORMALE"
        tipologia = str(data.get("TipologiaProcedimento") or "").strip() or "GENERICO"

        create = getattr(self.procedimento_repository, "crea_procedimento", None)
        if create is None:
            raise ValueError("Creazione procedimento non disponibile.")

        return create(
            {
                "CodiceProcedimento": codice,
                "Titolo": titolo,
                "Descrizione": self._clean_optional(data.get("Descrizione")),
                "AziendaSoggetto": self._clean_optional(data.get("AziendaSoggetto")),
                "ComandoCompetenza": self._clean_optional(
                    data.get("ComandoCompetenza")
                ),
                "SettoreCompetenza": self._clean_optional(
                    data.get("SettoreCompetenza")
                ),
                "TipologiaProcedimento": tipologia,
                "StatoProcedimento": "APERTO",
                "Priorita": priorita,
                "DataApertura": now,
                "DataUltimoAggiornamento": now,
                "DataScadenza": self._clean_date(data.get("DataScadenza")),
                "DataChiusura": None,
                "NoteInterne": self._clean_optional(data.get("NoteInterne")),
                "Attivo": True,
                "DataCreazione": now,
                "DataModifica": now,
            }
        )

    def list_procedimenti(self) -> list[dict[str, Any]]:
        """Restituisce l'elenco procedimenti.

        Fallback sicuro: lista vuota se il repository manca, non espone il
        metodo atteso o solleva errore.
        """

        if self.procedimento_repository is None:
            return []

        list_procedimenti = getattr(
            self.procedimento_repository,
            "list_procedimenti",
            None,
        )

        if list_procedimenti is None:
            return []

        try:
            return list_procedimenti()
        except Exception:
            return []

    @staticmethod
    def _payload_to_dict(payload: Any) -> dict[str, Any]:
        if payload is None:
            return {}
        if isinstance(payload, dict):
            return payload

        model_dump = getattr(payload, "model_dump", None)
        if model_dump is not None:
            return model_dump()

        dict_method = getattr(payload, "dict", None)
        if dict_method is not None:
            return dict_method()

        return {}

    @staticmethod
    def _clean_optional(value: Any) -> Any:
        if value is None:
            return None
        if isinstance(value, str):
            normalized = value.strip()
            return normalized or None
        return value

    @staticmethod
    def _clean_date(value: Any) -> Any:
        normalized = ProcedimentoService._clean_optional(value)
        if not isinstance(normalized, str):
            return normalized

        try:
            return datetime.fromisoformat(normalized)
        except ValueError:
            return normalized

    def get_procedimento_detail(self, id_procedimento: int) -> dict[str, Any] | None:
        """Restituisce il dettaglio procedimento oppure `None`.

        `None` rappresenta il caso "procedimento non trovato" finche non verra
        introdotta una route FastAPI che potra trasformarlo in HTTP 404.
        """

        if self.procedimento_repository is None:
            return None

        get_detail = getattr(
            self.procedimento_repository,
            "get_procedimento_detail",
            None,
        )

        if get_detail is None:
            return None

        try:
            return get_detail(id_procedimento)
        except Exception:
            return None

    def list_protocolli_collegati(
        self,
        id_procedimento: int,
    ) -> list[dict[str, Any]]:
        """Restituisce i protocolli collegati al procedimento."""

        if self.procedimento_repository is None:
            return []

        list_linked = getattr(
            self.procedimento_repository,
            "list_protocolli_collegati",
            None,
        )

        if list_linked is None:
            return []

        try:
            return list_linked(id_procedimento)
        except Exception:
            return []

    def count_protocolli_collegati(self, id_procedimento: int) -> int:
        """Conta i protocolli collegati al procedimento."""

        if self.procedimento_repository is None:
            return 0

        count_linked = getattr(
            self.procedimento_repository,
            "count_protocolli_collegati",
            None,
        )

        if count_linked is None:
            return 0

        try:
            return int(count_linked(id_procedimento) or 0)
        except Exception:
            return 0

    def list_procedimenti_by_protocollo_id(
        self,
        id_protocollo: int,
    ) -> list[dict[str, Any]]:
        """Restituisce i procedimenti collegati a un protocollo.

        Se il protocollo non esiste, solleva `ProtocolloNotFoundError` cosi la
        route FastAPI puo restituire un HTTP 404 esplicito.
        """

        if self.procedimento_repository is None:
            raise ProtocolloNotFoundError()

        if not self.procedimento_repository.protocollo_exists(id_protocollo):
            raise ProtocolloNotFoundError()

        return self.procedimento_repository.list_procedimenti_by_protocollo_id(
            id_protocollo
        )

    def link_protocollo_to_procedimento(
        self,
        *,
        id_protocollo: int,
        id_procedimento: int,
        ruolo_protocollo: str | None = None,
        principale: bool = False,
        note_collegamento: str | None = None,
    ) -> dict[str, Any]:
        """Collega un protocollo a un procedimento.

        Il service valida esistenza protocollo/procedimento e blocca duplicati
        prima dell'insert. Il vincolo univoco DB resta comunque la protezione
        finale contro race condition o chiamate concorrenti.
        """

        if self.procedimento_repository is None:
            raise ProtocolloNotFoundError()

        if not self.procedimento_repository.protocollo_exists(id_protocollo):
            raise ProtocolloNotFoundError()

        if not self.procedimento_repository.procedimento_exists(id_procedimento):
            raise ProcedimentoNotFoundError()

        if self.procedimento_repository.procedimento_protocollo_link_exists(
            id_protocollo,
            id_procedimento,
        ):
            raise ProcedimentoProtocolloLinkAlreadyExistsError()

        normalized_role = (ruolo_protocollo or "COLLEGATO").strip() or "COLLEGATO"

        created_link = self.procedimento_repository.link_protocollo_to_procedimento(
            id_protocollo=id_protocollo,
            id_procedimento=id_procedimento,
            ruolo_protocollo=normalized_role,
            principale=bool(principale),
            note_collegamento=note_collegamento,
        )

        if created_link is None:
            raise ProcedimentoProtocolloLinkAlreadyExistsError()

        return created_link
