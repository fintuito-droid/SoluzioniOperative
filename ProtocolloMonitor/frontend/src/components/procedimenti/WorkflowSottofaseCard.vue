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
</template>

<script setup>
import { computed, ref, watch } from 'vue'

import { getWorkflowSottofase } from '../../services/procedimentoApi'

const props = defineProps({
  idSottofase: {
    type: [Number, String],
    default: null
  }
})

const loading = ref(false)
const errore = ref('')
const workflow = ref(null)

const percentuale = computed(() => {
  return workflow.value?.percentualeAvanzamento ?? 0
})

watch(
  () => props.idSottofase,
  () => {
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
</style>
