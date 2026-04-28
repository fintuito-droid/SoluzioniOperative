from flask import Flask, request, jsonify
from flask_cors import CORS
from pathlib import Path
import json
import traceback
from datetime import datetime

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
        html = data.get("html", "")
        url = data.get("url", "")
        flags = data.get("flags", {}) if data else {}

        da_lavorare = bool(flags.get("daLavorare", False))
        data_scadenza = flags.get("data")

        scrivi_log(f"URL: {url}")
        scrivi_log(f"Lunghezza HTML: {len(html)}")

        if not html.strip():
            scrivi_log("ERRORE: HTML vuoto")
            return jsonify({"ok": False, "errore": "HTML vuoto"}), 400

        FILE_HTML.write_text(html, encoding="utf-8")
        scrivi_log(f"HTML salvato in: {FILE_HTML}")

        dati = estrai_dati_nodo(html)
        dati["url_sorgente"] = url
        dati["daLavorare"] = da_lavorare
        dati["dataScadenza"] = data_scadenza


        scrivi_log(f"Oggetto: {dati.get('oggetto', '')}")
        scrivi_log(f"Modalita: {dati.get('modalita', '')}")
        scrivi_log(f"DaLavorare: {dati.get('daLavorare')}")
        scrivi_log(f"DataScadenza: {dati.get('dataScadenza')}")

        FILE_JSON.write_text(
            json.dumps(dati, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        scrivi_log(f"JSON salvato in: {FILE_JSON}")

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

@app.route("/ping", methods=["GET"])
def ping():
    return "OK"

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True, use_reloader=False)