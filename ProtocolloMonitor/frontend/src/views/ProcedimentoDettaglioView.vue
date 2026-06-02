<template>
  <v-container fluid class="procedimento-page">
    <header class="procedimento-header">
      <v-btn
        class="btn-torna-procedimenti"
        variant="outlined"
        @click="tornaAElenco"
      >
        <img
          :src="elencoProcedimentoIcon"
          alt=""
          class="btn-procedimenti-icon"
        >
        <span class="btn-procedimenti-text">
          Elenco procedimenti
        </span>
      </v-btn>
    </header>

    <main class="procedimento-shell">
      <aside class="procedimento-rail">
        <div class="procedimento-title-vertical">
          {{ titoloProcedimentoVerticale }}
        </div>
      </aside>

      <section class="work-area">
        <v-window
          v-model="modalitaVista"
          class="work-window"
        >
          <v-window-item value="fasi-verticali">
            <div class="fasi-verticali-view">
              <section class="fasi-panel">
                <div class="fasi-header">
                  <div>
                    <div class="text-subtitle-1 font-weight-bold">
                      Fasi del procedimento
                    </div>
                    <div class="text-caption text-medium-emphasis">
                      Stepper verticale delle fasi configurate
                    </div>
                  </div>

                  <v-btn
                    color="primary"
                    variant="flat"
                    density="comfortable"
                    prepend-icon="mdi-plus"
                    @click="apriDialogNuovaFase"
                  >
                    Aggiungi fase
                  </v-btn>
                </div>

                <v-alert
                  v-if="loadingWorkflow"
                  type="info"
                  variant="tonal"
                  class="mt-4"
                >
                  Caricamento fasi in corso...
                </v-alert>

                <v-alert
                  v-else-if="erroreWorkflow"
                  type="warning"
                  variant="tonal"
                  class="mt-4"
                >
                  {{ erroreWorkflow }}
                </v-alert>

                <div
                  v-else-if="fasiWorkflow.length"
                  class="fasi-stepper-scroll"
                >
                  <div class="fasi-stepper">
                    <div
                      v-for="(fase, index) in fasiWorkflow"
                      :key="fase.id"
                      class="fase-step"
                      :class="{ 'fase-selezionata': fase.id === faseSelezionataId }"
                      @click="selezionaFase(fase.id)"
                    >
                      <div class="step-rail">
                        <div
                          class="step-dot"
                          :style="{ backgroundColor: coloreFaseDot(fase.stato) }"
                        >
                          {{ fase.ordine }}
                        </div>
                        <div
                          v-if="index < fasiWorkflow.length - 1"
                          class="step-line"
                        />
                      </div>

                      <v-card
                        rounded="lg"
                        variant="outlined"
                        class="fase-box"
                      >
                        <v-card-text class="fase-box-content">
                          <div class="fase-title-row">
                            <div class="fase-heading">
                              {{ fase.titolo }}
                            </div>

                            <v-btn
                              icon="mdi-pencil"
                              size="small"
                              variant="text"
                              class="fase-edit-btn"
                              @click.stop="apriDialogModificaFase(fase)"
                            />
                          </div>

                          <div class="fase-description">
                            {{ fase.descrizione || 'Nessuna descrizione.' }}
                          </div>

                          <div class="fase-meta">
                            <v-chip
                              :color="coloreStatoWorkflow(fase.stato)"
                              size="x-small"
                              variant="tonal"
                            >
                              {{ labelStatoWorkflow(fase.stato) }}
                            </v-chip>
                          </div>
                        </v-card-text>
                      </v-card>
                    </div>
                  </div>
                </div>

                <v-alert
                  v-else
                  type="info"
                  variant="tonal"
                  class="mt-4"
                >
                  Nessuna fase configurata per questo procedimento.
                </v-alert>
              </section>

              <section class="fase-detail-section">
                <v-alert
                  v-if="!faseSelezionata"
                  type="info"
                  variant="tonal"
                >
                  Seleziona una fase per visualizzare il dettaglio.
                </v-alert>

                <v-card
                  v-else
                  rounded="lg"
                  elevation="1"
                  class="fase-detail-card"
                >
                  <v-card-title class="fase-detail-title">
                    <div>
                      <div class="text-caption text-medium-emphasis">
                        Fase selezionata
                      </div>
                      <div class="fase-detail-heading">
                        {{ faseSelezionata.titolo }}
                      </div>
                    </div>

                    <div class="d-flex align-center ga-2">
                      <v-chip
                        :color="coloreStatoWorkflow(faseSelezionata.stato)"
                        variant="tonal"
                      >
                        {{ labelStatoWorkflow(faseSelezionata.stato) }}
                      </v-chip>

                      <v-btn
                        icon="mdi-pencil"
                        size="small"
                        variant="text"
                        @click="apriDialogModificaFase(faseSelezionata)"
                      />
                    </div>
                  </v-card-title>

                  <v-divider />

                  <v-card-text>
                    <div class="detail-label">Descrizione</div>
                    <div class="detail-description-box">
                      {{ faseSelezionata.descrizione || '-' }}
                    </div>

                    <div class="detail-grid">
                      <div class="detail-field">
                        <div class="detail-label">Ordine</div>
                        <div class="detail-value">
                          {{ valoreDettaglio(faseSelezionata.ordine) }}
                        </div>
                      </div>

                      <div class="detail-field">
                        <div class="detail-label">Stato</div>
                        <div class="detail-value">
                          {{ labelStatoWorkflow(faseSelezionata.stato) }}
                        </div>
                      </div>

                      <div class="detail-field">
                        <div class="detail-label">Responsabile</div>
                        <div class="detail-value">
                          {{ valoreDettaglio(faseSelezionata.responsabile) }}
                        </div>
                      </div>

                      <div class="detail-field">
                        <div class="detail-label">Data scadenza</div>
                        <div class="detail-value">
                          {{ valoreDettaglio(faseSelezionata.dataScadenza) }}
                        </div>
                      </div>

                      <div class="detail-field">
                        <div class="detail-label">Data avvio</div>
                        <div class="detail-value">
                          {{ valoreDettaglio(faseSelezionata.dataAvvio) }}
                        </div>
                      </div>

                      <div class="detail-field">
                        <div class="detail-label">Data completamento</div>
                        <div class="detail-value">
                          {{ valoreDettaglio(faseSelezionata.dataCompletamento) }}
                        </div>
                      </div>
                    </div>
                  </v-card-text>

                  <v-card-actions class="detail-actions">
                    <v-btn
                      color="primary"
                      variant="flat"
                      size="large"
                      prepend-icon="mdi-pencil-box-outline"
                      @click="entraLavorazioneFase(faseSelezionata)"
                    >
                      Redigi Fase {{ faseSelezionata.ordine }}
                    </v-btn>
                  </v-card-actions>
                </v-card>
              </section>
            </div>
          </v-window-item>

          <v-window-item value="lavorazione-fase">
            <div class="lavorazione-view">
              <div class="lavorazione-toolbar">
                <v-btn
                  class="btn-torna-fasi"
                  color="grey"
                  variant="tonal"
                  prepend-icon="mdi-arrow-left"
                  @click="tornaAlleFasiVerticali"
                >
                  Torna alle fasi verticali
                </v-btn>

                <h1 class="lavorazione-title">
                  {{ faseSelezionata?.titolo || 'Fase selezionata' }}
                </h1>
              </div>

              <v-alert
                v-if="erroreStepOrizzontali"
                type="warning"
                variant="tonal"
                class="mb-4"
              >
                {{ erroreStepOrizzontali }}
              </v-alert>

              <v-progress-linear
                v-if="loadingStepOrizzontali"
                color="primary"
                indeterminate
                rounded
                class="mb-4"
              />

              <div class="lavorazione-content-card">
                <div
                  v-if="stepOrizzontali.length"
                  class="stepper-orizzontale"
                >
                  <div
                    v-for="(step, index) in stepOrizzontali"
                    :key="step.id || step.codiceStep"
                    class="step-orizzontale-item"
                  >
                    <div class="step-orizzontale-node-wrap">
                      <div
                        class="step-orizzontale-node"
                        :class="classeStepOrizzontale(step.statoStep)"
                      >
                        {{ index + 1 }}
                      </div>

                      <div
                        v-if="index < stepOrizzontali.length - 1"
                        class="step-orizzontale-line"
                      />
                    </div>

                    <div class="step-orizzontale-title">
                      {{ step.titoloStep }}
                    </div>
                  </div>
                </div>

                <v-alert
                  v-else-if="!loadingStepOrizzontali"
                  type="info"
                  variant="tonal"
                  class="stepper-empty"
                >
                  Selezionare una fase per iniziare.
                </v-alert>

                <div class="work-content-placeholder">
                  <div class="placeholder-title">
                    Area contenuto fase
                  </div>
                  <div class="placeholder-subtitle">
                    Selezionare uno step per iniziare.
                  </div>
                </div>
              </div>
            </div>
          </v-window-item>
        </v-window>
      </section>
    </main>

    <v-dialog
      v-model="dialogFase"
      max-width="640"
      persistent
    >
      <v-card rounded="lg">
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
  createFaseProcedimento,
  getProcedimento,
  inizializzaStepOrizzontaliFase,
  listFasiProcedimento,
  listStepOrizzontaliFase,
  updateFaseProcedimento
} from '../services/procedimentoApi'
import { statiWorkflow } from '../mock/procedimentoWorkflowMock'
import elencoProcedimentoIcon from '../assets/ElencoProcedimentoICO.png'

const route = useRoute()
const router = useRouter()

const procedimento = ref(null)
const modalitaVista = ref('fasi-verticali')
const loadingWorkflow = ref(false)
const erroreWorkflow = ref('')
const fasiWorkflow = ref([])
const faseSelezionataId = ref(null)
const stepOrizzontali = ref([])
const loadingStepOrizzontali = ref(false)
const erroreStepOrizzontali = ref('')
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

const idProcedimento = computed(() => route.params.idProcedimento)

const titoloProcedimentoVerticale = computed(() => {
  const titolo =
    procedimento.value?.Titolo ||
    procedimento.value?.titolo ||
    procedimento.value?.CodiceProcedimento ||
    procedimento.value?.codice_procedimento ||
    'Procedimento'

  return String(titolo).trim() || 'Procedimento'
})

const faseSelezionata = computed(() => {
  return fasiWorkflow.value.find((fase) => fase.id === faseSelezionataId.value)
})

async function caricaProcedimento() {
  try {
    procedimento.value = await getProcedimento(idProcedimento.value)
  } catch {
    procedimento.value = null
  }
}

async function caricaWorkflow() {
  loadingWorkflow.value = true
  erroreWorkflow.value = ''

  try {
    const fasiApi = await listFasiProcedimento(idProcedimento.value)
    const fasiNormalizzate = fasiApi
      .map(normalizzaFaseWorkflow)
      .sort(confrontaOrdine)

    const faseSelezionataAncoraPresente = fasiNormalizzate.some(
      (fase) => fase.id === faseSelezionataId.value
    )

    fasiWorkflow.value = fasiNormalizzate
    faseSelezionataId.value = faseSelezionataAncoraPresente
      ? faseSelezionataId.value
      : fasiNormalizzate[0]?.id ?? null
  } catch {
    erroreWorkflow.value = 'Impossibile caricare le fasi da FastAPI.'
    fasiWorkflow.value = []
    faseSelezionataId.value = null
  } finally {
    loadingWorkflow.value = false
  }
}

function normalizzaFaseWorkflow(dato = {}) {
  return {
    id: dato.id_fase ?? dato.IDFase,
    ordine: dato.ordine ?? dato.Ordine ?? 0,
    titolo: dato.titolo ?? dato.Titolo ?? 'Fase senza titolo',
    descrizione: dato.descrizione ?? dato.Descrizione ?? '',
    stato: dato.stato_fase ?? dato.StatoFase ?? 'NON_AVVIATA',
    responsabile: dato.responsabile ?? dato.Responsabile ?? '-',
    dataScadenza: dato.data_scadenza ?? dato.DataScadenza ?? '-',
    dataAvvio: dato.data_avvio ?? dato.DataAvvio ?? '-',
    dataCompletamento:
      dato.data_completamento ?? dato.DataCompletamento ?? '-'
  }
}

function normalizzaStepOrizzontale(dato = {}) {
  const codiceStep =
    dato.codice_step ??
    dato.CodiceStep ??
    dato.codiceStep ??
    ''
  const titoloRaw =
    dato.titolo_step ??
    dato.TitoloStep ??
    dato.titoloStep ??
    labelStepOrizzontale(codiceStep)

  return {
    id:
      dato.id_step_orizzontale ??
      dato.IDStepOrizzontale ??
      dato.idStepOrizzontale ??
      dato.id,
    codiceStep,
    titoloStep: normalizzaTitoloStepOrizzontale(titoloRaw, codiceStep),
    ordine: dato.ordine ?? dato.Ordine ?? 0,
    statoStep:
      dato.stato_step ??
      dato.StatoStep ??
      dato.statoStep ??
      'NON_AVVIATO'
  }
}

function labelStepOrizzontale(codice) {
  const labels = {
    REDIGI: 'Redigi',
    REVISIONA: 'Revisiona',
    FIRMA: 'Firma',
    PROTOCOLLA: 'Protocolla',
    FINE: 'Fine'
  }
  return labels[String(codice || '').toUpperCase()] || 'Step'
}

function normalizzaTitoloStepOrizzontale(titolo, codice) {
  const titoloString = String(titolo || '').trim()
  const titoloUpper = titoloString.toUpperCase()
  const labelCodice = labelStepOrizzontale(codice)

  if (!titoloString || titoloUpper === String(codice || '').toUpperCase()) {
    return labelCodice
  }

  if (['REDIGI', 'REVISIONA', 'FIRMA', 'PROTOCOLLA', 'FINE'].includes(titoloUpper)) {
    return labelStepOrizzontale(titoloUpper)
  }

  return titoloString
}

async function entraLavorazioneFase(fase) {
  if (!fase) return

  faseSelezionataId.value = fase.id
  modalitaVista.value = 'lavorazione-fase'
  await caricaStepOrizzontaliFase(fase)
}

function tornaAlleFasiVerticali() {
  modalitaVista.value = 'fasi-verticali'
  erroreStepOrizzontali.value = ''
}

async function caricaStepOrizzontaliFase(fase) {
  if (!fase?.id) return

  loadingStepOrizzontali.value = true
  erroreStepOrizzontali.value = ''
  stepOrizzontali.value = []

  try {
    let step = await listStepOrizzontaliFase(idProcedimento.value, fase.id)

    if (!Array.isArray(step) || step.length === 0) {
      await inizializzaStepOrizzontaliFase(idProcedimento.value, fase.id)
      step = await listStepOrizzontaliFase(idProcedimento.value, fase.id)
    }

    stepOrizzontali.value = normalizzaListaStepOrizzontali(step)
  } catch {
    erroreStepOrizzontali.value =
      'Impossibile caricare gli step orizzontali della fase.'
    stepOrizzontali.value = normalizzaListaStepOrizzontali([])
  } finally {
    loadingStepOrizzontali.value = false
  }
}

function normalizzaListaStepOrizzontali(step) {
  const normalizzati = Array.isArray(step)
    ? step.map(normalizzaStepOrizzontale).sort(confrontaOrdine)
    : []

  if (normalizzati.length) return normalizzati

  return ['REDIGI', 'REVISIONA', 'FIRMA', 'PROTOCOLLA', 'FINE'].map(
    (codiceStep, index) => ({
      id: codiceStep,
      codiceStep,
      titoloStep: labelStepOrizzontale(codiceStep),
      ordine: index + 1,
      statoStep: 'NON_AVVIATO'
    })
  )
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

function valoreDettaglio(value) {
  if (value === null || value === undefined || value === '') return '-'
  return value
}

function classeStepOrizzontale(stato) {
  const normalizzato = String(stato || '').toUpperCase()
  if (normalizzato === 'NON_AVVIATO') return 'step-orizzontale-non-avviato'
  if (normalizzato.includes('COMPLET')) return 'step-orizzontale-completato'
  if (normalizzato.includes('CORSO') || normalizzato === 'ACTIVE') {
    return 'step-orizzontale-attivo'
  }
  return 'step-orizzontale-non-avviato'
}

function coloreFaseDot(stato) {
  const colore = coloreStatoWorkflow(stato)
  const palette = {
    green: '#2e7d32',
    blue: '#1976d2',
    orange: '#ef6c00',
    red: '#c62828',
    grey: '#757575'
  }
  return palette[colore] || '#1976d2'
}

onMounted(() => {
  caricaProcedimento()
  caricaWorkflow()
})
</script>

<style scoped>
.procedimento-page {
  --rail-width: 118px;
  box-sizing: border-box;
  height: calc(100vh - 112px);
  max-width: none;
  overflow: hidden;
  padding: 0;
}

.procedimento-header {
  align-items: center;
  display: flex;
  height: 112px;
  overflow: hidden;
  padding: 0;
}

.btn-torna-procedimenti {
  background: #eeeeee;
  border: 1px solid #c62828;
  color: #111111;
  font-weight: 800;
  letter-spacing: 0;
  min-height: 106px;
  min-width: 408px;
  margin-left: 0;
  padding: 6px 30px 6px 22px;
  flex: 0 0 auto;
  text-transform: none;
}

.btn-torna-procedimenti :deep(.v-btn__content) {
  align-items: center;
  display: flex;
  gap: 18px;
}

.btn-torna-procedimenti:hover {
  background: #ffeb3b;
  border-color: #c62828;
  color: #111111;
}

.btn-procedimenti-icon {
  display: block;
  height: 86px;
  object-fit: contain;
  width: 86px;
}

.btn-procedimenti-text {
  color: #111111;
  font-size: 1.2rem;
  font-weight: 850;
  letter-spacing: 0;
  line-height: 1.1;
}

.btn-torna-fasi {
  flex: 0 0 auto;
  font-weight: 750;
  letter-spacing: 0;
  min-height: 44px;
  text-transform: none;
  width: max(240px, calc(408px - var(--rail-width) - 26px));
}

.procedimento-shell {
  display: grid;
  grid-template-columns: var(--rail-width) minmax(0, 1fr);
  height: calc(100% - 112px);
  min-height: 0;
  overflow: hidden;
}

.procedimento-rail {
  align-items: center;
  background: #0d47a1;
  color: white;
  display: flex;
  justify-content: center;
  min-height: 0;
  overflow: hidden;
  padding: 18px 8px;
}

.procedimento-title-vertical {
  color: #ff9800;
  font-size: 1.55rem;
  font-weight: 900;
  letter-spacing: 0;
  line-height: 1.15;
  max-height: 100%;
  text-align: center;
  text-transform: uppercase;
  transform: rotate(180deg);
  transform-origin: center;
  writing-mode: vertical-rl;
}

.work-area,
.work-window,
.work-window :deep(.v-window__container),
.work-window :deep(.v-window-item) {
  height: 100%;
  min-height: 0;
}

.work-area {
  background: rgb(var(--v-theme-surface));
  min-width: 0;
  overflow: hidden;
}

.fasi-verticali-view {
  display: grid;
  gap: 24px;
  grid-template-columns: minmax(360px, 33%) minmax(0, 1fr);
  height: 100%;
  min-height: 0;
  overflow: hidden;
  padding: 22px 28px;
}

.fasi-panel,
.fase-detail-section {
  min-height: 0;
}

.fasi-header {
  align-items: center;
  display: flex;
  gap: 14px;
  justify-content: space-between;
  margin-bottom: 14px;
}

.fasi-stepper-scroll {
  height: calc(100% - 68px);
  min-height: 0;
  overflow-y: auto;
  padding-bottom: 28px;
  padding-right: 8px;
}

.fasi-stepper {
  display: grid;
  gap: 0;
}

.fase-step {
  display: grid;
  grid-template-columns: 54px minmax(0, 1fr);
  min-height: 126px;
}

.step-rail {
  align-items: center;
  display: flex;
  flex-direction: column;
  position: relative;
}

.step-dot {
  align-items: center;
  border: 3px solid white;
  border-radius: 999px;
  box-shadow: 0 0 0 1px rgba(var(--v-theme-on-surface), 0.18);
  color: white;
  display: flex;
  font-size: 0.95rem;
  font-weight: 800;
  height: 42px;
  justify-content: center;
  margin-top: 14px;
  width: 42px;
  z-index: 1;
}

.step-line {
  background: rgba(var(--v-theme-on-surface), 0.24);
  flex: 1;
  margin-top: 4px;
  min-height: 78px;
  width: 3px;
}

.fase-box {
  margin-bottom: 16px;
  transition: border-color 0.16s ease, background-color 0.16s ease;
}

.fase-step:hover .fase-box,
.fase-selezionata .fase-box {
  background: rgba(var(--v-theme-primary), 0.04);
  border-color: rgb(var(--v-theme-primary));
}

.fase-box-content {
  padding: 12px 14px;
}

.fase-title-row {
  align-items: start;
  display: flex;
  gap: 8px;
  justify-content: space-between;
}

.fase-heading {
  font-size: 0.95rem;
  font-weight: 800;
  overflow-wrap: anywhere;
}

.fase-description {
  color: rgba(var(--v-theme-on-surface), 0.68);
  font-size: 0.82rem;
  line-height: 1.35;
  margin-top: 4px;
  overflow-wrap: anywhere;
}

.fase-meta {
  margin-top: 10px;
}

.fase-detail-section {
  align-self: start;
}

.fase-detail-card {
  max-width: 920px;
}

.fase-detail-title {
  align-items: center;
  display: flex;
  gap: 16px;
  justify-content: space-between;
}

.fase-detail-heading {
  font-size: 1.35rem;
  font-weight: 900;
  letter-spacing: 0;
  line-height: 1.2;
  overflow-wrap: anywhere;
}

.detail-label {
  color: rgba(var(--v-theme-on-surface), 0.62);
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0;
  text-transform: uppercase;
}

.detail-description-box {
  border: 1px solid rgba(var(--v-theme-on-surface), 0.12);
  border-radius: 8px;
  margin-bottom: 20px;
  margin-top: 6px;
  min-height: 96px;
  overflow-wrap: anywhere;
  padding: 14px;
  white-space: pre-wrap;
}

.detail-grid {
  display: grid;
  gap: 16px;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.detail-field {
  border: 1px solid rgba(var(--v-theme-on-surface), 0.1);
  border-radius: 8px;
  padding: 12px;
}

.detail-value {
  font-size: 0.95rem;
  font-weight: 700;
  margin-top: 4px;
  overflow-wrap: anywhere;
}

.detail-actions {
  justify-content: flex-end;
  padding: 16px 24px 20px;
}

.lavorazione-view {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 0;
  overflow: hidden;
  padding: 12px 38px 28px 26px;
}

.lavorazione-toolbar {
  align-items: flex-start;
  display: flex;
  flex: 0 0 auto;
  justify-content: center;
  min-height: 112px;
  position: relative;
}

.lavorazione-toolbar .btn-torna-fasi {
  left: 0;
  position: absolute;
  top: 0;
}

.lavorazione-title {
  font-size: 1.75rem;
  font-weight: 850;
  letter-spacing: 0;
  line-height: 1.15;
  margin: 0;
  max-width: min(100%, 760px);
  overflow-wrap: anywhere;
  padding: 16px 28px;
  text-align: center;
}

.lavorazione-content-card {
  border: 1px dashed rgba(var(--v-theme-on-surface), 0.18);
  border-radius: 8px;
  display: flex;
  flex: 1 1 auto;
  flex-direction: column;
  min-height: 0;
  overflow: hidden;
  padding: 76px 40px 36px;
}

.stepper-orizzontale {
  align-items: start;
  display: grid;
  flex: 0 0 auto;
  grid-template-columns: repeat(5, minmax(120px, 1fr));
  margin: 0 auto;
  max-width: 1080px;
  width: min(100%, 1080px);
}

.step-orizzontale-item {
  min-width: 0;
  text-align: center;
}

.step-orizzontale-node-wrap {
  align-items: center;
  display: flex;
  justify-content: center;
  margin-bottom: 10px;
  position: relative;
}

.step-orizzontale-node {
  align-items: center;
  border: 4px solid white;
  border-radius: 999px;
  box-shadow: 0 0 0 1px rgba(var(--v-theme-on-surface), 0.16);
  color: white;
  display: flex;
  font-size: 1rem;
  font-weight: 900;
  height: 52px;
  justify-content: center;
  position: relative;
  width: 52px;
  z-index: 1;
}

.step-orizzontale-non-avviato {
  background: #9e9e9e;
}

.step-orizzontale-completato {
  background: #2e7d32;
}

.step-orizzontale-attivo {
  background: #f9a825;
}

.step-orizzontale-line {
  background: rgba(var(--v-theme-on-surface), 0.2);
  height: 3px;
  left: calc(50% + 28px);
  position: absolute;
  right: calc(-50% + 28px);
  top: 50%;
  transform: translateY(-50%);
}

.step-orizzontale-title {
  font-size: 1rem;
  font-weight: 900;
  margin-bottom: 8px;
  overflow-wrap: anywhere;
}

.stepper-empty {
  margin: 0 auto;
  max-width: 620px;
}

.work-content-placeholder {
  align-items: center;
  display: flex;
  flex: 1 1 auto;
  flex-direction: column;
  justify-content: center;
  margin-top: 34px;
  min-height: 0;
  text-align: center;
}

.placeholder-title {
  font-size: 1.45rem;
  font-weight: 900;
  letter-spacing: 0;
}

.placeholder-subtitle {
  color: rgba(var(--v-theme-on-surface), 0.58);
  font-size: 0.98rem;
  font-weight: 650;
  margin-top: 6px;
}

@media (max-width: 1100px) {
  .procedimento-page {
    --rail-width: 84px;
  }

  .fasi-verticali-view {
    grid-template-columns: minmax(340px, 46%) minmax(0, 1fr);
  }

  .stepper-orizzontale {
    grid-template-columns: repeat(5, minmax(96px, 1fr));
  }
}

@media (max-width: 720px) {
  .procedimento-page {
    --rail-width: 54px;
    height: auto;
    min-height: calc(100vh - 112px);
    overflow: visible;
  }

  .procedimento-header {
    align-items: flex-start;
    flex-wrap: wrap;
    gap: 12px;
    height: auto;
    padding: 14px;
  }

  .btn-torna-procedimenti {
    min-height: 72px;
  }

  .btn-procedimenti-icon {
    height: 58px;
    width: 58px;
  }

  .btn-procedimenti-text {
    font-size: 1rem;
  }

  .btn-torna-fasi {
    min-height: 40px;
    width: auto;
  }

  .procedimento-shell {
    min-height: calc(100vh - 210px);
  }

  .procedimento-title-vertical {
    font-size: 1rem;
  }

  .fasi-verticali-view {
    gap: 18px;
    grid-template-columns: 1fr;
    overflow-y: auto;
    padding: 18px 14px 22px;
  }

  .fasi-stepper-scroll {
    height: auto;
    max-height: 360px;
  }

  .detail-grid {
    grid-template-columns: 1fr;
  }

  .lavorazione-view {
    overflow-y: auto;
    padding: 18px 14px 22px;
  }

  .lavorazione-toolbar {
    align-items: stretch;
    gap: 14px;
    min-height: 0;
    position: static;
    flex-direction: column;
  }

  .lavorazione-toolbar .btn-torna-fasi {
    left: auto;
    position: static;
    top: auto;
  }

  .lavorazione-title {
    font-size: 1.55rem;
    max-width: none;
    padding: 14px 18px;
  }

  .lavorazione-content-card {
    margin-top: 18px;
    padding: 28px 16px;
  }

  .stepper-orizzontale {
    gap: 18px;
    grid-template-columns: 1fr;
    max-width: 420px;
  }

  .step-orizzontale-line {
    display: none;
  }

  .work-content-placeholder {
    min-height: 280px;
  }
}
</style>
