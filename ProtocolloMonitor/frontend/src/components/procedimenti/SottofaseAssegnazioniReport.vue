<template>
  <v-expansion-panels
    v-if="hasReport"
    variant="accordion"
    class="assegnazioni-report"
  >
    <v-expansion-panel>
      <v-expansion-panel-title>
        <div class="assegnazioni-report-title">
          <v-icon :color="reportColor">
            {{ reportIcon }}
          </v-icon>
          <span class="font-weight-bold">Assegnazioni automatiche</span>
          <v-chip
            :color="reportColor"
            variant="tonal"
            size="x-small"
          >
            {{ reportStatusLabel }}
          </v-chip>
        </div>
      </v-expansion-panel-title>

      <v-expansion-panel-text>
        <div class="assegnazioni-summary">
          <v-chip
            color="primary"
            variant="tonal"
            size="small"
          >
            Regole {{ numberOf(report.regole_valutate) }}
          </v-chip>
          <v-chip
            color="green"
            variant="tonal"
            size="small"
          >
            Creati {{ listOf(report.partecipanti_creati).length }}
          </v-chip>
          <v-chip
            color="blue-grey"
            variant="tonal"
            size="small"
          >
            Presenti {{ listOf(report.partecipanti_gia_presenti).length }}
          </v-chip>
          <v-chip
            :color="listOf(report.regole_senza_utenti).length ? 'amber' : 'grey'"
            variant="tonal"
            size="small"
          >
            Saltate {{ skippedCount }}
          </v-chip>
          <v-chip
            :color="errorsCount ? 'red' : 'grey'"
            variant="tonal"
            size="small"
          >
            Anomalie {{ errorsCount }}
          </v-chip>
        </div>

        <v-alert
          v-if="report.success === false"
          type="error"
          variant="tonal"
          density="compact"
          class="mt-3"
        >
          {{ report.errore || 'Applicazione automatica non completata.' }}
        </v-alert>

        <div class="assegnazioni-details">
          <ReportList
            title="Partecipanti creati"
            :items="listOf(report.partecipanti_creati)"
            empty-text="Nessun partecipante creato."
          />

          <ReportList
            title="Partecipanti gia presenti"
            :items="listOf(report.partecipanti_gia_presenti)"
            empty-text="Nessun partecipante gia presente segnalato."
          />

          <ReportList
            title="Regole senza utenti"
            :items="listOf(report.regole_senza_utenti)"
            empty-text="Nessuna regola senza utenti."
          />

          <ReportList
            title="Regole saltate"
            :items="listOf(report.regole_saltate)"
            empty-text="Nessuna regola saltata."
          />

          <ReportList
            title="Anomalie"
            :items="allErrors"
            empty-text="Nessuna anomalia."
          />
        </div>
      </v-expansion-panel-text>
    </v-expansion-panel>
  </v-expansion-panels>
</template>

<script setup>
import { computed, defineComponent, h } from 'vue'

const props = defineProps({
  report: {
    type: Object,
    default: null
  }
})

const hasReport = computed(() => {
  return props.report && typeof props.report === 'object'
})

const skippedCount = computed(() => {
  return (
    listOf(props.report?.regole_senza_utenti).length +
    listOf(props.report?.regole_saltate).length
  )
})

const allErrors = computed(() => {
  return [
    ...listOf(props.report?.errori_non_bloccanti),
    ...listOf(props.report?.anomalie)
  ]
})

const errorsCount = computed(() => {
  return allErrors.value.length + (props.report?.success === false ? 1 : 0)
})

const reportColor = computed(() => {
  if (props.report?.success === false) return 'red'
  if (skippedCount.value || errorsCount.value) return 'amber'

  return 'green'
})

const reportIcon = computed(() => {
  if (props.report?.success === false) return 'mdi-alert-circle-outline'
  if (skippedCount.value || errorsCount.value) return 'mdi-alert-outline'

  return 'mdi-check-circle-outline'
})

const reportStatusLabel = computed(() => {
  if (props.report?.success === false) return 'Errore non bloccante'
  if (skippedCount.value || errorsCount.value) return 'Con avvisi'

  return 'Completato'
})

function listOf(value) {
  return Array.isArray(value) ? value : []
}

function numberOf(value) {
  const number = Number(value)
  return Number.isFinite(number) ? number : 0
}

function itemTitle(item) {
  return (
    item?.nome_visualizzato ||
    item?.nomeVisualizzato ||
    item?.email ||
    item?.codice_step ||
    item?.codiceStep ||
    item?.motivo ||
    'Elemento'
  )
}

function itemSubtitle(item) {
  const parts = [
    item?.ruolo,
    item?.codice_step || item?.codiceStep,
    item?.motivo
  ].filter(Boolean)

  return parts.join(' - ')
}

const ReportList = defineComponent({
  name: 'ReportList',
  props: {
    title: {
      type: String,
      required: true
    },
    items: {
      type: Array,
      default: () => []
    },
    emptyText: {
      type: String,
      required: true
    }
  },
  setup(componentProps) {
    return () => h('div', { class: 'report-list' }, [
      h('div', { class: 'report-list-title' }, componentProps.title),
      componentProps.items.length
        ? h(
            'div',
            { class: 'report-list-items' },
            componentProps.items.map((item, index) => h(
              'div',
              { class: 'report-list-item', key: index },
              [
                h('div', { class: 'report-list-item-title' }, itemTitle(item)),
                h('div', { class: 'report-list-item-subtitle' }, itemSubtitle(item))
              ]
            ))
          )
        : h('div', { class: 'report-list-empty' }, componentProps.emptyText)
    ])
  }
})
</script>

<style scoped>
.assegnazioni-report-title {
  align-items: center;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  min-width: 0;
}

.assegnazioni-summary {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.assegnazioni-details {
  display: grid;
  gap: 10px;
  margin-top: 12px;
}

.report-list {
  border: 1px solid rgba(0, 0, 0, 0.06);
  border-radius: 8px;
  padding: 8px 10px;
}

.report-list-title {
  font-size: 0.82rem;
  font-weight: 800;
  margin-bottom: 6px;
}

.report-list-items {
  display: grid;
  gap: 6px;
}

.report-list-item {
  min-width: 0;
}

.report-list-item-title {
  font-size: 0.82rem;
  font-weight: 700;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.report-list-item-subtitle,
.report-list-empty {
  color: #6b7280;
  font-size: 0.74rem;
}
</style>
