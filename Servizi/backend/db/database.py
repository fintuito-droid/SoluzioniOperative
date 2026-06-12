"""
database.py — Livello di astrazione DB
=======================================
Due implementazioni della stessa interfaccia BaseDatabase:

  - PostgreSQLDatabase  (psycopg2)  ← motore di riferimento
  - AccessDatabase      (pyodbc)    ← fallback legacy

Selezione del motore (variabili d'ambiente):
  DB_ENGINE=postgres | access     (default: postgres; access = fallback d'emergenza)
  DATABASE_URL=postgresql://user:pw@host:porta/db   (per PostgreSQL)
  ACCESS_DB_PATH=C:\\percorso\\aib2026.accdb        (per Access)

Le query nel backend sono scritte in dialetto "Access-compatibile":
  - placeholder ?            → tradotto in %s per psycopg2
  - identificatori [quadre]  → tradotti in "doppi apici" per PostgreSQL
  - INSERT ritorna l'id      → @@IDENTITY su Access, lastval() su PostgreSQL
I letterali True/False e i JOIN annidati con parentesi sono validi in entrambi.
"""

import os
import re
from typing import Any
from contextlib import contextmanager

# ── Configurazione ──────────────────────────────────────────────────────────
DB_ENGINE = os.getenv("DB_ENGINE", "postgres").strip().lower()

DB_PATH = os.getenv(
    "ACCESS_DB_PATH",
    r"C:\SoluzioniOperative\aib2026.accdb"
)

CONN_STRING = (
    r"Driver={Microsoft Access Driver (*.mdb, *.accdb)};"
    rf"DBQ={DB_PATH};"
)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:1234@localhost:5432/aib2026"
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


# ── Implementazione PostgreSQL ───────────────────────────────────────────────
class PostgreSQLDatabase(BaseDatabase):
    """
    Implementazione PostgreSQL via psycopg2.
    Traduce a runtime il dialetto Access usato nel backend:
    [colonna] → "colonna", ? → %s, id da lastval() dopo gli INSERT.
    """

    _RE_QUADRE = re.compile(r"\[([^\]]+)\]")

    def __init__(self, dsn: str = DATABASE_URL):
        self.dsn = dsn

    @staticmethod
    def _traduci(query: str) -> str:
        query = PostgreSQLDatabase._RE_QUADRE.sub(r'"\1"', query)
        return query.replace("?", "%s")

    @contextmanager
    def _get_conn(self):
        import psycopg2
        import psycopg2.extras
        conn = psycopg2.connect(self.dsn)
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def fetch_all(self, query: str, params: tuple = ()) -> list[dict]:
        import psycopg2.extras
        with self._get_conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(self._traduci(query), params)
                return [dict(r) for r in cur.fetchall()]

    def fetch_one(self, query: str, params: tuple = ()) -> dict | None:
        import psycopg2.extras
        with self._get_conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(self._traduci(query), params)
                row = cur.fetchone()
                return dict(row) if row is not None else None

    def execute(self, query: str, params: tuple = ()) -> int:
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(self._traduci(query), params)
                if query.strip().upper().startswith("INSERT"):
                    # Equivalente di @@IDENTITY: id generato dall'ultima sequenza usata
                    try:
                        cur.execute("SELECT lastval()")
                        return int(cur.fetchone()[0])
                    except Exception:
                        return 0   # INSERT senza colonna seriale
                return cur.rowcount

    def execute_many(self, query: str, params_list: list[tuple]) -> None:
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                cur.executemany(self._traduci(query), params_list)


# ── Implementazione Access (legacy) ──────────────────────────────────────────
class AccessDatabase(BaseDatabase):
    """Implementazione Access via pyodbc. Fallback legacy (DB_ENGINE=access)."""

    @contextmanager
    def _get_conn(self):
        import pyodbc
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
# Importare `db` ovunque nel backend. Non istanziare le classi direttamente.
if DB_ENGINE == "postgres":
    db: BaseDatabase = PostgreSQLDatabase()
else:
    db: BaseDatabase = AccessDatabase()
