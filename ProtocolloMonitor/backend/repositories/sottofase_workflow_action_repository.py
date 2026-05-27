"""Repository di scrittura controllata per azioni workflow sottofase.

Questo repository e il primo punto autorizzato a modificare il workflow
operativo della sottofase. Le scritture sono limitate a:

- `T_ProcedimentoSottofasi`;
- `T_SottofaseStepOperativi`.

Non crea tabelle, non altera schema e non modifica altri oggetti Access.
Le due operazioni vengono eseguite nella stessa transazione: se update o insert
falliscono, viene eseguito rollback e nessuna scrittura parziale viene
confermata.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from .base import BaseRepository


class SottofaseWorkflowActionRepository(BaseRepository):
    """Repository Access-compatible per avanzare il workflow sottofase."""

    def applica_azione_workflow_sottofase(
        self,
        *,
        id_sottofase: int,
        step_corrente: str,
        step_destinazione: str,
        ordine_step: int,
        testo_operatore: str | None,
        utente_operatore: str | None,
        data_azione: datetime,
        chiudi_sottofase: bool = False,
    ) -> None:
        """Esegue update sottofase e insert storico in una sola transazione."""

        conn = self._open_access_connection()
        cursor = conn.cursor()

        try:
            updated = self.aggiorna_step_corrente_sottofase(
                cursor=cursor,
                id_sottofase=id_sottofase,
                step_destinazione=step_destinazione,
                testo_operatore=testo_operatore,
                utente_operatore=utente_operatore,
                data_azione=data_azione,
                chiudi_sottofase=chiudi_sottofase,
            )

            if not updated:
                raise RuntimeError("Sottofase non aggiornata.")

            self.inserisci_step_operativo_sottofase(
                cursor=cursor,
                id_sottofase=id_sottofase,
                codice_step=step_corrente,
                ordine_step=ordine_step,
                testo_operatore=testo_operatore,
                utente_operatore=utente_operatore,
                data_azione=data_azione,
            )

            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    def aggiorna_step_corrente_sottofase(
        self,
        *,
        cursor: Any,
        id_sottofase: int,
        step_destinazione: str,
        testo_operatore: str | None,
        utente_operatore: str | None,
        data_azione: datetime,
        chiudi_sottofase: bool = False,
    ) -> bool:
        """Aggiorna solo i campi di avanzamento workflow della sottofase.

        Se l'azione e `CHIUDI_SOTTOFASE`, vengono valorizzati anche
        `StatoSottofase` e `DataCompletamento`, perche sono campi gia esistenti
        e coerenti con la chiusura operativa. Non vengono creati campi nuovi.
        """

        if chiudi_sottofase:
            query = """
                UPDATE T_ProcedimentoSottofasi
                SET
                    StepCorrente = ?,
                    TestoOperatore = ?,
                    DataUltimaAzione = ?,
                    UtenteUltimaAzione = ?,
                    DataModifica = ?,
                    StatoSottofase = ?,
                    DataCompletamento = ?
                WHERE IDSottofase = ?
            """
            params = (
                step_destinazione,
                testo_operatore,
                data_azione,
                utente_operatore,
                data_azione,
                "COMPLETATA",
                data_azione,
                id_sottofase,
            )
        else:
            query = """
                UPDATE T_ProcedimentoSottofasi
                SET
                    StepCorrente = ?,
                    TestoOperatore = ?,
                    DataUltimaAzione = ?,
                    UtenteUltimaAzione = ?,
                    DataModifica = ?
                WHERE IDSottofase = ?
            """
            params = (
                step_destinazione,
                testo_operatore,
                data_azione,
                utente_operatore,
                data_azione,
                id_sottofase,
            )

        cursor.execute(query, params)

        return getattr(cursor, "rowcount", 1) != 0

    def inserisci_step_operativo_sottofase(
        self,
        *,
        cursor: Any,
        id_sottofase: int,
        codice_step: str,
        ordine_step: int,
        testo_operatore: str | None,
        utente_operatore: str | None,
        data_azione: datetime,
    ) -> None:
        """Inserisce lo storico dello step completato.

        Lo schema Access reale non contiene i campi `TitoloStep`, `Completato`,
        `Attivo`, `DataAzione`, `UtenteAzione` e `TestoOperatore` indicati nel
        contratto funzionale. La scrittura viene quindi adattata ai campi gia
        presenti:

        - `StatoStep = COMPLETATO`;
        - `DataAvvio` e `DataCompletamento` = data azione;
        - `NoteStep` = testo operatore;
        - `UtenteAssegnato` e `UtenteCompletamento` = utente operatore.
        """

        query = """
            INSERT INTO T_SottofaseStepOperativi (
                IDSottofase,
                CodiceStep,
                Ordine,
                StatoStep,
                DataAvvio,
                DataCompletamento,
                NoteStep,
                UtenteAssegnato,
                UtenteCompletamento,
                DataCreazione,
                DataModifica
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        cursor.execute(
            query,
            (
                id_sottofase,
                codice_step,
                ordine_step,
                "COMPLETATO",
                data_azione,
                data_azione,
                testo_operatore,
                utente_operatore,
                utente_operatore,
                data_azione,
                data_azione,
            ),
        )
