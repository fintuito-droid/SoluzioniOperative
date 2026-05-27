"""Service read-only per il workflow operativo standard della sottofase.

Il service centralizza le regole temporanee dello Step 30L-8 senza introdurre
scritture, nuove tabelle o nuovi campi Access. I dati vengono riusati dal
service documentale gia esistente.
"""

from __future__ import annotations

from typing import Any


class SottofaseWorkflowService:
    """Compone il workflow REDIGI/REVISIONA/FIRMA/PROTOCOLLA/FINE."""

    STANDARD_STEPS = (
        ("REDIGI", "Redigi"),
        ("REVISIONA", "Revisiona"),
        ("FIRMA", "Firma"),
        ("PROTOCOLLA", "Protocolla"),
        ("FINE", "Fine"),
    )

    def __init__(
        self,
        *,
        sottofase_documentale_service: Any | None = None,
    ) -> None:
        self.sottofase_documentale_service = sottofase_documentale_service

    def get_workflow(
        self,
        id_sottofase: int,
    ) -> dict[str, Any] | None:
        """Restituisce il workflow operativo della sottofase oppure `None`."""

        if self.sottofase_documentale_service is None:
            return None

        get_quadro = getattr(
            self.sottofase_documentale_service,
            "get_quadro_documentale",
            None,
        )

        if get_quadro is None:
            return None

        try:
            quadro = get_quadro(id_sottofase)
        except Exception:
            return None

        if quadro is None:
            return None

        return self._build_workflow(quadro)

    def _build_workflow(self, quadro: dict[str, Any]) -> dict[str, Any]:
        """Applica le regole temporanee read-only al quadro documentale."""

        step_operativi = quadro.get("step_operativi") or []
        documenti = quadro.get("documenti") or []
        documento_corrente = quadro.get("documento_corrente")
        step_corrente_raw = quadro.get("step_corrente")

        step_operativi_by_code = {
            step.get("codice_step"): step
            for step in step_operativi
            if step.get("codice_step")
        }

        has_document = bool(
            quadro.get("ha_documento_collegato")
            or documento_corrente
            or documenti
        )
        has_current_document = bool(
            documento_corrente
            or quadro.get("id_documento_corrente")
        )
        versione_documento = self._to_int(
            quadro.get("versione_documento")
            or (documento_corrente or {}).get("versione_documento")
        )

        completed = {
            "REDIGI": has_document,
            "REVISIONA": versione_documento >= 2,
            "FIRMA": self._is_step_completed(step_operativi_by_code, "FIRMA"),
            "PROTOCOLLA": self._is_step_completed(
                step_operativi_by_code,
                "PROTOCOLLA",
            ),
            "FINE": self._is_step_completed(step_operativi_by_code, "FINE"),
        }

        if (
            not completed["FINE"]
            and step_corrente_raw == "FINE"
            and completed["PROTOCOLLA"]
        ):
            completed["FINE"] = True

        active_rules = {
            "REDIGI": not completed["REDIGI"],
            "REVISIONA": completed["REDIGI"] and not completed["REVISIONA"],
            "FIRMA": (
                has_document
                and has_current_document
                and not completed["FIRMA"]
            ),
            "PROTOCOLLA": (
                has_current_document
                and completed["FIRMA"]
                and not completed["PROTOCOLLA"]
            ),
            "FINE": (
                bool(step_corrente_raw)
                and completed["PROTOCOLLA"]
                and not completed["FINE"]
            ),
        }

        active_code = self._first_active_code(completed, active_rules)
        workflow = []

        for index, (code, title) in enumerate(self.STANDARD_STEPS, start=1):
            metadata = self._step_metadata(
                code=code,
                quadro=quadro,
                step=step_operativi_by_code.get(code),
                documento_corrente=documento_corrente,
            )
            workflow.append(
                {
                    "codice": code,
                    "titolo": title,
                    "completato": completed[code],
                    "attivo": code == active_code,
                    "timestamp": metadata.get("timestamp"),
                    "operatore": metadata.get("operatore"),
                    "ordine": index,
                }
            )

        completed_count = sum(1 for step in workflow if step["completato"])
        percentuale = int(round((completed_count / len(self.STANDARD_STEPS)) * 100))

        return {
            "stepCorrente": self._current_step_number(workflow),
            "workflow": workflow,
            "percentualeAvanzamento": percentuale,
        }

    @staticmethod
    def _to_int(value: Any) -> int:
        """Converte valori Access/stringa in intero prudente."""

        try:
            return int(value)
        except (TypeError, ValueError):
            return 0

    @staticmethod
    def _is_step_completed(
        steps_by_code: dict[str, dict[str, Any]],
        code: str,
    ) -> bool:
        """Verifica se uno step operativo persistito e completato."""

        return steps_by_code.get(code, {}).get("stato_step") == "COMPLETATO"

    @classmethod
    def _first_active_code(
        cls,
        completed: dict[str, bool],
        active_rules: dict[str, bool],
    ) -> str | None:
        """Restituisce il primo step non completato e attivabile."""

        for code, _title in cls.STANDARD_STEPS:
            if not completed[code] and active_rules[code]:
                return code

        return None

    @staticmethod
    def _step_metadata(
        *,
        code: str,
        quadro: dict[str, Any],
        step: dict[str, Any] | None,
        documento_corrente: dict[str, Any] | None,
    ) -> dict[str, Any]:
        """Ricava timestamp e operatore dai dati documentali disponibili."""

        if step:
            return {
                "timestamp": (
                    step.get("data_completamento")
                    or step.get("data_avvio")
                    or step.get("data_creazione")
                ),
                "operatore": (
                    step.get("utente_completamento")
                    or step.get("utente_assegnato")
                ),
            }

        if code in {"REDIGI", "REVISIONA"} and documento_corrente:
            return {
                "timestamp": documento_corrente.get("data_collegamento"),
                "operatore": (
                    documento_corrente.get("utente_collegamento")
                    or quadro.get("utente_ultima_azione")
                ),
            }

        return {
            "timestamp": None,
            "operatore": None,
        }

    @staticmethod
    def _current_step_number(workflow: list[dict[str, Any]]) -> int:
        """Calcola il numero di step corrente da esporre all'API."""

        for step in workflow:
            if step["attivo"]:
                return step["ordine"]

        completed_steps = [step["ordine"] for step in workflow if step["completato"]]

        if not completed_steps:
            return 1

        return min(max(completed_steps) + 1, len(workflow))
