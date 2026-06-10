// stores/presenze.js — Pinia store presenze AIB
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { presenzeApi, lookupApi } from '@/api/api'

export const usePresenzeStore = defineStore('presenze', () => {
  // ── Stato ────────────────────────────────────────────────────────────────
  const presenze     = ref([])
  const monteOre     = ref([])
  const postazioni   = ref([])
  const funzioni     = ref([])
  const campagne     = ref([])
  const qualifiche   = ref([])
  const comandi      = ref([])
  const loading      = ref(false)
  const error        = ref(null)

  const campagnaAttiva = computed(() =>
    campagne.value.find(c => c.attiva) || campagne.value[0] || null
  )

  // ── Lookup ───────────────────────────────────────────────────────────────
  async function caricaLookup() {
    const [po, fu, ca, qu, co] = await Promise.all([
      lookupApi.postazioni(),
      lookupApi.funzioni(),
      lookupApi.campagne(),
      lookupApi.qualifiche(),
      lookupApi.comandi(),
    ])
    if (po.data) postazioni.value = po.data
    if (fu.data) funzioni.value   = fu.data
    if (ca.data) campagne.value   = ca.data
    if (qu.data) qualifiche.value = qu.data
    if (co.data) comandi.value    = co.data
  }

  // ── Presenze ─────────────────────────────────────────────────────────────
  async function caricaPresenze(filtri = {}) {
    loading.value = true
    error.value   = null
    // Inietta campagna attiva se non specificata
    if (!filtri.campagna_id && campagnaAttiva.value) {
      filtri = { campagna_id: campagnaAttiva.value.id, ...filtri }
    }
    const { data, error: err } = await presenzeApi.lista(filtri)
    if (err) error.value = err
    else presenze.value = data || []
    loading.value = false
  }

  async function creaPresenza(data) {
    const { data: nuova, error: err } = await presenzeApi.crea(data)
    if (!err && nuova) presenze.value.push(nuova)
    return { data: nuova, error: err }
  }

  async function consuntivaPresenza(id, data) {
    const { data: aggiornata, error: err } = await presenzeApi.consuntiva(id, data)
    if (!err && aggiornata) {
      const idx = presenze.value.findIndex(p => p.id === id)
      if (idx >= 0) presenze.value[idx] = aggiornata
    }
    return { data: aggiornata, error: err }
  }

  async function eliminaPresenza(id) {
    const { error: err } = await presenzeApi.elimina(id)
    if (!err) presenze.value = presenze.value.filter(p => p.id !== id)
    return { error: err }
  }

  async function creaPresenzeGiorno(items) {
    const { data, error: err } = await presenzeApi.batch(items)
    if (!err && data) presenze.value.push(...data)
    return { data, error: err }
  }

  // ── Monte ore ─────────────────────────────────────────────────────────────
  async function caricaMonteOre(filtri = {}) {
    loading.value = true
    if (filtri.campagna_id === undefined && campagnaAttiva.value) {
      filtri = { campagna_id: campagnaAttiva.value.id, ...filtri }
    }
    const { data, error: err } = await presenzeApi.monteOre(filtri)
    if (!err) monteOre.value = data || []
    loading.value = false
  }

  // ── Postazioni (gestione admin) ──────────────────────────────────────────
  async function creaPostazione(body) {
    const { data, error: err } = await lookupApi.creaPostazione(body)
    if (!err && data) postazioni.value.push(data)
    return { data, error: err }
  }

  async function aggiornaPostazione(id, body) {
    const { data, error: err } = await lookupApi.aggiornaPostazione(id, body)
    if (!err && data) {
      const idx = postazioni.value.findIndex(p => p.id === id)
      if (idx >= 0) postazioni.value[idx] = data
    }
    return { data, error: err }
  }

  return {
    presenze, monteOre, postazioni, funzioni, campagne, qualifiche, comandi,
    loading, error, campagnaAttiva,
    caricaLookup, caricaPresenze, creaPresenza, consuntivaPresenza, eliminaPresenza,
    caricaMonteOre, creaPostazione, aggiornaPostazione, creaPresenzeGiorno
  }
})
