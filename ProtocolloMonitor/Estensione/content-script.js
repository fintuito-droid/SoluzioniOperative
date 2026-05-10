// =====================================================
// ProtocolloMonitor - content-script.js
// Grisù v2 - Vue 3 + Vuetify + Chrome Extension
// =====================================================

if (window.__protocolloMonitorLoaded) {
  console.log("ProtocolloMonitor già avviato");
} else {
  window.__protocolloMonitorLoaded = true;

  console.log("ProtocolloMonitor - Grisù v2 avviato");

  const VALORI_TIPO_DOCUMENTO_UFFICIO_GARE = [
    "Preventivo",
    "POA",
    "VdC",
    "Ispezione",
    "Rendiconto",
    "Determina",
    "Contratto",
    "Consuntivo",
    "Richiesta preventivo"
  ];

  function inviaMessaggioRuntime(payload) {
    return new Promise((resolve) => {
      try {
        chrome.runtime.sendMessage(payload, (response) => {
          if (chrome.runtime.lastError) {
            console.error(
              "Errore chrome.runtime.sendMessage:",
              chrome.runtime.lastError.message
            );
            resolve(null);
            return;
          }

          resolve(response);
        });
      } catch (err) {
        console.error("Eccezione sendMessage:", err);
        resolve(null);
      }
    });
  }

  function normalizzaTesto(testo) {
    return (testo || "")
      .toString()
      .replace(/\s+/g, " ")
      .trim()
      .toUpperCase();
  }

  function paginaContieneUfficioGare() {
    const divAssegnazioni = document.getElementById("divAssegnazioni");
    if (!divAssegnazioni) return false;

    const righe = divAssegnazioni.querySelectorAll("table.griglia tr");

    for (const riga of righe) {
      const celle = riga.querySelectorAll("td.cella-griglia");
      if (celle.length === 0) continue;

      const assegnatario = normalizzaTesto(celle[0].innerText);

      if (assegnatario === "UFFICIO GARE") {
        return true;
      }
    }

    return false;
  }

function caricaGrisuV2() {

  setTimeout(() => {

    const iframe = document.createElement("iframe");

    iframe.id = "grisu-v2-frame";
    iframe.src = chrome.runtime.getURL("grisu-v2/dist/index.html");

    iframe.style.position = "fixed";
    iframe.style.top = "0";
    iframe.style.left = "0";
    iframe.style.width = "100vw";
    iframe.style.height = "360px";

    iframe.style.border = "none";
    iframe.style.background = "transparent";
    iframe.style.backgroundColor = "transparent";
    iframe.style.zIndex = "2147483647";
    iframe.style.overflow = "visible";
    iframe.style.pointerEvents = "auto";

    iframe.style.display = "block";
    iframe.style.margin = "0";
    iframe.style.padding = "0";

    document.body.appendChild(iframe);

    iframe.onload = function () {
      iframe.contentWindow.postMessage({
        source: "protocollo-monitor",
        type: "CONFIG_GRISU",
        mostraTipoDocumento: paginaContieneUfficioGare(),
        valoriTipoDocumento: VALORI_TIPO_DOCUMENTO_UFFICIO_GARE
      }, "*");
    };

  }, 500);

}

function estraiTokenDocumentoProtocollato() {
  const links = [...document.querySelectorAll("a")];

  const linkProtocollato = links.find(a =>
    (a.innerText || "").trim().toLowerCase() === "download documento protocollato"
  );

  if (!linkProtocollato) {
    return null;
  }

  const onclick = linkProtocollato.getAttribute("onclick") || "";

  const match = onclick.match(/downloadDoc\('([^']+)'\)/);

  return match ? match[1] : null;
}

  if (!window.__grisuV2Iniettato) {
    window.__grisuV2Iniettato = true;

    inviaMessaggioRuntime({ type: "MASSIMIZZA_FINESTRA" }).then(() => {
      caricaGrisuV2();
    });
  }

  window.addEventListener("message", async function (event) {
    if (!event.data) return;
    if (event.data.source !== "grisu-v2") return;
    if (event.data.type !== "ACQUISISCI_PROTOCOLLO") return;

    const tokenDocumentoProtocollato = estraiTokenDocumentoProtocollato();
    const sqiDownload = estraiSqiDownload();

    const documentoProtocollatoBase64 =
      await scaricaDocumentoProtocollatoBase64(
        tokenDocumentoProtocollato,
        sqiDownload
      );

    const payload = {
      TokenDocumentoProtocollato: tokenDocumentoProtocollato,
      SqiDownload: sqiDownload,
      DocumentoProtocollatoBase64: documentoProtocollatoBase64,
      NomeFileDocumentoProtocollato: "documento_protocollato.pdf",

      html: document.documentElement.outerHTML,
      url: window.location.href,

      daLavorare: event.data.dati.daLavorare,
      dataScadenza: event.data.dati.dataScadenza,
      tipoDocumento: event.data.dati.tipoDocumento
    };

    async function scaricaDocumentoProtocollatoBase64(tokenDocumentoProtocollato, sqiDownload) {
  if (!tokenDocumentoProtocollato || !sqiDownload) {
    return null;
  }

  const urlDownload =
    `/folium/docviewer?id=${tokenDocumentoProtocollato}&sqi=${sqiDownload}&download=true`;

  const response = await fetch(urlDownload, {
    credentials: "include"
  });

  if (!response.ok) {
    console.error("Errore download documento protocollato:", response.status);
    return null;
  }

  const blob = await response.blob();

  return await new Promise((resolve, reject) => {
    const reader = new FileReader();

    reader.onloadend = () => {
      const base64 = reader.result.split(",")[1];
      resolve(base64);
    };

    reader.onerror = reject;
    reader.readAsDataURL(blob);
  });
}

function estraiSqiDownload() {
  const html = document.documentElement.innerHTML;

  const match = html.match(/docviewer\?id='\s*\+\s*id\s*\+\s*'&sqi=([^&']+)&download=true/);

  return match ? match[1] : null;
}

    try {
      const response = await fetch("http://127.0.0.1:5000/ricevi-html", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(payload)
      });

      const testo = await response.text();
      console.log("Risposta Flask:", testo);

      chrome.runtime.sendMessage({
        type: "CHIUDI_SCHEDA_CORRENTE"
      });

    } catch (errore) {
      console.error("Errore invio Flask:", errore);
    }
  });
}