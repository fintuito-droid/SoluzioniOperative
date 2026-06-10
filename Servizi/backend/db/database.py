"""
database.py — Livello di astrazione DB
=======================================
Questo è l'UNICO file da sostituire per migrare da Access a PostgreSQL.
Il resto del backend non sa quale DB sta usando.

Per migrare a PostgreSQL:
  1. Sostituire AccessDatabase con una classe PostgreSQLDatabase
     che implementa gli stessi metodi: fetch_all, fetch_one, execute
  2. Aggiornare DB_PATH / connstring in config.py
  3. Nessun'altra modifica necessaria.
"""

import pyodbc
import os
from typing import Any
from contextlib import contextmanager

# ── Configurazione ──────────────────────────────────────────────────────────
# In produzione, leggere da variabile d'ambiente o config file
DB_PATH = os.getenv(
    "ACCESS_DB_PATH",
    r"C:\SoluzioniOperative\aib2026.accdb"
)

CONN_STRING = (
    r"Driver={Microsoft Access Driver (*.mdb, *.accdb)};"
    rf"DBQ={DB_PATH};"
)


# ── Classe base (interfaccia contrattuale) ───────────────────────────────────
class BaseDatabase:
    """
    Interfaccia che TUTTE le implementazioni DB devono rispettare.
    Cambiare DB = creare una nuova classe che estende questa.
    """
    def fetch_all(self, query: str, params: tuple = ()) -> list[dict]:
        raise NotImplementedError

    def fetch_one(self, query: str, params: tuple = ()) -> dict | None:
        raise NotImplementedError

    def execute(self, query: str, params: tuple = ()) -> int:
        """Ritorna il numero di righe affette, o lastrowid per INSERT."""
        raise NotImplementedError

    def execute_many(self, query: str, params_list: list[tuple]) -> None:
        raise NotImplementedError


# ── Implementazione Access ───────────────────────────────────────────────────
class AccessDatabase(BaseDatabase):
    """
    Implementazione Access via pyodbc.
    Le query usano ? come placeholder (stile DBAPI2) —
    PostgreSQL usa %s, ma psycopg2 accetta anche ? se usi
    il parametro paramstyle corretto. In alternativa, un
    piccolo adattatore converte ? → %s a runtime.
    """

    @contextmanager
    def _get_conn(self):
        conn = pyodbc.connect(CONN_STRING, autocommit=False)
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _row_to_dict(self, cursor, row) -> dict:
        """Converte una riga pyodbc in dizionario."""
        columns = [col[0].lower() for col in cursor.description]
        return dict(zip(columns, row))

    def fetch_all(self, query: str, params: tuple = ()) -> list[dict]:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [self._row_to_dict(cursor, row) for row in cursor.fetchall()]

    def fetch_one(self, query: str, params: tuple = ()) -> dict | None:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            row = cursor.fetchone()
            if row is None:
                return None
            return self._row_to_dict(cursor, row)

    def execute(self, query: str, params: tuple = ()) -> int:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            # Access non supporta RETURNING — usiamo @@IDENTITY
            if query.strip().upper().startswith("INSERT"):
                last_id = cursor.execute("SELECT @@IDENTITY").fetchone()[0]
                return int(last_id) if last_id else 0
            return cursor.rowcount

    def execute_many(self, query: str, params_list: list[tuple]) -> None:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.executemany(query, params_list)


# ── Singleton ────────────────────────────────────────────────────────────────
# Importare `db` ovunque nel backend. Non istanziare direttamente AccessDatabase.
db: BaseDatabase = AccessDatabase()


# ── Nota migrazione PostgreSQL ───────────────────────────────────────────────
# Quando si passa a PostgreSQL, sostituire le righe sopra con:
#
# import psycopg2
# import psycopg2.extras
#
# class PostgreSQLDatabase(BaseDatabase):
#     def __init__(self):
#         self.dsn = os.getenv("DATABASE_URL")  # es. postgresql://user:pw@host/db
#
#     @contextmanager
#     def _get_conn(self):
#         conn = psycopg2.connect(self.dsn)
#         conn.cursor_factory = psycopg2.extras.RealDictCursor
#         try:
#             yield conn
#             conn.commit()
#         except Exception:
#             conn.rollback()
#             raise
#         finally:
#             conn.close()
#
#     def fetch_all(self, query, params=()):
#         with self._get_conn() as conn:
#             with conn.cursor() as cur:
#                 cur.execute(query.replace("?", "%s"), params)
#                 return [dict(r) for r in cur.fetchall()]
#
#     # ... (stessa struttura)
#
# db: BaseDatabase = PostgreSQLDatabase()
