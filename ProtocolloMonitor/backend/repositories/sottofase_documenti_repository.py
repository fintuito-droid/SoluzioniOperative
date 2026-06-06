"""Repository per il modello documentale unificato della sottofase."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from .base import BaseRepository


class SottofaseDocumentiRepository(BaseRepository):
    """Access repository per documenti principali e allegati di sottofase."""

    SELECT_COLUMNS = """
        IDDocumentoSottofase,
        IDSottofase,
        RuoloDocumento,
        TipoOrigine,
        TitoloDocumento,
        DescrizioneDocumento,
        TipoDocumento,
        NomeFile,
        Estensione,
        PercorsoDocumento,
        IDProtocolloCollegato,
        MimeType,
        DimensioneBytes,
        HashFile,
        VersioneDocumento,
        StatoDocumento,
        Ordine,
        DataCollegamento,
        UtenteCollegamento,
        Attivo,
        DataCreazione,
        DataModifica
    """

    WRITABLE_COLUMNS = {
        "RuoloDocumento",
        "TipoOrigine",
        "TitoloDocumento",
        "DescrizioneDocumento",
        "TipoDocumento",
        "NomeFile",
        "Estensione",
        "PercorsoDocumento",
        "IDProtocolloCollegato",
        "MimeType",
        "DimensioneBytes",
        "HashFile",
        "VersioneDocumento",
        "StatoDocumento",
        "Ordine",
        "DataCollegamento",
        "UtenteCollegamento",
        "Attivo",
        "DataCreazione",
        "DataModifica",
    }

    @staticmethod
    def _normalize_value(value: Any) -> Any:
        if isinstance(value, datetime):
            return value.isoformat(sep=" ")
        if isinstance(value, date):
            return value.isoformat()
        return value

    @staticmethod
    def _get(row: Any, name: str, default: Any = None) -> Any:
        if row is None:
            return default
        if isinstance(row, dict):
            return row.get(name, default)
        return getattr(row, name, default)

    def _documento_row_to_dict(self, row: Any) -> dict[str, Any]:
        """Converte righe pyodbc/fake row nel formato JSON usato dal backend."""

        return {
            "id_documento_sottofase": self._normalize_value(
                self._get(row, "IDDocumentoSottofase")
            ),
            "id_sottofase": self._normalize_value(self._get(row, "IDSottofase")),
            "ruolo_documento": self._normalize_value(self._get(row, "RuoloDocumento")),
            "tipo_origine": self._normalize_value(self._get(row, "TipoOrigine")),
            "titolo_documento": self._normalize_value(
                self._get(row, "TitoloDocumento")
            ),
            "descrizione_documento": self._normalize_value(
                self._get(row, "DescrizioneDocumento")
            ),
            "tipo_documento": self._normalize_value(self._get(row, "TipoDocumento")),
            "nome_file": self._normalize_value(self._get(row, "NomeFile")),
            "estensione": self._normalize_value(self._get(row, "Estensione")),
            "percorso_documento": self._normalize_value(
                self._get(row, "PercorsoDocumento")
            ),
            "id_protocollo_collegato": self._normalize_value(
                self._get(row, "IDProtocolloCollegato")
            ),
            "mime_type": self._normalize_value(self._get(row, "MimeType")),
            "dimensione_bytes": self._normalize_value(
                self._get(row, "DimensioneBytes")
            ),
            "hash_file": self._normalize_value(self._get(row, "HashFile")),
            "versione_documento": self._normalize_value(
                self._get(row, "VersioneDocumento")
            ),
            "stato_documento": self._normalize_value(self._get(row, "StatoDocumento")),
            "ordine": self._normalize_value(self._get(row, "Ordine")),
            "data_collegamento": self._normalize_value(
                self._get(row, "DataCollegamento")
            ),
            "utente_collegamento": self._normalize_value(
                self._get(row, "UtenteCollegamento")
            ),
            "attivo": bool(self._get(row, "Attivo"))
            if self._get(row, "Attivo") is not None
            else False,
            "data_creazione": self._normalize_value(self._get(row, "DataCreazione")),
            "data_modifica": self._normalize_value(self._get(row, "DataModifica")),
        }

    def get_documenti_sottofase(
        self,
        id_sottofase: int,
        *,
        attivi_only: bool = True,
    ) -> list[dict[str, Any]]:
        query = f"""
            SELECT {self.SELECT_COLUMNS}
            FROM T_SottofaseDocumenti
            WHERE IDSottofase = ?
        """
        params: list[Any] = [id_sottofase]

        if attivi_only:
            query += " AND Attivo = ?"
            params.append(True)

        query += " ORDER BY Ordine ASC, IDDocumentoSottofase ASC"

        conn = self._open_access_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(query, tuple(params))
            return [self._documento_row_to_dict(row) for row in cursor.fetchall()]
        finally:
            cursor.close()
            conn.close()

    def get_documento_principale(
        self,
        id_sottofase: int,
    ) -> dict[str, Any] | None:
        query = f"""
            SELECT TOP 1 {self.SELECT_COLUMNS}
            FROM T_SottofaseDocumenti
            WHERE IDSottofase = ?
              AND RuoloDocumento = ?
              AND Attivo = ?
            ORDER BY Ordine ASC, IDDocumentoSottofase DESC
        """

        conn = self._open_access_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(query, (id_sottofase, "PRINCIPALE", True))
            row = cursor.fetchone()
            return self._documento_row_to_dict(row) if row else None
        finally:
            cursor.close()
            conn.close()

    def get_allegati(
        self,
        id_sottofase: int,
        *,
        attivi_only: bool = True,
    ) -> list[dict[str, Any]]:
        query = f"""
            SELECT {self.SELECT_COLUMNS}
            FROM T_SottofaseDocumenti
            WHERE IDSottofase = ?
              AND RuoloDocumento = ?
        """
        params: list[Any] = [id_sottofase, "ALLEGATO"]

        if attivi_only:
            query += " AND Attivo = ?"
            params.append(True)

        query += " ORDER BY Ordine ASC, IDDocumentoSottofase ASC"

        conn = self._open_access_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(query, tuple(params))
            return [self._documento_row_to_dict(row) for row in cursor.fetchall()]
        finally:
            cursor.close()
            conn.close()

    def get_documento_by_id(
        self,
        id_documento_sottofase: int,
    ) -> dict[str, Any] | None:
        query = f"""
            SELECT {self.SELECT_COLUMNS}
            FROM T_SottofaseDocumenti
            WHERE IDDocumentoSottofase = ?
        """

        conn = self._open_access_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(query, (id_documento_sottofase,))
            row = cursor.fetchone()
            return self._documento_row_to_dict(row) if row else None
        finally:
            cursor.close()
            conn.close()

    def exists_documento_principale_attivo(
        self,
        id_sottofase: int,
        *,
        exclude_id_documento: int | None = None,
    ) -> bool:
        query = """
            SELECT COUNT(*) AS Totale
            FROM T_SottofaseDocumenti
            WHERE IDSottofase = ?
              AND RuoloDocumento = ?
              AND Attivo = ?
        """
        params: list[Any] = [id_sottofase, "PRINCIPALE", True]

        if exclude_id_documento is not None:
            query += " AND IDDocumentoSottofase <> ?"
            params.append(exclude_id_documento)

        conn = self._open_access_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(query, tuple(params))
            row = cursor.fetchone()
            totale = self._get_count(row)
            return totale > 0
        finally:
            cursor.close()
            conn.close()

    def create_documento(self, payload: dict[str, Any]) -> dict[str, Any]:
        now = payload.get("DataCreazione") or datetime.now()
        values = {
            **payload,
            "Attivo": payload.get("Attivo", True),
            "DataCreazione": now,
            "DataModifica": payload.get("DataModifica") or now,
        }

        if values.get("Ordine") is None:
            values["Ordine"] = self._get_next_ordine(int(values["IDSottofase"]))

        columns = [
            "IDSottofase",
            *[column for column in self.WRITABLE_COLUMNS if column in values],
        ]
        placeholders = ", ".join("?" for _ in columns)
        query = f"""
            INSERT INTO T_SottofaseDocumenti (
                {", ".join(columns)}
            )
            VALUES ({placeholders})
        """

        conn = self._open_access_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(query, tuple(values.get(column) for column in columns))
            cursor.execute("SELECT @@IDENTITY AS IDDocumentoSottofase")
            id_documento = self._identity_from_row(cursor.fetchone())
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

        return self.get_documento_by_id(id_documento) or {
            "id_documento_sottofase": id_documento,
            "id_sottofase": values["IDSottofase"],
        }

    def update_documento(
        self,
        id_documento_sottofase: int,
        payload: dict[str, Any],
    ) -> dict[str, Any] | None:
        values = {
            key: value
            for key, value in payload.items()
            if key in self.WRITABLE_COLUMNS
        }
        values["DataModifica"] = payload.get("DataModifica") or datetime.now()

        if not values:
            return self.get_documento_by_id(id_documento_sottofase)

        assignments = ", ".join(f"{column} = ?" for column in values)
        query = f"""
            UPDATE T_SottofaseDocumenti
            SET {assignments}
            WHERE IDDocumentoSottofase = ?
        """

        conn = self._open_access_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                query,
                tuple(values.values()) + (id_documento_sottofase,),
            )
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

        return self.get_documento_by_id(id_documento_sottofase)

    def disattiva_documento(
        self,
        id_documento_sottofase: int,
        *,
        data_modifica: datetime | None = None,
    ) -> dict[str, Any] | None:
        return self.update_documento(
            id_documento_sottofase,
            {
                "Attivo": False,
                "DataModifica": data_modifica or datetime.now(),
            },
        )

    def _get_next_ordine(self, id_sottofase: int) -> int:
        query = """
            SELECT MAX(Ordine) AS MaxOrdine
            FROM T_SottofaseDocumenti
            WHERE IDSottofase = ?
        """
        conn = self._open_access_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(query, (id_sottofase,))
            row = cursor.fetchone()
            max_ordine = self._get(row, "MaxOrdine")
            return int(max_ordine) + 1 if max_ordine is not None else 1
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def _get_count(row: Any) -> int:
        if row is None:
            return 0
        if isinstance(row, (tuple, list)):
            return int(row[0] or 0)
        try:
            return int(row[0] or 0)
        except (TypeError, IndexError):
            return int(getattr(row, "Totale", 0) or 0)

    @staticmethod
    def _identity_from_row(row: Any) -> int:
        if row is None:
            raise RuntimeError("ID documento non restituito da Access.")
        if isinstance(row, (tuple, list)):
            value = row[0]
        else:
            try:
                value = row[0]
            except (TypeError, IndexError):
                value = getattr(row, "IDDocumentoSottofase", None)
        if value is None:
            raise RuntimeError("ID documento non leggibile da Access.")
        return int(value)
