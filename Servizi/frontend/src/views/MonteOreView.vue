<template>
  <div>
    <div class="d-flex align-center mb-4 flex-wrap gap-2">
      <div>
        <h1 class="text-h5 font-weight-medium">Monte ore</h1>
        <p class="text-caption text-medium-emphasis mb-0">
          Riepilogo ore per dipendente — AIB {{ store.campagnaAttiva?.anno }}
        </p>
      </div>
      <v-spacer/>
      <v-btn prepend-icon="mdi-download" variant="outlined" @click="esporta">
        Esporta CSV
      </v-btn>
    </div>

    <!-- Filtri -->
    <v-card class="mb-4" variant="outlined">
      <v-card-text>
        <v-row dense align="center">
          <v-col cols="12" sm="4" md="3">
            <v-select v-model="filtri.campagna_id"
                      :items="store.campagne"
                      :item-title="c => `AIB ${c.anno}`"
                      item-value="id"
                      label="Campagna"
                      density="compact" clearable
                      @update:model-value="onCampagnaChange"/>
          </v-col>
          <v-col cols="12" sm="4" md="3">
            <v-text-field v-model="filtri.mese_da" type="month"
                          label="Dal (mese)" density="compact" clearable/>
          </v-col>
          <v-col cols="12" sm="4" md="3">
            <v-text-field v-model="filtri.mese_a" type="month"
                          label="Al (mese)" density="compact" clearable/>
          </v-col>
          <v-col cols="auto">
            <v-btn color="primary" @click="carica" :loading="store.loading">
              Aggiorna
            </v-btn>
          </v-col>
        </v-row>
        <v-row dense class="mt-1">
          <v-col cols="12" sm="6" md="4">
            <v-select v-model="filtri.funzione"
                      :items="funzioniDisponibili"
                      label="Funzione"
                      density="compact" clearable placeholder="Tutte le funzioni"/>
          </v-col>
          <v-col cols="12" sm="6" md="4">
            <v-select v-model="filtri.comando"
                      :items="store.comandi"
                      item-title="codice"
                      item-value="id"
                      label="Comando"
                      density="compact" clearable placeholder="Tutti i comandi"/>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- Totali rapidi -->
    <v-row class="mb-4" dense>
      <v-col cols="6" sm="3">
        <v-card variant="tonal" color="primary">
          <v-card-text>
            <p class="text-caption mb-1">Dipendenti coinvolti</p>
            <p class="text-h4 font-weight-medium mb-0">{{ monteOreFiltrato.length }}</p>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="6" sm="3">
        <v-card variant="tonal" color="secondary">
          <v-card-text>
            <p class="text-caption mb-1">Ore totali</p>
            <p class="text-h4 font-weight-medium mb-0">{{ oreTotaliSomma }}</p>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="6" sm="3">
        <v-card variant="tonal" color="success">
          <v-card-text>
            <p class="text-caption mb-1">Turni totali</p>
            <p class="text-h4 font-weight-medium mb-0">{{ turniTotaliSomma }}</p>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="6" sm="3">
        <v-card variant="tonal" color="info">
          <v-card-text>
            <p class="text-caption mb-1">Media ore/dip.</p>
            <p class="text-h4 font-weight-medium mb-0">{{ mediaOre }}</p>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Tabella monte ore -->
    <v-card>
      <v-text-field
        v-model="ricerca"
        prepend-inner-icon="mdi-magnify"
        placeholder="Cerca dipendente…"
        variant="solo-filled"
        flat
        hide-details
        density="compact"
        class="px-4 pt-3"
      />
      <v-data-table
        :headers="headers"
        :items="monteOreFiltrato"
        :loading="store.loading"
        :search="ricerca"
        density="comfortable"
        :sort-by="[{ key: 'ore_totali', order: 'desc' }]"
        no-data-text="Nessun dato disponibile"
      >
        <template #item.ore_totali="{ item }">
          <span class="font-weight-bold text-primary">{{ item.ore_totali }}h</span>
        </template>

        <template #item.ore_per_funzione="{ item }">
          <div class="d-flex flex-wrap gap-1 py-1">
            <v-chip v-for="(ore, funz) in item.ore_per_funzione"
                    :key="funz" size="x-small" variant="outlined">
              {{ funz }}: {{ ore }}h
            </v-chip>
          </div>
        </template>

        <!-- Dettaglio su click -->
        <template #item.actions="{ item }">
          <v-btn icon="mdi-eye" size="small" variant="text"
                 @click="apriDettaglio(item)"/>
        </template>
      </v-data-table>
    </v-card>

    <!-- Dialog dettaglio dipendente -->
    <v-dialog v-model="dialogDettaglio" max-width="700">
      <v-card v-if="dettaglioDip">
        <v-card-title class="d-flex align-center gap-2">
          <v-icon icon="mdi-account"/>
          {{ dettaglioDip.cognome }} {{ dettaglioDip.nome }}
          <v-chip size="small" variant="outlined">{{ dettaglioDip.qualifica }}</v-chip>
        </v-card-title>
        <v-divider/>
        <v-card-text>
          <v-data-table
            :headers="headersDettaglio"
            :items="presenzeDettaglio"
            :loading="loadingDettaglio"
            density="compact"
            no-data-text="Nessuna presenza"
          >
            <template #item.stato="{ item }">
              <v-chip :color="statoColor(item.stato)" size="x-small" variant="tonal">
                {{ item.stato }}
              </v-chip>
            </template>
          </v-data-table>
        </v-card-text>
        <v-card-actions>
          <v-spacer/>
          <v-btn @click="dialogDettaglio = false">Chiudi</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { usePresenzeStore } from '@/stores/presenze'
import { presenzeApi } from '@/api/api'

const store = usePresenzeStore()
const filtri = ref({ campagna_id: null, mese_da: null, mese_a: null, funzione: null, comando: null })
const ricerca = ref('')
const dialogDettaglio = ref(false)
const dettaglioDip = ref(null)
const presenzeDettaglio = ref([])
const loadingDettaglio  = ref(false)

// Funzioni disponibili estratte dai dati caricati
const funzioniDisponibili = computed(() => {
  const set = new Set()
  store.monteOre.forEach(r => Object.keys(r.ore_per_funzione || {}).forEach(f => set.add(f)))
  return [...set].sort()
})

// Filtra per funzione e comando lato client
const monteOreFiltrato = computed(() => {
  let rows = store.monteOre

  // Filtro comando: il backend aggiunge comando_id al personale aggregato
  if (filtri.value.comando) {
    rows = rows.filter(r => r.comando_id === filtri.value.comando)
  }

  // Filtro funzione
  const f = filtri.value.funzione
  if (f) {
    rows = rows
      .filter(r => r.ore_per_funzione && r.ore_per_funzione[f] > 0)
      .map(r => ({ ...r, ore_totali: r.ore_per_funzione[f] || 0, turni_totali: undefined }))
  }

  return rows
})

const oreTotaliSomma = computed(() =>
  monteOreFiltrato.value.reduce((s, r) => s + (r.ore_totali || 0), 0)
)
const turniTotaliSomma = computed(() =>
  monteOreFiltrato.value.reduce((s, r) => s + (r.turni_totali || 0), 0)
)
const mediaOre = computed(() =>
  monteOreFiltrato.value.length ? Math.round(oreTotaliSomma.value / monteOreFiltrato.value.length) : 0
)

const headers = [
  { title: 'Qualifica', key: 'qualifica', sortable: true },
  { title: 'Cognome',   key: 'cognome',   sortable: true },
  { title: 'Nome',      key: 'nome',      sortable: true },
  { title: 'Turni',   key: 'turni_totali', sortable: true },
  { title: 'Ore tot.', key: 'ore_totali', sortable: true },
  { title: 'Per funzione', key: 'ore_per_funzione', sortable: false },
  { title: '',        key: 'actions', sortable: false, align: 'end' },
]

const headersDettaglio = [
  { title: 'Data',       key: 'data_servizio' },
  { title: 'Funzione',   key: 'funzione' },
  { title: 'Postazione', key: 'postazione' },
  { title: 'Inizio',     key: 'orario_inizio' },
  { title: 'Fine',       key: 'orario_fine' },
  { title: 'Ore',        key: 'ore_totali' },
  { title: 'Stato',      key: 'stato' },
]

function statoColor(s) {
  return { programmato:'blue', confermato:'green', modificato:'orange', assente:'red' }[s] || 'grey'
}

function onCampagnaChange(id) {
  const c = store.campagne.find(x => x.id === id)
  if (!c) return
  // Imposta mese iniziale e finale della campagna
  filtri.value.mese_da = c.data_inizio?.slice(0, 7) || null
  filtri.value.mese_a  = c.data_fine?.slice(0, 7)   || null
}

async function carica() {
  const f = {}
  if (filtri.value.campagna_id) f.campagna_id = filtri.value.campagna_id
  // Converti mese (YYYY-MM) in date complete
  if (filtri.value.mese_da) f.data_da = filtri.value.mese_da + '-01'
  if (filtri.value.mese_a)  f.data_a  = filtri.value.mese_a  + '-31'
  await store.caricaMonteOre(f)
}

async function apriDettaglio(dip) {
  dettaglioDip.value = dip
  dialogDettaglio.value = true
  loadingDettaglio.value = true
  const { data } = await presenzeApi.lista({ personale_id: dip.personale_id })
  presenzeDettaglio.value = data || []
  loadingDettaglio.value = false
}

function esporta() {
  const rows = store.monteOre.map(r => ({
    cognome: r.cognome, nome: r.nome, qualifica: r.qualifica,
    turni: r.turni_totali, ore_tot: r.ore_totali,
    ...r.ore_per_funzione
  }))
  const keys = Object.keys(rows[0] || {})
  const csv  = [keys.join(';'), ...rows.map(r => keys.map(k => r[k] ?? '').join(';'))].join('\n')
  const blob = new Blob(['\ufeff' + csv], { type: 'text/csv;charset=utf-8;' })
  const url  = URL.createObjectURL(blob)
  const a    = document.createElement('a')
  a.href = url; a.download = `monte_ore_aib2026.csv`; a.click()
  URL.revokeObjectURL(url)
}

onMounted(carica)
</script>
