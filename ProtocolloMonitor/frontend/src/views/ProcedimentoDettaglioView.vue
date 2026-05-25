<template>
  <v-container fluid class="pa-4">
    <v-alert
      v-if="errore"
      type="warning"
      variant="tonal"
      class="mb-4"
    >
      {{ errore }}
    </v-alert>

    <v-row>
      <v-col cols="12" lg="5">
        <v-card rounded="xl" elevation="2" class="h-100">
          <v-card-title class="d-flex align-center justify-space-between">
            <span class="text-subtitle-1 font-weight-bold">
              Informazioni procedimento
            </span>

            <v-btn
              color="primary"
              variant="tonal"
              prepend-icon="mdi-arrow-left"
              density="compact"
              @click="tornaAElenco"
            >
              Elenco
            </v-btn>
          </v-card-title>

          <v-divider />

          <v-card-text>
            <v-alert
              v-if="loading"
              type="info"
              variant="tonal"
            >
              Caricamento procedimento in corso...
            </v-alert>

            <v-row v-else-if="procedimento">
              <v-col cols="12" md="6">
                <div class="label">Codice</div>
                <div class="value">
                  {{ procedimento.CodiceProcedimento || '-' }}
                </div>
              </v-col>

              <v-col cols="12" md="6">
                <div class="label">Stato</div>
                <v-chip
                  :color="coloreStato(procedimento.StatoProcedimento)"
                  size="small"
                  variant="tonal"
                >
                  {{ procedimento.StatoProcedimento || 'Non definito' }}
                </v-chip>
              </v-col>

              <v-col cols="12">
                <div class="label">Titolo</div>
                <div class="value">
                  {{ procedimento.Titolo || '-' }}
                </div>
              </v-col>

              <v-col cols="12">
                <div class="label">Azienda/Soggetto</div>
                <div class="value">
                  {{ procedimento.AziendaSoggetto || '-' }}
                </div>
              </v-col>

              <v-col cols="12" md="6">
                <div class="label">Comando</div>
                <div class="value">
                  {{ procedimento.ComandoCompetenza || '-' }}
                </div>
              </v-col>

              <v-col cols="12" md="6">
                <div class="label">Settore</div>
                <div class="value">
                  {{ procedimento.SettoreCompetenza || '-' }}
                </div>
              </v-col>

              <v-col cols="12" md="6">
                <div class="label">Priorita</div>
                <v-chip
                  :color="colorePriorita(procedimento.Priorita)"
                  size="small"
                  variant="tonal"
                >
                  {{ procedimento.Priorita || 'Normale' }}
                </v-chip>
              </v-col>

              <v-col cols="12" md="6">
                <div class="label">Data scadenza</div>
                <div class="value">
                  {{ procedimento.DataScadenza || '-' }}
                </div>
              </v-col>

              <v-col cols="12">
                <div class="label">Descrizione</div>
                <div class="box-testo">
                  {{ procedimento.Descrizione || 'Nessuna descrizione disponibile.' }}
                </div>
              </v-col>
            </v-row>

            <v-alert v-else type="info" variant="tonal">
              Nessun procedimento disponibile.
            </v-alert>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" lg="7">
        <v-card rounded="xl" elevation="2" class="mb-4">
          <v-card-title class="d-flex align-center justify-space-between">
            <span class="text-subtitle-1 font-weight-bold">
              Protocolli collegati
            </span>

            <v-chip color="indigo" variant="tonal">
              {{ numeroProtocolli }} protocolli
            </v-chip>
          </v-card-title>

          <v-divider />

          <v-data-table
            :headers="headersProtocolli"
            :items="protocolliNormalizzati"
            :loading="loadingProtocolli"
            density="compact"
            fixed-header
            hover
            class="tabella-protocolli"
          >
            <template #no-data>
              <div class="pa-6 text-medium-emphasis">
                Nessun protocollo collegato.
              </div>
            </template>
          </v-data-table>
        </v-card>

        <v-card rounded="xl" elevation="2">
          <v-card-title class="text-subtitle-1 font-weight-bold">
            Evoluzioni operative
          </v-card-title>

          <v-divider />

          <v-card-text>
            <v-row>
              <v-col cols="12" md="4">
                <v-sheet class="placeholder-box" rounded="lg">
                  <v-icon color="primary" class="mb-2">
                    mdi-tag-outline
                  </v-icon>
                  <div class="font-weight-bold">Tag</div>
                </v-sheet>
              </v-col>

              <v-col cols="12" md="4">
                <v-sheet class="placeholder-box" rounded="lg">
                  <v-icon color="orange" class="mb-2">
                    mdi-calendar-clock-outline
                  </v-icon>
                  <div class="font-weight-bold">Scadenze</div>
                </v-sheet>
              </v-col>

              <v-col cols="12" md="4">
                <v-sheet class="placeholder-box" rounded="lg">
                  <v-icon color="indigo" class="mb-2">
                    mdi-source-branch
                  </v-icon>
                  <div class="font-weight-bold">Workflow futuro</div>
                </v-sheet>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import {
  countProtocolliProcedimento,
  getProcedimento,
  listProtocolliProcedimento
} from '../services/procedimentoApi'

const route = useRoute()
const router = useRouter()

const procedimento = ref(null)
const protocolli = ref([])
const numeroProtocolliApi = ref(null)
const loading = ref(false)
const loadingProtocolli = ref(false)
const errore = ref('')

const headersProtocolli = [
  { title: 'Numero protocollo', key: 'NumeroProtocollo' },
  { title: 'Data', key: 'DataProtocollo' },
  { title: 'Oggetto', key: 'Oggetto' },
  { title: 'Modalita', key: 'Modalita' }
]

const idProcedimento = computed(() => route.params.idProcedimento)

const numeroProtocolli = computed(() => {
  return numeroProtocolliApi.value ?? protocolli.value.length
})

const protocolliNormalizzati = computed(() => {
  return protocolli.value.map((protocollo) => ({
    NumeroProtocollo:
      protocollo.numero_protocollo ??
      protocollo.NumeroProtocollo ??
      '',
    DataProtocollo:
      protocollo.data_protocollo ??
      protocollo.DataProtocollo ??
      '',
    Oggetto:
      protocollo.oggetto ??
      protocollo.Oggetto ??
      '',
    Modalita:
      protocollo.modalita ??
      protocollo.Modalita ??
      ''
  }))
})

async function caricaDettaglio() {
  loading.value = true
  loadingProtocolli.value = true
  errore.value = ''

  try {
    const [dettaglio, protocolliCollegati, conteggio] = await Promise.all([
      getProcedimento(idProcedimento.value),
      listProtocolliProcedimento(idProcedimento.value),
      countProtocolliProcedimento(idProcedimento.value)
    ])

    procedimento.value = normalizzaProcedimento(dettaglio)
    protocolli.value = protocolliCollegati
    numeroProtocolliApi.value =
      conteggio.protocolli_collegati ??
      conteggio.NumeroProtocolli ??
      conteggio.count ??
      protocolliCollegati.length
  } catch (error) {
    if (error.status === 404) {
      errore.value = 'Procedimento non trovato.'
    } else {
      errore.value = 'Impossibile caricare il procedimento da FastAPI.'
    }

    procedimento.value = null
    protocolli.value = []
    numeroProtocolliApi.value = 0
  } finally {
    loading.value = false
    loadingProtocolli.value = false
  }
}

function normalizzaProcedimento(dato) {
  if (!dato) return null

  return {
    idProcedimento:
      dato.id_procedimento ??
      dato.IDProcedimento ??
      dato.idProcedimento,
    CodiceProcedimento:
      dato.codice_procedimento ??
      dato.CodiceProcedimento ??
      '',
    Titolo:
      dato.titolo ??
      dato.Titolo ??
      '',
    Descrizione:
      dato.descrizione ??
      dato.Descrizione ??
      '',
    AziendaSoggetto:
      dato.azienda_soggetto ??
      dato.AziendaSoggetto ??
      '',
    ComandoCompetenza:
      dato.comando_competenza ??
      dato.ComandoCompetenza ??
      '',
    SettoreCompetenza:
      dato.settore_competenza ??
      dato.SettoreCompetenza ??
      '',
    StatoProcedimento:
      dato.stato_procedimento ??
      dato.StatoProcedimento ??
      '',
    Priorita:
      dato.priorita ??
      dato.Priorita ??
      '',
    DataScadenza:
      dato.data_scadenza ??
      dato.DataScadenza ??
      ''
  }
}

function tornaAElenco() {
  router.push('/protocollo-monitor/procedimenti')
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
  caricaDettaglio()
})
</script>

<style scoped>
.label {
  font-size: 0.75rem;
  color: #6b7280;
  margin-bottom: 4px;
}

.value {
  font-size: 0.95rem;
  font-weight: 700;
}

.box-testo {
  background: #f8fafc;
  border: 1px solid rgba(0, 0, 0, 0.06);
  border-radius: 10px;
  line-height: 1.55;
  min-height: 90px;
  padding: 12px;
  text-align: left;
}

.tabella-protocolli {
  min-height: 320px;
}

.placeholder-box {
  border: 1px dashed rgba(0, 0, 0, 0.18);
  min-height: 96px;
  padding: 18px;
  text-align: center;
}

:deep(thead th) {
  color: #42a5f5 !important;
  font-weight: 800 !important;
  font-size: 0.72rem !important;
  letter-spacing: 0;
}

:deep(tbody tr:hover td) {
  background-color: #fff8c6 !important;
}
</style>
