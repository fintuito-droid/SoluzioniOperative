from bs4 import BeautifulSoup
import html
import json
import re
from pathlib import Path


def pulisci_testo(s):
    if s is None:
        return ""
    s = html.unescape(str(s))
    s = s.replace("\xa0", " ")
    s = re.sub(r"\s+", " ", s).strip()
    return s


def testo_cella(td):
    if not td:
        return ""
    return pulisci_testo(td.get_text(" ", strip=True))


def estrai_token_download(onclick_value):
    if not onclick_value:
        return ""
    m = re.search(r"downloadDoc\('([^']+)'\)", onclick_value)
    return m.group(1) if m else ""


def cerca_valore_per_etichetta(soup, etichetta):
    for span in soup.find_all("span", class_="titolo-pagina"):
        testo = pulisci_testo(span.get_text(" ", strip=True))
        if testo.lower() == etichetta.lower():
            tr = span.find_parent("tr")
            if tr:
                tds = tr.find_all("td", recursive=False)
                if len(tds) >= 2:
                    return testo_cella(tds[1])
    return ""


def estrai_blocco_protocollo(soup):
    risultato = {
        "registro_descrizione": "",
        "registro_sigla": "",
        "numero_protocollo": "",
        "data_protocollo": ""
    }

    profilo = soup.find("div", id="profilo")
    if not profilo:
        return risultato

    testo = profilo.get_text("\n", strip=True)
    testo = pulisci_testo(testo)

    m = re.search(
        r"(REGISTRO\s+.+?)\s*\((.*?)\)\s*,\s*N\.(\d+).*?Data:\s*(\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2})",
        testo,
        re.IGNORECASE | re.DOTALL
    )
    if m:
        risultato["registro_descrizione"] = pulisci_testo(m.group(1))
        risultato["registro_sigla"] = pulisci_testo(m.group(2))
        risultato["numero_protocollo"] = pulisci_testo(m.group(3))
        risultato["data_protocollo"] = pulisci_testo(m.group(4))

    return risultato


def estrai_titolo_pagina_centrale(soup):
    td = soup.find("td", class_="titolo-pagina", align="center")
    return testo_cella(td)


def estrai_oggetto(soup):
    nodo = soup.find("label", id="bossiStyle")
    return testo_cella(nodo)


def estrai_destinatari(soup):
    risultati = []

    div = soup.find("div", id="divMittDest")
    if not div:
        return risultati

    table = div.find("table", class_="griglia")
    if not table:
        return risultati

    righe = table.find_all("tr")
    if len(righe) <= 1:
        return risultati

    for tr in righe[1:]:
        tds = tr.find_all("td", recursive=False)
        if len(tds) < 4:
            continue

        record = {
            "destinatario": testo_cella(tds[0]),
            "mezzo": testo_cella(tds[1]),
            "email": testo_cella(tds[2]),
            "data_spedizione": "",
            "numero_raccomandata": "",
            "data_consegna": "",
            "dati_aggiuntivi": "",
            "stato_spedizione": ""
        }

        tooltip = tds[3].find("span", class_="CellTooltip")
        if tooltip:
            tab_tooltip = tooltip.find("table", class_="griglia")
            if tab_tooltip:
                righe_tooltip = tab_tooltip.find_all("tr")
                if len(righe_tooltip) >= 2:
                    celle_dati = righe_tooltip[1].find_all("td")
                    if len(celle_dati) >= 5:
                        record["data_spedizione"] = testo_cella(celle_dati[0])
                        record["numero_raccomandata"] = testo_cella(celle_dati[1])
                        record["data_consegna"] = testo_cella(celle_dati[2])
                        record["dati_aggiuntivi"] = testo_cella(celle_dati[3])
                        record["stato_spedizione"] = testo_cella(celle_dati[4])

        risultati.append(record)

    return risultati


def estrai_firmatari(soup):
    risultati = []

    div = soup.find("div", id="divFirmatari")
    if not div:
        return risultati

    table = div.find("table", class_="griglia")
    if not table:
        return risultati

    righe = table.find_all("tr")
    if len(righe) <= 1:
        return risultati

    for tr in righe[1:]:
        tds = tr.find_all("td", recursive=False)
        if len(tds) < 4:
            continue

        risultati.append({
            "nome": testo_cella(tds[0]),
            "data_firma": testo_cella(tds[1]),
            "valida_dal": testo_cella(tds[2]),
            "sino_al": testo_cella(tds[3]),
        })

    return risultati


def estrai_assegnazioni(soup):
    risultati = []

    div = soup.find("div", id="divAssegnazioni")
    if not div:
        return risultati

    table = div.find("table", class_="griglia")
    if not table:
        return risultati

    righe = table.find_all("tr")
    if len(righe) <= 1:
        return risultati

    for tr in righe[1:]:
        tds = tr.find_all("td", recursive=False)
        if len(tds) < 6:
            continue

        risultati.append({
            "assegnatario": testo_cella(tds[0]),
            "do": testo_cella(tds[1]),
            "assegnante_ufficio": testo_cella(tds[2]),
            "azione": testo_cella(tds[3]),
            "data_inizio": testo_cella(tds[4]),
            "note": testo_cella(tds[5]),
        })

    return risultati


def estrai_download(soup):
    risultato = {
        "documento_originale_token": "",
        "documento_protocollato_token": "",
        "documento_originale_onclick": "",
        "documento_protocollato_onclick": ""
    }

    for a in soup.find_all("a"):
        testo = testo_cella(a)
        onclick = a.get("onclick", "")

        if "Download documento originale" in testo:
            risultato["documento_originale_onclick"] = onclick
            risultato["documento_originale_token"] = estrai_token_download(onclick)

        elif "Download documento protocollato" in testo:
            risultato["documento_protocollato_onclick"] = onclick
            risultato["documento_protocollato_token"] = estrai_token_download(onclick)

    return risultato


def estrai_iframe_documento(soup):
    iframe = soup.find("iframe", id="documento")
    if not iframe:
        return {"iframe_documento_src": ""}
    return {"iframe_documento_src": iframe.get("src", "")}


def estrai_dati_nodo(html_text):
    soup = BeautifulSoup(html_text, "html.parser")

    dati = {}

    dati.update(estrai_blocco_protocollo(soup))
    dati["titolo_pagina"] = estrai_titolo_pagina_centrale(soup)
    dati["data_spedizione"] = cerca_valore_per_etichetta(soup, "Data Spedizione:")
    dati["oggetto"] = estrai_oggetto(soup)
    dati["modalita"] = cerca_valore_per_etichetta(soup, "Modalità:")
    dati["data_documento"] = cerca_valore_per_etichetta(soup, "Data documento:")
    dati["operatore"] = cerca_valore_per_etichetta(soup, "Operatore:")
    dati["livello_riservatezza"] = cerca_valore_per_etichetta(soup, "Livello Riservatezza:")
    dati["destinatari"] = estrai_destinatari(soup)
    dati["firmatari"] = estrai_firmatari(soup)
    dati["assegnazioni"] = estrai_assegnazioni(soup)
    dati.update(estrai_download(soup))
    dati.update(estrai_iframe_documento(soup))

    return dati


if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parent.parent
    file_input = base_dir / "dati" / "pagina_protocollo.html"
    file_output = base_dir / "dati" / "ultimo_protocollo.json"

    if not file_input.exists():
        print(f"File non trovato: {file_input}")
        raise SystemExit(1)

    html_text = file_input.read_text(encoding="utf-8")
    dati = estrai_dati_nodo(html_text)

    file_output.write_text(
        json.dumps(dati, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    print("Estrazione completata.")
    print(f"Output scritto in: {file_output}")