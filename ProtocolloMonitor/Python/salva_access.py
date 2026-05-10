import pyodbc
from datetime import datetime


DB_PATH = r"G:\ProtocolloMonitor.accdb"


def connessione_access():
    conn_str = (
        r"DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};"
        rf"DBQ={DB_PATH};"
    )
    return pyodbc.connect(conn_str)


def nz(v, default=None):
    if v is None:
        return default

    if isinstance(v, str):
        v = v.strip()
        if v == "":
            return default

    return v


def crea_chiave_univoca(dati: dict) -> str:
    numero = nz(dati.get("numero_protocollo"))
    data = nz(dati.get("data_protocollo"))
    return f"{numero}|{data}"


def cerca_id_protocollo(cursor, chiave_univoca: str):
    sql = "SELECT IDProtocollo FROM T_Protocolli WHERE ChiaveUnivoca = ?"
    row = cursor.execute(sql, chiave_univoca).fetchone()
    return row[0] if row else None


def inserisci_padre(cursor, dati: dict) -> int:
    chiave = crea_chiave_univoca(dati)
    da_lavorare = -1 if bool(dati.get("daLavorare", False)) else 0
    data_scadenza_raw = dati.get("dataScadenza")
    nz(dati.get("tipologia_documento"))

    if data_scadenza_raw:
        data_scadenza = datetime.strptime(data_scadenza_raw, "%Y-%m-%d")
    else:
        data_scadenza = None

  

    id_esistente = cerca_id_protocollo(cursor, chiave)
    if id_esistente:
        return int(id_esistente)

    sql = """
    INSERT INTO T_Protocolli
    (
        NumeroProtocollo,
        DataProtocollo,
        RegistroDescrizione,
        RegistroSigla,
        TitoloPagina,
        DataSpedizione,
        Oggetto,
        Modalita,
        DataDocumento,
        Operatore,
        LivelloRiservatezza,
        UrlSorgente,
        DataAcquisizione,
        ChiaveUnivoca,
        DaLavorare,
        dataScadenza,
        TipologiaDocumento,
        PercorsoDocumentoProtocollato
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    cursor.execute(
        sql,
        nz(dati.get("numero_protocollo")),
        nz(dati.get("data_protocollo")),
        nz(dati.get("registro_descrizione")),
        nz(dati.get("registro_sigla")),
        nz(dati.get("titolo_pagina")),
        nz(dati.get("data_spedizione")),
        nz(dati.get("oggetto")),
        nz(dati.get("modalita")),
        nz(dati.get("data_documento")),
        nz(dati.get("operatore")),
        nz(dati.get("livello_riservatezza")),
        nz(dati.get("url_sorgente")),
        datetime.now(),
        chiave,
        da_lavorare,
        data_scadenza,
        nz(dati.get("tipologia_documento")),
        nz(dati.get("percorsoDocumentoProtocollato"))
    )

    row = cursor.execute("SELECT @@IDENTITY").fetchone()
    return int(row[0])


def elimina_figli_esistenti(cursor, id_protocollo: int):
    cursor.execute("DELETE FROM T_ProtocolloDestinatari WHERE IDProtocollo = ?", id_protocollo)
    cursor.execute("DELETE FROM T_ProtocolloFirmatari WHERE IDProtocollo = ?", id_protocollo)
    cursor.execute("DELETE FROM T_ProtocolloAssegnazioni WHERE IDProtocollo = ?", id_protocollo)


def inserisci_destinatari(cursor, id_protocollo: int, destinatari: list):
    sql = """
    INSERT INTO T_ProtocolloDestinatari
    (
        IDProtocollo,
        Destinatario,
        Mezzo,
        Email,
        DataSpedizione,
        NumeroRaccomandata,
        DataConsegna,
        DatiAggiuntivi,
        StatoSpedizione
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    for d in destinatari:
        cursor.execute(
            sql,
            id_protocollo,
            nz(d.get("destinatario")),
            nz(d.get("mezzo")),
            nz(d.get("email")),
            nz(d.get("data_spedizione")),
            nz(d.get("numero_raccomandata")),
            nz(d.get("data_consegna")),
            nz(d.get("dati_aggiuntivi")),
            nz(d.get("stato_spedizione"))
        )


def inserisci_firmatari(cursor, id_protocollo: int, firmatari: list):
    sql = """
    INSERT INTO T_ProtocolloFirmatari
    (
        IDProtocollo,
        Nome,
        DataFirma,
        ValidaDal,
        SinoAl
    )
    VALUES (?, ?, ?, ?, ?)
    """

    for f in firmatari:
        cursor.execute(
            sql,
            id_protocollo,
            nz(f.get("nome")),
            nz(f.get("data_firma")),
            nz(f.get("valida_dal")),
            nz(f.get("sino_al"))
        )


def inserisci_assegnazioni(cursor, id_protocollo: int, assegnazioni: list):
    sql = """
    INSERT INTO T_ProtocolloAssegnazioni
    (
        IDProtocollo,
        Assegnatario,
        DOFlag,
        AssegnanteUfficio,
        Azione,
        DataInizio,
        NoteAssegnazione
    )
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """

    for a in assegnazioni:
        cursor.execute(
            sql,
            id_protocollo,
            nz(a.get("assegnatario")),
            nz(a.get("do")),
            nz(a.get("assegnante_ufficio")),
            nz(a.get("azione")),
            nz(a.get("data_inizio")),
            nz(a.get("note"))
        )


def salva_protocollo_access(dati: dict) -> int:
    conn = connessione_access()
    cursor = conn.cursor()

    try:
        id_protocollo = inserisci_padre(cursor, dati)

        elimina_figli_esistenti(cursor, id_protocollo)

        inserisci_destinatari(cursor, id_protocollo, dati.get("destinatari", []))
        inserisci_firmatari(cursor, id_protocollo, dati.get("firmatari", []))
        inserisci_assegnazioni(cursor, id_protocollo, dati.get("assegnazioni", []))

        conn.commit()
        return id_protocollo

    except Exception:
        conn.rollback()
        raise

    finally:
        cursor.close()
        conn.close()