"""Migrazione dati 2025 da PresenzeSour verso aib2026.accdb"""
import pyodbc

SRC = r"Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=C:\Users\fintu\Desktop\PresenzeSour - Copia.accdb;"
DST = r"Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=C:\SoluzioniOperative\aib2026.accdb;"

src = pyodbc.connect(SRC)
dst = pyodbc.connect(DST)
sc  = src.cursor()
dc  = dst.cursor()

# ── 1. Qualifiche mancanti ───────────────────────────────────────────────────
qualifiche_extra = ['CR','CS','CSE','D','DCS','DS','DV','EDCS','IA','IAE','VC','VCSC','VE','VESC','VIG']
for q in qualifiche_extra:
    try:
        dc.execute("INSERT INTO qualifiche ([codice],[descrizione]) VALUES (?,?)", (q, q))
    except:
        pass  # già esistente

# ── 2. Comandi mancanti ──────────────────────────────────────────────────────
comandi_extra = [('CALTANISSETTA','Comando Caltanissetta'),
                 ('ENNA','Comando Enna'),
                 ('MESSINA','Comando Messina')]
for codice, nome in comandi_extra:
    try:
        dc.execute("INSERT INTO comandi ([codice],[nome],[attivo]) VALUES (?,?,True)", (codice, nome))
    except:
        pass

# ── 3. Postazioni mancanti ───────────────────────────────────────────────────
postazioni_extra = [('SOR','Sala Operativa Regionale'),
                    ('COMANDO PALERMO','Comando Provinciale Palermo')]
for codice, nome in postazioni_extra:
    try:
        dc.execute("INSERT INTO postazioni ([codice],[nome],[attiva]) VALUES (?,?,True)", (codice, nome))
    except:
        pass

# ── 4. Funzioni mancanti ─────────────────────────────────────────────────────
funzioni_extra = [('AUTISTA DOS','Autista DOS'), ('TAS 2','TAS 2')]
for codice, nome in funzioni_extra:
    try:
        dc.execute("INSERT INTO funzioni_servizio ([codice],[descrizione]) VALUES (?,?)", (codice, nome))
    except:
        pass

dst.commit()

# ── Leggi lookup IDs dal DST ─────────────────────────────────────────────────
def fetch_map(table, key_col, id_col='id'):
    dc.execute(f"SELECT [{key_col}], [{id_col}] FROM [{table}]")
    return {r[0]: r[1] for r in dc.fetchall()}

qualifiche_map = fetch_map('qualifiche', 'codice')
comandi_map    = fetch_map('comandi',    'codice')
postazioni_map = fetch_map('postazioni', 'codice')
funzioni_map   = fetch_map('funzioni_servizio', 'codice')

# ── 5. Campagna 2025 ─────────────────────────────────────────────────────────
try:
    dc.execute("INSERT INTO campagne_aib ([anno],[data_inizio],[data_fine],[descrizione],[attiva]) VALUES (2025,{d '2025-06-15'},{d '2025-10-15'},'Campagna AIB 2025 Sicilia',False)")
    dst.commit()
except:
    pass

dc.execute("SELECT [id] FROM campagne_aib WHERE [anno]=2025")
row = dc.fetchone()
campagna_2025_id = row[0] if row else None
print(f"Campagna 2025 id={campagna_2025_id}")

# ── 6. Personale ─────────────────────────────────────────────────────────────
sc.execute("SELECT [ID],[QUALIFICA],[COGNOME],[NOME],[TELEFONO],[COMANDO] FROM Personale")
personale_src = sc.fetchall()

personale_id_map = {}  # ID_src → ID_dst

for row in personale_src:
    src_id, qualifica, cognome, nome, telefono, comando = row
    q_id = qualifiche_map.get(qualifica)
    c_id = comandi_map.get(comando)
    tel  = str(int(telefono)) if telefono and str(telefono).replace('.','').isdigit() else (str(telefono) if telefono else None)

    # Controlla se già esiste
    dc.execute("SELECT [id] FROM personale WHERE [cognome]=? AND [nome]=?", (cognome, nome))
    existing = dc.fetchone()
    if existing:
        personale_id_map[src_id] = existing[0]
        print(f"  EXISTS personale: {cognome} {nome}")
        continue

    dc.execute(
        "INSERT INTO personale ([qualifica_id],[cognome],[nome],[telefono],[comando_id],[attivo]) VALUES (?,?,?,?,?,True)",
        (q_id, cognome, nome, tel, c_id)
    )
    dst.commit()
    dc.execute("SELECT @@IDENTITY")
    new_id = dc.fetchone()[0]
    personale_id_map[src_id] = int(new_id)
    print(f"  INSERT personale: {cognome} {nome} -> {new_id}")

# ── 7. Presenze ──────────────────────────────────────────────────────────────
sc.execute("SELECT [Data],[Funzione],[Orario inizio],[Orario Fine],[Totale Ore],[Personale_ID],[Postazione] FROM Presenze")
presenze_src = sc.fetchall()

ok = skip = 0
for row in presenze_src:
    data, funzione, ora_i, ora_f, ore, pid_src, postazione = row

    pid_dst  = personale_id_map.get(pid_src)
    post_id  = postazioni_map.get(postazione)
    funz_id  = funzioni_map.get(funzione)

    if not pid_dst or not post_id or not funz_id or not campagna_2025_id:
        skip += 1
        print(f"  SKIP presenza: pid_src={pid_src} post={postazione} funz={funzione}")
        continue

    # Normalizza orari
    def fmt_time(t):
        if t is None: return '00:00'
        s = str(t).strip()
        if ':' in s: return s[:5]
        return '00:00'

    oi = fmt_time(ora_i)
    of = fmt_time(ora_f)

    # Normalizza data
    if hasattr(data, 'strftime'):
        data_str = data.strftime('%Y-%m-%d')
    else:
        data_str = str(data)[:10]

    try:
        dc.execute(
            "INSERT INTO presenze ([campagna_id],[personale_id],[postazione_id],[funzione_id],[data_servizio],[orario_inizio],[orario_fine],[ore_totali],[stato]) VALUES (?,?,?,?,?,?,?,?,?)",
            (campagna_2025_id, pid_dst, post_id, funz_id,
             data_str, oi, of, ore, 'confermato')
        )
        ok += 1
    except Exception as ex:
        skip += 1
        print(f"  ERR: {ex}")

dst.commit()
src.close()
dst.close()
print(f"\nMigrazione completata: {ok} presenze importate, {skip} saltate.")
