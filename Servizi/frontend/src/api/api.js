/**
 * api.js — Layer di astrazione API
 * ==================================
 * Questo è l'UNICO file Vue da toccare per la migrazione.
 * Tutti i componenti e le store importano da qui.
 * La baseURL punta al FastAPI che parla con Access.
 * Quando si passa a PostgreSQL, FastAPI rimane identico:
 * si cambia solo database.py nel backend.
 *
 * Pattern: ogni funzione ritorna sempre { data, error }
 * in modo che i componenti non debbano gestire try/catch.
 */

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

// ── Token storage ─────────────────────────────────────────────────────────
// In produzione con CAS/JWT: sostituire con cookie httpOnly o sessionStorage
let _token = localStorage.getItem('aib_token') || null

export function setToken(token) {
  _token = token
  if (token) localStorage.setItem('aib_token', token)
  else localStorage.removeItem('aib_token')
}

export function getToken() { return _token }

// ── HTTP base ─────────────────────────────────────────────────────────────
async function request(method, path, body = null) {
  const headers = { 'Content-Type': 'application/json' }
  if (_token) headers['Authorization'] = `Bearer ${_token}`

  const opts = { method, headers }
  if (body) opts.body = JSON.stringify(body)

  try {
    const res = await fetch(`${BASE_URL}${path}`, opts)

    if (res.status === 401) {
      setToken(null)
      window.location.href = '/login'
      return { data: null, error: 'Non autenticato' }
    }

    const data = res.ok ? await res.json() : null
    const error = res.ok ? null : (await res.json())?.detail || `Errore ${res.status}`
    return { data, error, status: res.status }

  } catch (e) {
    return { data: null, error: 'Errore di rete: ' + e.message }
  }
}

const get    = (path)        => request('GET',    path)
const post   = (path, body)  => request('POST',   path, body)
const put    = (path, body)  => request('PUT',    path, body)
const patch  = (path, body)  => request('PATCH',  path, body)
const del    = (path)        => request('DELETE', path)


// ── Auth ──────────────────────────────────────────────────────────────────
export const authApi = {
  login:  (username, password) => post('/auth/login',  { username, password }),
  logout: ()                   => post('/auth/logout', {}),
  me:     ()                   => get('/auth/me'),
  cambiaPassword: (vecchia, nuova) =>
    post('/auth/cambia-password', { vecchia_password: vecchia, nuova_password: nuova }),
}

// ── Utenti (solo admin) ───────────────────────────────────────────────────
export const utentiApi = {
  lista:         ()           => get('/utenti'),
  crea:          (body)       => post('/utenti', body),
  aggiorna:      (id, body)   => put(`/utenti/${id}`, body),
  resetPassword: (id, password) => put(`/utenti/${id}/password`, { password }),
}


// ── Lookup (dati di configurazione) ──────────────────────────────────────
export const lookupApi = {
  postazioni:  () => get('/lookup/postazioni'),
  funzioni:    () => get('/lookup/funzioni'),
  campagne:    () => get('/lookup/campagne'),
  qualifiche:  () => get('/lookup/qualifiche'),
  comandi:     () => get('/lookup/comandi'),
  specialita:  () => get('/lookup/specialita'),

  creaPostazione:     (body)     => post('/lookup/postazioni',       body),
  aggiornaPostazione: (id, body) => put(`/lookup/postazioni/${id}`,  body),

  creaCampagna:       (body)     => post('/lookup/campagne',         body),
  aggiornaCampagna:   (id, body) => put(`/lookup/campagne/${id}`,    body),

  creaSpecialita:     (body)     => post('/lookup/specialita',       body),
  aggiornaSpecialita: (id, body) => put(`/lookup/specialita/${id}`,  body),
  eliminaSpecialita:  (id)       => del(`/lookup/specialita/${id}`),
}


// ── Personale ─────────────────────────────────────────────────────────────
export const personaleApi = {
  lista:            ()              => get('/personale'),
  get:              (id)            => get(`/personale/${id}`),
  crea:             (data)          => post('/personale',                  data),
  aggiorna:         (id, data)      => put(`/personale/${id}/anagrafica`,  data),
  aggiornaSpecialita: (id, ids)     => put(`/personale/${id}/specialita`,  ids),
  disattiva:        (id)            => del(`/personale/${id}`),
}


// ── Presenze ──────────────────────────────────────────────────────────────
export const presenzeApi = {
  /**
   * @param {Object} filtri - campagna_id, personale_id, data_da, data_a, stato, postazione_id
   */
  lista(filtri = {}) {
    const params = new URLSearchParams()
    Object.entries(filtri).forEach(([k, v]) => { if (v != null) params.set(k, v) })
    const qs = params.toString()
    return get(`/presenze${qs ? '?' + qs : ''}`)
  },

  get:         (id)        => get(`/presenze/${id}`),
  crea:        (data)      => post('/presenze',              data),
  consuntiva:  (id, data)  => patch(`/presenze/${id}/consuntivo`, data),
  elimina:     (id)        => del(`/presenze/${id}`),

  /**
   * Monte ore aggregato per dipendente
   * @param {Object} filtri - campagna_id, data_da, data_a
   */
  monteOre(filtri = {}) {
    const params = new URLSearchParams()
    // Supporta campagna_id, data_da, data_a, postazione_id
    Object.entries(filtri).forEach(([k, v]) => { if (v != null) params.set(k, v) })
    const qs = params.toString()
    return get(`/presenze/monte-ore${qs ? '?' + qs : ''}`)
  },

  batch: (items) => post('/presenze/batch', items),
}
