<template>
  <div>
    <!-- Barra superiore -->
    <div class="d-flex align-center mb-4 flex-wrap gap-2">
      <v-btn icon="mdi-arrow-left" variant="text" to="/report"/>
      <div class="flex-1">
        <v-text-field v-model="nomeModello" label="Nome modello" density="compact"
                      hide-details style="max-width: 360px"/>
      </div>
      <v-btn variant="outlined" prepend-icon="mdi-eye" :loading="anteprimaLoading" @click="anteprima">
        Anteprima
      </v-btn>
      <v-btn color="primary" prepend-icon="mdi-content-save" :loading="salvando" @click="salva">
        Salva
      </v-btn>
    </div>

    <v-row dense>
      <!-- ── Pannello sinistro: strumenti ── -->
      <v-col cols="12" md="3">
        <v-card variant="outlined" class="mb-3">
          <v-card-title class="text-subtitle-2 py-2">Aggiungi elemento</v-card-title>
          <v-divider/>
          <v-card-text class="py-2">
            <v-btn-toggle v-model="bandaAttiva" mandatory density="compact" color="primary" class="mb-2 w-100">
              <v-btn value="intestazione" size="small" class="flex-1">Intestazione</v-btn>
              <v-btn value="pie" size="small" class="flex-1">Piè di pagina</v-btn>
            </v-btn-toggle>
            <div class="d-flex flex-wrap gap-1">
              <v-btn v-for="t in tipiElemento" :key="t.tipo" size="small" variant="tonal"
                     :prepend-icon="t.icona" @click="aggiungiElemento(t.tipo)">
                {{ t.nome }}
              </v-btn>
            </div>
          </v-card-text>
        </v-card>

        <!-- Proprietà elemento selezionato -->
        <v-card variant="outlined" class="mb-3" v-if="elSel">
          <v-card-title class="text-subtitle-2 py-2 d-flex align-center">
            Proprietà — {{ nomeTipo(elSel.tipo) }}
            <v-spacer/>
            <v-btn icon="mdi-delete-outline" size="x-small" variant="text" color="error"
                   @click="eliminaElemento"/>
          </v-card-title>
          <v-divider/>
          <v-card-text class="py-2">
            <v-text-field v-if="elSel.tipo === 'testo'" v-model="elSel.testo" label="Testo"
                          density="compact" class="mb-1"/>
            <v-select v-if="elSel.tipo === 'campo'" v-model="elSel.campo" :items="campiIntestazione"
                      label="Campo dinamico" density="compact" class="mb-1"/>
            <v-row dense>
              <v-col cols="4"><v-text-field v-model.number="elSel.x" label="X (mm)" type="number" density="compact"/></v-col>
              <v-col cols="4"><v-text-field v-model.number="elSel.y" label="Y (mm)" type="number" density="compact"/></v-col>
              <v-col cols="4"><v-text-field v-model.number="elSel.w" label="Largh." type="number" density="compact"/></v-col>
            </v-row>
            <template v-if="haTesto(elSel.tipo)">
              <v-row dense align="center">
                <v-col cols="5">
                  <v-text-field v-model.number="elSel.font.size" label="Font pt" type="number" density="compact"/>
                </v-col>
                <v-col cols="7" class="d-flex gap-1">
                  <v-btn :variant="elSel.font.bold ? 'flat' : 'outlined'" color="primary" size="small"
                         icon="mdi-format-bold" @click="elSel.font.bold = !elSel.font.bold"/>
                  <v-btn :variant="elSel.font.italic ? 'flat' : 'outlined'" color="primary" size="small"
                         icon="mdi-format-italic" @click="elSel.font.italic = !elSel.font.italic"/>
                  <v-btn-toggle v-model="elSel.align" density="compact" mandatory>
                    <v-btn value="left" size="x-small" icon="mdi-format-align-left"/>
                    <v-btn value="center" size="x-small" icon="mdi-format-align-center"/>
                    <v-btn value="right" size="x-small" icon="mdi-format-align-right"/>
                  </v-btn-toggle>
                </v-col>
              </v-row>
            </template>
            <v-text-field v-if="elSel.tipo === 'rettangolo'" v-model.number="elSel.h"
                          label="Altezza (mm)" type="number" density="compact"/>
            <div class="d-flex align-center gap-2 mt-1">
              <span class="text-caption">Colore</span>
              <input type="color" v-model="elSel.font.colore" class="color-input"/>
            </div>
          </v-card-text>
        </v-card>

        <!-- Pagina e bande -->
        <v-card variant="outlined" class="mb-3">
          <v-card-title class="text-subtitle-2 py-2">Pagina</v-card-title>
          <v-divider/>
          <v-card-text class="py-2">
            <v-select v-model="def.pagina.orientamento"
                      :items="[{title:'Verticale',value:'portrait'},{title:'Orizzontale',value:'landscape'}]"
                      label="Orientamento" density="compact" class="mb-1"/>
            <v-row dense>
              <v-col cols="6">
                <v-text-field v-model.number="def.intestazione.altezza" label="H intestaz. (mm)"
                              type="number" density="compact"/>
              </v-col>
              <v-col cols="6">
                <v-text-field v-model.number="def.pie.altezza" label="H piè (mm)"
                              type="number" density="compact"/>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>

        <!-- Stile tabella -->
        <v-card variant="outlined">
          <v-card-title class="text-subtitle-2 py-2">Stile tabella</v-card-title>
          <v-divider/>
          <v-card-text class="py-2">
            <div class="d-flex align-center gap-2 mb-2">
              <span class="text-caption">Colore intestazione</span>
              <input type="color" v-model="def.tabella.stile.colore_header" class="color-input"/>
            </div>
            <v-text-field v-model.number="def.tabella.stile.font_size" label="Font dati (pt)"
                          type="number" density="compact" class="mb-1"/>
            <v-switch v-model="def.tabella.stile.zebra" label="Righe alternate" color="primary"
                      density="compact" hide-details/>
            <v-switch v-model="def.tabella.stile.bordi" label="Bordi riga" color="primary"
                      density="compact" hide-details/>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- ── Canvas centrale ── -->
      <v-col cols="12" md="6">
        <v-card variant="outlined" class="pa-4 d-flex justify-center" style="overflow:auto">
          <div class="pagina" :style="stilePagina" @mousedown.self="elSelIdx = null">
            <!-- Banda intestazione -->
            <div class="banda banda-int" :style="{ height: def.intestazione.altezza * SCALA + 'px' }"
                 @mousedown.self="selezionaBanda('intestazione')">
              <div v-for="(el, i) in def.intestazione.elementi" :key="'i'+i"
                   class="elemento" :class="{ selezionato: bandaSel === 'intestazione' && elSelIdx === i }"
                   :style="stileElemento(el)"
                   @mousedown.stop="iniziaDrag($event, 'intestazione', i)">
                <component :is="'div'" :style="stileTestoElemento(el)">{{ anteprimaElemento(el) }}</component>
              </div>
            </div>

            <!-- Area tabella -->
            <div class="area-tabella">
              <div class="tab-header" :style="{ background: def.tabella.stile.colore_header }">
                <span v-for="(col, i) in def.tabella.colonne" :key="i"
                      class="tab-cell" :style="{ flex: col.larghezza, color: def.tabella.stile.testo_header || '#fff' }">
                  {{ col.etichetta }}
                </span>
              </div>
              <div v-for="r in 4" :key="r" class="tab-riga"
                   :style="def.tabella.stile.zebra && r % 2 === 0 ? 'background:#F5F5F5' : ''">
                <span v-for="(col, i) in def.tabella.colonne" :key="i"
                      class="tab-cell text-medium-emphasis" :style="{ flex: col.larghezza, textAlign: col.align }">
                  ···
                </span>
              </div>
              <div class="text-center text-caption text-disabled py-2">— dati —</div>
            </div>

            <!-- Banda piè -->
            <div class="banda banda-pie" :style="{ height: def.pie.altezza * SCALA + 'px' }"
                 @mousedown.self="selezionaBanda('pie')">
              <div v-for="(el, i) in def.pie.elementi" :key="'p'+i"
                   class="elemento" :class="{ selezionato: bandaSel === 'pie' && elSelIdx === i }"
                   :style="stileElemento(el)"
                   @mousedown.stop="iniziaDrag($event, 'pie', i)">
                <component :is="'div'" :style="stileTestoElemento(el)">{{ anteprimaElemento(el) }}</component>
              </div>
            </div>
          </div>
        </v-card>
        <p class="text-caption text-medium-emphasis mt-2 text-center">
          Trascina gli elementi nelle bande · clicca per selezionare e modificarne le proprietà
        </p>
      </v-col>

      <!-- ── Pannello destro: colonne tabella ── -->
      <v-col cols="12" md="3">
        <v-card variant="outlined">
          <v-card-title class="text-subtitle-2 py-2">Colonne tabella</v-card-title>
          <v-divider/>
          <v-card-text class="py-2">
            <div v-for="(col, i) in def.tabella.colonne" :key="i" class="colonna-cfg mb-2">
              <div class="d-flex align-center gap-1">
                <v-btn icon="mdi-chevron-up" size="x-small" variant="text" :disabled="i === 0"
                       @click="spostaColonna(i, -1)"/>
                <v-btn icon="mdi-chevron-down" size="x-small" variant="text"
                       :disabled="i === def.tabella.colonne.length - 1" @click="spostaColonna(i, 1)"/>
                <v-text-field v-model="col.etichetta" density="compact" hide-details class="flex-1"/>
                <v-text-field v-model.number="col.larghezza" type="number" density="compact"
                              hide-details style="max-width:64px" title="Larghezza relativa"/>
                <v-btn icon="mdi-close" size="x-small" variant="text" color="error"
                       @click="def.tabella.colonne.splice(i, 1)"/>
              </div>
            </div>
            <v-select v-model="campoDaAggiungere" :items="campiDisponibili"
                      item-title="etichetta" item-value="campo"
                      label="Aggiungi colonna" density="compact" class="mt-2"
                      @update:model-value="aggiungiColonna"/>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <v-snackbar v-model="snack.show" :color="snack.color" timeout="4000">{{ snack.text }}</v-snackbar>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { usePresenzeStore } from '@/stores/presenze'
import { reportApi } from '@/api/api'

const route  = useRoute()
const router = useRouter()
const store  = usePresenzeStore()

const SCALA = 3.2   // px per mm (canvas)

const templateId   = Number(route.params.id)
const nomeModello  = ref('')
const sorgente     = ref('presenze')
const salvando     = ref(false)
const anteprimaLoading = ref(false)
const snack        = ref({ show: false, text: '', color: 'success' })

// Catalogo campi dal backend
const catalogoSorgenti  = ref({})
const campiIntestazione = ref([])

// Definizione di default (sovrascritta dal load)
const def = reactive({
  pagina: { formato: 'A4', orientamento: 'portrait', margini: { sx: 15, dx: 15, alto: 12, basso: 12 } },
  intestazione: { altezza: 28, elementi: [] },
  pie:          { altezza: 12, elementi: [] },
  tabella:      { colonne: [], stile: { colore_header: '#C0392B', testo_header: '#FFFFFF', zebra: true, bordi: true, font_size: 8 } },
})

// ── Selezione e drag ──────────────────────────────────────────────────────────
const bandaAttiva = ref('intestazione')
const bandaSel    = ref(null)
const elSelIdx    = ref(null)

const elSel = computed(() => {
  if (bandaSel.value == null || elSelIdx.value == null) return null
  const el = def[bandaSel.value]?.elementi[elSelIdx.value] || null
  if (el && !el.font) el.font = { size: 9, bold: false, italic: false, colore: '#000000' }
  return el
})

let drag = null

function iniziaDrag(e, banda, idx) {
  bandaSel.value = banda
  elSelIdx.value = idx
  const el = def[banda].elementi[idx]
  drag = { banda, idx, startX: e.clientX, startY: e.clientY, origX: el.x, origY: el.y }
}

function onMouseMove(e) {
  if (!drag) return
  const el = def[drag.banda].elementi[drag.idx]
  el.x = Math.max(0, Math.round(drag.origX + (e.clientX - drag.startX) / SCALA))
  el.y = Math.max(0, Math.round(drag.origY + (e.clientY - drag.startY) / SCALA))
}

function onMouseUp() { drag = null }

function selezionaBanda(b) {
  bandaAttiva.value = b
  bandaSel.value = null
  elSelIdx.value = null
}

// ── Elementi ──────────────────────────────────────────────────────────────────
const tipiElemento = [
  { tipo: 'testo',      nome: 'Testo',     icona: 'mdi-format-text' },
  { tipo: 'campo',      nome: 'Campo',     icona: 'mdi-variable' },
  { tipo: 'linea',      nome: 'Linea',     icona: 'mdi-minus' },
  { tipo: 'rettangolo', nome: 'Riquadro',  icona: 'mdi-rectangle-outline' },
  { tipo: 'data',       nome: 'Data',      icona: 'mdi-calendar' },
  { tipo: 'numpagina',  nome: 'N. pagina', icona: 'mdi-numeric' },
]

function nomeTipo(t) { return tipiElemento.find(x => x.tipo === t)?.nome || t }
function haTesto(t)  { return ['testo', 'campo', 'data', 'numpagina'].includes(t) }

function aggiungiElemento(tipo) {
  const nuovo = {
    tipo, x: 5, y: 5, w: tipo === 'linea' ? 100 : 60, h: tipo === 'rettangolo' ? 10 : (tipo === 'linea' ? 0 : 6),
    testo: tipo === 'testo' ? 'Nuovo testo' : '',
    campo: tipo === 'campo' ? 'sottotitolo' : '',
    font: { size: 9, bold: false, italic: false, colore: '#000000' },
    align: 'left',
  }
  def[bandaAttiva.value].elementi.push(nuovo)
  bandaSel.value = bandaAttiva.value
  elSelIdx.value = def[bandaAttiva.value].elementi.length - 1
}

function eliminaElemento() {
  if (bandaSel.value == null || elSelIdx.value == null) return
  def[bandaSel.value].elementi.splice(elSelIdx.value, 1)
  elSelIdx.value = null
}

// Tasto Canc elimina l'elemento selezionato
function onKeydown(e) {
  if (e.key === 'Delete' && elSel.value) {
    const tag = document.activeElement?.tagName
    if (tag !== 'INPUT' && tag !== 'TEXTAREA') eliminaElemento()
  }
}

// ── Render canvas ─────────────────────────────────────────────────────────────
const stilePagina = computed(() => {
  const [w, h] = def.pagina.orientamento === 'portrait' ? [210, 297] : [297, 210]
  const m = def.pagina.margini
  return {
    width:  w * SCALA + 'px',
    minHeight: h * 0.55 * SCALA + 'px',   // pagina compressa: bande reali, dati simbolici
    padding: `${m.alto * SCALA}px ${m.dx * SCALA}px ${m.basso * SCALA}px ${m.sx * SCALA}px`,
  }
})

function stileElemento(el) {
  const base = {
    left:  el.x * SCALA + 'px',
    top:   el.y * SCALA + 'px',
    width: el.w * SCALA + 'px',
  }
  if (el.tipo === 'linea')      base.borderTop = `2px solid ${el.font?.colore || '#000'}`
  if (el.tipo === 'rettangolo') {
    base.height = (el.h || 10) * SCALA + 'px'
    base.border = `1px solid ${el.font?.colore || '#000'}`
  }
  return base
}

function stileTestoElemento(el) {
  if (!haTesto(el.tipo)) return {}
  const f = el.font || {}
  return {
    fontSize:  (f.size || 9) * 1.05 * SCALA / 3.2 + 'px',
    fontWeight: f.bold ? 700 : 400,
    fontStyle:  f.italic ? 'italic' : 'normal',
    color:      f.colore || '#000',
    textAlign:  el.align || 'left',
    whiteSpace: 'nowrap',
    overflow:   'hidden',
  }
}

function anteprimaElemento(el) {
  switch (el.tipo) {
    case 'testo':     return el.testo || '(testo)'
    case 'campo':     return `{${el.campo || 'campo'}}`
    case 'data':      return new Date().toLocaleDateString('it-IT')
    case 'numpagina': return 'Pag. 1'
    default:          return ''
  }
}

// ── Colonne tabella ───────────────────────────────────────────────────────────
const campoDaAggiungere = ref(null)

const campiDisponibili = computed(() => {
  const usati = new Set(def.tabella.colonne.map(c => c.campo))
  return (catalogoSorgenti.value[sorgente.value] || []).filter(c => !usati.has(c.campo))
})

function aggiungiColonna(campo) {
  if (!campo) return
  const info = (catalogoSorgenti.value[sorgente.value] || []).find(c => c.campo === campo)
  def.tabella.colonne.push({
    campo,
    etichetta: info?.etichetta || campo,
    larghezza: 20,
    align: 'left',
    ...(info?.formato ? { formato: info.formato } : {}),
  })
  campoDaAggiungere.value = null
}

function spostaColonna(i, delta) {
  const cols = def.tabella.colonne
  const [c] = cols.splice(i, 1)
  cols.splice(i + delta, 0, c)
}

// ── Salva / anteprima ─────────────────────────────────────────────────────────
async function salva() {
  salvando.value = true
  const { error } = await reportApi.aggiorna(templateId, {
    nome: nomeModello.value,
    definizione: JSON.parse(JSON.stringify(def)),
  })
  salvando.value = false
  showSnack(error ? error : 'Modello salvato', error ? 'error' : 'success')
}

async function anteprima() {
  anteprimaLoading.value = true
  const { url, error } = await reportApi.anteprima({
    sorgente: sorgente.value,
    definizione: JSON.parse(JSON.stringify(def)),
    filtri: { campagna_id: store.campagnaAttiva?.id },
  })
  anteprimaLoading.value = false
  if (error) return showSnack(error, 'error')
  window.open(url, '_blank')
  setTimeout(() => URL.revokeObjectURL(url), 60000)
}

function showSnack(text, color = 'success') {
  snack.value = { show: true, text, color }
}

// ── Load ──────────────────────────────────────────────────────────────────────
onMounted(async () => {
  window.addEventListener('mousemove', onMouseMove)
  window.addEventListener('mouseup', onMouseUp)
  window.addEventListener('keydown', onKeydown)

  if (!store.campagne.length) store.caricaLookup()

  const [tplRes, srcRes] = await Promise.all([
    reportApi.template(templateId),
    reportApi.sorgenti(),
  ])
  if (srcRes.data) {
    catalogoSorgenti.value  = srcRes.data.sorgenti || {}
    campiIntestazione.value = srcRes.data.campi_intestazione || []
  }
  if (tplRes.error || !tplRes.data) {
    showSnack(tplRes.error || 'Modello non trovato', 'error')
    return router.push('/report')
  }
  nomeModello.value = tplRes.data.nome
  sorgente.value    = tplRes.data.sorgente
  const d = tplRes.data.definizione || {}
  if (d.pagina)       Object.assign(def.pagina, d.pagina)
  if (d.intestazione) Object.assign(def.intestazione, d.intestazione)
  if (d.pie)          Object.assign(def.pie, d.pie)
  if (d.tabella) {
    def.tabella.colonne = d.tabella.colonne || []
    Object.assign(def.tabella.stile, d.tabella.stile || {})
  }
})

onUnmounted(() => {
  window.removeEventListener('mousemove', onMouseMove)
  window.removeEventListener('mouseup', onMouseUp)
  window.removeEventListener('keydown', onKeydown)
})
</script>

<style scoped>
.pagina {
  background: #fff;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.18);
  position: relative;
  display: flex;
  flex-direction: column;
}

.banda {
  position: relative;
  border: 1px dashed rgba(192, 57, 43, 0.35);
  background: rgba(192, 57, 43, 0.025);
  overflow: hidden;
  flex-shrink: 0;
}
.banda-pie { margin-top: auto; }

.elemento {
  position: absolute;
  cursor: move;
  min-height: 8px;
  user-select: none;
}
.elemento.selezionato {
  outline: 2px solid #1976D2;
  outline-offset: 1px;
}

.area-tabella {
  flex: 1;
  margin: 8px 0;
  border: 1px dashed #BBB;
  display: flex;
  flex-direction: column;
  min-height: 120px;
}
.tab-header { display: flex; }
.tab-riga   { display: flex; border-bottom: 1px solid #EEE; }
.tab-cell {
  padding: 3px 4px;
  font-size: 10px;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}
.tab-header .tab-cell { font-weight: 700; }

.color-input {
  width: 36px;
  height: 24px;
  border: 1px solid #CCC;
  border-radius: 4px;
  padding: 0;
  cursor: pointer;
}

.colonna-cfg {
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
  padding-bottom: 4px;
}
</style>
