import pyodbc
conn = pyodbc.connect(r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=C:\SoluzioniOperative\aib2026.accdb;')
cur = conn.cursor()

query = """
    SELECT
        pr.id, pr.campagna_id, pr.personale_id, pr.postazione_id, pr.funzione_id,
        pr.data_servizio, pr.orario_inizio, pr.orario_fine, pr.ore_totali, pr.stato,
        pr.note_consuntivo, pr.creato_da, pr.creato_il, pr.modificato_il,
        pe.cognome,
        pe.nome        AS nome_dip,
        q.codice       AS qualifica,
        po.codice      AS postazione,
        f.codice       AS funzione
    FROM ((((presenze pr
    LEFT JOIN personale     pe ON pe.id = pr.personale_id)
    LEFT JOIN qualifiche    q  ON q.id  = pe.qualifica_id)
    LEFT JOIN postazioni    po ON po.id = pr.postazione_id)
    LEFT JOIN funzioni_servizio f ON f.id = pr.funzione_id)
    WHERE 1=1 AND pr.campagna_id=?
    ORDER BY pr.data_servizio, pe.cognome
"""
try:
    cur.execute(query, (3,))
    rows = cur.fetchmany(3)
    print(f"OK: {len(rows)} righe (prime 3)")
    for r in rows: print(dict(zip([c[0] for c in cur.description], r)))
except Exception as ex:
    print("ERRORE:", ex)
conn.close()
