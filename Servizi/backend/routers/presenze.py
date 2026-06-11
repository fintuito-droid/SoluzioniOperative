"""
routers/presenze.py — Pianificazione e consuntivo presenze AIB
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from datetime import date
from db.database import db
from models.models import Presenza, PresenzaCreate, PresenzaConsuntivo, MonteOrePersonale, StatoPresenza
from datetime import datetime
from auth import get_current_user, require_role

router = APIRouter(prefix="/presenze", tags=["Presenze"])


# ── Query base con JOIN (identica per Access e PostgreSQL) ───────────────────
PRESENZE_SELECT = """
    SELECT
        pr.id, pr.campagna_id, pr.personale_id, pr.postazione_id, pr.funzione_id,
        pr.data_servizio, pr.orario_inizio, pr.orario_fine, pr.ore_totali, pr.stato,
        pr.note_consuntivo, pr.fascia_oraria, pr.creato_da, pr.creato_il, pr.modificato_il,
        pe.cognome,
        pe.nome        AS nome_dip,
        pe.comando_id,
        q.codice       AS qualifica,
        po.codice      AS postazione,
        f.codice       AS funzione
    FROM ((((presenze pr
    LEFT JOIN personale     pe ON pe.id = pr.personale_id)
    LEFT JOIN qualifiche    q  ON q.id  = pe.qualifica_id)
    LEFT JOIN postazioni    po ON po.id = pr.postazione_id)
    LEFT JOIN funzioni_servizio f ON f.id = pr.funzione_id)
"""


def _valida_data_campagna(campagna_id: int, data_servizio) -> None:
    """La data del turno deve cadere nel periodo della campagna."""
    if not campagna_id:
        return
    c = db.fetch_one("SELECT * FROM campagne_aib WHERE id=?", (campagna_id,))
    if not c:
        raise HTTPException(422, "Campagna inesistente")
    di = str(c["data_inizio"])[:10]
    df = str(c["data_fine"])[:10]
    ds = str(data_servizio)[:10]
    if not (di <= ds <= df):
        raise HTTPException(422,
            f"La data {ds} è fuori dal periodo della campagna AIB {c['anno']} ({di} → {df})")


def _verifica_sovrapposizione(personale_id: int, data_servizio, fascia) -> None:
    """
    Una persona non può avere due turni sovrapposti nello stesso giorno:
    stessa fascia (M+M, P+P, U+U) oppure turno unico U contro qualsiasi
    altra fascia (U copre l'intera giornata).
    """
    if not fascia:
        return
    rows = db.fetch_all(
        "SELECT pr.fascia_oraria, pe.cognome, pe.nome FROM (presenze pr "
        "LEFT JOIN personale pe ON pe.id = pr.personale_id) "
        "WHERE pr.personale_id=? AND pr.data_servizio=?",
        (personale_id, str(data_servizio))
    )
    fascia_label = {'U': 'turno unico', 'M': 'mattina', 'P': 'pomeriggio'}
    for r in rows:
        f_ex = r.get("fascia_oraria")
        if not f_ex:
            continue  # presenze storiche senza fascia: nessun blocco
        if f_ex == fascia or f_ex == 'U' or fascia == 'U':
            nome = f"{r.get('cognome','')} {r.get('nome','')}".strip()
            raise HTTPException(409,
                f"{nome} è già assegnato in {fascia_label.get(f_ex, f_ex)} "
                f"per il {str(data_servizio)[:10]}")


def _scope_filter(current_user: dict) -> tuple[str, list]:
    """Costruisce il filtro di scope in base al ruolo."""
    if current_user["ruolo"] == "admin":
        return "", []
    elif current_user["ruolo"] == "responsabile":
        return " AND pe.comando_id=?", [current_user["comando_id"]]
    else:
        return " AND pr.personale_id=?", [current_user["personale_id"]]


@router.get("/", response_model=list[Presenza])
def lista_presenze(
    campagna_id:   Optional[int]  = Query(None),
    personale_id:  Optional[int]  = Query(None),
    postazione_id: Optional[int]  = Query(None),
    data_da:       Optional[date] = Query(None),
    data_a:        Optional[date] = Query(None),
    stato:         Optional[str]  = Query(None),
    current_user:  dict           = Depends(get_current_user)
):
    where = ["1=1"]
    params = []

    # Filtri opzionali
    if campagna_id:
        where.append("pr.campagna_id=?"); params.append(campagna_id)
    if personale_id:
        where.append("pr.personale_id=?"); params.append(personale_id)
    if postazione_id:
        where.append("pr.postazione_id=?"); params.append(postazione_id)
    if data_da:
        where.append("pr.data_servizio>=?"); params.append(str(data_da))
    if data_a:
        where.append("pr.data_servizio<=?"); params.append(str(data_a))
    if stato:
        where.append("pr.stato=?"); params.append(stato)

    # Scope ruolo
    scope_sql, scope_params = _scope_filter(current_user)
    params.extend(scope_params)

    query = (PRESENZE_SELECT
             + " WHERE " + " AND ".join(where)
             + scope_sql
             + " ORDER BY pr.data_servizio, pe.cognome")

    return db.fetch_all(query, tuple(params))


@router.get("/monte-ore", response_model=list[MonteOrePersonale])
def monte_ore(
    campagna_id:   Optional[int]  = Query(None),
    data_da:       Optional[date] = Query(None),
    data_a:        Optional[date] = Query(None),
    postazione_id: Optional[int]  = Query(None),
    current_user:  dict           = Depends(get_current_user)
):
    """
    Aggregazione ore per dipendente.
    Supporta filtro per postazione (monte ore separato per postazione).
    Access non supporta GROUP BY con JOIN complessi —
    aggregazione in Python per mantenere la stessa logica in Postgres.
    """
    rows = lista_presenze(
        campagna_id=campagna_id,
        personale_id=None,
        postazione_id=postazione_id,
        data_da=data_da,
        data_a=data_a,
        stato=None,
        current_user=current_user
    )

    # Aggrega in Python
    aggregati: dict[int, dict] = {}
    for r in rows:
        pid = r["personale_id"]
        if pid not in aggregati:
            aggregati[pid] = {
                "personale_id":    pid,
                "cognome":         r.get("cognome", ""),
                "nome":            r.get("nome_dip", ""),
                "qualifica":       r.get("qualifica"),
                "comando":         None,
                "comando_id":      r.get("comando_id"),
                "ore_totali":      0.0,
                "turni_totali":    0,
                "ore_per_funzione": {}
            }
        agg = aggregati[pid]
        ore = r.get("ore_totali") or 0
        agg["ore_totali"]   += ore
        agg["turni_totali"] += 1
        funz = r.get("funzione") or "N/D"
        agg["ore_per_funzione"][funz] = agg["ore_per_funzione"].get(funz, 0) + ore

    result = sorted(aggregati.values(), key=lambda x: x["cognome"])
    return result


@router.post("/batch", response_model=list[Presenza])
def crea_presenze_batch(
    items: list[PresenzaCreate],
    current_user: dict = Depends(get_current_user)
):
    """
    Crea N presenze in sequenza (composizione giorno dal calendario).
    Validazione anti-duplicato: se una persona è già assegnata nella
    stessa fascia+data risponde HTTP 409 e interrompe — le presenze
    precedenti del batch rimangono (Access non supporta transazioni
    multi-statement affidabili via ODBC).
    Solo Admin e Responsabile.
    """
    if current_user["ruolo"] == "dipendente":
        raise HTTPException(403, "I dipendenti non possono pianificare turni")

    # Validazioni preventive su TUTTO il batch prima di scrivere
    # (riduce il rischio di scritture parziali su Access senza transazioni)
    for data in items:
        _valida_data_campagna(data.campagna_id, data.data_servizio)
        _verifica_sovrapposizione(data.personale_id, data.data_servizio, data.fascia_oraria)

    creati = []
    for data in items:
        ore = data.ore_totali
        if ore is None:
            try:
                h1, m1 = map(int, data.orario_inizio.split(":"))
                h2, m2 = map(int, data.orario_fine.split(":"))
                ore = round((h2 * 60 + m2 - h1 * 60 - m1) / 60, 1)
            except Exception:
                ore = 0.0

        new_id = db.execute(
            """INSERT INTO presenze
               (campagna_id, personale_id, postazione_id, funzione_id,
                data_servizio, orario_inizio, orario_fine, ore_totali,
                stato, note_consuntivo, fascia_oraria, creato_da, creato_il)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (data.campagna_id, data.personale_id, data.postazione_id, data.funzione_id,
             str(data.data_servizio), data.orario_inizio, data.orario_fine, ore,
             StatoPresenza.programmato.value, data.note_consuntivo, data.fascia_oraria,
             current_user["id"], datetime.now())
        )
        creati.append(get_presenza(new_id, current_user))

    return creati


@router.get("/{pid_presenza}", response_model=Presenza)
def get_presenza(pid_presenza: int, current_user: dict = Depends(get_current_user)):
    row = db.fetch_one(
        PRESENZE_SELECT + " WHERE pr.id=?",
        (pid_presenza,)
    )
    if not row:
        raise HTTPException(404, "Presenza non trovata")
    return row


@router.post("/", response_model=Presenza)
def crea_presenza(
    data: PresenzaCreate,
    current_user: dict = Depends(get_current_user)
):
    """Crea un turno programmato. Solo Admin e Responsabile."""
    if current_user["ruolo"] == "dipendente":
        raise HTTPException(403, "I dipendenti non possono pianificare turni")

    _valida_data_campagna(data.campagna_id, data.data_servizio)
    _verifica_sovrapposizione(data.personale_id, data.data_servizio, data.fascia_oraria)

    # Calcola ore_totali se non fornite
    ore = data.ore_totali
    if ore is None:
        try:
            h1, m1 = map(int, data.orario_inizio.split(":"))
            h2, m2 = map(int, data.orario_fine.split(":"))
            ore = round((h2 * 60 + m2 - h1 * 60 - m1) / 60, 1)
        except Exception:
            ore = 0.0

    new_id = db.execute(
        """INSERT INTO presenze
           (campagna_id, personale_id, postazione_id, funzione_id,
            data_servizio, orario_inizio, orario_fine, ore_totali,
            stato, note_consuntivo, fascia_oraria, creato_da, creato_il)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (data.campagna_id, data.personale_id, data.postazione_id, data.funzione_id,
         str(data.data_servizio), data.orario_inizio, data.orario_fine, ore,
         StatoPresenza.programmato.value, data.note_consuntivo, data.fascia_oraria,
         current_user["id"], datetime.now())
    )
    return get_presenza(new_id, current_user)


@router.patch("/{pid_presenza}/consuntivo", response_model=Presenza)
def consuntiva_presenza(
    pid_presenza: int,
    data: PresenzaConsuntivo,
    current_user: dict = Depends(get_current_user)
):
    """
    Conferma o modifica un turno programmato.
    Admin → qualsiasi turno.
    Responsabile → turni del proprio comando.
    Dipendente → non consentito.
    """
    if current_user["ruolo"] == "dipendente":
        raise HTTPException(403, "Accesso non consentito")

    row = db.fetch_one("SELECT * FROM presenze WHERE id=?", (pid_presenza,))
    if not row:
        raise HTTPException(404, "Presenza non trovata")

    # Aggiorna solo i campi forniti
    orario_i = data.orario_inizio or row["orario_inizio"]
    orario_f = data.orario_fine   or row["orario_fine"]

    ore = data.ore_totali
    if ore is None:
        try:
            h1, m1 = map(int, orario_i.split(":"))
            h2, m2 = map(int, orario_f.split(":"))
            ore = round((h2 * 60 + m2 - h1 * 60 - m1) / 60, 1)
        except Exception:
            ore = row["ore_totali"]

    db.execute(
        """UPDATE presenze SET
           orario_inizio=?, orario_fine=?, ore_totali=?,
           stato=?, note_consuntivo=?, modificato_il=NOW()
           WHERE id=?""",
        (orario_i, orario_f, ore,
         data.stato.value,
         data.note_consuntivo or row.get("note_consuntivo"),
         pid_presenza)
    )
    return get_presenza(pid_presenza, current_user)


@router.delete("/{pid_presenza}", dependencies=[Depends(require_role("admin"))])
def elimina_presenza(pid_presenza: int):
    """Solo Admin. Elimina fisicamente (i dati AIB devono poter essere corretti)."""
    n = db.execute("DELETE FROM presenze WHERE id=?", (pid_presenza,))
    if n == 0:
        raise HTTPException(404, "Presenza non trovata")
    return {"ok": True}
