import pyodbc
from datetime import datetime
import re


def estrai_comando_mittente(oggetto):
    """
    Estrae la sigla del comando mittente dall'oggetto.

    Esempio:
    Protocollo nr: 6629 - del 09/05/2026 - COM-AG - testo restante

    Risultato:
    COM-AG
    """

    if not oggetto:
        return None

    pattern = r"Protocollo\s+nr:\s*.*?\s*-\s*del\s+.*?\s*-\s*([A-Z]{2,5}-[A-Z]{2,5})\s*-"

    match = re.search(pattern, oggetto, re.IGNORECASE)

    if match:
        return match.group(1).upper().strip()

    return None


# ============================================================
# CONFIGURAZIONE DATABASE
# ============================================================

DB_PATH = r"G:\ProtocolloMonitor.accdb"

ID_UTENTE_CORRENTE = 1


# ============================================================
# CONNESSIONE ACCESS
# ============================================================

def connessione_access():
    conn_str = (
        r"DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};"
        rf"DBQ={DB_PATH};"
    )
    return pyodbc.connect(conn_str)


# ============================================================
# FUNZIONI DI UTILITÀ
# ============================================================

def nz(v, default=None):
    if v is None:
        return default

    if isinstance(v, str):
        v = v.strip()
        if v == "":
            return default

    return v


def normalizza_tipo_documento(dati: dict) -> str:
    modalita = str(nz(dati.get("modalita"), "")).upper()

    if "ENTRATA" in modalita:
        return "E"

    if "USCITA" in modalita:
        return "U"

    return "N"


def formatta_data_nome_file(data_protocollo) -> str:
    if data_protocollo is None:
        return datetime.now().strftime("%Y%m%d")

    if isinstance(data_protocollo, datetime):
        return data_protocollo.strftime("%Y%m%d")

    testo = str(data_protocollo).strip()

    for formato in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
        try:
            return datetime.strptime(testo, formato).strftime("%Y%m%d")
        except ValueError:
            pass

    return testo.replace("/", "").replace("-", "")


def crea_chiave_univoca(dati: dict) -> str:
    numero = nz(dati.get("numero_protocollo"))
    data = nz(dati.get("data_protocollo"))
    return f"{numero}|{data}"


def crea_chiave_documento(dati: dict) -> str:
    tipo = normalizza_tipo_documento(dati)
    comando = nz(dati.get("registro_sigla"), "ND")
    numero = nz(dati.get("numero_protocollo"), "SENZA-PROT")
    data = formatta_data_nome_file(nz(dati.get("data_protocollo")))

    return f"{tipo}_{comando}_{numero}_{data}"


def crea_nome_file_documento(dati: dict) -> str:
    return crea_chiave_documento(dati) + ".pdf"


# ============================================================
# GESTIONE T_PROTOCOLLI
# ============================================================

def cerca_id_protocollo(cursor, chiave_univoca: str):
    sql = "SELECT IDProtocollo FROM T_Protocolli WHERE ChiaveUnivoca = ?"
    row = cursor.execute(sql, chiave_univoca).fetchone()
    return row[0] if row else None


def inserisci_padre(cursor, dati: dict) -> int:
    chiave = crea_chiave_univoca(dati)

    da_lavorare = -1 if bool(dati.get("daLavorare", False)) else 0

    data_scadenza_raw = dati.get("dataScadenza")
    if data_scadenza_raw:
        data_scadenza = datetime.strptime(data_scadenza_raw, "%Y-%m-%d")
    else:
        data_scadenza = None

    oggetto = nz(dati.get("oggetto"))
    comando_mittente = estrai_comando_mittente(oggetto)

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
        ComandoMittente,
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
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    cursor.execute(
        sql,
        nz(dati.get("numero_protocollo")),
        nz(dati.get("data_protocollo")),
        nz(dati.get("registro_descrizione")),
        nz(dati.get("registro_sigla")),
        nz(dati.get("titolo_pagina")),
        nz(dati.get("data_spedizione")),
        oggetto,
        comando_mittente,
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


# ============================================================
# GESTIONE T_DOCUMENTI
# ============================================================

def cerca_id_documento(cursor, chiave_documento: str):
    sql = "SELECT id_documento FROM T_Documenti WHERE chiave_univoca = ?"
    row = cursor.execute(sql, chiave_documento).fetchone()
    return int(row[0]) if row else None


def inserisci_o_recupera_documento(cursor, dati: dict) -> int:
    chiave_documento = crea_chiave_documento(dati)

    id_esistente = cerca_id_documento(cursor, chiave_documento)
    if id_esistente:
        return id_esistente

    tipo = normalizza_tipo_documento(dati)
    nome_file = crea_nome_file_documento(dati)

    sql = """
    INSERT INTO T_Documenti
    (
        tipo,
        comando_vigilia,
        numero_protocollo,
        data_protocollo,
        nome_file,
        percorso_file,
        chiave_univoca,
        data_acquisizione
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """

    cursor.execute(
        sql,
        tipo,
        nz(dati.get("registro_sigla")),
        nz(dati.get("numero_protocollo")),
        nz(dati.get("data_protocollo")),
        nome_file,
        nz(dati.get("percorsoDocumentoProtocollato")),
        chiave_documento,
        datetime.now()
    )

    row = cursor.execute("SELECT @@IDENTITY").fetchone()
    return int(row[0])


# ============================================================
# GESTIONE T_DOCUMENTIACCESSI
# ============================================================

def accesso_documento_esiste(cursor, id_documento: int, id_utente: int) -> bool:
    sql = """
    SELECT id_accesso
    FROM T_DocumentiAccessi
    WHERE id_documento = ?
      AND id_utente = ?
      AND attivo = True
    """

    row = cursor.execute(sql, id_documento, id_utente).fetchone()
    return row is not None


def inserisci_accesso_documento_da_vigilia(cursor, id_documento: int, id_utente: int):
    if accesso_documento_esiste(cursor, id_documento, id_utente):
        return

    sql = """
    INSERT INTO T_DocumentiAccessi
    (
        id_documento,
        id_utente,
        fonte_accesso,
        id_utente_condivisione,
        data_accesso,
        permesso,
        attivo
    )
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """

    cursor.execute(
        sql,
        id_documento,
        id_utente,
        "VIGILIA",
        None,
        datetime.now(),
        "LETTURA",
        True
    )


# ============================================================
# TABELLE FIGLIE
# ============================================================

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


# ============================================================
# FUNZIONE PRINCIPALE
# ============================================================

def salva_protocollo_access(dati: dict) -> int:
    conn = connessione_access()
    cursor = conn.cursor()

    try:
        id_protocollo = inserisci_padre(cursor, dati)

        elimina_figli_esistenti(cursor, id_protocollo)

        inserisci_destinatari(cursor, id_protocollo, dati.get("destinatari", []))
        inserisci_firmatari(cursor, id_protocollo, dati.get("firmatari", []))
        inserisci_assegnazioni(cursor, id_protocollo, dati.get("assegnazioni", []))

        id_documento = inserisci_o_recupera_documento(cursor, dati)

        inserisci_accesso_documento_da_vigilia(
            cursor,
            id_documento,
            ID_UTENTE_CORRENTE
        )

        conn.commit()

        return id_protocollo

    except Exception:
        conn.rollback()
        raise

    finally:
        cursor.close()
        conn.close()