from flask import Flask, request, jsonify
from flask_cors import CORS
from pathlib import Path
import json
import traceback
from datetime import datetime
import pyodbc
import os
import re
import requests
from datetime import datetime
import base64
import sys

from estrai_protocollo import estrai_dati_nodo
from salva_access import salva_protocollo_access

app = Flask(__name__)
CORS(app)

BASE_DIR = Path(__file__).resolve().parent.parent
DATI_DIR = BASE_DIR / "dati"
DATI_DIR.mkdir(exist_ok=True)

FILE_HTML = DATI_DIR / "pagina_protocollo.html"
FILE_JSON = DATI_DIR / "ultimo_protocollo.json"
FILE_LOG = DATI_DIR / "errore_server.txt"

DB_ACCESS = r"G:\ProtocolloMonitor.accdb"


def get_connessione_access():
    conn_str = (
        r"DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};"
        rf"DBQ={DB_ACCESS};"
    )
    return pyodbc.connect(conn_str)


def scrivi_log(testo):
    with open(FILE_LOG, "a", encoding="utf-8") as f:
        f.write("\n" + "=" * 80 + "\n")
        f.write(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + "\n")
        f.write(testo + "\n")


@app.route("/ricevi-html", methods=["POST"])
def ricevi_html():
    try:
        scrivi_log("Richiesta ricevuta")

        data = request.get_json(force=True)

        print("TokenDocumentoProtocollato:", data.get("TokenDocumentoProtocollato"))
        print("SqiDownload:", data.get("SqiDownload"))
        print("DocumentoProtocollatoBase64 presente:", bool(data.get("DocumentoProtocollatoBase64")))
        print("NomeFileDocumentoProtocollato:", data.get("NomeFileDocumentoProtocollato"))

        print("TokenDocumentoOriginale:", data.get("TokenDocumentoOriginale"))
        print("TokenDocumentoProtocollato:", data.get("TokenDocumentoProtocollato"))
        print("SqiDownload:", data.get("SqiDownload"))
# Download lato Python disattivato:
# il documento verrà ricevuto da Chrome in Base64.

        html = data.get("html", "")
        url = data.get("url", "")

        da_lavorare = bool(data.get("daLavorare", False))
        data_scadenza = data.get("dataScadenza")
        tipologia_documento = data.get("tipoDocumento")

        scrivi_log(f"URL: {url}")
        scrivi_log(f"Lunghezza HTML: {len(html)}")

        if not html.strip():
            scrivi_log("ERRORE: HTML vuoto")
            return jsonify({"ok": False, "errore": "HTML vuoto"}), 400

        FILE_HTML.write_text(html, encoding="utf-8")
        scrivi_log(f"HTML salvato in: {FILE_HTML}")

        dati = estrai_dati_nodo(html)

        percorso_protocollato = salva_documento_protocollato_base64(
            data,
            dati
        )

        dati["percorsoDocumentoProtocollato"] = percorso_protocollato
        dati["url_sorgente"] = url
        dati["daLavorare"] = da_lavorare
        dati["dataScadenza"] = data_scadenza
        dati["tipologia_documento"] = tipologia_documento

        scrivi_log(f"Oggetto: {dati.get('oggetto', '')}")
        scrivi_log(f"Modalita: {dati.get('modalita', '')}")
        scrivi_log(f"DaLavorare: {dati.get('daLavorare')}")
        scrivi_log(f"DataScadenza: {dati.get('dataScadenza')}")

        FILE_JSON.write_text(
            json.dumps(dati, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        scrivi_log(f"JSON salvato in: {FILE_JSON}")

        dati["tipologia_documento"] = tipologia_documento

        scrivi_log(f"TIPOLOGIA PRIMA DI ACCESS: {dati.get('tipologia_documento')}")

        id_protocollo = salva_protocollo_access(dati)

        scrivi_log(f"Salvato in Access. IDProtocollo = {id_protocollo}")

        return jsonify({
            "ok": True,
            "messaggio": "HTML ricevuto, dati estratti e salvati in Access",
            "oggetto": dati.get("oggetto", ""),
            "modalita": dati.get("modalita", ""),
            "file_json": str(FILE_JSON),
            "id_protocollo": id_protocollo
        })

    except Exception as e:
        dettaglio = traceback.format_exc()
        scrivi_log("=== ERRORE NEL SERVER ===")
        scrivi_log(str(e))
        scrivi_log(dettaglio)

        return jsonify({
            "ok": False,
            "errore": str(e),
            "dettaglio": dettaglio
        }), 500


@app.route("/liste/tipologia-documento", methods=["POST"])
def liste_tipologia_documento():

    try:
        data = request.get_json(force=True)
        titolo_pagina = data.get("titoloPagina", "").strip()

        conn = get_connessione_access()
        cur = conn.cursor()

        cur.execute("""
            SELECT IDModulo
            FROM L_ModuliApplicativi
            WHERE CodiceModulo='PROTOCOLLO_MONITOR'
        """)

        row = cur.fetchone()
        if not row:
            return jsonify({"success": True, "valori": []})

        id_modulo = row.IDModulo

        cur.execute("""
            SELECT IDAmbito, CodiceAmbito
            FROM L_AmbitiOperativi
            WHERE IDModulo=?
        """, (id_modulo,))

        id_ambito = None

        for r in cur.fetchall():
            if r.CodiceAmbito in titolo_pagina:
                id_ambito = r.IDAmbito
                break

        if not id_ambito:
            return jsonify({"success": True, "valori": []})

        cur.execute("""
            SELECT V.IDValore, V.DescrizioneValore
            FROM L_ListeContesto LC
            INNER JOIN L_ValoriLista V
                ON LC.IDLista = V.IDLista
            WHERE
                LC.IDModulo=?
                AND LC.IDAmbito=?
                AND LC.CodiceCampo='tipologia_documento'
                AND LC.Attiva=True
                AND V.Attivo=True
            ORDER BY V.[Ordine]
        """, (id_modulo, id_ambito))

        valori = []

        for r in cur.fetchall():
            valori.append({
                "idValore": r.IDValore,
                "descrizioneValore": r.DescrizioneValore
            })

        cur.close()
        conn.close()

        return jsonify({
            "success": True,
            "valori": valori
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "errore": str(e),
            "valori": []
        }), 500
def liste_tipologia_documento():

    try:
        data = request.get_json(force=True)
        titolo_pagina = data.get("titoloPagina", "").strip()

        scrivi_log("Richiesta lista tipologia documento")
        scrivi_log(f"TitoloPagina: {titolo_pagina}")

        sql = """
        SELECT
            L_ValoriLista.IDValore,
            L_ValoriLista.DescrizioneValore
        FROM
            ((L_ModuliApplicativi
            INNER JOIN L_AmbitiOperativi
                ON L_ModuliApplicativi.IDModulo = L_AmbitiOperativi.IDModulo)
            INNER JOIN L_ListeContesto
                ON L_AmbitiOperativi.IDAmbito = L_ListeContesto.IDAmbito)
            INNER JOIN L_ValoriLista
                ON L_ListeContesto.IDLista = L_ValoriLista.IDLista
        WHERE
            L_ModuliApplicativi.CodiceModulo='PROTOCOLLO_MONITOR'
            AND ?
                LIKE L_AmbitiOperativi.CodiceAmbito & '*'
            AND L_ListeContesto.CodiceCampo='tipologia_documento'
            AND L_ValoriLista.Attivo=True
        ORDER BY
            L_ValoriLista.[Ordine]
        """

        conn = get_connessione_access()
        cur = conn.cursor()

        cur.execute(sql, (titolo_pagina,))
        righe = cur.fetchall()

        valori = []

        for r in righe:
            valori.append({
                "idValore": r.IDValore,
                "descrizioneValore": r.DescrizioneValore
            })

        cur.close()
        conn.close()

        scrivi_log(f"Valori trovati: {len(valori)}")

        return jsonify({
            "success": True,
            "valori": valori
        })

    except Exception as e:

        dettaglio = traceback.format_exc()

        scrivi_log("ERRORE lista tipologia documento")
        scrivi_log(str(e))
        scrivi_log(dettaglio)

        return jsonify({
            "success": False,
            "errore": str(e),
            "valori": []
        }), 500
    
def pulisci_nome_file(testo):
    testo = str(testo)
    testo = re.sub(r'[\\/:*?"<>|]', "_", testo)
    return testo.strip()


def estrai_pdf_protocollato_base64(data):
    """
    Estrae i bytes del PDF protocollato dal payload ricevuto da Grisu.

    Cosa fa:
    legge la stessa chiave gia usata dal flusso esistente,
    `DocumentoProtocollatoBase64`, e la decodifica in bytes.

    Perche esiste:
    separa la responsabilita di decodifica dalla responsabilita di salvare il
    file. Questo rende testabile il primo pezzo del flusso senza FileServer,
    database o Service Layer.

    Parametri:
    - `data`: dizionario payload ricevuto da `/ricevi-html`.

    Valori restituiti:
    - bytes PDF quando la chiave Base64 e presente;
    - `None` quando la chiave non e presente o e vuota.

    Rischi evitati:
    - duplicare la lettura della chiave Base64;
    - mischiare parsing payload e scrittura filesystem;
    - accedere al database durante la sola decodifica.
    """

    base64_file = data.get("DocumentoProtocollatoBase64")

    if not base64_file:
        print("Nessun DocumentoProtocollatoBase64 ricevuto")
        return None

    try:
        return base64.b64decode(base64_file)
    except Exception as errore:
        scrivi_log("ERRORE decodifica DocumentoProtocollatoBase64")
        scrivi_log(str(errore))
        raise


def _normalizza_data_protocollo_per_storage(data_protocollo):
    """
    Converte la data protocollo mantenendo il fallback storico del server.

    La vecchia funzione usava la data corrente quando la data protocollo era
    assente o non interpretabile. `DocumentStorageService`, invece, per design
    usa `00000000` sui valori non validi. Per non cambiare i nomi file gia
    prodotti dal flusso Flask, qui normalizziamo prima la data e passiamo al
    service un oggetto `datetime` coerente con il comportamento precedente.
    """

    if not data_protocollo:
        return datetime.now()

    testo_data = str(data_protocollo)

    for formato in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
        try:
            return datetime.strptime(testo_data, formato)
        except ValueError:
            pass

    return datetime.now()


def costruisci_metadati_pdf_protocollo(dati):
    """
    Costruisce i metadati minimi necessari al salvataggio PDF.

    Cosa fa:
    recupera dal dizionario estratto dal protocollo i valori gia usati dalla
    vecchia funzione di salvataggio: modalita, comando, numero protocollo e
    data protocollo.

    Perche esiste:
    separa la costruzione dei metadati dalla scrittura del file. In questo modo
    il passaggio futuro a `PdfDocumentService.save_and_register_protocollo_pdf`
    potra riusare gli stessi dati senza duplicare logica.

    Parametri:
    - `dati`: dizionario prodotto da `estrai_dati_nodo(html)`.

    Valori restituiti:
    dizionario con:
    - `modalita`;
    - `comando`;
    - `numero_protocollo`;
    - `data_protocollo`;
    - `data_protocollo_storage`.

    Rischi evitati:
    - perdere il comando effettivo quando e disponibile nel payload/dati;
    - cambiare il fallback storico `DIR-SIC` quando il comando non esiste;
    - cambiare fallback e pulizia del numero protocollo;
    - rendere il salvataggio dipendente dal database.
    """

    modalita = str(dati.get("modalita", ""))
    comando = pulisci_nome_file(
        dati.get("comando_mittente")
        or dati.get("ComandoMittente")
        or dati.get("comando")
        or "DIR-SIC"
    )
    numero_protocollo = pulisci_nome_file(
        dati.get("numero_protocollo", "SENZA_PROTOCOLLO")
    )
    data_protocollo = dati.get("data_protocollo")

    return {
        "modalita": modalita,
        "comando": comando,
        "numero_protocollo": numero_protocollo,
        "data_protocollo": data_protocollo,
        "data_protocollo_storage": _normalizza_data_protocollo_per_storage(
            data_protocollo
        ),
    }


def _crea_document_storage_service():
    """
    Crea il `DocumentStorageService` reale senza cambiare avvio del runtime Flask.

    L'import resta locale per mantenere `server_protocollo.py` avviabile come
    script legacy dalla cartella `Python`, usando la stessa compatibilita gia
    introdotta nello Step 19.
    """

    _garantisci_backend_importabile()
    from backend.services.document_storage_service import DocumentStorageService

    return DocumentStorageService()


def _salva_pdf_con_document_storage_service(pdf_bytes, metadati, storage_service):
    """
    Salva il PDF tramite `DocumentStorageService` preservando il riuso file.

    La vecchia funzione non riscriveva il file se gia presente. Prima di
    chiamare `save_pdf`, quindi, calcoliamo path atteso con il service e
    restituiamo il path esistente quando il file e gia presente.
    """

    storage_dir = storage_service.build_storage_dir(
        metadati["data_protocollo_storage"]
    )
    filename = storage_service.build_filename(
        metadati["modalita"],
        metadati["comando"],
        metadati["numero_protocollo"],
        metadati["data_protocollo_storage"],
    )
    percorso_file = storage_dir / filename

    if percorso_file.exists():
        print("Documento gia esistente:")
        print(percorso_file)
        return str(percorso_file)

    percorso_salvato = storage_service.save_pdf(
        pdf_bytes,
        metadati["modalita"],
        metadati["comando"],
        metadati["numero_protocollo"],
        metadati["data_protocollo_storage"],
    )

    print("Nuovo documento salvato:")
    print(percorso_salvato)

    return str(percorso_salvato)


def salva_documento_protocollato_base64(data, dati_protocollo, storage_service=None):
    """
    Salva il PDF protocollato una sola volta.
    Se il file esiste gia, restituisce il percorso esistente.

    Step 20:
    la funzione mantiene il contratto storico, ma separa internamente:
    - decodifica Base64;
    - costruzione metadati;
    - salvataggio fisico tramite `DocumentStorageService`;
    - aggiornamento del dizionario `dati_protocollo`.

    Non chiama `PdfDocumentService.save_and_register_protocollo_pdf`, perche
    in questo punto del flusso `id_protocollo` non e ancora disponibile.
    """

    contenuto_pdf = estrai_pdf_protocollato_base64(data)

    if contenuto_pdf is None:
        return None

    metadati = costruisci_metadati_pdf_protocollo(dati_protocollo)

    if storage_service is None:
        storage_service = _crea_document_storage_service()

    percorso_file = _salva_pdf_con_document_storage_service(
        contenuto_pdf,
        metadati,
        storage_service,
    )

    dati_protocollo["percorsoDocumentoProtocollato"] = percorso_file

    scrivi_log(
        "Documento protocollato Base64 salvato tramite DocumentStorageService: "
        f"{percorso_file}"
    )

    return percorso_file


def _garantisci_backend_importabile():
    """
    Rende importabile il package backend quando il server Flask viene avviato
    dalla cartella Python.

    Il collegamento con `PdfDocumentService` deve restare minimale e
    reversibile. Per questo non spostiamo il runtime Flask dentro il package
    backend e non cambiamo il modo in cui `server_protocollo.py` viene avviato:
    aggiungiamo soltanto la root del progetto al `sys.path` quando serve
    istanziare il service.
    """

    base_dir = str(BASE_DIR)

    if base_dir not in sys.path:
        sys.path.insert(0, base_dir)


def salva_pdf_protocollo_con_service(
    id_protocollo,
    pdf_bytes,
    modalita,
    comando,
    numero_protocollo,
    data_protocollo,
    pdf_document_service=None,
):
    """
    Wrapper preparatorio per salvare e registrare il PDF tramite Service Layer.

    Cosa fa:
    istanzia `PdfDocumentService`, salvo fake/service iniettato dai test, e
    chiama `save_and_register_protocollo_pdf(...)`.

    Perche esiste:
    Step 19 prepara il punto di contatto tra il flusso reale Flask/Grisu e il
    nuovo backend layer senza sostituire subito il salvataggio esistente. Oggi
    `salva_documento_protocollato_base64(...)` salva gia il file prima che
    `salva_protocollo_access(dati)` restituisca `id_protocollo`; collegare qui
    il nuovo service in automatico rischierebbe un doppio salvataggio o un
    riordino invasivo dell'inserimento Access.

    Parametri:
    - `id_protocollo`: ID Access gia disponibile dopo `salva_protocollo_access`;
    - `pdf_bytes`: contenuto binario del PDF gia ottenuto dal flusso chiamante;
    - `modalita`, `comando`, `numero_protocollo`, `data_protocollo`: metadati
      necessari a `DocumentStorageService` per costruire path e nome file;
    - `pdf_document_service`: dipendenza opzionale per test/fake.

    Valori restituiti:
    dizionario applicativo prodotto da `PdfDocumentService` oppure esito
    fallito controllato in caso di eccezione.

    Punto futuro di collegamento:
    dopo `id_protocollo = salva_protocollo_access(dati)` in `ricevi_html`,
    quando si decidera di sostituire il vecchio salvataggio Base64 evitando
    duplicazioni e preservando il path scritto in Access.
    """

    try:
        if pdf_document_service is None:
            _garantisci_backend_importabile()
            from backend.services.pdf_document_service import PdfDocumentService

            pdf_document_service = PdfDocumentService()

        esito = pdf_document_service.save_and_register_protocollo_pdf(
            id_protocollo,
            pdf_bytes,
            modalita,
            comando,
            numero_protocollo,
            data_protocollo,
        )

        if esito.get("saved") and esito.get("registered"):
            scrivi_log(
                "PdfDocumentService: PDF salvato e path registrato. "
                f"IDProtocollo={id_protocollo}; path={esito.get('path')}"
            )
        else:
            scrivi_log(
                "PdfDocumentService: registrazione PDF non completata. "
                f"IDProtocollo={id_protocollo}; esito={esito}"
            )

        return esito

    except Exception as errore:
        dettaglio = traceback.format_exc()
        scrivi_log("PdfDocumentService: errore nel wrapper preparatorio")
        scrivi_log(str(errore))
        scrivi_log(dettaglio)

        return {
            "saved": False,
            "registered": False,
            "id_protocollo": id_protocollo,
            "path": None,
            "filename": None,
            "error": str(errore),
        }


def scarica_documenti_protocollo(data):
    token_originale = data.get("TokenDocumentoOriginale")
    token_protocollato = data.get("TokenDocumentoProtocollato")
    sqi = data.get("SqiDownload")

    numero_protocollo = data.get("NumeroProtocollo") or "SENZA_PROTOCOLLO"

    oggi = datetime.now()
    anno = oggi.strftime("%Y")
    mese = oggi.strftime("%m")
    data_file = oggi.strftime("%Y%m%d")

    cartella_destinazione = os.path.join(
        r"C:\Users\fintu\Documents\GitHub\SoluzioniOperative\ProtocolloMonitor\backend\FileServer",
        anno,
        mese
    )

    os.makedirs(cartella_destinazione, exist_ok=True)

    risultati = {
        "PercorsoDocumentoOriginale": None,
        "PercorsoDocumentoProtocollato": None
    }

    def scarica_singolo(token, tipo):
        if not token or not sqi:
            return None

        url_download = (
            "https://protocollo.dipvvf.it/folium/docviewer"
            f"?id={token}&sqi={sqi}&download=true"
        )

        nome_file = f"{pulisci_nome_file(numero_protocollo)}_{data_file}_{tipo}.pdf"
        percorso_file = os.path.join(cartella_destinazione, nome_file)

        response = requests.get(url_download, timeout=30)

        if response.status_code != 200:
            print(f"Errore download {tipo}: HTTP {response.status_code}")
            return None

        with open(percorso_file, "wb") as f:
            f.write(response.content)

        print(f"Documento {tipo} salvato in:", percorso_file)

        return percorso_file

    
    risultati["PercorsoDocumentoOriginale"] = scarica_singolo(
        token_originale,
        "ORIGINALE"
    )

    risultati["PercorsoDocumentoProtocollato"] = scarica_singolo(
        token_protocollato,
        "PROTOCOLLATO"
    )

    return risultati


@app.route("/ping", methods=["GET"])
def ping():
    return "OK"


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True, use_reloader=False)
