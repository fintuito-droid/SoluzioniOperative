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
            dati.get("numero_protocollo", "SENZA_PROTOCOLLO")
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

import base64

def salva_documento_protocollato_base64(data, numero_protocollo):
    base64_file = data.get("DocumentoProtocollatoBase64")

    if not base64_file:
        print("Nessun DocumentoProtocollatoBase64 ricevuto")
        return None

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

    nome_file = f"{pulisci_nome_file(numero_protocollo)}_{data_file}_PROTOCOLLATO.pdf"
    percorso_file = os.path.join(cartella_destinazione, nome_file)

    contenuto = base64.b64decode(base64_file)

    with open(percorso_file, "wb") as f:
        f.write(contenuto)

    print("Documento protocollato salvato in:", percorso_file)

    return percorso_file


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