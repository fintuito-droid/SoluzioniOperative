const URL_PREFIX_1 =
  "https://protocollo.dipvvf.it/folium/visualizzaDocumento.do?cmd=visualizzaDoc&assegnato=";

const URL_PREFIX_2 =
  "https://protocollo.dipvvf.it/folium/visualizzaDocumento.do?cmd=visualizzaDoc&secureId=";

const tabTimers = new Map();

chrome.webNavigation.onCompleted.addListener(async (details) => {
  if (details.frameId !== 0) return;

  try {
    const tab = await chrome.tabs.get(details.tabId);
    const url = tab.url || "";

    if (
      !url.startsWith(URL_PREFIX_1) &&
      !url.startsWith(URL_PREFIX_2)
    ) {
      return;
    }

    if (tabTimers.has(details.tabId)) {
      clearTimeout(tabTimers.get(details.tabId));
    }

    const timer = setTimeout(async () => {
      try {
        await chrome.scripting.executeScript({
          target: { tabId: details.tabId },
          files: ["content-script.js"]
        });
      } catch (err) {
        console.error("Errore inject script:", err);
      }
    }, 2000);

    tabTimers.set(details.tabId, timer);
  } catch (err) {
    console.error("Errore monitoraggio tab:", err);
  }
}, {
  url: [{ hostEquals: "protocollo.dipvvf.it", pathPrefix: "/folium/visualizzaDocumento.do" }]
});

chrome.tabs.onRemoved.addListener((tabId) => {
  if (tabTimers.has(tabId)) {
    clearTimeout(tabTimers.get(tabId));
    tabTimers.delete(tabId);
  }
});

async function massimizzaFinestraDaTab(tabId) {
  try {
    const tab = await chrome.tabs.get(tabId);
    if (!tab || typeof tab.windowId !== "number") return;

    await chrome.windows.update(tab.windowId, {
      state: "maximized",
      focused: true
    });
  } catch (err) {
    console.error("Errore massimizzazione finestra:", err);
  }
}

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === "INVIA_HTML_A_FLASK") {
    fetch("http://127.0.0.1:5000/ricevi-html", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        url: message.url,
        html: message.html,
        flags: message.flags
      })
    })
      .then(async (r) => {
        const txt = await r.text();
        sendResponse({
          ok: true,
          status: r.status,
          body: txt
        });
      })
      .catch((err) => {
        sendResponse({
          ok: false,
          errore: String(err)
        });
      });

    return true;
  }

    if (message.type === "MASSIMIZZA_FINESTRA") {
    const tabId = sender?.tab?.id;

    if (typeof tabId !== "number") {
      sendResponse({ ok: false, errore: "Tab ID non disponibile" });
      return;
    }

    massimizzaFinestraDaTab(tabId)
      .then(() => sendResponse({ ok: true }))
      .catch((err) => sendResponse({ ok: false, errore: String(err) }));

    return true;
  }


});