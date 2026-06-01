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

        <div class="d-flex align-center ga-2">
          <v-chip color="primary" variant="tonal">
            {{ procedimentiFiltrati.length }} record
          </v-chip>

          <v-btn
            color="primary"
            variant="flat"
            size="small"
            prepend-icon="mdi-plus"
            @click="apriDialogNuovoProcedimento"
          >
            Nuovo procedimento
          </v-btn>
        </div>
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

    <v-dialog
      v-model="dialogNuovoProcedimento"
      max-width="780"
      persistent
    >
      <v-card rounded="xl">
        <v-card-title class="text-subtitle-1 font-weight-bold">
          Nuovo procedimento
        </v-card-title>

        <v-card-text>
          <v-alert
            v-if="erroreCreazione"
            type="error"
            variant="tonal"
            density="compact"
            class="mb-4"
          >
            {{ erroreCreazione }}
          </v-alert>

          <v-form ref="formNuovoProcedimentoRef">
            <v-row>
              <v-col cols="12" md="8">
                <v-text-field
                  v-model="nuovoProcedimento.Titolo"
                  label="Titolo"
                  variant="outlined"
                  density="compact"
                  :rules="[regole.obbligatorio]"
                  autofocus
                />
              </v-col>

              <v-col cols="12" md="4">
                <v-text-field
                  v-model="nuovoProcedimento.CodiceProcedimento"
                  label="Codice procedimento"
                  variant="outlined"
                  density="compact"
                  hint="Opzionale"
                  persistent-hint
                />
              </v-col>

              <v-col cols="12" md="6">
                <v-text-field
                  v-model="nuovoProcedimento.AziendaSoggetto"
                  label="Azienda/Soggetto"
                  variant="outlined"
                  density="compact"
                />
              </v-col>

              <v-col cols="12" md="3">
                <v-text-field
                  v-model="nuovoProcedimento.ComandoCompetenza"
                  label="Comando competenza"
                  variant="outlined"
                  density="compact"
                />
              </v-col>

              <v-col cols="12" md="3">
                <v-text-field
                  v-model="nuovoProcedimento.SettoreCompetenza"
                  label="Settore competenza"
                  variant="outlined"
                  density="compact"
                />
              </v-col>

              <v-col cols="12" md="4">
                <v-text-field
                  v-model="nuovoProcedimento.TipologiaProcedimento"
                  label="Tipologia procedimento"
                  variant="outlined"
                  density="compact"
                />
              </v-col>

              <v-col cols="12" md="4">
                <v-select
                  v-model="nuovoProcedimento.Priorita"
                  :items="prioritaCreazione"
                  label="Priorita"
                  variant="outlined"
                  density="compact"
                />
              </v-col>

              <v-col cols="12" md="4">
                <v-text-field
                  v-model="nuovoProcedimento.DataScadenza"
                  label="Data scadenza"
                  type="date"
                  variant="outlined"
                  density="compact"
                />
              </v-col>

              <v-col cols="12">
                <v-textarea
                  v-model="nuovoProcedimento.Descrizione"
                  label="Descrizione"
                  variant="outlined"
                  rows="3"
                  auto-grow
                />
              </v-col>

              <v-col cols="12">
                <v-textarea
                  v-model="nuovoProcedimento.NoteInterne"
                  label="Note interne"
                  variant="outlined"
                  rows="2"
                  auto-grow
                />
              </v-col>
            </v-row>
          </v-form>
        </v-card-text>

        <v-card-actions class="justify-end">
          <v-btn
            variant="text"
            :disabled="creazioneInCorso"
            @click="chiudiDialogNuovoProcedimento"
          >
            Annulla
          </v-btn>
          <v-btn
            color="primary"
            variant="flat"
            :loading="creazioneInCorso"
            @click="creaNuovoProcedimento"
          >
            Crea
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-snackbar
      v-model="snackbarCreazione"
      color="success"
      timeout="3500"
    >
      Procedimento creato.
    </v-snackbar>
  </v-container>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

import { createProcedimento, listProcedimenti } from '../services/procedimentoApi'

const router = useRouter()

const procedimenti = ref([])
const loading = ref(false)
const errore = ref('')
const dialogNuovoProcedimento = ref(false)
const formNuovoProcedimentoRef = ref(null)
const creazioneInCorso = ref(false)
const erroreCreazione = ref('')
const snackbarCreazione = ref(false)

const nuovoProcedimento = reactive(creaModelloNuovoProcedimento())

const filtri = reactive({
  testo: '',
  stato: null,
  priorita: null
})

const prioritaCreazione = ['NORMALE', 'BASSA', 'MEDIA', 'ALTA', 'URGENTE']
const regole = {
  obbligatorio: (value) => Boolean(String(value || '').trim()) || 'Campo obbligatorio'
}

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

function creaModelloNuovoProcedimento() {
  return {
    Titolo: '',
    CodiceProcedimento: '',
    AziendaSoggetto: '',
    ComandoCompetenza: '',
    SettoreCompetenza: '',
    TipologiaProcedimento: '',
    Priorita: 'NORMALE',
    DataScadenza: '',
    Descrizione: '',
    NoteInterne: ''
  }
}

function resetNuovoProcedimento() {
  Object.assign(nuovoProcedimento, creaModelloNuovoProcedimento())
}

function apriDialogNuovoProcedimento() {
  erroreCreazione.value = ''
  resetNuovoProcedimento()
  dialogNuovoProcedimento.value = true
}

function chiudiDialogNuovoProcedimento() {
  if (creazioneInCorso.value) return

  dialogNuovoProcedimento.value = false
  erroreCreazione.value = ''
}

async function creaNuovoProcedimento() {
  const validation = await formNuovoProcedimentoRef.value?.validate()
  if (validation && !validation.valid) return

  creazioneInCorso.value = true
  erroreCreazione.value = ''

  try {
    const creato = await createProcedimento(pulisciPayloadProcedimento(
      nuovoProcedimento
    ))
    dialogNuovoProcedimento.value = false
    snackbarCreazione.value = true
    await caricaProcedimenti()

    const idProcedimento =
      creato?.id_procedimento ?? creato?.IDProcedimento ?? creato?.idProcedimento
    if (idProcedimento) {
      router.push(`/protocollo-monitor/procedimenti/${idProcedimento}`)
    }
  } catch (error) {
    erroreCreazione.value = messaggioErroreCreazione(error)
  } finally {
    creazioneInCorso.value = false
  }
}

function pulisciPayloadProcedimento(payload) {
  return Object.fromEntries(
    Object.entries(payload).map(([key, value]) => [
      key,
      typeof value === 'string' ? value.trim() || null : value
    ])
  )
}

function messaggioErroreCreazione(error) {
  const dettaglio = error?.payload?.detail
  if (typeof dettaglio === 'string') return dettaglio

  return 'Impossibile creare il procedimento.'
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
