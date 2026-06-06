const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'
const WORD_HELPER_BASE_URL =
  import.meta.env.VITE_WORD_HELPER_BASE_URL || 'http://127.0.0.1:8020'

async function fetchJson(path, options = {}) {
  const isFormData = options.body instanceof FormData
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      ...(!isFormData && options.body ? { 'Content-Type': 'application/json' } : {}),
      ...(options.headers || {})
    }
  })

  if (!response.ok) {
    const error = new Error(`Errore HTTP ${response.status}`)
    error.status = response.status

    try {
      error.payload = await response.json()
    } catch {
      error.payload = null
    }

    throw error
  }

  return response.json()
}

async function fetchBlob(path) {
  const response = await fetch(`${API_BASE_URL}${path}`)

  if (!response.ok) {
    const error = new Error(`Errore HTTP ${response.status}`)
    error.status = response.status

    try {
      error.payload = await response.json()
    } catch {
      error.payload = null
    }

    throw error
  }

  return response.blob()
}

export function listProcedimenti() {
  return fetchJson('/protocollo-monitor/procedimenti')
}

export function listProtocolli() {
  return fetchJson('/protocollo-monitor/protocolli')
}

export function apriPdfProtocolloEsterno(idProtocollo) {
  return fetchJson(`/protocollo-monitor/protocolli/${idProtocollo}/apri-pdf`)
}

export function createProcedimento(payload) {
  return fetchJson('/protocollo-monitor/procedimenti', {
    method: 'POST',
    body: JSON.stringify(payload || {})
  })
}

export function getProcedimento(idProcedimento) {
  return fetchJson(`/protocollo-monitor/procedimenti/${idProcedimento}`)
}

export function listProtocolliProcedimento(idProcedimento) {
  return fetchJson(`/protocollo-monitor/procedimenti/${idProcedimento}/protocolli`)
}

export function countProtocolliProcedimento(idProcedimento) {
  return fetchJson(`/protocollo-monitor/procedimenti/${idProcedimento}/protocolli/count`)
}

export function listProcedimentiByProtocollo(idProtocollo) {
  return fetchJson(`/protocollo-monitor/protocolli/${idProtocollo}/procedimenti`)
}

export function linkProtocolloToProcedimento(idProtocollo, idProcedimento, payload) {
  return fetchJson(
    `/protocollo-monitor/protocolli/${idProtocollo}/procedimenti/${idProcedimento}`,
    {
      method: 'POST',
      body: JSON.stringify(payload || {})
    }
  )
}

export function listFasiProcedimento(idProcedimento) {
  return fetchJson(`/protocollo-monitor/procedimenti/${idProcedimento}/fasi`)
}

export function createFaseProcedimento(idProcedimento, payload) {
  return fetchJson(`/protocollo-monitor/procedimenti/${idProcedimento}/fasi`, {
    method: 'POST',
    body: JSON.stringify(payload || {})
  })
}

export function updateFaseProcedimento(idProcedimento, idFase, payload) {
  return fetchJson(
    `/protocollo-monitor/procedimenti/${idProcedimento}/fasi/${idFase}`,
    {
      method: 'PUT',
      body: JSON.stringify(payload || {})
    }
  )
}

export function getFaseWorkflow(idFase) {
  return fetchJson(`/protocollo-monitor/procedimenti/fasi/${idFase}`)
}

export function listSottofasiFase(idFase) {
  return fetchJson(`/protocollo-monitor/procedimenti/fasi/${idFase}/sottofasi`)
}

export function listStepOrizzontaliFase(idProcedimento, idFase) {
  return fetchJson(
    `/protocollo-monitor/procedimenti/${idProcedimento}/fasi/${idFase}/step-orizzontali`
  )
}

export function inizializzaStepOrizzontaliFase(idProcedimento, idFase) {
  return fetchJson(
    `/protocollo-monitor/procedimenti/${idProcedimento}/fasi/${idFase}/step-orizzontali/inizializza`,
    { method: 'POST' }
  )
}

export function configuraStepOrizzontaliIstanzaFine(idProcedimento, idFase) {
  return fetchJson(
    `/protocollo-monitor/procedimenti/${idProcedimento}/fasi/${idFase}/step-orizzontali/configura-istanza-fine`,
    { method: 'POST' }
  )
}

export function configuraStepOrizzontaliPredefinito(idProcedimento, idFase) {
  return fetchJson(
    `/protocollo-monitor/procedimenti/${idProcedimento}/fasi/${idFase}/step-orizzontali/configura-predefinito`,
    { method: 'POST' }
  )
}

export function inserisciStepOrizzontaleDopo(
  idProcedimento,
  idFase,
  idStep,
  payload
) {
  return fetchJson(
    `/protocollo-monitor/procedimenti/${idProcedimento}/fasi/${idFase}/step-orizzontali/${idStep}/inserisci-dopo`,
    {
      method: 'POST',
      body: JSON.stringify(payload || {})
    }
  )
}

export function eliminaStepOrizzontale(idProcedimento, idFase, idStep) {
  return fetchJson(
    `/protocollo-monitor/procedimenti/${idProcedimento}/fasi/${idFase}/step-orizzontali/${idStep}`,
    { method: 'DELETE' }
  )
}

export function collegaProtocolloStepIstanza(idProcedimento, idFase, idStep, payload) {
  return fetchJson(
    `/protocollo-monitor/procedimenti/${idProcedimento}/fasi/${idFase}/step-orizzontali/${idStep}/collega-protocollo`,
    {
      method: 'POST',
      body: JSON.stringify(payload || {})
    }
  )
}

export function avviaStepRedigi(idProcedimento, idFase, idStep) {
  return fetchJson(
    `/protocollo-monitor/procedimenti/${idProcedimento}/fasi/${idFase}/step-orizzontali/${idStep}/avvia`,
    { method: 'POST' }
  )
}

export function completaStepRedigi(idProcedimento, idFase, idStep) {
  return fetchJson(
    `/protocollo-monitor/procedimenti/${idProcedimento}/fasi/${idFase}/step-orizzontali/${idStep}/completa`,
    { method: 'POST' }
  )
}

export function salvaNoteStepRedigi(idProcedimento, idFase, idStep, payload) {
  return fetchJson(
    `/protocollo-monitor/procedimenti/${idProcedimento}/fasi/${idFase}/step-orizzontali/${idStep}/note-operative`,
    {
      method: 'PUT',
      body: JSON.stringify(payload || {})
    }
  )
}

export function listCatalogoSottofasi(attivoOnly = true) {
  const params = new URLSearchParams({
    attivo_only: String(attivoOnly)
  })

  return fetchJson(`/protocollo-monitor/catalogo-sottofasi?${params.toString()}`)
}

export function getSottofaseDocumentale(idSottofase) {
  return fetchJson(`/protocollo-monitor/sottofasi/${idSottofase}/documentale`)
}

export function listDocumentiSottofase(idSottofase) {
  return fetchJson(`/protocollo-monitor/sottofasi/${idSottofase}/documenti`)
}

export function getDocumentoPrincipaleSottofase(idSottofase) {
  return fetchJson(`/protocollo-monitor/sottofasi/${idSottofase}/documento-principale`)
}

export function createDocumentoPrincipaleSottofase(idSottofase) {
  return fetchJson(`/protocollo-monitor/sottofasi/${idSottofase}/documento-principale`, {
    method: 'POST'
  })
}

export function updateDocumentoPrincipaleMetadatiSottofase(idSottofase, payload) {
  return fetchJson(
    `/protocollo-monitor/sottofasi/${idSottofase}/documento-principale/metadati`,
    {
      method: 'PUT',
      body: JSON.stringify(payload || {})
    }
  )
}

export function getWorkflowDocumentaleSottofase(idSottofase) {
  return fetchJson(`/protocollo-monitor/sottofasi/${idSottofase}/workflow-documentale`)
}

export function creaBozzaDocumentoPrincipale(idSottofase, payload) {
  return fetchJson(`/protocollo-monitor/sottofasi/${idSottofase}/workflow-documentale/bozza`, {
    method: 'POST',
    body: JSON.stringify(payload || {})
  })
}

export function eseguiAzioneWorkflowDocumentale(idSottofase, idDocumento, payload) {
  return fetchJson(
    `/protocollo-monitor/sottofasi/${idSottofase}/workflow-documentale/${idDocumento}/azione`,
    {
      method: 'POST',
      body: JSON.stringify(payload || {})
    }
  )
}

export function listAllegatiSottofase(idSottofase) {
  return fetchJson(`/protocollo-monitor/sottofasi/${idSottofase}/allegati`)
}

export function getAllegatiEliminati(idSottofase) {
  return fetchJson(`/protocollo-monitor/sottofasi/${idSottofase}/allegati/eliminati`)
}

export function collegaProtocolloAllegatoSottofase(idSottofase, payload) {
  return fetchJson(`/protocollo-monitor/sottofasi/${idSottofase}/allegati/protocollo`, {
    method: 'POST',
    body: JSON.stringify(payload || {})
  })
}

export function uploadAllegatoFileSottofase(idSottofase, file) {
  const formData = new FormData()
  formData.append('file', file)

  return fetchJson(`/protocollo-monitor/sottofasi/${idSottofase}/allegati/upload`, {
    method: 'POST',
    body: formData
  })
}

export function eliminaAllegatoSottofase(idSottofase, idDocumento, payload) {
  return fetchJson(
    `/protocollo-monitor/sottofasi/${idSottofase}/allegati/${idDocumento}/elimina`,
    {
      method: 'POST',
      body: JSON.stringify(payload || {})
    }
  )
}

export function ripristinaAllegatoSottofase(idSottofase, idDocumento, payload) {
  return fetchJson(
    `/protocollo-monitor/sottofasi/${idSottofase}/allegati/${idDocumento}/ripristina`,
    {
      method: 'POST',
      body: JSON.stringify(payload || {})
    }
  )
}

export function listStepOperativiSottofase(idSottofase) {
  return fetchJson(`/protocollo-monitor/sottofasi/${idSottofase}/step-operativi`)
}

export function listPartecipantiStepSottofase(idSottofase, idStep) {
  return fetchJson(
    `/protocollo-monitor/sottofasi/${idSottofase}/step-operativi/${idStep}/partecipanti`
  )
}

export function completaPartecipanteStepSottofase(
  idSottofase,
  idStep,
  idPartecipante
) {
  return fetchJson(
    `/protocollo-monitor/sottofasi/${idSottofase}/step/${idStep}/partecipanti/${idPartecipante}/completa`,
    { method: 'POST' }
  )
}

export function apriDocumentoSottofase(idDocumento) {
  return fetchBlob(`/protocollo-monitor/sottofase-documenti/${idDocumento}/apri`)
}

export function scaricaDocumentoSottofase(idDocumento) {
  return fetchBlob(`/protocollo-monitor/sottofase-documenti/${idDocumento}/scarica`)
}

export async function apriDocumentoConWord(idDocumento) {
  let response

  try {
    response = await fetch(`${WORD_HELPER_BASE_URL}/open-word`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ idDocumento })
    })
  } catch (error) {
    const helperError = new Error('Helper locale Word non raggiungibile')
    helperError.status = 0
    helperError.cause = error
    throw helperError
  }

  if (!response.ok) {
    const error = new Error(`Errore helper Word ${response.status}`)
    error.status = response.status

    try {
      error.payload = await response.json()
    } catch {
      error.payload = null
    }

    throw error
  }

  return response.json()
}

export function getWorkflowSottofase(idSottofase) {
  return fetchJson(`/protocollo-monitor/sottofasi/${idSottofase}/workflow`)
}

export function eseguiAzioneWorkflowSottofase(idSottofase, payload) {
  return fetchJson(
    `/protocollo-monitor/sottofasi/${idSottofase}/workflow/azioni`,
    {
      method: 'POST',
      body: JSON.stringify(payload || {})
    }
  )
}

export function caricaDocumentoWordSottofase(idSottofase, file, utenteOperatore) {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('utenteOperatore', utenteOperatore || '')

  return fetchJson(
    `/protocollo-monitor/sottofasi/${idSottofase}/documenti`,
    {
      method: 'POST',
      body: formData
    }
  )
}
