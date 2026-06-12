// stores/auth.js — Pinia store autenticazione
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi, setToken, getToken } from '@/api/api'

const USER_KEY = 'so_user'

function loadStoredUser() {
  try { return JSON.parse(localStorage.getItem(USER_KEY)) || null }
  catch { return null }
}

export const useAuthStore = defineStore('auth', () => {
  const user       = ref(loadStoredUser())   // { username, ruolo, personale_id }
  const token      = ref(getToken())
  const loading    = ref(false)
  const error      = ref(null)

  const isAuth          = computed(() => !!token.value)
  const isAdmin         = computed(() => user.value?.ruolo === 'admin')
  const isResponsabile  = computed(() => user.value?.ruolo === 'responsabile')
  const isDipendente    = computed(() => user.value?.ruolo === 'dipendente')
  const canPlanificare  = computed(() => isAdmin.value || isResponsabile.value)
  const canConsuntivare = computed(() => isAdmin.value || isResponsabile.value)

  /** True se l'utente è abilitato al modulo (gli admin lo sono sempre). */
  function hasModulo(codice) {
    if (isAdmin.value) return true
    const m = user.value?.moduli
    return Array.isArray(m) && m.includes(codice)
  }

  function _setUser(u) {
    user.value = u
    if (u) localStorage.setItem(USER_KEY, JSON.stringify(u))
    else   localStorage.removeItem(USER_KEY)
  }

  async function login(username, password) {
    loading.value = true
    error.value   = null
    const { data, error: err } = await authApi.login(username, password)
    if (err) {
      error.value = err
    } else {
      token.value = data.access_token
      setToken(data.access_token)
      _setUser({
        username:     data.username,
        ruolo:        data.ruolo,
        personale_id: data.personale_id,
        moduli:       data.moduli || [],
      })
    }
    loading.value = false
    return !err
  }

  async function logout() {
    await authApi.logout()
    token.value = null
    _setUser(null)
    setToken(null)
  }

  /**
   * Valida la sessione salvata all'avvio dell'app (F5 / riapertura browser).
   * Se il token è scaduto o invalido, pulisce lo stato locale:
   * il guard del router rimanda al login.
   */
  async function verificaSessione() {
    if (!token.value) return false
    const { data, error: err } = await authApi.me()
    if (err || !data) {
      token.value = null
      _setUser(null)
      setToken(null)
      return false
    }
    _setUser(data)   // dati freschi dal server (ruolo aggiornato)
    return true
  }

  return { user, token, loading, error, isAuth, isAdmin, isResponsabile,
           isDipendente, canPlanificare, canConsuntivare, hasModulo,
           login, logout, verificaSessione }
})
