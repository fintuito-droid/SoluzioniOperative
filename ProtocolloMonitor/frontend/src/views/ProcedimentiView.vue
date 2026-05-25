<template>
  <v-container fluid class="pa-4">
    <v-card class="mb-4" rounded="xl" elevation="2">
      <v-card-title class="text-subtitle-1 font-weight-bold">
        Filtri
      </v-card-title>

      <v-card-text>
        <v-row>
          <v-col cols="12" md="5">
            <v-text-field
              v-model="filtri.testo"
              label="Cerca procedimento"
              variant="outlined"
              density="compact"
              clearable
              hide-details
            />
          </v-col>

          <v-col cols="12" md="3">
            <v-select
              v-model="filtri.stato"
              :items="statiDisponibili"
              label="Stato"
              variant="outlined"
              density="compact"
              clearable
              hide-details
            />
          </v-col>

          <v-col cols="12" md="3">
            <v-select
              v-model="filtri.priorita"
              :items="prioritaDisponibili"
              label="Priorita"
              variant="outlined"
              density="compact"
              clearable
              hide-details
            />
          </v-col>

          <v-col cols="12" md="1" class="d-flex align-center">
            <v-btn
              color="primary"
              variant="flat"
              block
              :loading="loading"
              @click="caricaProcedimenti"
            >
              Aggiorna
            </v-btn>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <v-alert
      v-if="errore"
      type="warning"
      variant="tonal"
      class="mb-4"
    >
      {{ errore }}
    </v-alert>

    <v-card rounded="xl" elevation="2" class="card-procedimenti">
      <v-card-title class="d-flex align-center justify-space-between">
        <span class="text-subtitle-1 font-weight-bold">
          Procedimenti
        </span>

        <v-chip color="primary" variant="tonal">
          {{ procedimentiFiltrati.length }} record
        </v-chip>
      </v-card-title>

      <v-data-table
        :headers="headers"
        :items="procedimentiFiltrati"
        :loading="loading"
        item-value="idProcedimento"
        density="compact"
        fixed-header
        hover
        class="tabella-procedimenti"
        @click:row="apriDettaglio"
      >
        <template #no-data>
          <div class="pa-6 text-medium-emphasis">
            Nessun procedimento disponibile.
          </div>
        </template>

        <template #item.CodiceProcedimento="{ item }">
          <span class="font-weight-bold">
            {{ item.CodiceProcedimento || '-' }}
          </span>
        </template>

        <template #item.StatoProcedimento="{ item }">
          <v-chip
            :color="coloreStato(item.StatoProcedimento)"
            size="x-small"
            variant="tonal"
          >
            {{ item.StatoProcedimento || 'Non definito' }}
          </v-chip>
        </template>

        <template #item.Priorita="{ item }">
          <v-chip
            :color="colorePriorita(item.Priorita)"
            size="x-small"
            variant="tonal"
          >
            {{ item.Priorita || 'Normale' }}
          </v-chip>
        </template>

        <template #item.NumeroProtocolli="{ item }">
          <v-chip color="indigo" size="x-small" variant="tonal">
            {{ item.NumeroProtocolli }}
          </v-chip>
        </template>
      </v-data-table>
    </v-card>
  </v-container>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

import { listProcedimenti } from '../services/procedimentoApi'

const router = useRouter()

const procedimenti = ref([])
const loading = ref(false)
const errore = ref('')

const filtri = reactive({
  testo: '',
  stato: null,
  priorita: null
})

const headers = [
  { title: 'CodiceProcedimento', key: 'CodiceProcedimento' },
  { title: 'Titolo', key: 'Titolo' },
  { title: 'AziendaSoggetto', key: 'AziendaSoggetto' },
  { title: 'ComandoCompetenza', key: 'ComandoCompetenza' },
  { title: 'SettoreCompetenza', key: 'SettoreCompetenza' },
  { title: 'StatoProcedimento', key: 'StatoProcedimento' },
  { title: 'Priorita', key: 'Priorita' },
  { title: 'DataScadenza', key: 'DataScadenza' },
  { title: 'NumeroProtocolli', key: 'NumeroProtocolli', align: 'end' }
]

const procedimentiNormalizzati = computed(() => {
  return procedimenti.value.map(normalizzaProcedimento)
})

const statiDisponibili = computed(() => {
  return valoriUnici('StatoProcedimento')
})

const prioritaDisponibili = computed(() => {
  return valoriUnici('Priorita')
})

const procedimentiFiltrati = computed(() => {
  const testo = String(filtri.testo || '').toLowerCase()

  return procedimentiNormalizzati.value.filter((procedimento) => {
    const matchTesto =
      !testo ||
      [
        procedimento.CodiceProcedimento,
        procedimento.Titolo,
        procedimento.AziendaSoggetto,
        procedimento.ComandoCompetenza,
        procedimento.SettoreCompetenza
      ].some((valore) => String(valore || '').toLowerCase().includes(testo))

    const matchStato =
      !filtri.stato || procedimento.StatoProcedimento === filtri.stato

    const matchPriorita =
      !filtri.priorita || procedimento.Priorita === filtri.priorita

    return matchTesto && matchStato && matchPriorita
  })
})

function valoriUnici(campo) {
  return Array.from(
    new Set(
      procedimentiNormalizzati.value
        .map((procedimento) => procedimento[campo])
        .filter(Boolean)
    )
  )
}

function normalizzaProcedimento(procedimento) {
  return {
    idProcedimento:
      procedimento.id_procedimento ??
      procedimento.IDProcedimento ??
      procedimento.idProcedimento,
    CodiceProcedimento:
      procedimento.codice_procedimento ??
      procedimento.CodiceProcedimento ??
      '',
    Titolo:
      procedimento.titolo ??
      procedimento.Titolo ??
      '',
    AziendaSoggetto:
      procedimento.azienda_soggetto ??
      procedimento.AziendaSoggetto ??
      '',
    ComandoCompetenza:
      procedimento.comando_competenza ??
      procedimento.ComandoCompetenza ??
      '',
    SettoreCompetenza:
      procedimento.settore_competenza ??
      procedimento.SettoreCompetenza ??
      '',
    StatoProcedimento:
      procedimento.stato_procedimento ??
      procedimento.StatoProcedimento ??
      '',
    Priorita:
      procedimento.priorita ??
      procedimento.Priorita ??
      '',
    DataScadenza:
      procedimento.data_scadenza ??
      procedimento.DataScadenza ??
      '',
    NumeroProtocolli:
      procedimento.protocolli_collegati ??
      procedimento.NumeroProtocolli ??
      procedimento.numero_protocolli ??
      0
  }
}

async function caricaProcedimenti() {
  loading.value = true
  errore.value = ''

  try {
    procedimenti.value = await listProcedimenti()
  } catch {
    errore.value = 'Impossibile caricare i procedimenti da FastAPI.'
    procedimenti.value = []
  } finally {
    loading.value = false
  }
}

function apriDettaglio(event, row) {
  const idProcedimento = row.item.idProcedimento

  if (!idProcedimento) return

  router.push(`/protocollo-monitor/procedimenti/${idProcedimento}`)
}

function colorePriorita(valore) {
  switch (valore) {
    case 'Urgente':
      return 'red'
    case 'Alta':
      return 'orange'
    case 'Bassa':
      return 'grey'
    default:
      return 'green'
  }
}

function coloreStato(valore) {
  switch (valore) {
    case 'Chiuso':
    case 'CHIUSO':
      return 'green'
    case 'Sospeso':
    case 'SOSPESO':
      return 'orange'
    case 'Aperto':
    case 'APERTO':
      return 'blue'
    default:
      return 'grey'
  }
}

onMounted(() => {
  caricaProcedimenti()
})
</script>

<style scoped>
.card-procedimenti {
  min-height: 640px;
}

.tabella-procedimenti {
  width: 100% !important;
}

.tabella-procedimenti :deep(table) {
  width: 100% !important;
  table-layout: fixed;
}

:deep(thead th) {
  color: #42a5f5 !important;
  font-weight: 800 !important;
  font-size: 0.72rem !important;
  letter-spacing: 0;
}

:deep(tbody tr) {
  cursor: pointer;
}

:deep(tbody tr:hover td) {
  background-color: #fff8c6 !important;
}
</style>
