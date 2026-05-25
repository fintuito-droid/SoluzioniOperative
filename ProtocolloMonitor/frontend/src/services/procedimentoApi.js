const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

async function fetchJson(path) {
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

  return response.json()
}

export function listProcedimenti() {
  return fetchJson('/protocollo-monitor/procedimenti')
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
