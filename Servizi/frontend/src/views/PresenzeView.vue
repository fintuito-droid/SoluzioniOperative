<template>
  <div>
    <!-- Intestazione -->
    <div class="d-flex align-center mb-4 flex-wrap gap-2">
      <div>
        <h1 class="text-h5 font-weight-medium">Presenze</h1>
        <p class="text-caption text-medium-emphasis mb-0">
          Campagna AIB {{ store.campagnaAttiva?.anno }}
        </p>
      </div>
      <v-spacer/>
      <v-btn v-if="auth.canPlanificare"
             color="primary" prepend-icon="mdi-plus"
             @click="dialogNuova = true">
        Nuovo turno
      </v-btn>
    </div>

    <!-- Filtri -->
    <v-card class="mb-4" variant="outlined">
      <v-card-text>
        <v-row dense>
          <v-col cols="12" sm="6" md="3">
            <v-select v-model="filtri.postazione_id" :items="store.postazioni"
                      item-title="codice" item-value="id"
                      label="Postazione" clearable density="compact"/>
          </v-col>
          <v-col cols="12" sm="6" md="2">
            <v-select v-model="filtri.stato" :items="statiItems"
                      label="Stato" clearable density="compact"/>
          </v-col>
          <v-col cols="12" sm="6" md="3">
            <v-text-field v-model="filtri.data_da" type="date"
                          label="Dal" density="compact" clearable/>
          </v-col>
          <v-col cols="12" sm="6" md="3">
            <v-text-field v-model="filtri.data_a" type="date"
                          label="Al" density="compact" clearable/>
          </v-col>
          <v-col cols="12" md="1" class="d-flex align-center">
            <v-btn color="primary" variant="tonal" icon="mdi-magnify"
                   @click="carica" :loading="store.loading"/>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- Tabella -->
    <v-card>
      <v-data-table
        :headers="headers"
        :items="store.presenze"
        :loading="store.loading"
        density="comfortable"
        :sort-by="[{ key: 'data_servizio', order: 'desc' }]"
        no-data-text="Nessuna presenza trovata"
        items-per-page-text="Righe per pagina"
      >
        <!-- Stato badge -->
        <template #item.stato="{ item }">
          <v-chip :color="statoColor(item.stato)" size="small" variant="tonal">
            {{ item.stato }}
          </v-chip>
        </template>

        <!-- Dipendente -->
        <template #item.nominativo="{ item }">
          {{ item.cognome }} {{ item.nome_dip }}
          <span class="text-caption text-medium-emphasis ml-1">{{ item.qualifica }}</span>
        </template>

        <!-- Ore -->
        <template #item.ore_totali="{ item }">
          <span class="font-weight-medium">{{ item.ore_totali }}h</span>
        </template>

        <!-- Azioni -->
        <template #item.actions="{ item }">
          <div class="d-flex gap-1">
            <v-btn v-if="auth.canConsuntivare && item.stato === 'programmato'"
                   icon="mdi-check-circle" size="small" variant="text" color="success"
                   title="Consuntiva" @click="apriConsuntivo(item)"/>
            <v-btn v-if="auth.canConsuntivare && item.stato === 'programmato'"
                   icon="mdi-pencil" size="small" variant="text" color="primary"
                   title="Modifica" @click="apriModifica(item)"/>
            <v-btn v-if="auth.isAdmin"
                   icon="mdi-delete" size="small" variant="text" color="error"
                   title="Elimina" @click="confermaElimina(item)"/>
          </div>
        </template>
      </v-data-table>
    </v-card>

    <!-- Dialog nuovo turno -->
    <v-dialog v-model="dialogNuova" max-width="600" persistent>
      <PresenzaForm
        :campagna-id="store.campagnaAttiva?.id"
        :personale-list="personaleList"
        :postazioni="store.postazioni"
        :funzioni="store.funzioni"
        @save="salvaNuova"
        @cancel="dialogNuova = false"
      />
    </v-dialog>

    <!-- Dialog consuntivo -->
    <v-dialog v-model="dialogConsuntivo" max-width="500" persistent>
      <ConsuntivoForm
        v-if="presenzaSelezionata"
        :presenza="presenzaSelezionata"
        @save="salvaConsuntivo"
        @cancel="dialogConsuntivo = false"
      />
    </v-dialog>

    <!-- Snackbar feedback -->
    <v-snackbar v-model="snack.show" :color="snack.color" timeout="3000">
      {{ snack.text }}
    </v-snackbar>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { usePresenzeStore } from '@/stores/presenze'
import { useAuthStore } from '@/stores/auth'
import { personaleApi } from '@/api/api'
import PresenzaForm   from '@/components/PresenzaForm.vue'
import ConsuntivoForm from '@/components/ConsuntivoForm.vue'

const store = usePresenzeStore()
const auth  = useAuthStore()

const filtri = ref({ postazione_id: null, stato: null, data_da: null, data_a: null })
const dialogNuova       = ref(false)
const dialogConsuntivo  = ref(false)
const presenzaSelezionata = ref(null)
const personaleList     = ref([])
const snack = ref({ show: false, text: '', color: 'success' })

const statiItems = ['programmato','confermato','modificato','assente']

const headers = [
  { title: 'Data',        key: 'data_servizio',  sortable: true },
  { title: 'Dipendente',  key: 'nominativo',     sortable: false },
  { title: 'Funzione',    key: 'funzione',        sortable: true },
  { title: 'Postazione',  key: 'postazione',      sortable: true },
  { title: 'Inizio',      key: 'orario_inizio',   sortable: false },
  { title: 'Fine',        key: 'orario_fine',     sortable: false },
  { title: 'Ore',         key: 'ore_totali',      sortable: true },
  { title: 'Stato',       key: 'stato',           sortable: true },
  { title: '',            key: 'actions',          sortable: false, align: 'end' },
]

function statoColor(stato) {
  return { programmato:'blue', confermato:'green', modificato:'orange', assente:'red' }[stato] || 'grey'
}

async function carica() {
  const f = {}
  if (filtri.value.postazione_id) f.postazione_id = filtri.value.postazione_id
  if (filtri.value.stato)         f.stato         = filtri.value.stato
  if (filtri.value.data_da)       f.data_da       = filtri.value.data_da
  if (filtri.value.data_a)        f.data_a        = filtri.value.data_a
  await store.caricaPresenze(f)
}

function apriConsuntivo(item) {
  presenzaSelezionata.value = item
  dialogConsuntivo.value = true
}

function apriModifica(item) {
  presenzaSelezionata.value = { ...item, stato: 'modificato' }
  dialogConsuntivo.value = true
}

async function salvaNuova(data) {
  const { error } = await store.creaPresenza(data)
  dialogNuova.value = false
  showSnack(error ? error : 'Turno creato', error ? 'error' : 'success')
}

async function salvaConsuntivo(data) {
  const { error } = await store.consuntivaPresenza(presenzaSelezionata.value.id, data)
  dialogConsuntivo.value = false
  showSnack(error ? error : 'Consuntivo salvato', error ? 'error' : 'success')
}

async function confermaElimina(item) {
  if (!confirm(`Eliminare il turno di ${item.cognome} del ${item.data_servizio}?`)) return
  const { error } = await store.eliminaPresenza(item.id)
  showSnack(error ? error : 'Turno eliminato', error ? 'error' : 'success')
}

function showSnack(text, color = 'success') {
  snack.value = { show: true, text, color }
}

onMounted(async () => {
  const { data } = await personaleApi.lista()
  if (data) personaleList.value = data
  await carica()
})
</script>
