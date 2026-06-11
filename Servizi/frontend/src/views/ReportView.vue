<template>
  <div>
    <div class="d-flex align-center mb-4 flex-wrap gap-2">
      <div class="flex-1">
        <h1 class="text-h5 font-weight-medium">Report</h1>
        <p class="text-caption text-medium-emphasis mb-0">Generazione e modelli personalizzati</p>
      </div>
      <v-btn
        v-if="auth.isAdmin"
        color="primary"
        prepend-icon="mdi-plus"
        @click="nuovoModello"
      >
        Nuovo modello
      </v-btn>
    </div>

    <!-- Filtri generazione -->
    <v-card class="mb-4" variant="outlined">
      <v-card-text>
        <v-row dense align="center">
          <v-col cols="12" sm="4" md="3">
            <v-select v-model="filtri.campagna_id" :items="store.campagne"
                      :item-title="c => `AIB ${c.anno}`" item-value="id"
                      label="Campagna" clearable density="compact" hide-details/>
          </v-col>
          <v-col cols="12" sm="4" md="3">
            <v-select v-model="filtri.postazione_id" :items="store.postazioni"
                      item-title="codice" item-value="id"
                      label="Postazione" clearable density="compact" hide-details/>
          </v-col>
          <v-col cols="12" sm="4" md="2">
            <v-text-field v-model="filtri.data_da" type="date" label="Dal"
                          clearable density="compact" hide-details/>
          </v-col>
          <v-col cols="12" sm="4" md="2">
            <v-text-field v-model="filtri.data_a" type="date" label="Al"
                          clearable density="compact" hide-details/>
          </v-col>
          <v-col cols="12" sm="4" md="2">
            <v-select v-model="filtri.stato" :items="['programmato','confermato','modificato','assente']"
                      label="Stato" clearable density="compact" hide-details/>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- Modelli PDF -->
    <h2 class="text-subtitle-1 font-weight-medium mb-2">Modelli PDF</h2>
    <v-row dense class="mb-4">
      <v-col v-for="t in templates" :key="t.id" cols="12" sm="6" md="4">
        <v-card variant="outlined" class="h-100">
          <v-card-text class="pb-2">
            <div class="d-flex align-center gap-2 mb-1">
              <v-icon color="primary">mdi-file-pdf-box</v-icon>
              <span class="text-subtitle-2 font-weight-medium">{{ t.nome }}</span>
            </div>
            <v-chip size="x-small" variant="tonal" color="secondary">{{ etichettaSorgente(t.sorgente) }}</v-chip>
          </v-card-text>
          <v-card-actions class="pt-0">
            <v-btn color="primary" variant="tonal" size="small"
                   prepend-icon="mdi-download" :loading="generando === t.id"
                   @click="generaPdf(t)">
              Genera PDF
            </v-btn>
            <v-spacer/>
            <v-btn v-if="auth.isAdmin" icon="mdi-pencil-ruler" size="x-small"
                   variant="text" color="primary" title="Apri nel designer"
                   :to="`/report/designer/${t.id}`"/>
            <v-btn v-if="auth.isAdmin" icon="mdi-delete-outline" size="x-small"
                   variant="text" color="error" title="Elimina"
                   @click="chiediElimina(t)"/>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>

    <!-- Export Excel layout fisso -->
    <h2 class="text-subtitle-1 font-weight-medium mb-2">Export Excel</h2>
    <v-row dense>
      <v-col v-for="e in exportExcel" :key="e.sorgente" cols="12" sm="6" md="4">
        <v-card variant="outlined">
          <v-card-text class="d-flex align-center gap-2 pb-2">
            <v-icon color="success">mdi-file-excel-box</v-icon>
            <span class="text-subtitle-2 font-weight-medium">{{ e.titolo }}</span>
          </v-card-text>
          <v-card-actions class="pt-0">
            <v-btn color="success" variant="tonal" size="small"
                   prepend-icon="mdi-download" :loading="generandoXls === e.sorgente"
                   @click="generaExcel(e.sorgente)">
              Scarica Excel
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>

    <!-- Dialog nuovo modello -->
    <v-dialog v-model="dlgNuovo" max-width="440" persistent>
      <v-card>
        <v-card-title class="text-subtitle-1 font-weight-medium pa-4 pb-2">Nuovo modello</v-card-title>
        <v-divider/>
        <v-card-text class="pt-4">
          <v-text-field v-model="nuovo.nome" label="Nome modello *" density="compact" class="mb-2"/>
          <v-select v-model="nuovo.sorgente" :items="sorgentiItems"
                    item-title="titolo" item-value="valore"
                    label="Sorgente dati *" density="compact"/>
        </v-card-text>
        <v-divider/>
        <v-card-actions>
          <v-btn variant="text" @click="dlgNuovo = false">Annulla</v-btn>
          <v-spacer/>
          <v-btn color="primary" :disabled="!nuovo.nome || !nuovo.sorgente"
                 :loading="creando" @click="creaModello">
            Crea e apri designer
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Dialog elimina -->
    <v-dialog v-model="dlgElimina" max-width="420">
      <v-card>
        <v-card-title class="text-subtitle-1 font-weight-medium pa-4 pb-2">Conferma eliminazione</v-card-title>
        <v-card-text>Eliminare il modello <strong>{{ modelloDaEliminare?.nome }}</strong>?</v-card-text>
        <v-card-actions>
          <v-btn variant="text" @click="dlgElimina = false">Annulla</v-btn>
          <v-spacer/>
          <v-btn color="error" variant="tonal" @click="eseguiElimina">Elimina</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-snackbar v-model="snack.show" :color="snack.color" timeout="4000">{{ snack.text }}</v-snackbar>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { usePresenzeStore } from '@/stores/presenze'
import { useAuthStore } from '@/stores/auth'
import { reportApi } from '@/api/api'

const store  = usePresenzeStore()
const auth   = useAuthStore()
const router = useRouter()

const templates    = ref([])
const generando    = ref(null)
const generandoXls = ref(null)
const creando      = ref(false)
const dlgNuovo     = ref(false)
const dlgElimina   = ref(false)
const modelloDaEliminare = ref(null)
const snack        = ref({ show: false, text: '', color: 'success' })

const filtri = reactive({ campagna_id: null, postazione_id: null, data_da: null, data_a: null, stato: null })

const nuovo = reactive({ nome: '', sorgente: 'presenze' })

const sorgentiItems = [
  { titolo: 'Presenze',           valore: 'presenze' },
  { titolo: 'Monte ore',          valore: 'monte_ore' },
  { titolo: 'Riepilogo campagna', valore: 'riepilogo' },
]
const exportExcel = [
  { titolo: 'Presenze',           sorgente: 'presenze' },
  { titolo: 'Monte ore',          sorgente: 'monte_ore' },
  { titolo: 'Riepilogo campagna', sorgente: 'riepilogo' },
]

function etichettaSorgente(s) {
  return sorgentiItems.find(x => x.valore === s)?.titolo || s
}

async function caricaTemplates() {
  const { data } = await reportApi.templates()
  if (data) templates.value = data
}

async function generaPdf(t) {
  generando.value = t.id
  const { error } = await reportApi.scaricaPdf(t.id, filtri, t.nome.replace(/\s+/g, '_').toLowerCase())
  generando.value = null
  if (error) showSnack(error, 'error')
}

async function generaExcel(sorgente) {
  generandoXls.value = sorgente
  const { error } = await reportApi.scaricaExcel(sorgente, filtri)
  generandoXls.value = null
  if (error) showSnack(error, 'error')
}

function nuovoModello() {
  nuovo.nome = ''
  nuovo.sorgente = 'presenze'
  dlgNuovo.value = true
}

async function creaModello() {
  creando.value = true
  // Parte dalla definizione di un modello esistente con la stessa sorgente (se c'è)
  const base = templates.value.find(t => t.sorgente === nuovo.sorgente)
  const { data, error } = await reportApi.crea({
    nome: nuovo.nome,
    sorgente: nuovo.sorgente,
    definizione: base?.definizione || {},
  })
  creando.value = false
  if (error) return showSnack(error, 'error')
  dlgNuovo.value = false
  router.push(`/report/designer/${data.id}`)
}

function chiediElimina(t) {
  modelloDaEliminare.value = t
  dlgElimina.value = true
}

async function eseguiElimina() {
  const { error } = await reportApi.elimina(modelloDaEliminare.value.id)
  dlgElimina.value = false
  if (error) return showSnack(error, 'error')
  showSnack('Modello eliminato')
  await caricaTemplates()
}

function showSnack(text, color = 'success') {
  snack.value = { show: true, text, color }
}

onMounted(async () => {
  if (!store.campagne.length) store.caricaLookup()
  // Default: campagna attiva
  await caricaTemplates()
  if (store.campagnaAttiva) filtri.campagna_id = store.campagnaAttiva.id
})
</script>
