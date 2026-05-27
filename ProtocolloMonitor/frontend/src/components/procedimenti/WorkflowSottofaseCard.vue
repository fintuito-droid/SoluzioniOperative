<template>
  <v-card rounded="lg" variant="outlined" class="workflow-sottofase-card">
    <v-card-title class="d-flex flex-wrap align-center justify-space-between ga-3">
      <span class="text-subtitle-1 font-weight-bold">
        Workflow operativo
      </span>

      <v-chip color="primary" variant="tonal" size="small">
        {{ percentuale }}%
      </v-chip>
    </v-card-title>

    <v-divider />

    <v-card-text>
      <v-skeleton-loader
        v-if="loading"
        type="list-item-avatar-three-line, list-item-avatar-three-line, actions"
      />

      <v-alert
        v-else-if="errore"
        type="warning"
        variant="tonal"
        density="compact"
      >
        {{ errore }}
      </v-alert>

      <template v-else-if="workflow">
        <v-progress-linear
          :model-value="percentuale"
          color="primary"
          height="8"
          rounded
          class="mb-4"
        />

        <div class="workflow-steps">
          <div
            v-for="step in workflow.workflow"
            :key="step.codice"
            class="workflow-step"
            :class="{ 'workflow-step-attivo': step.attivo }"
          >
            <v-avatar
              :color="coloreStep(step)"
              size="34"
            >
              <v-icon color="white" size="20">
                {{ iconaStep(step) }}
              </v-icon>
            </v-avatar>

            <div class="workflow-step-body">
              <div class="d-flex flex-wrap align-center ga-2">
                <div class="font-weight-bold">
                  {{ step.ordine }}. {{ step.titolo }}
                </div>

                <v-chip
                  v-if="step.attivo"
                  color="blue"
                  size="x-small"
                  variant="flat"
                >
                  Attivo
                </v-chip>
              </div>

              <div class="text-caption text-medium-emphasis">
                <span v-if="step.operatore">
                  Operatore: {{ step.operatore }}
                </span>
                <span v-else>
                  Operatore: -
                </span>
              </div>

              <div class="text-caption text-medium-emphasis">
                Data: {{ formattaDataOra(step.timestamp) }}
              </div>
            </div>
          </div>
        </div>

        <v-divider class="my-4" />

        <section>
          <div class="text-subtitle-2 font-weight-bold mb-3">
            Azioni disponibili
          </div>

          <div class="azioni-workflow">
            <v-tooltip
              v-for="azione in azioniWorkflow"
              :key="azione.codice"
              location="top"
              :text="azione.tooltip"
            >
              <template #activator="{ props: tooltipProps }">
                <span
                  v-bind="tooltipProps"
                  class="azione-tooltip-wrapper"
                >
                  <v-btn
                    :color="azione.disponibile ? azione.colore : 'grey'"
                    :disabled="!azione.disponibile || richiestaInCorso"
                    :prepend-icon="azione.icona"
                    size="small"
                    variant="tonal"
                    @click="apriDialogAzione(azione)"
                  >
                    {{ azione.titolo }}
                  </v-btn>
                </span>
              </template>
            </v-tooltip>
          </div>

          <v-alert
            v-if="messaggioSuccesso"
            type="success"
            variant="tonal"
            density="compact"
            class="mt-3"
          >
            {{ messaggioSuccesso }}
          </v-alert>

          <v-alert
            v-if="erroreAzione"
            type="warning"
            variant="tonal"
            density="compact"
            class="mt-3"
          >
            {{ erroreAzione }}
          </v-alert>

          <v-alert
            type="info"
            variant="tonal"
            density="compact"
            class="mt-3"
          >
            Le azioni registrano l'avanzamento tramite il backend e richiedono backup Access automatico.
          </v-alert>
        </section>
      </template>

      <v-alert
        v-else
        type="info"
        variant="tonal"
        density="compact"
      >
        Seleziona una sottofase per leggere il workflow operativo.
      </v-alert>
    </v-card-text>
  </v-card>

  <v-dialog
    v-model="dialogAzione"
    max-width="560"
    persistent
  >
    <v-card rounded="lg">
      <v-card-title class="text-subtitle-1 font-weight-bold">
        Azione guidata
      </v-card-title>

      <v-card-text>
        <v-alert
          v-if="erroreDialog"
          type="warning"
          variant="tonal"
          density="compact"
          class="mb-4"
        >
          {{ erroreDialog }}
        </v-alert>

        <v-alert
          type="info"
          variant="tonal"
          density="compact"
          class="mb-4"
        >
          L'azione verra registrata sul workflow della sottofase usando l'endpoint backend reale.
        </v-alert>

        <v-row dense>
          <v-col cols="12" sm="6">
            <div class="label-azione">Azione selezionata</div>
            <div class="value-azione">
              {{ azioneSelezionata?.titolo || '-' }}
            </div>
          </v-col>

          <v-col cols="12" sm="6">
            <div class="label-azione">Sottofase interessata</div>
            <div class="value-azione">
              {{ sottofaseLabel }}
            </div>
          </v-col>

          <v-col cols="12" sm="6">
            <div class="label-azione">Operatore provvisorio</div>
            <div class="value-azione">
              {{ UTENTE_OPERATORE_PROVVISORIO }}
            </div>
          </v-col>

          <v-col cols="12">
            <v-textarea
              v-model="testoOperatore"
              auto-grow
              density="compact"
              hide-details
              label="Testo libero operatore"
              rows="3"
              variant="outlined"
            />
          </v-col>
        </v-row>
      </v-card-text>

      <v-card-actions>
        <v-spacer />

        <v-btn
          variant="text"
          :disabled="richiestaInCorso"
          @click="annullaDialogAzione"
        >
          Annulla
        </v-btn>

        <v-btn
          color="primary"
          :disabled="!azioneSelezionata || richiestaInCorso"
          :loading="richiestaInCorso"
          variant="flat"
          @click="confermaAzioneWorkflow"
        >
          Conferma
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { computed, ref, watch } from 'vue'

import {
  eseguiAzioneWorkflowSottofase,
  getWorkflowSottofase
} from '../../services/procedimentoApi'

const emit = defineEmits(['workflow-aggiornato'])

const props = defineProps({
  idSottofase: {
    type: [Number, String],
    default: null
  },
  titoloSottofase: {
    type: String,
    default: ''
  }
})

const loading = ref(false)
const errore = ref('')
const workflow = ref(null)
const dialogAzione = ref(false)
const azioneSelezionata = ref(null)
const testoOperatore = ref('')
const richiestaInCorso = ref(false)
const erroreDialog = ref('')
const erroreAzione = ref('')
const messaggioSuccesso = ref('')

const UTENTE_OPERATORE_PROVVISORIO = 'Francesco Matranga'

const AZIONI_WORKFLOW = [
  {
    codice: 'AVVIA_REDAZIONE',
    step: 'REDIGI',
    titolo: 'Avvia redazione',
    icona: 'mdi-file-edit-outline',
    colore: 'primary'
  },
  {
    codice: 'INVIA_REVISIONE',
    step: 'REVISIONA',
    titolo: 'Invia a revisione',
    icona: 'mdi-send-check-outline',
    colore: 'blue'
  },
  {
    codice: 'SEGNA_FIRMATO',
    step: 'FIRMA',
    titolo: 'Segna come firmato',
    icona: 'mdi-draw-pen',
    colore: 'deep-purple'
  },
  {
    codice: 'SEGNA_PROTOCOLLATO',
    step: 'PROTOCOLLA',
    titolo: 'Segna come protocollato',
    icona: 'mdi-stamper',
    colore: 'teal'
  },
  {
    codice: 'CHIUDI_SOTTOFASE',
    step: 'FINE',
    titolo: 'Chiudi sottofase',
    icona: 'mdi-check-circle-outline',
    colore: 'green'
  }
]

const percentuale = computed(() => {
  return workflow.value?.percentualeAvanzamento ?? 0
})

const stepAttivo = computed(() => {
  return workflow.value?.workflow?.find((step) => step.attivo) || null
})

const azioniWorkflow = computed(() => {
  return AZIONI_WORKFLOW.map((azione) => {
    const disponibile = stepAttivo.value?.codice === azione.step

    return {
      ...azione,
      disponibile,
      tooltip: tooltipAzione(azione, disponibile)
    }
  })
})

const sottofaseLabel = computed(() => {
  if (props.titoloSottofase) return props.titoloSottofase
  if (props.idSottofase) return `Sottofase ${props.idSottofase}`

  return '-'
})

watch(
  () => props.idSottofase,
  () => {
    resetStatoAzione()
    caricaWorkflowSottofase()
  },
  { immediate: true }
)

async function caricaWorkflowSottofase() {
  if (!props.idSottofase) {
    workflow.value = null
    errore.value = ''
    return
  }

  loading.value = true
  errore.value = ''

  try {
    const response = await getWorkflowSottofase(props.idSottofase)
    workflow.value = normalizzaWorkflow(response)
  } catch (error) {
    workflow.value = null
    errore.value =
      error.status === 404
        ? 'Sottofase non trovata.'
        : 'Impossibile caricare il workflow operativo.'
  } finally {
    loading.value = false
  }
}

function normalizzaWorkflow(dato = {}) {
  return {
    stepCorrente: dato.stepCorrente ?? dato.step_corrente ?? 1,
    percentualeAvanzamento:
      dato.percentualeAvanzamento ?? dato.percentuale_avanzamento ?? 0,
    workflow: Array.isArray(dato.workflow)
      ? dato.workflow.map(normalizzaStep).sort(confrontaOrdine)
      : []
  }
}

function normalizzaStep(step = {}) {
  return {
    codice: step.codice ?? '',
    titolo: step.titolo ?? step.codice ?? 'Step',
    ordine: step.ordine ?? 0,
    completato: Boolean(step.completato),
    attivo: Boolean(step.attivo),
    timestamp: step.timestamp ?? null,
    operatore: step.operatore ?? ''
  }
}

function confrontaOrdine(a, b) {
  return Number(a?.ordine ?? 0) - Number(b?.ordine ?? 0)
}

function coloreStep(step) {
  if (step.completato) return 'green'
  if (step.attivo) return 'blue'
  return 'grey'
}

function iconaStep(step) {
  if (step.completato) return 'mdi-check'
  if (step.attivo) return 'mdi-progress-clock'
  return 'mdi-circle-outline'
}

function tooltipAzione(azione, disponibile) {
  if (richiestaInCorso.value) {
    return 'Richiesta in corso: attendi il completamento dell azione.'
  }

  if (disponibile) {
    return 'Azione disponibile per lo step attivo.'
  }

  return tooltipAzioneNonDisponibile(azione)
}

function tooltipAzioneNonDisponibile(azione) {
  if (!stepAttivo.value) {
    return 'Azione non disponibile: il workflow non ha uno step attivo.'
  }

  return `Azione disponibile solo quando lo step attivo e ${labelStep(azione.step)}.`
}

function labelStep(value) {
  const labels = {
    REDIGI: 'Redigi',
    REVISIONA: 'Revisiona',
    FIRMA: 'Firma',
    PROTOCOLLA: 'Protocolla',
    FINE: 'Fine'
  }

  return labels[value] || value || 'non definito'
}

function apriDialogAzione(azione) {
  if (!azione?.disponibile || richiestaInCorso.value) return

  azioneSelezionata.value = azione
  testoOperatore.value = ''
  erroreDialog.value = ''
  erroreAzione.value = ''
  messaggioSuccesso.value = ''
  dialogAzione.value = true
}

function annullaDialogAzione() {
  if (richiestaInCorso.value) return

  dialogAzione.value = false
  azioneSelezionata.value = null
  testoOperatore.value = ''
  erroreDialog.value = ''
}

async function confermaAzioneWorkflow() {
  if (!azioneSelezionata.value || richiestaInCorso.value) return

  richiestaInCorso.value = true
  erroreDialog.value = ''
  erroreAzione.value = ''
  messaggioSuccesso.value = ''

  try {
    const response = await eseguiAzioneWorkflowSottofase(props.idSottofase, {
      azione: azioneSelezionata.value.codice,
      testoOperatore: testoOperatore.value || null,
      utenteOperatore: UTENTE_OPERATORE_PROVVISORIO
    })

    if (response?.workflow) {
      workflow.value = normalizzaWorkflow(response.workflow)
    } else {
      await caricaWorkflowSottofase()
    }

    messaggioSuccesso.value = 'Azione workflow registrata correttamente.'
    dialogAzione.value = false
    azioneSelezionata.value = null
    testoOperatore.value = ''

    emit('workflow-aggiornato', {
      idSottofase: props.idSottofase,
      azione: response?.azione,
      workflow: response?.workflow,
      backupCreato: response?.backupCreato
    })
  } catch (error) {
    erroreDialog.value = messaggioErroreWorkflow(error)
    erroreAzione.value = erroreDialog.value
  } finally {
    richiestaInCorso.value = false
  }
}

function messaggioErroreWorkflow(error) {
  const dettaglio = error?.payload?.detail

  if (error?.status === 400) {
    return dettaglio || 'Azione non valida per lo stato corrente della sottofase.'
  }

  if (error?.status === 404) {
    return 'Sottofase non trovata.'
  }

  if (error?.status === 500) {
    return dettaglio || 'Errore tecnico durante la registrazione del workflow.'
  }

  return 'Impossibile registrare l azione workflow.'
}

function resetStatoAzione() {
  dialogAzione.value = false
  azioneSelezionata.value = null
  testoOperatore.value = ''
  richiestaInCorso.value = false
  erroreDialog.value = ''
  erroreAzione.value = ''
  messaggioSuccesso.value = ''
}

function formattaDataOra(value) {
  if (!value) return '-'

  const date = new Date(value)

  if (Number.isNaN(date.getTime())) return value

  return new Intl.DateTimeFormat('it-IT', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).format(date)
}
</script>

<style scoped>
.workflow-sottofase-card {
  background: #ffffff;
}

.workflow-steps {
  display: grid;
  gap: 10px;
}

.workflow-step {
  align-items: flex-start;
  border: 1px solid rgba(0, 0, 0, 0.07);
  border-radius: 8px;
  display: flex;
  gap: 12px;
  padding: 10px 12px;
}

.workflow-step-attivo {
  background: rgba(25, 118, 210, 0.07);
  border-color: rgba(25, 118, 210, 0.32);
}

.workflow-step-body {
  min-width: 0;
}

.azioni-workflow {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.azione-tooltip-wrapper {
  display: inline-flex;
}

.label-azione {
  color: #6b7280;
  font-size: 0.74rem;
  margin-bottom: 4px;
}

.value-azione {
  font-size: 0.92rem;
  font-weight: 700;
}
</style>
