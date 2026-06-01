<template>
  <section class="timeline-operativa">
    <div class="timeline-operativa-toolbar">
      <div>
        <div class="text-subtitle-2 font-weight-bold">
          Timeline operativa
        </div>
        <div class="text-caption text-medium-emphasis">
          {{ stepsCompletati }}/{{ steps.length }} step completati
        </div>
      </div>

      <v-chip
        :color="avanzamentoTotale === 100 ? 'green' : 'primary'"
        variant="tonal"
        size="small"
      >
        {{ avanzamentoTotale }}%
      </v-chip>
    </div>

    <v-progress-linear
      :model-value="avanzamentoTotale"
      :color="avanzamentoTotale === 100 ? 'green' : 'primary'"
      height="8"
      rounded
      class="mb-4"
    />

    <v-alert
      v-if="!steps.length"
      type="info"
      variant="tonal"
      density="compact"
    >
      Nessuno step operativo documentale registrato.
    </v-alert>

    <div
      v-else
      class="timeline-operativa-track"
    >
      <article
        v-for="(step, index) in steps"
        :key="step.idStepSottofase || step.codiceStep || index"
        class="timeline-operativa-step"
        :class="`timeline-operativa-step--${classeStatoStep(step.statoStep)}`"
      >
        <div class="timeline-operativa-marker">
          <v-avatar
            :color="coloreStep(step.statoStep)"
            size="34"
          >
            <v-icon
              v-if="stepCompletato(step)"
              color="white"
              size="20"
            >
              mdi-check
            </v-icon>
            <span
              v-else
              class="text-caption font-weight-bold text-white"
            >
              {{ step.ordine || index + 1 }}
            </span>
          </v-avatar>
        </div>

        <v-card
          variant="outlined"
          rounded="lg"
          class="timeline-operativa-card"
        >
          <v-card-text>
            <div class="timeline-step-heading">
              <div class="timeline-step-title">
                {{ labelStep(step.codiceStep) }}
              </div>
              <v-chip
                :color="coloreStep(step.statoStep)"
                variant="tonal"
                size="x-small"
              >
                <v-icon
                  start
                  size="14"
                >
                  {{ iconaStep(step.statoStep) }}
                </v-icon>
                {{ labelStatoStep(step.statoStep) }}
              </v-chip>
            </div>

            <div class="timeline-step-meta">
              <span>Ordine {{ step.ordine || index + 1 }}</span>
              <span v-if="step.dataCompletamento">
                Completato {{ formattaDataOra(step.dataCompletamento) }}
              </span>
            </div>

            <div class="timeline-step-progress">
              <v-progress-linear
                :model-value="avanzamentoPartecipanti(step)"
                :color="coloreStep(step.statoStep)"
                height="6"
                rounded
              />
              <div class="timeline-step-progress-label">
                {{ conteggiPartecipanti(step).completati }}/{{ conteggiPartecipanti(step).totali }}
                partecipanti
              </div>
            </div>

            <div class="timeline-step-stats">
              <v-chip
                color="green"
                variant="tonal"
                size="x-small"
              >
                Obbligatori
                {{ conteggiPartecipanti(step).obbligatoriCompletati }}/{{ conteggiPartecipanti(step).obbligatoriTotali }}
              </v-chip>
              <v-chip
                color="grey"
                variant="tonal"
                size="x-small"
              >
                Facoltativi {{ conteggiPartecipanti(step).facoltativiTotali }}
              </v-chip>
            </div>

            <v-skeleton-loader
              v-if="loadingPartecipanti"
              type="list-item-two-line"
              class="mt-2"
            />

            <div
              v-else-if="partecipantiStep(step).length"
              class="timeline-partecipanti"
            >
              <div
                v-for="partecipante in partecipantiStep(step)"
                :key="partecipante.idPartecipante"
                class="timeline-partecipante-row"
              >
                <v-avatar
                  :color="colorePartecipante(partecipante)"
                  size="30"
                  class="timeline-partecipante-avatar"
                >
                  <span class="text-caption font-weight-bold">
                    {{ partecipante.iniziali || inizialiPartecipante(partecipante.nomeVisualizzato) }}
                  </span>
                </v-avatar>

                <div class="timeline-partecipante-main">
                  <div class="timeline-partecipante-title">
                    {{ partecipante.nomeVisualizzato || 'Partecipante' }}
                  </div>
                  <div class="timeline-partecipante-meta">
                    {{ labelRuoloPartecipante(partecipante.ruolo) }}
                    <span v-if="partecipante.dataAzione">
                      · {{ formattaDataOra(partecipante.dataAzione) }}
                    </span>
                  </div>
                </div>

                <div class="timeline-partecipante-chips">
                  <v-chip
                    :color="coloreStatoPartecipante(partecipante.statoPartecipante)"
                    variant="tonal"
                    size="x-small"
                  >
                    {{ labelStatoPartecipante(partecipante.statoPartecipante) }}
                  </v-chip>
                  <v-chip
                    :color="partecipante.partecipanteObbligatorio ? 'deep-orange' : 'grey'"
                    variant="tonal"
                    size="x-small"
                  >
                    {{ partecipante.partecipanteObbligatorio ? 'Obbligatorio' : 'Facoltativo' }}
                  </v-chip>
                </div>

                <v-btn
                  v-if="partecipanteCompletabile(partecipante)"
                  color="green"
                  variant="tonal"
                  size="small"
                  prepend-icon="mdi-check"
                  :loading="completamentoPartecipanteInCorso === partecipante.idPartecipante"
                  :disabled="completamentoPartecipanteInCorso !== null"
                  @click="$emit('completa-partecipante', step, partecipante)"
                >
                  Completa
                </v-btn>
              </div>
            </div>

            <v-alert
              v-else
              type="info"
              variant="tonal"
              density="compact"
              class="mt-2"
            >
              Nessun partecipante collegato a questo step.
            </v-alert>
          </v-card-text>
        </v-card>
      </article>
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  steps: {
    type: Array,
    default: () => []
  },
  partecipantiPerStep: {
    type: Object,
    default: () => ({})
  },
  loadingPartecipanti: {
    type: Boolean,
    default: false
  },
  completamentoPartecipanteInCorso: {
    type: [Number, String],
    default: null
  }
})

defineEmits(['completa-partecipante'])

const stepsCompletati = computed(() => {
  return props.steps.filter(stepCompletato).length
})

const avanzamentoTotale = computed(() => {
  if (!props.steps.length) return 0

  return Math.round((stepsCompletati.value / props.steps.length) * 100)
})

function partecipantiStep(step) {
  return props.partecipantiPerStep[step?.idStepSottofase] || []
}

function conteggiPartecipanti(step) {
  const partecipanti = partecipantiStep(step)
  const obbligatori = partecipanti.filter(
    (partecipante) => partecipante.partecipanteObbligatorio
  )
  const completati = partecipanti.filter(partecipanteCompletato)
  const obbligatoriCompletati = obbligatori.filter(partecipanteCompletato)
  const facoltativiTotali = partecipanti.length - obbligatori.length

  return {
    totali: partecipanti.length,
    completati: completati.length,
    obbligatoriTotali: obbligatori.length,
    obbligatoriCompletati: obbligatoriCompletati.length,
    facoltativiTotali
  }
}

function avanzamentoPartecipanti(step) {
  const conteggi = conteggiPartecipanti(step)

  if (!conteggi.totali) return stepCompletato(step) ? 100 : 0

  return Math.round((conteggi.completati / conteggi.totali) * 100)
}

function stepCompletato(step) {
  return ['COMPLETATO', 'COMPLETED'].includes(
    String(step?.statoStep || '').toUpperCase()
  )
}

function partecipanteCompletato(partecipante) {
  return ['COMPLETATO', 'COMPLETED'].includes(
    String(partecipante?.statoPartecipante || '').toUpperCase()
  )
}

function partecipanteCompletabile(partecipante) {
  return ['ASSEGNATO', 'IN_ATTESA', 'IN_CORSO'].includes(
    partecipante?.statoPartecipante
  )
}

function labelStep(value) {
  const labels = {
    REDIGI: 'Redigi',
    REVISIONA: 'Revisiona',
    FIRMA: 'Firma',
    PROTOCOLLA: 'Protocolla',
    FINE: 'Fine'
  }

  return labels[value] || value || 'Non definito'
}

function labelStatoStep(value) {
  const labels = {
    NON_AVVIATO: 'Non avviato',
    IN_CORSO: 'In corso',
    ACTIVE: 'Attivo',
    LOCKED: 'Bloccato',
    COMPLETATO: 'Completato',
    COMPLETED: 'Completato',
    BLOCCATO: 'Bloccato',
    CANCELLED: 'Annullato',
    ANNULLATO: 'Annullato'
  }

  return labels[value] || value || 'Non definito'
}

function coloreStep(value) {
  const stato = String(value || '').toUpperCase()

  if (['COMPLETATO', 'COMPLETED'].includes(stato)) return 'green'
  if (['IN_CORSO', 'ACTIVE'].includes(stato)) return 'amber'
  if (['BLOCCATO', 'LOCKED'].includes(stato)) return 'grey'
  if (['CANCELLED', 'ANNULLATO'].includes(stato)) return 'grey-darken-1'

  return 'blue-grey'
}

function classeStatoStep(value) {
  return coloreStep(value).replaceAll('-', '_')
}

function iconaStep(value) {
  const stato = String(value || '').toUpperCase()

  if (['COMPLETATO', 'COMPLETED'].includes(stato)) return 'mdi-check'
  if (['IN_CORSO', 'ACTIVE'].includes(stato)) return 'mdi-progress-clock'
  if (['BLOCCATO', 'LOCKED'].includes(stato)) return 'mdi-lock-outline'
  if (['CANCELLED', 'ANNULLATO'].includes(stato)) return 'mdi-cancel'

  return 'mdi-circle-outline'
}

function labelRuoloPartecipante(value) {
  const labels = {
    OPERATORE: 'Operatore',
    REVISORE: 'Revisore',
    FIRMATARIO: 'Firmatario',
    PROTOCOLLATORE: 'Protocollatore',
    APPROVATORE: 'Approvatore',
    OSSERVATORE: 'Osservatore'
  }

  return labels[value] || value || 'Ruolo non definito'
}

function labelStatoPartecipante(value) {
  const labels = {
    ASSEGNATO: 'Assegnato',
    IN_ATTESA: 'In attesa',
    IN_CORSO: 'In corso',
    COMPLETATO: 'Completato',
    COMPLETED: 'Completato',
    RESPINTO: 'Respinto',
    ANNULLATO: 'Annullato',
    CANCELLED: 'Annullato'
  }

  return labels[value] || value || 'Non definito'
}

function coloreStatoPartecipante(value) {
  const stato = String(value || '').toUpperCase()

  if (['COMPLETATO', 'COMPLETED'].includes(stato)) return 'green'
  if (stato === 'IN_CORSO') return 'amber'
  if (stato === 'RESPINTO') return 'red'
  if (['ANNULLATO', 'CANCELLED'].includes(stato)) return 'grey-darken-1'

  return 'grey'
}

function colorePartecipante(partecipante) {
  if (partecipanteCompletato(partecipante)) {
    return partecipante.coloreAvatar || 'green'
  }

  return coloreStatoPartecipante(partecipante?.statoPartecipante)
}

function inizialiPartecipante(nomeVisualizzato) {
  const parts = String(nomeVisualizzato || '')
    .trim()
    .split(/\s+/)
    .filter(Boolean)

  if (!parts.length) return '?'
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase()

  return `${parts[0][0]}${parts[parts.length - 1][0]}`.toUpperCase()
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
.timeline-operativa-toolbar {
  align-items: center;
  display: flex;
  gap: 12px;
  justify-content: space-between;
  margin-bottom: 10px;
}

.timeline-operativa-track {
  display: grid;
  gap: 14px;
}

.timeline-operativa-step {
  display: grid;
  gap: 10px;
  grid-template-columns: 42px minmax(0, 1fr);
  position: relative;
}

.timeline-operativa-step:not(:last-child)::before {
  background: rgba(31, 41, 55, 0.16);
  bottom: -18px;
  content: "";
  left: 16px;
  position: absolute;
  top: 40px;
  width: 2px;
}

.timeline-operativa-marker {
  align-items: flex-start;
  display: flex;
  justify-content: center;
  padding-top: 10px;
}

.timeline-operativa-card {
  background: #ffffff;
}

.timeline-step-heading {
  align-items: flex-start;
  display: flex;
  gap: 8px;
  justify-content: space-between;
}

.timeline-step-title {
  font-size: 0.95rem;
  font-weight: 800;
  min-width: 0;
}

.timeline-step-meta {
  color: #6b7280;
  display: flex;
  flex-wrap: wrap;
  font-size: 0.74rem;
  gap: 8px;
  margin-top: 2px;
}

.timeline-step-progress {
  margin-top: 10px;
}

.timeline-step-progress-label {
  color: #6b7280;
  font-size: 0.72rem;
  margin-top: 4px;
}

.timeline-step-stats {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 8px;
}

.timeline-partecipanti {
  border-top: 1px solid rgba(0, 0, 0, 0.06);
  display: grid;
  gap: 6px;
  margin-top: 10px;
  padding-top: 8px;
}

.timeline-partecipante-row {
  align-items: center;
  display: grid;
  gap: 8px;
  grid-template-columns: 30px minmax(130px, 1fr) auto auto;
  min-height: 40px;
}

.timeline-partecipante-avatar {
  color: #ffffff;
}

.timeline-partecipante-main {
  min-width: 0;
}

.timeline-partecipante-title {
  font-size: 0.86rem;
  font-weight: 700;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.timeline-partecipante-meta {
  color: #6b7280;
  font-size: 0.72rem;
}

.timeline-partecipante-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  justify-content: flex-end;
}

@media (max-width: 760px) {
  .timeline-operativa-step {
    grid-template-columns: 34px minmax(0, 1fr);
  }

  .timeline-operativa-step:not(:last-child)::before {
    left: 16px;
  }

  .timeline-step-heading {
    align-items: flex-start;
    flex-direction: column;
  }

  .timeline-partecipante-row {
    grid-template-columns: 30px minmax(0, 1fr);
  }

  .timeline-partecipante-chips {
    grid-column: 1 / -1;
    justify-content: flex-start;
  }

  .timeline-partecipante-row .v-btn {
    grid-column: 1 / -1;
    justify-self: start;
  }
}
</style>
