// stores/auth.js — Pinia store autenticazione
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi, setToken, getToken } from '@/api/api'

export const useAuthStore = defineStore('auth', () => {
  const user       = ref(null)   // { username, ruolo, personale_id }
  const token      = ref(getToken())
  const loading    = ref(false)
  const error      = ref(null)

  const isAuth          = computed(() => !!token.value)
  const isAdmin         = computed(() => user.value?.ruolo === 'admin')
  const isResponsabile  = computed(() => user.value?.ruolo === 'responsabile')
  const isDipendente    = computed(() => user.value?.ruolo === 'dipendente')
  const canPlanificare  = computed(() => isAdmin.value || isResponsabile.value)
  const canConsuntivare = computed(() => isAdmin.value || isResponsabile.value)

  async function login(username, password) {
    loading.value = true
    error.value   = null
    const { data, error: err } = await authApi.login(username, password)
    if (err) {
      error.value = err
    } else {
      token.value = data.access_token
      setToken(data.access_token)
      user.value = {
        username:    data.username,
        ruolo:       data.ruolo,
        personale_id: data.personale_id
      }
    }
    loading.value = false
    return !err
  }

  async function logout() {
    await authApi.logout()
    token.value = null
    user.value  = null
    setToken(null)
  }

  // Ripristina sessione da localStorage al mount dell'app
  function restoreSession(userData) {
    if (token.value && userData) user.value = userData
  }

  return { user, token, loading, error, isAuth, isAdmin, isResponsabile,
           isDipendente, canPlanificare, canConsuntivare, login, logout, restoreSession }
})
