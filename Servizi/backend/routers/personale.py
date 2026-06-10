"""
routers/personale.py — Anagrafica dipendenti
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List
from db.database import db
from models.models import Personale, PersonaleCreate, PersonaleUpdate, PersonaleAdminUpdate
from auth import get_current_user, require_role

router = APIRouter(prefix="/personale", tags=["Personale"])


def _build_personale(row: dict) -> dict:
    """Aggiunge campi denormalizzati e lista specialità."""
    if not row:
        return row
    q = db.fetch_one("SELECT codice FROM qualifiche WHERE id=?", (row.get("qualifica_id"),))
    c = db.fetch_one("SELECT codice FROM comandi WHERE id=?",    (row.get("comando_id"),))
    specs = db.fetch_all(
        "SELECT s.id, s.codice, s.descrizione "
        "FROM (personale_specialita ps LEFT JOIN specialita s ON s.id = ps.specialita_id) "
        "WHERE ps.personale_id=? ORDER BY s.codice",
        (row["id"],)
    )
    return {**row,
            "qualifica_cod": q["codice"] if q else None,
            "comando_cod":   c["codice"] if c else None,
            "specialita":    specs or []}


def _set_specialita(personale_id: int, specialita_ids: list[int]):
    """Rimpiazza tutte le specialità di un dipendente."""
    db.execute("DELETE FROM personale_specialita WHERE personale_id=?", (personale_id,))
    for sid in specialita_ids:
        db.execute(
            "INSERT INTO personale_specialita ([personale_id],[specialita_id]) VALUES (?,?)",
            (personale_id, sid)
        )


@router.get("/", response_model=list[Personale])
def lista_personale(current_user: dict = Depends(get_current_user)):
    """
    Admin → tutto.
    Responsabile → solo il proprio comando.
    Dipendente → solo sé stesso.
    """
    if current_user["ruolo"] == "admin":
        rows = db.fetch_all("SELECT * FROM personale WHERE attivo=True ORDER BY cognome, nome")

    elif current_user["ruolo"] == "responsabile":
        rows = db.fetch_all(
            "SELECT * FROM personale WHERE comando_id=? AND attivo=True ORDER BY cognome, nome",
            (current_user["comando_id"],)
        )
    else:
        # dipendente: solo sé stesso
        rows = db.fetch_all(
            "SELECT * FROM personale WHERE id=? AND attivo=True",
            (current_user["personale_id"],)
        )

    return [_build_personale(r) for r in rows]


@router.get("/{pid}", response_model=Personale)
def get_personale(pid: int, current_user: dict = Depends(get_current_user)):
    row = db.fetch_one("SELECT * FROM personale WHERE id=? AND attivo=True", (pid,))
    if not row:
        raise HTTPException(404, "Dipendente non trovato")

    # Dipendente può vedere solo sé stesso
    if current_user["ruolo"] == "dipendente" and current_user["personale_id"] != pid:
        raise HTTPException(403, "Accesso non autorizzato")
    # Responsabile può vedere solo il proprio comando
    if current_user["ruolo"] == "responsabile" and row["comando_id"] != current_user["comando_id"]:
        raise HTTPException(403, "Accesso non autorizzato")

    return _build_personale(row)


@router.post("/", response_model=Personale, dependencies=[Depends(require_role("admin"))])
def crea_personale(data: PersonaleCreate):
    new_id = db.execute(
        """INSERT INTO personale
           (matricola, qualifica_id, cognome, nome, telefono, comando_id, email, attivo, note)
           VALUES (?,?,?,?,?,?,?,?,?)""",
        (data.matricola, data.qualifica_id, data.cognome, data.nome,
         data.telefono, data.comando_id, data.email, data.attivo, data.note)
    )
    return get_personale(new_id, {"ruolo": "admin"})


@router.put("/{pid}/anagrafica", response_model=Personale)
def aggiorna_anagrafica(
    pid: int,
    data: PersonaleAdminUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Admin e Responsabile possono aggiornare tutto. Dipendente solo telefono/email."""
    row = db.fetch_one("SELECT * FROM personale WHERE id=?", (pid,))
    if not row:
        raise HTTPException(404, "Dipendente non trovato")

    if current_user["ruolo"] == "dipendente":
        if current_user["personale_id"] != pid:
            raise HTTPException(403)
        db.execute(
            "UPDATE personale SET telefono=?, email=? WHERE id=?",
            (data.telefono, data.email, pid)
        )
    else:
        db.execute(
            """UPDATE personale SET
               matricola=?, qualifica_id=?, cognome=?, nome=?,
               telefono=?, comando_id=?, email=?, attivo=?, note=?
               WHERE id=?""",
            (data.matricola, data.qualifica_id, data.cognome, data.nome,
             data.telefono, data.comando_id, data.email, data.attivo, data.note, pid)
        )

    return get_personale(pid, current_user)


@router.put("/{pid}/specialita", response_model=Personale, dependencies=[Depends(require_role("admin"))])
def aggiorna_specialita(pid: int, specialita_ids: list[int]):
    """Aggiorna solo le specialità di un dipendente."""
    row = db.fetch_one("SELECT id FROM personale WHERE id=?", (pid,))
    if not row:
        raise HTTPException(404, "Dipendente non trovato")
    _set_specialita(pid, specialita_ids)
    return get_personale(pid, {"ruolo": "admin"})


@router.delete("/{pid}", dependencies=[Depends(require_role("admin"))])
def disattiva_personale(pid: int):
    """Soft delete: attivo=False. I dati storici rimangono intatti."""
    db.execute("UPDATE personale SET attivo=False WHERE id=?", (pid,))
    return {"ok": True}
