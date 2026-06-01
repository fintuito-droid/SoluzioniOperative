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

export function getFaseWorkflow(idFase) {
  return fetchJson(`/protocollo-monitor/procedimenti/fasi/${idFase}`)
}

export function listSottofasiFase(idFase) {
  return fetchJson(`/protocollo-monitor/procedimenti/fasi/${idFase}/sottofasi`)
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
