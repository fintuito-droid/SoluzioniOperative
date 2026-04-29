(async function () {
  if (window.__protocolloAssistenteIniettato) return;
  window.__protocolloAssistenteIniettato = true;

  if (document.getElementById("grisu")) return;

  function inviaMessaggioRuntime(payload) {
    return new Promise((resolve) => {
      try {
        chrome.runtime.sendMessage(payload, (response) => {
          if (chrome.runtime.lastError) {
            console.error("Errore chrome.runtime.sendMessage:", chrome.runtime.lastError.message);
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

  async function chiudiFinestraAssistente() {
    const risposta = await inviaMessaggioRuntime({
      type: "CHIUDI_FINESTRA_ASSISTENTE"
    });

    if (!risposta || risposta.ok !== true) {
      try {
        window.close();
      } catch (err) {
        console.error("Impossibile chiudere la finestra con window.close():", err);
      }
    }
  }

  try {
    await inviaMessaggioRuntime({ type: "MASSIMIZZA_FINESTRA" });

    const htmlUrl = chrome.runtime.getURL("grisu_assistente_menu_operativo.html");
    const res = await fetch(htmlUrl);
    const htmlText = await res.text();

    const parser = new DOMParser();
    const doc = parser.parseFromString(htmlText, "text/html");

    const styleEl = doc.querySelector("style");
    if (styleEl && !document.getElementById("grisu-style-injected")) {
      const s = document.createElement("style");
      s.id = "grisu-style-injected";
      s.textContent = styleEl.textContent;
      document.head.appendChild(s);
    }

    const grisuNode = doc.getElementById("grisu");
    const overlayNode = doc.getElementById("overlay");

    if (!grisuNode || !overlayNode) {
      console.error("Assistente Grisù: nodi HTML non trovati.");
      return;
    }

    document.body.appendChild(document.importNode(grisuNode, true));
    document.body.appendChild(document.importNode(overlayNode, true));

    const grisu = document.getElementById("grisu");
    const grisuImg = document.getElementById("grisuImg");
    const overlay = document.getElementById("overlay");
    const trail = document.getElementById("trail");

    const chkScadenza = document.getElementById("chkScadenza");
    const chkLavorare = document.getElementById("chkLavorare");
    const dateWrap = document.getElementById("dateWrap");
    const dataScadenza = document.getElementById("dataScadenza");
    const boxTipoDocumento = document.getElementById("boxTipoDocumento");
    const tipoDocumento = document.getElementById("tipoDocumento");

    const acquisisciBtn = overlay.querySelector(".btn");
    const chiudiBtn = overlay.querySelector(".close-btn");

    if (
      !grisu || !grisuImg || !overlay || !trail ||
      !chkScadenza || !chkLavorare || !dateWrap || !dataScadenza ||
      !acquisisciBtn || !chiudiBtn
    ) {
      console.error("Assistente Grisù: elementi DOM mancanti dopo l'iniezione.");
      return;
    }

    acquisisciBtn.removeAttribute("onclick");
    chiudiBtn.removeAttribute("onclick");

    let isOpen = false;
    let isAnimating = false;
    let peekTimeout = null;
    let autoHideTimeout = null;
    let smokeInterval = null;
    let peekInterval = null;

    function setPeekImage() {
      grisuImg.src = chrome.runtime.getURL("grisu_piccolo.png");
      grisuImg.alt = "Grisù piccolo";
    }

    function setFlyImage() {
      grisuImg.src = chrome.runtime.getURL("grisu_fly.png");
      grisuImg.alt = "Grisù al top centro";
    }

    function peek() {
      if (isOpen || isAnimating) return;

      setPeekImage();
      grisu.classList.add("peek");

      clearTimeout(autoHideTimeout);
      autoHideTimeout = setTimeout(() => {
        if (!isOpen && !isAnimating) {
          grisu.classList.remove("peek");
        }
      }, 5000);
    }

    function scheduleFirstPeek() {
      clearTimeout(peekTimeout);
      peekTimeout = setTimeout(peek, 10);
    }

    function startSmoke() {
      trail.style.display = "block";

      clearInterval(smokeInterval);
      smokeInterval = setInterval(() => {
        const puff = document.createElement("div");
        puff.className = "smoke";
        puff.style.top = Math.random() * 20 + "px";
        trail.appendChild(puff);
        setTimeout(() => puff.remove(), 1000);
      }, 120);
    }

    function stopSmoke() {
      clearInterval(smokeInterval);
      smokeInterval = null;
      trail.style.display = "none";
      trail.innerHTML = "";
    }

    function aggiornaDataWrap() {
      if (chkScadenza.checked) {
        dateWrap.classList.add("show");
      } else {
        dateWrap.classList.remove("show");
        dataScadenza.value = "";
      }
    }

    function getTitoloPaginaFolium() {
      const el = document.querySelector(".titolo-pagina");
      return el ? el.textContent.trim() : document.title;
    }

    async function caricaTipologiaDocumento() {
      console.log("CHIAMO FLASK PER LISTA TIPO DOCUMENTO");

      if (!boxTipoDocumento || !tipoDocumento) {
        console.error("Elementi tipo documento non trovati nel popup.");
        return;
      }

      const titoloPagina = getTitoloPaginaFolium();
      console.log("TitoloPagina Folium:", titoloPagina);

      boxTipoDocumento.style.display = "none";
      tipoDocumento.innerHTML = '<option value="">Tipo documento</option>';

      try {
        const response = await fetch(
          "http://127.0.0.1:5000/liste/tipologia-documento",
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json"
            },
            body: JSON.stringify({
              titoloPagina: titoloPagina
            })
          }
        );

        console.log("Status risposta Flask:", response.status);

        const data = await response.json();
        console.log("Risposta lista tipologia documento:", data);

        if (!data.success || !data.valori || data.valori.length === 0) {
          return;
        }

        data.valori.forEach(v => {
          const op = document.createElement("option");
          op.value = v.idValore;
          op.textContent = v.descrizioneValore;
          tipoDocumento.appendChild(op);
        });

        boxTipoDocumento.style.display = "block";

      } catch (err) {
        console.error("Errore caricamento tipologie documento:", err);
      }
    }

    function openPopup() {
      isOpen = true;
      overlay.classList.add("show");
      overlay.setAttribute("aria-hidden", "false");

      caricaTipologiaDocumento();
    }

    function closePopup() {
      overlay.classList.remove("show");
      overlay.setAttribute("aria-hidden", "true");
      isOpen = false;
      isAnimating = false;
      stopSmoke();
      grisu.classList.remove("fly");
      setPeekImage();

      setTimeout(() => {
        grisu.classList.remove("peek");
      }, 50);
    }

    async function acquisisciDati() {
  const tipoDocumentoTesto =
    tipoDocumento && tipoDocumento.value
      ? tipoDocumento.options[tipoDocumento.selectedIndex].text.trim()
      : null;

    const payload = {
      daLavorare: chkLavorare.checked,
      scadenza: chkScadenza.checked,
      data: chkScadenza.checked ? (dataScadenza.value || null) : null,
      tipoDocumento: tipoDocumentoTesto
    };

  const htmlCorrente = document.documentElement.outerHTML;

  closePopup();

  await inviaMessaggioRuntime({
    type: "INVIA_HTML_A_FLASK",
    url: window.location.href,
    html: htmlCorrente,
    flags: payload
  });

  await chiudiFinestraAssistente();
}

    setPeekImage();
    aggiornaDataWrap();

    chkScadenza.addEventListener("change", aggiornaDataWrap);

    grisu.addEventListener("click", () => {
      if (isOpen || isAnimating) return;

      isAnimating = true;
      grisu.classList.remove("peek");
      clearTimeout(autoHideTimeout);

      startSmoke();
      setFlyImage();
      grisu.classList.add("fly");

      setTimeout(() => {
        stopSmoke();
        openPopup();
      }, 700);
    });

    acquisisciBtn.addEventListener("click", async (e) => {
      e.preventDefault();
      e.stopPropagation();
      await acquisisciDati();
    });

    chiudiBtn.addEventListener("click", async (e) => {
      e.preventDefault();
      e.stopPropagation();
      closePopup();
      await chiudiFinestraAssistente();
    });

    document.addEventListener("keydown", async (e) => {
      if (e.key === "Escape" && isOpen) {
        closePopup();
        await chiudiFinestraAssistente();
      }
    });

    scheduleFirstPeek();

    clearInterval(peekInterval);
    peekInterval = setInterval(peek, 10000);

    console.log("Assistente Grisù iniettato correttamente");
    console.log("Finestra richiesta a schermo intero. Lo scraping parte solo al click su 'Acquisisci'.");

  } catch (err) {
    console.error("Errore iniezione assistente:", err);
  }
})();