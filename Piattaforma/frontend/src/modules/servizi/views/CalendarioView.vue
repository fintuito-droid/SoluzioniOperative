<template>
  <div>
    <!-- Intestazione -->
    <div class="d-flex align-center mb-4 flex-wrap gap-2">
      <div>
        <h1 class="text-h5 font-weight-medium">Calendario</h1>
        <p class="text-caption text-medium-emphasis mb-0">
          Campagna AIB {{ store.campagnaAttiva?.anno }}
        </p>
      </div>
    </div>

    <!-- Filtri + navigazione mese -->
    <v-card class="mb-4" variant="outlined">
      <v-card-text>
        <v-row dense align="center">
          <v-col cols="12" sm="5" md="4">
            <v-select
              v-model="filtroPostazione"
              :items="store.postazioni"
              item-title="codice"
              item-value="id"
              label="Postazione"
              clearable
              density="compact"
              hide-details
              @update:model-value="onCambioPostazione"
            />
          </v-col>
          <v-spacer/>
          <v-col v-if="filtroPostazione" cols="auto" class="d-flex align-center gap-1">
            <v-btn icon="mdi-chevron-left" variant="text" density="comfortable" @click="mesePrecedente"/>
            <span class="text-subtitle-1 font-weight-medium px-2 nav-mese-label">
              {{ nomeMese }} {{ annoVis }}
            </span>
            <v-btn icon="mdi-chevron-right" variant="text" density="comfortable" @click="meseSuccessivo"/>
            <v-btn variant="tonal" size="small" class="ml-2" @click="vaiAdOggi">Oggi</v-btn>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- Placeholder: nessuna postazione selezionata -->
    <v-card v-if="!filtroPostazione" variant="outlined" class="d-flex align-center justify-center" style="min-height:300px">
      <div class="text-center text-medium-emphasis pa-8">
        <v-icon size="48" class="mb-3">mdi-map-marker-outline</v-icon>
        <div class="text-h6 mb-1">Seleziona una postazione</div>
        <div class="text-body-2">Scegli una postazione dal menu in alto per visualizzare il calendario.</div>
      </div>
    </v-card>

    <!-- Griglia calendario -->
    <v-card v-else :loading="store.loading">
      <!-- Intestazione giorni settimana -->
      <v-row dense no-gutters class="px-1 pt-2 pb-1">
        <v-col
          v-for="g in giorniSettimana"
          :key="g"
          class="text-center text-caption text-medium-emphasis font-weight-medium py-1"
        >
          {{ g }}
        </v-col>
      </v-row>
      <v-divider/>

      <!-- Settimane -->
      <div class="px-1 pb-1">
        <v-row
          v-for="(settimana, si) in grigliaCalendario"
          :key="si"
          dense
          no-gutters
          class="settimana-row"
        >
          <v-col
            v-for="(giorno, gi) in settimana"
            :key="gi"
            class="giorno-cella pa-0"
            :class="{
              'fuori-mese': giorno && !giorno.meseCorrente,
              'giorno-oggi': giorno && giorno.isOggi,
              'giorno-cella-hover': giorno && giorno.meseCorrente,
            }"
            @click="onClickGiorno(giorno)"
          >
            <template v-if="giorno">
              <!-- Wrapper unico: bordo colorato + numero + contenuto -->
              <div
                class="cella-inner"
                :class="cellDataPerGiorno[giorno.data] ? `turno-${cellDataPerGiorno[giorno.data].stato}` : ''"
              >
                <!-- Numero giorno sempre dentro la cornice -->
                <div class="num-row">
                  <span
                    class="num-giorno"
                    :class="giorno.isOggi ? 'badge-oggi' : ''"
                    :style="!giorno.isOggi ? { color: giorno.isFestivo ? '#D32F2F' : '#1565C0' } : {}"
                  >{{ giorno.day }}</span>
                </div>

                <!-- Contenuto turno -->
                <template v-if="cellDataPerGiorno[giorno.data]">
                  <!-- Header colonne -->
                  <div class="tc-header" :class="cellDataPerGiorno[giorno.data].isSOUR ? 'tc-cols-3' : 'tc-cols-2'">
                    <span class="tc-time-col"></span>
                    <span class="tc-name-col">{{ cellDataPerGiorno[giorno.data].isSOUR ? 'Funzionario' : 'Addetto' }}</span>
                    <span v-if="cellDataPerGiorno[giorno.data].isSOUR" class="tc-name-col">TAS</span>
                  </div>
                  <!-- Righe turno -->
                  <div
                    v-for="(r, i) in cellDataPerGiorno[giorno.data].righe"
                    :key="i"
                    class="tc-row"
                    :class="cellDataPerGiorno[giorno.data].isSOUR ? 'tc-cols-3' : 'tc-cols-2'"
                  >
                    <span class="tc-time-col">{{ r.orario }}</span>
                    <span class="tc-name-col">{{ r.col1 }}</span>
                    <span v-if="cellDataPerGiorno[giorno.data].isSOUR" class="tc-name-col">{{ r.col2 }}</span>
                  </div>
                </template>
              </div>
            </template>
          </v-col>
        </v-row>
      </div>
    </v-card>

    <!-- ── Dialog: composizione giorno ─────────────────────────────────────── -->
    <v-dialog v-model="dialogComposizione" max-width="600" persistent>
      <v-card v-if="giornoSelezionato">
        <v-card-title class="text-subtitle-1 font-weight-medium pa-4 pb-2">
          {{ formatDataLabel(giornoSelezionato.data) }} — Pianificazione
        </v-card-title>
        <v-divider/>
        <v-card-text class="pt-4">

          <!-- Postazione fissa (non selezionabile — viene dal filtro) -->
          <div class="d-flex align-center gap-2 mb-4">
            <v-icon color="primary">mdi-map-marker</v-icon>
            <span class="text-subtitle-2 font-weight-medium">{{ postazioneLabel }}</span>
          </div>

          <!-- ── SOR ── -->
          <template v-if="isSOR">
            <div class="text-caption text-medium-emphasis mb-2">
              Turno unico · 08:00 – 20:00
            </div>
            <v-row dense>
              <v-col cols="12" sm="6">
                <v-select
                  v-model="dlg.addetto"
                  :items="personaleAddetti"
                  item-title="label"
                  item-value="id"
                  label="Addetto *"
                  density="compact"
                  clearable
                />
              </v-col>
              <v-col cols="12" sm="6">
                <v-select
                  v-model="dlg.funzione_sor"
                  :items="store.funzioni"
                  item-title="codice"
                  item-value="id"
                  label="Funzione *"
                  density="compact"
                />
              </v-col>
            </v-row>
          </template>

          <!-- ── SOUR ── -->
          <template v-else-if="isSOUR">

            <!-- Toggle turno unico / due turni -->
            <v-btn-toggle
              v-model="dlg.doppioTurno"
              mandatory
              density="compact"
              color="primary"
              variant="outlined"
              class="mb-4"
            >
              <v-btn :value="false">
                <v-icon start>mdi-clock-outline</v-icon>
                Turno unico 08:00 – 20:00
              </v-btn>
              <v-btn :value="true">
                <v-icon start>mdi-clock-split-12</v-icon>
                Due turni
              </v-btn>
            </v-btn-toggle>

            <!-- Mattina (sempre visibile) -->
            <div class="fascia-header mb-1">
              <v-icon size="14" color="orange-darken-2">mdi-weather-sunset-up</v-icon>
              <span class="ml-1">{{ dlg.doppioTurno ? 'Mattina · 08:00 – 14:00' : 'Turno unico · 08:00 – 20:00' }}</span>
            </div>
            <v-row dense class="mb-2">
              <v-col cols="12" sm="6">
                <v-select
                  v-model="dlg.funzM"
                  :items="personaleFunzionari"
                  item-title="label"
                  item-value="id"
                  label="Funzionario *"
                  density="compact"
                  clearable
                />
              </v-col>
              <v-col cols="12" sm="6">
                <v-select
                  v-model="dlg.tas2M"
                  :items="personaleTas2"
                  item-title="label"
                  item-value="id"
                  label="TAS 2 *"
                  density="compact"
                  clearable
                />
              </v-col>
            </v-row>

            <!-- Pomeriggio (solo due turni) -->
            <template v-if="dlg.doppioTurno">
              <div class="fascia-header mb-1">
                <v-icon size="14" color="deep-orange-darken-2">mdi-weather-sunset-down</v-icon>
                <span class="ml-1">Pomeriggio · 14:00 – 20:00</span>
              </div>
              <v-row dense>
                <v-col cols="12" sm="6">
                  <v-select
                    v-model="dlg.funzP"
                    :items="personaleFunzionari"
                    item-title="label"
                    item-value="id"
                    label="Funzionario *"
                    density="compact"
                    clearable
                  />
                </v-col>
                <v-col cols="12" sm="6">
                  <v-select
                    v-model="dlg.tas2P"
                    :items="personaleTas2"
                    item-title="label"
                    item-value="id"
                    label="TAS 2 *"
                    density="compact"
                    clearable
                  />
                </v-col>
              </v-row>
            </template>
          </template>

          <!-- Nessuna regola definita -->
          <template v-else-if="dlg.postazione_id">
            <v-alert type="warning" variant="tonal" density="compact">
              Regole di composizione non configurate per questa postazione.
            </v-alert>
          </template>

          <!-- Note -->
          <v-textarea
            v-model="dlg.note"
            label="Note"
            rows="2"
            auto-grow
            density="compact"
            class="mt-3"
          />

          <!-- Avviso duplicati -->
          <v-alert v-if="avvisoDuplicati" type="warning" variant="tonal" density="compact" class="mt-2">
            {{ avvisoDuplicati }}
          </v-alert>
        </v-card-text>

        <v-divider/>
        <v-card-actions>
          <v-btn variant="text" @click="dialogComposizione = false">Annulla</v-btn>
          <v-spacer/>
          <v-btn
            color="primary"
            :disabled="!isValidComposizione || !!avvisoDuplicati"
            :loading="salvando"
            @click="salvaComposizione"
          >
            Salva
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- ── Dialog: dettaglio giorno ─────────────────────────────────────────── -->
    <v-dialog v-model="dialogDettaglio" max-width="580">
      <v-card v-if="giornoSelezionato">
        <v-card-title class="text-subtitle-1 font-weight-medium pa-4 pb-2">
          {{ formatDataLabel(giornoSelezionato.data) }} — {{ postazioneLabel }}
        </v-card-title>
        <v-divider/>
        <v-card-text class="pt-3 pb-1">
          <div v-if="presenzeGiorno.length === 0" class="text-medium-emphasis text-body-2 py-2">
            Nessun turno programmato.
          </div>
          <v-list v-else density="compact" class="pa-0">
            <v-list-item
              v-for="p in presenzeGiorno"
              :key="p.id"
              :subtitle="`${p.funzione || '—'} · ${p.orario_inizio}–${p.orario_fine}`"
              class="px-0"
            >
              <template #title>
                <span class="font-weight-medium">{{ p.cognome }} {{ p.nome_dip }}</span>
                <span class="text-caption text-medium-emphasis ml-1">{{ p.qualifica }}</span>
              </template>
              <template #append>
                <div class="d-flex align-center gap-1">
                  <v-chip :color="statoColor(p.stato)" size="x-small" variant="tonal">
                    {{ p.stato }}
                  </v-chip>
                  <v-btn
                    v-if="auth.canConsuntivare && p.stato === 'programmato'"
                    icon="mdi-check-circle"
                    size="x-small"
                    variant="text"
                    color="success"
                    title="Conferma"
                    @click="apriConsuntivo(p)"
                  />
                  <v-btn
                    v-if="auth.canPlanificare"
                    icon="mdi-delete-outline"
                    size="x-small"
                    variant="text"
                    color="error"
                    title="Elimina turno"
                    :loading="eliminando === p.id"
                    @click="eliminaTurno(p)"
                  />
                </div>
              </template>
            </v-list-item>
          </v-list>
        </v-card-text>
        <v-divider/>
        <v-card-actions>
          <v-btn
            v-if="auth.canPlanificare"
            color="primary"
            prepend-icon="mdi-pencil"
            variant="tonal"
            @click="switchAComposizione"
          >
            Modifica composizione
          </v-btn>
          <v-spacer/>
          <v-btn variant="text" @click="dialogDettaglio = false">Chiudi</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- ── Dialog: consuntivo ───────────────────────────────────────────────── -->
    <v-dialog v-model="dialogConsuntivo" max-width="500" persistent>
      <ConsuntivoForm
        v-if="presenzaSelezionata"
        :presenza="presenzaSelezionata"
        @save="salvaConsuntivo"
        @cancel="dialogConsuntivo = false"
      />
    </v-dialog>

    <!-- Snackbar -->
    <v-snackbar v-model="snack.show" :color="snack.color" timeout="4000">
      {{ snack.text }}
    </v-snackbar>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, reactive } from 'vue'
import { usePresenzeStore } from '@/stores/presenze'
import { useAuthStore }     from '@/stores/auth'
import ConsuntivoForm       from '@/components/ConsuntivoForm.vue'

const store = usePresenzeStore()
const auth  = useAuthStore()

// ── Navigazione ───────────────────────────────────────────────────────────────
const oggi   = new Date()
const meseVis = ref(oggi.getMonth())
const annoVis = ref(oggi.getFullYear())

const filtroPostazione = ref(null)

// ── Dati ─────────────────────────────────────────────────────────────────────
const salvando       = ref(false)
const eliminando     = ref(null)
const snack          = ref({ show: false, text: '', color: 'success' })

// ── Dialog state ──────────────────────────────────────────────────────────────
const dialogComposizione = ref(false)
const dialogDettaglio    = ref(false)
const dialogConsuntivo   = ref(false)
const giornoSelezionato  = ref(null)
const presenzaSelezionata = ref(null)

const dlg = reactive({
  postazione_id: null,
  doppioTurno:   false,
  funzM: null, tas2M: null,
  funzP: null, tas2P: null,
  addetto: null,
  funzione_sor: null,
  note: '',
})

// ── Costanti ──────────────────────────────────────────────────────────────────
const giorniSettimana = ['Lun','Mar','Mer','Gio','Ven','Sab','Dom']
const nomiMesi = ['Gennaio','Febbraio','Marzo','Aprile','Maggio','Giugno',
                  'Luglio','Agosto','Settembre','Ottobre','Novembre','Dicembre']

// ── Lookup funzioni per slot SOUR ─────────────────────────────────────────────
const funzFunzionario = computed(() => store.funzioni.find(f => f.codice === 'FUNZIONARIO'))
const funzTas2        = computed(() => store.funzioni.find(f => f.codice === 'TAS 2'))

// ── Monte ore map per ordinamento personale ───────────────────────────────────
const monteOreMap = computed(() =>
  Object.fromEntries(store.monteOre.map(m => [m.personale_id, m.ore_totali]))
)

// ── Regole personale ──────────────────────────────────────────────────────────
// Funzionario = qualifica IA, IAE, DCS, DS, DV. Nel calendario è inseribile
// solo il personale del comando DIR-SIC.
const QUALIFICHE_FUNZIONARIO = new Set(['IA', 'IAE', 'DCS', 'DS', 'DV'])

function isFunzionario(p) {
  return QUALIFICHE_FUNZIONARIO.has((p.qualifica_cod || '').toUpperCase().trim())
}

function conMonteOre(lista) {
  return lista
    .map(p => ({
      ...p,
      ore_tot: monteOreMap.value[p.id] ?? 0,
      label: `${p.cognome} ${p.nome}  (${monteOreMap.value[p.id] ?? 0}h)`,
    }))
    .sort((a, b) => a.ore_tot - b.ore_tot)
}

// Base: solo comando DIR-SIC (vale per SOR e SOUR)
const personaleDirSic = computed(() =>
  store.personale.filter(p => (p.comando_cod || '').toUpperCase().trim() === 'DIR-SIC')
)

// SOUR slot Funzionario: solo funzionari
const personaleFunzionari = computed(() =>
  conMonteOre(personaleDirSic.value.filter(isFunzionario))
)

// SOR slot Addetto: tutti i non funzionari
const personaleAddetti = computed(() =>
  conMonteOre(personaleDirSic.value.filter(p => !isFunzionario(p)))
)

// SOUR slot TAS: solo personale con specialità TAS 2
const personaleTas2 = computed(() =>
  conMonteOre(personaleDirSic.value.filter(p =>
    (p.specialita || []).some(s => (s.codice || '').toUpperCase().trim() === 'TAS 2')
  ))
)

// ── Postazione attiva (da filtro, non da dialog) ──────────────────────────────
const dlgPostazione = computed(() =>
  store.postazioni.find(po => po.id === filtroPostazione.value) || null
)
const postazioneLabel = computed(() => dlgPostazione.value?.codice || '—')

// ── Tipo postazione (null-safe) ───────────────────────────────────────────────
const isSOR  = computed(() => (dlgPostazione.value?.slot_addetto    ?? 0) > 0)
const isSOUR = computed(() => (dlgPostazione.value?.slot_funzionario ?? 0) > 0)

// ── Validazione dialog ────────────────────────────────────────────────────────
const isValidComposizione = computed(() => {
  if (!dlg.postazione_id || !dlgPostazione.value) return false
  if (isSOR.value)  return !!dlg.addetto && !!dlg.funzione_sor
  if (isSOUR.value) {
    const baseOk = !!dlg.funzM && !!dlg.tas2M
    if (!dlg.doppioTurno) return baseOk
    return baseOk && !!dlg.funzP && !!dlg.tas2P
  }
  return false
})

const avvisoDuplicati = computed(() => {
  const ids = [dlg.funzM, dlg.tas2M, dlg.funzP, dlg.tas2P, dlg.addetto].filter(Boolean)
  const unici = new Set(ids)
  if (ids.length !== unici.size) return 'Lo stesso dipendente è selezionato in più slot.'
  return null
})

// ── Computed display ──────────────────────────────────────────────────────────
const nomeMese = computed(() => nomiMesi[meseVis.value])

const presenzeFiltrate = computed(() => {
  if (!filtroPostazione.value) return []
  return store.presenze.filter(p => p.postazione_id === filtroPostazione.value)
})

const presenzePerGiorno = computed(() => {
  const map = {}
  for (const p of presenzeFiltrate.value) {
    const k = normData(p.data_servizio)
    if (!map[k]) map[k] = []
    map[k].push(p)
  }
  return map
})

function derivaFascia(p) {
  if (p.orario_inizio === '08:00' && p.orario_fine === '14:00') return 'M'
  if (p.orario_inizio === '14:00' && p.orario_fine === '20:00') return 'P'
  return 'U'
}

// Priorità stato: programmato vince su tutto (determina il colore della card)
const _statoPriority = { programmato: 4, assente: 3, modificato: 2, confermato: 1 }

function buildCellData(presenze) {
  if (!presenze || presenze.length === 0) return null

  // Raggruppa per fascia
  const fasce = {}
  for (const p of presenze) {
    const f = p.fascia_oraria || derivaFascia(p)
    if (!fasce[f]) {
      fasce[f] = { orario: `${p.orario_inizio} -- ${p.orario_fine}`, funzionario: '', tas2: '', addetto: '' }
    }
    const cod = (p.funzione || '').toUpperCase().trim()
    if (cod === 'FUNZIONARIO') fasce[f].funzionario = p.cognome || ''
    else if (cod.startsWith('TAS')) fasce[f].tas2 = p.cognome || ''
    else fasce[f].addetto = p.cognome || ''
  }

  // Stato dominante (peggiore vince)
  const stato = presenze.reduce((acc, p) => {
    return (_statoPriority[p.stato] || 0) > (_statoPriority[acc] || 0) ? p.stato : acc
  }, 'confermato')

  const isSOUR = Object.values(fasce).some(f => f.funzionario || f.tas2)

  // Righe ordinate: prima M, poi P, poi U
  const righe = ['M', 'P', 'U']
    .filter(f => fasce[f])
    .map(f => ({
      orario: fasce[f].orario,
      col1:   isSOUR ? fasce[f].funzionario : fasce[f].addetto,
      col2:   isSOUR ? fasce[f].tas2 : '',
    }))

  return { righe, stato, isSOUR }
}

const cellDataPerGiorno = computed(() => {
  const map = {}
  for (const [data, presenze] of Object.entries(presenzePerGiorno.value)) {
    const cd = buildCellData(presenze)
    if (cd) map[data] = cd
  }
  return map
})

const presenzeGiorno = computed(() =>
  giornoSelezionato.value ? (presenzePerGiorno.value[giornoSelezionato.value.data] || []) : []
)

// Festivi italiani fissi MM-DD
const _festiviFissi = new Set(['01-01','01-06','04-25','05-01','06-02','08-15','11-01','12-08','12-25','12-26'])

// ── Griglia calendario ─────────────────────────────────────────────────────────
const grigliaCalendario = computed(() => {
  const mese  = meseVis.value
  const anno  = annoVis.value
  const primo = new Date(anno, mese, 1)
  const ultimoGiorno = new Date(anno, mese + 1, 0).getDate()
  const oggiStr = formatData(oggi)

  let startDow = primo.getDay() - 1
  if (startDow < 0) startDow = 6

  const settimane = []
  let settimana = []

  for (let i = 0; i < startDow; i++) settimana.push(null)

  for (let d = 1; d <= ultimoGiorno; d++) {
    const data = `${anno}-${pad(mese + 1)}-${pad(d)}`
    const dow  = new Date(anno, mese, d).getDay()   // 0=dom, 6=sab — costruttore locale, nessun problema UTC
    const isFestivo = dow === 0 || _festiviFissi.has(`${pad(mese + 1)}-${pad(d)}`)
    settimana.push({ day: d, data, meseCorrente: true, isOggi: data === oggiStr, isFestivo })
    if (settimana.length === 7) { settimane.push(settimana); settimana = [] }
  }
  if (settimana.length > 0) {
    while (settimana.length < 7) settimana.push(null)
    settimane.push(settimana)
  }
  return settimane
})

// ── Utilità ───────────────────────────────────────────────────────────────────
function pad(n)       { return String(n).padStart(2, '0') }
function formatData(d){ return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())}` }
function normData(v)  {
  // Normalizza da Date ISO o da stringa con T (Access a volte ritorna datetime)
  if (!v) return ''
  const s = typeof v === 'string' ? v : String(v)
  return s.slice(0, 10)
}
function formatDataLabel(data) {
  const [y, m, d] = data.split('-')
  return `${parseInt(d)} ${nomiMesi[parseInt(m)-1]} ${y}`
}
function statoColor(stato) {
  return { programmato:'blue', confermato:'green', modificato:'orange', assente:'red' }[stato] || 'grey'
}
function statoColorHex(stato) {
  return { programmato:'#1565C0', confermato:'#2E7D32', modificato:'#E65100', assente:'#B71C1C' }[stato] || '#616161'
}


// ── Navigazione mese ──────────────────────────────────────────────────────────
function mesePrecedente() {
  if (meseVis.value === 0) { meseVis.value = 11; annoVis.value-- }
  else meseVis.value--
}
function meseSuccessivo() {
  if (meseVis.value === 11) { meseVis.value = 0; annoVis.value++ }
  else meseVis.value++
}
function vaiAdOggi() {
  meseVis.value = oggi.getMonth()
  annoVis.value = oggi.getFullYear()
}

// ── Caricamento dati ──────────────────────────────────────────────────────────
async function caricaMese() {
  const data_da = `${annoVis.value}-${pad(meseVis.value + 1)}-01`
  const ultimo  = new Date(annoVis.value, meseVis.value + 1, 0).getDate()
  const data_a  = `${annoVis.value}-${pad(meseVis.value + 1)}-${pad(ultimo)}`
  await store.caricaPresenze({ data_da, data_a })
}

watch([meseVis, annoVis], caricaMese)

async function onCambioPostazione() {
  await Promise.all([
    caricaMese(),
    caricaMonteOrePostazione(),
  ])
}

async function caricaMonteOrePostazione() {
  if (!filtroPostazione.value) return
  await store.caricaMonteOre({
    campagna_id:   store.campagnaAttiva?.id,
    postazione_id: filtroPostazione.value,
  })
}

// ── Azioni dialog ─────────────────────────────────────────────────────────────
function onClickGiorno(giorno) {
  if (!giorno || !giorno.meseCorrente) return
  apriComposizione(giorno)
}

function apriComposizione(giorno) {
  giornoSelezionato.value = giorno
  resetDlg()
  dlg.postazione_id = filtroPostazione.value
  const po = dlgPostazione.value
  if (po?.slot_addetto > 0 && store.funzioni.length) {
    dlg.funzione_sor = store.funzioni.find(f => f.codice === 'ADDETTO')?.id || store.funzioni[0]?.id
  }
  // Se il giorno ha già presenze → dettaglio; altrimenti → composizione
  const haPresenze = !!cellDataPerGiorno.value[giorno.data]
  if (haPresenze) {
    dialogDettaglio.value = true
  } else if (auth.canPlanificare) {
    dialogComposizione.value = true
  }
}

function switchAComposizione() {
  dialogDettaglio.value = false
  resetDlg()
  if (filtroPostazione.value) dlg.postazione_id = filtroPostazione.value

  // Pre-carica i dati esistenti nel form
  const presenze = presenzeGiorno.value
  if (presenze.length > 0) {
    const haM = presenze.some(p => (p.fascia_oraria || derivaFascia(p)) === 'M')
    const haP = presenze.some(p => (p.fascia_oraria || derivaFascia(p)) === 'P')
    dlg.doppioTurno = haM && haP

    for (const p of presenze) {
      const fascia = p.fascia_oraria || derivaFascia(p)
      const funz   = (p.funzione || '').toUpperCase().trim()
      if (isSOR.value) {
        dlg.addetto      = p.personale_id
        dlg.funzione_sor = p.funzione_id
      } else if (isSOUR.value) {
        if (fascia === 'U' || fascia === 'M') {
          if (funz === 'FUNZIONARIO')      dlg.funzM = p.personale_id
          else if (funz.startsWith('TAS')) dlg.tas2M = p.personale_id
        } else if (fascia === 'P') {
          if (funz === 'FUNZIONARIO')      dlg.funzP = p.personale_id
          else if (funz.startsWith('TAS')) dlg.tas2P = p.personale_id
        }
      }
    }
  }

  dialogComposizione.value = true
}

function resetDlg() {
  dlg.postazione_id = null
  dlg.doppioTurno   = false
  dlg.funzM = dlg.tas2M = dlg.funzP = dlg.tas2P = dlg.addetto = null
  dlg.funzione_sor  = null
  dlg.note          = ''
}

function resetSlot() {
  dlg.doppioTurno = false
  dlg.funzM = dlg.tas2M = dlg.funzP = dlg.tas2P = dlg.addetto = null
  const po = dlgPostazione.value
  if (po?.slot_addetto > 0) {
    dlg.funzione_sor = store.funzioni.find(f => f.codice === 'ADDETTO')?.id || store.funzioni[0]?.id
  } else {
    dlg.funzione_sor = null
  }
}

async function eliminaTurno(p) {
  eliminando.value = p.id
  const { error } = await store.eliminaPresenza(p.id)
  eliminando.value = null
  if (error) {
    showSnack(error, 'error')
  } else {
    showSnack('Turno eliminato', 'success')
    await caricaMese()
    // Se non ci sono più presenze in quel giorno chiudi il dettaglio
    if (!presenzeGiorno.value?.length) dialogDettaglio.value = false
  }
}

function apriConsuntivo(p) {
  presenzaSelezionata.value = p
  dialogDettaglio.value  = false
  dialogConsuntivo.value = true
}

async function salvaConsuntivo(data) {
  const { error } = await store.consuntivaPresenza(presenzaSelezionata.value.id, data)
  dialogConsuntivo.value = false
  showSnack(error ? error : 'Consuntivo salvato', error ? 'error' : 'success')
  if (!error) await caricaMese()
}

async function salvaComposizione() {
  if (!isValidComposizione.value || avvisoDuplicati.value) return
  salvando.value = true

  // Elimina presenze esistenti per questo giorno (modifica composizione)
  const esistenti = presenzeGiorno.value
  for (const p of esistenti) {
    await store.eliminaPresenza(p.id)
  }

  const base = {
    campagna_id:   store.campagnaAttiva?.id,
    postazione_id: dlg.postazione_id,
    data_servizio: giornoSelezionato.value.data,
    note_consuntivo: dlg.note || null,
  }

  const po = dlgPostazione.value
  const items = []

  if (isSOR.value) {
    // SOR — turno unico
    items.push({
      ...base,
      personale_id:  dlg.addetto,
      funzione_id:   dlg.funzione_sor,
      orario_inizio: '08:00',
      orario_fine:   '20:00',
      fascia_oraria: 'U',
    })
  } else if (isSOUR.value) {
    const fId = funzFunzionario.value?.id
    const tId = funzTas2.value?.id

    if (!dlg.doppioTurno) {
      // SOUR turno unico
      items.push({ ...base, personale_id: dlg.funzM, funzione_id: fId, orario_inizio: '08:00', orario_fine: '20:00', fascia_oraria: 'U' })
      items.push({ ...base, personale_id: dlg.tas2M, funzione_id: tId, orario_inizio: '08:00', orario_fine: '20:00', fascia_oraria: 'U' })
    } else {
      // SOUR due turni
      items.push({ ...base, personale_id: dlg.funzM, funzione_id: fId, orario_inizio: '08:00', orario_fine: '14:00', fascia_oraria: 'M' })
      items.push({ ...base, personale_id: dlg.tas2M, funzione_id: tId, orario_inizio: '08:00', orario_fine: '14:00', fascia_oraria: 'M' })
      items.push({ ...base, personale_id: dlg.funzP, funzione_id: fId, orario_inizio: '14:00', orario_fine: '20:00', fascia_oraria: 'P' })
      items.push({ ...base, personale_id: dlg.tas2P, funzione_id: tId, orario_inizio: '14:00', orario_fine: '20:00', fascia_oraria: 'P' })
    }
  }

  const { error } = await store.creaPresenzeGiorno(items)
  salvando.value = false
  dialogComposizione.value = false

  if (error) {
    showSnack(error, 'error')
  } else {
    showSnack(`${items.length} turno${items.length > 1 ? 'i' : ''} creato${items.length > 1 ? 'i' : ''}`, 'success')
    await caricaMese()
  }
}

function showSnack(text, color = 'success') {
  snack.value = { show: true, text, color }
}

// ── Navigazione tastiera (← → cambia mese) ────────────────────────────────────
function onKeydown(e) {
  // Ignora se un dialog è aperto o il focus è su un input
  if (dialogComposizione.value || dialogDettaglio.value || dialogConsuntivo.value) return
  const tag = document.activeElement?.tagName
  if (tag === 'INPUT' || tag === 'TEXTAREA') return
  if (!filtroPostazione.value) return
  if (e.key === 'ArrowLeft')  mesePrecedente()
  if (e.key === 'ArrowRight') meseSuccessivo()
}

// ── Mount ─────────────────────────────────────────────────────────────────────
onMounted(async () => {
  window.addEventListener('keydown', onKeydown)
  // Lookup e personale sono già caricati dal Layout al login (cache store);
  // ricarica solo se lo store è vuoto (es. accesso diretto via URL)
  if (!store.postazioni.length) await store.caricaLookup()
  else store.caricaPersonale()
  // Presenze e monte ore vengono caricati al momento della selezione postazione
})

onUnmounted(() => {
  window.removeEventListener('keydown', onKeydown)
})
</script>

<style scoped>
.nav-mese-label {
  min-width: 190px;
  text-align: center;
  display: inline-block;
}

/* ── Griglia ── */
.settimana-row {
  border-bottom: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
}
.settimana-row:last-child { border-bottom: none; }

.giorno-cella {
  min-height: 110px;
  border-right: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
  vertical-align: top;
  transition: background-color 150ms ease;
  display: flex !important;
  flex-direction: column;
}
.giorno-cella:last-child { border-right: none; }

.giorno-cella-hover:hover {
  background-color: rgba(255, 214, 0, 0.18);
  cursor: pointer;
}

.fuori-mese {
  opacity: 0.22;
  pointer-events: none;
}

.giorno-oggi {
  background-color: rgba(var(--v-theme-primary), 0.05);
}

/* ── Numero giorno ── */
.num-row {
  padding: 3px 5px 2px;
  flex-shrink: 0;
}

.num-giorno {
  font-size: 1.15rem;
  font-style: italic;
  font-weight: 700;
  line-height: 1;
}

.num-normale {
  color: rgb(var(--v-theme-primary));
}

.num-festivo {
  color: #D32F2F;
}

.badge-oggi {
  background: rgb(var(--v-theme-primary));
  color: rgb(var(--v-theme-on-primary));
  border-radius: 50%;
  width: 20px;
  height: 20px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 0.68rem;
  font-weight: 700;
}

/* ── Wrapper cella: riempie tutto, bordo colorato ── */
.cella-inner {
  flex: 1;
  display: flex;
  flex-direction: column;
  margin: 2px;
  border-radius: 4px;
  border: 2px solid transparent;
  overflow: hidden;
  font-size: 0.62rem;
  min-height: 0;
}

.cella-inner.turno-programmato {
  border-color: #90CAF9;
  background-color: rgba(144, 202, 249, 0.1);
}
.cella-inner.turno-confermato {
  border-color: #66BB6A;
  background-color: rgba(102, 187, 106, 0.1);
}
.cella-inner.turno-modificato {
  border-color: #FFA726;
  background-color: rgba(255, 167, 38, 0.1);
}
.cella-inner.turno-assente {
  border-color: #EF5350;
  background-color: rgba(239, 83, 80, 0.1);
}

/* ── Righe header e dati ── */
.tc-header {
  display: grid;
  font-size: 0.58rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  padding: 2px 4px 1px;
  color: rgba(var(--v-theme-on-surface), 0.55);
  border-bottom: 1px solid rgba(var(--v-theme-on-surface), 0.08);
}

.tc-row {
  display: grid;
  padding: 1px 4px;
  align-items: center;
}

/* Layout 2 colonne: orario + nome (SOR) */
.tc-cols-2 {
  grid-template-columns: 72px 1fr;
}

/* Layout 3 colonne: orario + funzionario + TAS (SOUR) */
.tc-cols-3 {
  grid-template-columns: 72px 1fr 1fr;
}

.tc-time-col {
  font-size: 0.58rem;
  color: rgba(var(--v-theme-on-surface), 0.5);
  white-space: nowrap;
  padding-right: 2px;
}

.tc-name-col {
  font-size: 0.63rem;
  font-weight: 600;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  padding: 0 2px;
}

/* ── Dialog form ── */
.fascia-header {
  display: flex;
  align-items: center;
  font-size: 0.78rem;
  font-weight: 600;
  color: rgba(var(--v-theme-on-surface), 0.7);
  margin-bottom: 4px;
}
</style>
