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
    STEP_ORDER = {
        "REDIGI": 1,
        "REVISIONA": 2,
        "FIRMA": 3,
        "PROTOCOLLA": 4,
        "FINE": 5,
    }

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
        documento_corrente = quadro.get("documento_corrente")
        step_corrente_raw = quadro.get("step_corrente")
        step_corrente = self._normalize_step_code(step_corrente_raw)

        step_operativi_by_code = {
            step.get("codice_step"): step
            for step in step_operativi
            if step.get("codice_step")
        }

        has_current_document = bool(
            documento_corrente
            or quadro.get("id_documento_corrente")
        )
        sottofase_completata = self._is_sottofase_completed(quadro)

        completed = {
            "REDIGI": (
                self._is_step_completed(step_operativi_by_code, "REDIGI")
                or self._is_step_after(step_corrente, "REDIGI")
            ),
            "REVISIONA": (
                self._is_step_completed(step_operativi_by_code, "REVISIONA")
                or self._is_step_after(step_corrente, "REVISIONA")
            ),
            "FIRMA": (
                self._is_step_completed(step_operativi_by_code, "FIRMA")
                or self._is_step_after(step_corrente, "FIRMA")
            ),
            "PROTOCOLLA": (
                self._is_step_completed(step_operativi_by_code, "PROTOCOLLA")
                or self._is_step_after(step_corrente, "PROTOCOLLA")
            ),
            "FINE": (
                sottofase_completata
                or self._is_step_completed(step_operativi_by_code, "FINE")
            ),
        }

        active_code = self._active_code_from_step_corrente(
            step_corrente=step_corrente,
            completed=completed,
        )
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
            "documentoCorrenteMancante": (
                step_corrente in {"FIRMA", "PROTOCOLLA", "FINE"}
                and not has_current_document
            ),
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
    def _active_code_from_step_corrente(
        cls,
        *,
        step_corrente: str | None,
        completed: dict[str, bool],
    ) -> str | None:
        """Restituisce lo step attivo usando `StepCorrente` come fonte primaria."""

        if step_corrente in cls.STEP_ORDER and not completed.get(step_corrente):
            return step_corrente

        for code, _title in cls.STANDARD_STEPS:
            if not completed[code]:
                return code

        return None

    @classmethod
    def _normalize_step_code(cls, value: Any) -> str | None:
        """Normalizza `StepCorrente` letto da Access."""

        if value is None:
            return None

        normalized_value = str(value).strip().upper()

        if normalized_value in cls.STEP_ORDER:
            return normalized_value

        return None

    @classmethod
    def _is_step_after(cls, current_code: str | None, reference_code: str) -> bool:
        """Indica se `StepCorrente` e successivo allo step di riferimento."""

        current_order = cls.STEP_ORDER.get(current_code or "")
        reference_order = cls.STEP_ORDER.get(reference_code)

        if current_order is None or reference_order is None:
            return False

        return current_order > reference_order

    @staticmethod
    def _is_sottofase_completed(quadro: dict[str, Any]) -> bool:
        """Valuta se la sottofase risulta completata usando campi gia esistenti."""

        stato = str(quadro.get("stato_sottofase") or "").strip().upper()

        return stato == "COMPLETATA" or bool(quadro.get("data_completamento"))

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
