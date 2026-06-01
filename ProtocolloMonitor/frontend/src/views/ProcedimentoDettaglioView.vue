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
                  :color="coloreProcedimento(procedimento.StatoProcedimento)"
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
        <v-card rounded="xl" elevation="2">
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
      </v-col>
    </v-row>

    <v-card rounded="xl" elevation="2" class="mt-4 workflow-card">
      <v-row no-gutters>
        <v-col cols="12" md="1" class="procedimento-side">
          <div class="procedimento-verticale">
            {{ nomeProcedimentoVerticale }}
          </div>
        </v-col>

        <v-col cols="12" md="4" class="workflow-column">
          <div class="pa-4">
            <div class="d-flex flex-wrap align-center justify-space-between ga-2 mb-4">
              <div class="text-subtitle-1 font-weight-bold">
                Fasi del procedimento
              </div>

              <div class="d-flex align-center ga-2">
                <v-chip color="primary" variant="tonal" size="small">
                  Step fissi
                </v-chip>

                <v-btn
                  color="primary"
                  variant="tonal"
                  density="compact"
                  prepend-icon="mdi-plus"
                  @click="apriDialogNuovaFase"
                >
                  Aggiungi fase
                </v-btn>
              </div>
            </div>

            <v-alert
              v-if="loadingWorkflow"
              type="info"
              variant="tonal"
              class="mb-4"
            >
              Caricamento workflow in corso...
            </v-alert>

            <v-alert
              v-else-if="erroreWorkflow"
              type="warning"
              variant="tonal"
              class="mb-4"
            >
              {{ erroreWorkflow }}
            </v-alert>

            <div
              v-else-if="fasiWorkflow.length"
              class="timeline-scroll"
            >
              <div
                v-for="fase in fasiWorkflow"
                :key="fase.id"
                class="timeline-item"
              >
                <div class="timeline-marker">
                  <v-avatar
                    :color="coloreStatoWorkflow(fase.stato)"
                    size="28"
                  >
                    <span class="timeline-number">
                      {{ fase.ordine }}
                    </span>
                  </v-avatar>
                </div>

                <v-card
                  rounded="lg"
                  variant="tonal"
                  class="fase-card"
                  :class="{ 'fase-selezionata': fase.id === faseSelezionataId }"
                  @click="selezionaFase(fase.id)"
                >
                  <v-card-text>
                    <div class="d-flex align-center justify-space-between ga-3">
                      <strong>{{ fase.titolo }}</strong>

                      <div class="d-flex align-center ga-2">
                        <v-btn
                          icon="mdi-pencil"
                          size="x-small"
                          variant="text"
                          @click.stop="apriDialogModificaFase(fase)"
                        />

                        <v-chip
                          :color="coloreStatoWorkflow(fase.stato)"
                          size="x-small"
                          variant="flat"
                        >
                          {{ labelStatoWorkflow(fase.stato) }}
                        </v-chip>
                      </div>
                    </div>

                    <div class="text-caption mt-3">
                      Responsabile: {{ fase.responsabile }}
                    </div>

                    <div
                      class="text-caption"
                      :class="classeScadenza(fase.dataScadenza)"
                    >
                      Scadenza: {{ fase.dataScadenza }}
                    </div>

                    <div class="step-mini-row mt-4">
                      <span
                        v-for="step in fase.stepOrizzontali"
                        :key="step.id || step.codice"
                        class="step-mini-dot"
                        :class="classeStep(step.stato)"
                      />
                    </div>
                  </v-card-text>
                </v-card>
              </div>
            </div>

            <v-alert
              v-else
              type="info"
              variant="tonal"
            >
              Nessuna fase workflow configurata per questo procedimento.
            </v-alert>
          </div>
        </v-col>

        <v-col cols="12" md="7" class="workflow-detail-column">
          <v-card
            v-if="faseSelezionata"
            class="ma-4"
            rounded="xl"
            elevation="0"
          >
            <v-card-title class="d-flex align-center justify-space-between">
              <span class="font-weight-bold">
                {{ faseSelezionata.titolo }}
              </span>

              <div class="d-flex align-center ga-2">
                <v-btn
                  icon="mdi-pencil"
                  size="small"
                  variant="text"
                  @click="apriDialogModificaFase(faseSelezionata)"
                />

                <v-chip
                  :color="coloreStatoWorkflow(faseSelezionata.stato)"
                  variant="flat"
                >
                  {{ labelStatoWorkflow(faseSelezionata.stato) }}
                </v-chip>
              </div>
            </v-card-title>

            <v-divider class="mb-4" />

            <v-card-text>
              <p class="mb-4">
                {{ faseSelezionata.descrizione || 'Nessuna descrizione disponibile.' }}
              </p>

              <v-row>
                <v-col cols="12" md="6">
                  <div class="label">Responsabile</div>
                  <div class="value">{{ faseSelezionata.responsabile }}</div>
                </v-col>

                <v-col cols="12" md="6">
                  <div class="label">Scadenza</div>
                  <div
                    class="value"
                    :class="classeScadenza(faseSelezionata.dataScadenza)"
                  >
                    {{ faseSelezionata.dataScadenza }}
                  </div>
                </v-col>
              </v-row>

              <v-divider class="my-4" />

              <div class="text-subtitle-2 font-weight-bold mb-3">
                Step orizzontali della fase
              </div>

              <div
                v-if="faseSelezionata.stepOrizzontali.length"
                class="stepper-orizzontale"
              >
                <div
                  v-for="(step, index) in faseSelezionata.stepOrizzontali"
                  :key="step.id || step.codice"
                  class="stepper-item"
                >
                  <div class="step-node-wrap">
                    <v-avatar
                      :color="coloreStep(step.stato)"
                      size="42"
                      class="step-node"
                    >
                      <v-icon size="22" color="white">
                        {{ iconaStep(step.stato) }}
                      </v-icon>
                    </v-avatar>

                    <div
                      v-if="index < faseSelezionata.stepOrizzontali.length - 1"
                      class="step-line"
                    />
                  </div>

                  <div class="step-title">
                    {{ step.titolo }}
                  </div>

                  <v-chip
                    size="x-small"
                    :color="coloreStep(step.stato)"
                    variant="tonal"
                  >
                    {{ step.stato }}
                  </v-chip>
                </div>
              </div>

              <v-alert
                v-else
                type="info"
                variant="tonal"
                density="compact"
              >
                Gli step verranno inizializzati automaticamente al caricamento della fase.
              </v-alert>
            </v-card-text>
          </v-card>

          <v-alert
            v-else
            type="info"
            variant="tonal"
            class="ma-4"
          >
            Seleziona una fase del workflow.
          </v-alert>
        </v-col>
      </v-row>
    </v-card>

    <v-dialog
      v-model="dialogFase"
      max-width="640"
      persistent
    >
      <v-card rounded="xl">
        <v-card-title class="text-subtitle-1 font-weight-bold">
          {{ faseDialogMode === 'create' ? 'Aggiungi fase' : 'Modifica fase' }}
        </v-card-title>

        <v-card-text>
          <v-alert
            v-if="erroreFaseDialog"
            type="error"
            variant="tonal"
            density="compact"
            class="mb-4"
          >
            {{ erroreFaseDialog }}
          </v-alert>

          <v-form ref="faseFormRef">
            <v-text-field
              v-model="faseForm.Titolo"
              label="Titolo fase"
              variant="outlined"
              density="compact"
              :rules="[regoleFase.titolo]"
              autofocus
            />

            <v-textarea
              v-model="faseForm.Descrizione"
              label="Descrizione"
              variant="outlined"
              rows="3"
              auto-grow
            />
          </v-form>
        </v-card-text>

        <v-card-actions class="justify-end">
          <v-btn
            variant="text"
            :disabled="salvataggioFaseInCorso"
            @click="chiudiDialogFase"
          >
            Annulla
          </v-btn>
          <v-btn
            color="primary"
            variant="flat"
            :loading="salvataggioFaseInCorso"
            @click="salvaFase"
          >
            Salva
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-snackbar
      v-model="snackbarFase"
      color="success"
      timeout="3000"
    >
      {{ messaggioFase }}
    </v-snackbar>
  </v-container>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import {
  countProtocolliProcedimento,
  createFaseProcedimento,
  getProcedimento,
  listFasiProcedimento,
  listProtocolliProcedimento,
  listStepOrizzontaliFase,
  updateFaseProcedimento
} from '../services/procedimentoApi'
import { statiWorkflow } from '../mock/procedimentoWorkflowMock'

const route = useRoute()
const router = useRouter()

const procedimento = ref(null)
const protocolli = ref([])
const numeroProtocolliApi = ref(null)
const loading = ref(false)
const loadingProtocolli = ref(false)
const loadingWorkflow = ref(false)
const errore = ref('')
const erroreWorkflow = ref('')

const fasiWorkflow = ref([])
const faseSelezionataId = ref(null)
const dialogFase = ref(false)
const faseDialogMode = ref('create')
const faseInModificaId = ref(null)
const faseFormRef = ref(null)
const salvataggioFaseInCorso = ref(false)
const erroreFaseDialog = ref('')
const snackbarFase = ref(false)
const messaggioFase = ref('')
const faseForm = reactive({
  Titolo: '',
  Descrizione: ''
})

const regoleFase = {
  titolo: (value) => Boolean(String(value || '').trim()) || 'Titolo fase obbligatorio'
}

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

const faseSelezionata = computed(() => {
  return fasiWorkflow.value.find((fase) => fase.id === faseSelezionataId.value)
})

const nomeProcedimentoVerticale = computed(() => {
  const nome =
    procedimento.value?.Titolo ||
    procedimento.value?.CodiceProcedimento ||
    'Procedimento'

  return nome.length > 74 ? `${nome.substring(0, 71)}...` : nome
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

async function caricaWorkflow() {
  loadingWorkflow.value = true
  erroreWorkflow.value = ''

  try {
    const fasiApi = await listFasiProcedimento(idProcedimento.value)

    const fasiNormalizzate = await Promise.all(
      fasiApi.map(async (fase) => {
        const faseNormalizzata = normalizzaFaseWorkflow(fase)

        try {
          const step = await listStepOrizzontaliFase(
            idProcedimento.value,
            faseNormalizzata.id
          )
          faseNormalizzata.stepOrizzontali = step
            .map(normalizzaStepOrizzontale)
            .sort(confrontaOrdine)
        } catch {
          faseNormalizzata.stepOrizzontali = []
        }

        return faseNormalizzata
      })
    )

    fasiWorkflow.value = fasiNormalizzate.sort(confrontaOrdine)
    faseSelezionataId.value = fasiNormalizzate[0]?.id ?? null
  } catch (error) {
    erroreWorkflow.value = 'Impossibile caricare il workflow da FastAPI.'
    fasiWorkflow.value = []
    faseSelezionataId.value = null
  } finally {
    loadingWorkflow.value = false
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

function normalizzaFaseWorkflow(dato) {
  return {
    id: dato.id_fase ?? dato.IDFase,
    idProcedimento: dato.id_procedimento ?? dato.IDProcedimento,
    ordine: dato.ordine ?? dato.Ordine ?? 0,
    titolo: dato.titolo ?? dato.Titolo ?? 'Fase senza titolo',
    descrizione: dato.descrizione ?? dato.Descrizione ?? '',
    stato: dato.stato_fase ?? dato.StatoFase ?? 'NON_AVVIATA',
    responsabile: dato.responsabile ?? dato.Responsabile ?? '-',
    dataScadenza: dato.data_scadenza ?? dato.DataScadenza ?? '-',
    stepOrizzontali: []
  }
}

function normalizzaStepOrizzontale(dato) {
  return {
    id: dato.id_step_orizzontale ?? dato.IDStepOrizzontale,
    idFase: dato.id_fase ?? dato.IDFase,
    codice: dato.codice_step ?? dato.CodiceStep ?? '',
    titolo: dato.titolo_step ?? dato.TitoloStep ?? 'Step',
    ordine: dato.ordine ?? dato.Ordine ?? 0,
    stato: dato.stato_step ?? dato.StatoStep ?? 'NON_AVVIATO'
  }
}

function tornaAElenco() {
  router.push('/protocollo-monitor/procedimenti')
}

function confrontaOrdine(a, b) {
  return Number(a?.ordine ?? 0) - Number(b?.ordine ?? 0)
}

function apriDialogNuovaFase() {
  faseDialogMode.value = 'create'
  faseInModificaId.value = null
  faseForm.Titolo = ''
  faseForm.Descrizione = ''
  erroreFaseDialog.value = ''
  dialogFase.value = true
}

function apriDialogModificaFase(fase) {
  if (!fase) return

  faseDialogMode.value = 'edit'
  faseInModificaId.value = fase.id
  faseForm.Titolo = fase.titolo || ''
  faseForm.Descrizione = fase.descrizione || ''
  erroreFaseDialog.value = ''
  dialogFase.value = true
}

function chiudiDialogFase() {
  if (salvataggioFaseInCorso.value) return

  dialogFase.value = false
  erroreFaseDialog.value = ''
}

async function salvaFase() {
  const validation = await faseFormRef.value?.validate()
  if (validation && !validation.valid) return

  salvataggioFaseInCorso.value = true
  erroreFaseDialog.value = ''

  try {
    const payload = pulisciPayloadFase(faseForm)
    const faseSalvata = faseDialogMode.value === 'create'
      ? await createFaseProcedimento(idProcedimento.value, payload)
      : await updateFaseProcedimento(
        idProcedimento.value,
        faseInModificaId.value,
        payload
      )

    const faseNormalizzata = normalizzaFaseWorkflow(faseSalvata)
    await caricaWorkflow()
    faseSelezionataId.value = faseNormalizzata.id
    dialogFase.value = false
    messaggioFase.value = faseDialogMode.value === 'create'
      ? 'Fase creata.'
      : 'Fase aggiornata.'
    snackbarFase.value = true
  } catch (error) {
    erroreFaseDialog.value = messaggioErroreFase(error)
  } finally {
    salvataggioFaseInCorso.value = false
  }
}

function pulisciPayloadFase(payload) {
  return {
    Titolo: String(payload.Titolo || '').trim() || null,
    Descrizione: String(payload.Descrizione || '').trim() || null
  }
}

function messaggioErroreFase(error) {
  const dettaglio = error?.payload?.detail
  if (typeof dettaglio === 'string') return dettaglio

  if (error?.status === 404) return 'Fase non trovata.'
  return 'Impossibile salvare la fase.'
}

function selezionaFase(idFase) {
  faseSelezionataId.value = idFase
}

function coloreStatoWorkflow(stato) {
  return statiWorkflow[stato]?.color || 'grey'
}

function labelStatoWorkflow(stato) {
  return statiWorkflow[stato]?.label || stato
}

function classeScadenza(valore) {
  if (!valore || valore === '-') return 'scadenza-standard'

  const data = new Date(valore)

  if (Number.isNaN(data.getTime())) return 'scadenza-standard'

  const oggi = new Date()
  oggi.setHours(0, 0, 0, 0)

  const scadenza = new Date(data)
  scadenza.setHours(0, 0, 0, 0)

  const differenzaGiorni = Math.ceil(
    (scadenza.getTime() - oggi.getTime()) / 86400000
  )

  if (differenzaGiorni < 0) return 'scadenza-scaduta'
  if (differenzaGiorni <= 3) return 'scadenza-vicina'
  return 'scadenza-standard'
}

function coloreProcedimento(stato) {
  const normalizzato = String(stato || '').toUpperCase()
  if (normalizzato.includes('CHIUS')) return 'green'
  if (normalizzato.includes('SOSP')) return 'orange'
  if (normalizzato.includes('ANNULL')) return 'red'
  return 'blue'
}

function colorePriorita(priorita) {
  const normalizzata = String(priorita || '').toUpperCase()
  if (normalizzata.includes('ALTA') || normalizzata.includes('URGENTE')) {
    return 'red'
  }
  if (normalizzata.includes('BASSA')) return 'grey'
  return 'blue'
}

function coloreStep(stato) {
  const normalizzato = String(stato || '').toUpperCase()
  if (normalizzato === 'COMPLETATO' || normalizzato === 'COMPLETATA') return 'green'
  if (normalizzato === 'IN_CORSO' || normalizzato === 'ACTIVE') return 'amber'
  if (normalizzato === 'BLOCCATO' || normalizzato === 'LOCKED') return 'grey'
  if (normalizzato === 'ANNULLATO' || normalizzato === 'CANCELLED') return 'grey-darken-1'
  return 'grey'
}

function classeStep(stato) {
  return `step-mini-${coloreStep(stato).replace('-darken-1', '')}`
}

function iconaStep(stato) {
  const normalizzato = String(stato || '').toUpperCase()
  if (normalizzato === 'COMPLETATO' || normalizzato === 'COMPLETATA') {
    return 'mdi-check'
  }
  if (normalizzato === 'IN_CORSO' || normalizzato === 'ACTIVE') {
    return 'mdi-play'
  }
  return 'mdi-circle-outline'
}

onMounted(() => {
  caricaDettaglio()
  caricaWorkflow()
})
</script>

<style scoped>
.label {
  color: rgba(var(--v-theme-on-surface), 0.62);
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0;
  text-transform: uppercase;
}

.value {
  font-size: 0.95rem;
  font-weight: 600;
  word-break: break-word;
}

.box-testo {
  border: 1px solid rgba(var(--v-theme-on-surface), 0.12);
  border-radius: 8px;
  padding: 12px;
  white-space: pre-wrap;
}

.tabella-protocolli {
  min-height: 260px;
}

.workflow-card {
  overflow: hidden;
}

.procedimento-side {
  background: rgb(var(--v-theme-primary));
  color: white;
  min-height: 520px;
}

.procedimento-verticale {
  align-items: center;
  display: flex;
  font-size: 0.82rem;
  font-weight: 800;
  height: 100%;
  justify-content: center;
  letter-spacing: 0;
  padding: 16px 8px;
  text-align: center;
  text-transform: uppercase;
  writing-mode: vertical-rl;
}

.workflow-column {
  border-right: 1px solid rgba(var(--v-theme-on-surface), 0.08);
}

.timeline-scroll {
  max-height: 620px;
  overflow-y: auto;
  padding-right: 6px;
}

.timeline-item {
  display: grid;
  gap: 12px;
  grid-template-columns: 32px 1fr;
  margin-bottom: 14px;
}

.timeline-marker {
  display: flex;
  justify-content: center;
  padding-top: 18px;
}

.timeline-number {
  color: white;
  font-size: 0.78rem;
  font-weight: 800;
}

.fase-card {
  cursor: pointer;
  transition: border-color 0.16s ease, transform 0.16s ease;
}

.fase-card:hover,
.fase-selezionata {
  border-color: rgb(var(--v-theme-primary));
  transform: translateY(-1px);
}

.step-mini-row {
  display: flex;
  gap: 6px;
}

.step-mini-dot {
  border-radius: 999px;
  display: inline-block;
  height: 8px;
  width: 24px;
}

.step-mini-grey {
  background: #9e9e9e;
}

.step-mini-green {
  background: #2e7d32;
}

.step-mini-amber {
  background: #f9a825;
}

.workflow-detail-column {
  min-height: 520px;
}

.stepper-orizzontale {
  display: grid;
  gap: 12px;
  grid-template-columns: repeat(5, minmax(96px, 1fr));
  overflow-x: auto;
  padding: 8px 0 4px;
}

.stepper-item {
  min-width: 96px;
  text-align: center;
}

.step-node-wrap {
  align-items: center;
  display: flex;
  justify-content: center;
  margin-bottom: 8px;
  position: relative;
}

.step-node {
  z-index: 1;
}

.step-line {
  background: rgba(var(--v-theme-on-surface), 0.18);
  height: 2px;
  left: calc(50% + 22px);
  position: absolute;
  right: calc(-50% + 22px);
  top: 50%;
  transform: translateY(-50%);
}

.step-title {
  font-size: 0.82rem;
  font-weight: 800;
  margin-bottom: 6px;
  min-height: 36px;
}

.scadenza-standard {
  color: rgba(var(--v-theme-on-surface), 0.78);
}

.scadenza-vicina {
  color: rgb(var(--v-theme-warning));
  font-weight: 800;
}

.scadenza-scaduta {
  color: rgb(var(--v-theme-error));
  font-weight: 800;
}

@media (max-width: 960px) {
  .procedimento-side {
    min-height: auto;
  }

  .procedimento-verticale {
    min-height: 64px;
    writing-mode: horizontal-tb;
  }

  .workflow-column {
    border-right: 0;
    border-bottom: 1px solid rgba(var(--v-theme-on-surface), 0.08);
  }

  .stepper-orizzontale {
    grid-template-columns: repeat(5, minmax(84px, 1fr));
  }
}
</style>
