<template>
  <v-container fluid class="pa-4 dettaglio-procedimento-page">
    <div class="page-header">
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
    </div>

    <div class="procedimento-layout">
      <section class="fasi-section">
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
          class="fasi-stepper-shell"
        >
          <div class="procedimento-title-rail">
            <div class="procedimento-title-vertical">
              {{ titoloProcedimentoVerticale }}
            </div>
          </div>

          <div class="fasi-stepper-scroll">
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
                    <div class="fase-main">
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

                        <span v-if="fase.responsabile && fase.responsabile !== '-'">
                          Responsabile: {{ fase.responsabile }}
                        </span>

                        <span v-if="fase.dataScadenza && fase.dataScadenza !== '-'">
                          Scadenza: {{ fase.dataScadenza }}
                        </span>
                      </div>
                    </div>
                  </v-card-text>
                </v-card>
              </div>
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
                <div class="detail-value">{{ valoreDettaglio(faseSelezionata.ordine) }}</div>
              </div>

              <div class="detail-field">
                <div class="detail-label">Stato</div>
                <div class="detail-value">{{ labelStatoWorkflow(faseSelezionata.stato) }}</div>
              </div>

              <div class="detail-field">
                <div class="detail-label">Responsabile</div>
                <div class="detail-value">{{ valoreDettaglio(faseSelezionata.responsabile) }}</div>
              </div>

              <div class="detail-field">
                <div class="detail-label">Data scadenza</div>
                <div class="detail-value">{{ valoreDettaglio(faseSelezionata.dataScadenza) }}</div>
              </div>

              <div class="detail-field">
                <div class="detail-label">Data avvio</div>
                <div class="detail-value">{{ valoreDettaglio(faseSelezionata.dataAvvio) }}</div>
              </div>

              <div class="detail-field">
                <div class="detail-label">Data completamento</div>
                <div class="detail-value">{{ valoreDettaglio(faseSelezionata.dataCompletamento) }}</div>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </section>
    </div>

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
  listFasiProcedimento,
  updateFaseProcedimento
} from '../services/procedimentoApi'
import { statiWorkflow } from '../mock/procedimentoWorkflowMock'
import elencoProcedimentoIcon from '../assets/ElencoProcedimentoICO.png'

const route = useRoute()
const router = useRouter()

const procedimento = ref(null)
const loadingWorkflow = ref(false)
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

    fasiWorkflow.value = fasiNormalizzate
    faseSelezionataId.value = fasiNormalizzate[0]?.id ?? null
  } catch (error) {
    erroreWorkflow.value = 'Impossibile caricare le fasi da FastAPI.'
    fasiWorkflow.value = []
    faseSelezionataId.value = null
  } finally {
    loadingWorkflow.value = false
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
    dataAvvio: dato.data_avvio ?? dato.DataAvvio ?? '-',
    dataCompletamento:
      dato.data_completamento ??
      dato.DataCompletamento ??
      '-'
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

function valoreDettaglio(value) {
  if (value === null || value === undefined || value === '') return '-'
  return value
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
.dettaglio-procedimento-page {
  --stepper-bottom-gap: 40px;
  --stepper-fixed-height: calc(100vh - 246px);
  box-sizing: border-box;
  height: calc(100vh - 112px);
  margin: 0;
  max-width: none;
  overflow: hidden;
}

.page-header {
  align-items: center;
  display: flex;
  gap: 16px;
  justify-content: flex-start;
  margin-bottom: 18px;
}

.btn-torna-procedimenti {
  background: #eeeeee;
  border: 1px solid #c62828;
  color: #111111;
  font-weight: 800;
  min-height: 96px;
  letter-spacing: 0;
  padding: 6px 30px 6px 18px;
  text-transform: none;
}

.btn-torna-procedimenti :deep(.v-btn__content) {
  align-items: center;
  display: flex;
  gap: 20px;
}

.btn-torna-procedimenti:hover {
  background: #ffeb3b;
  border-color: #c62828;
  color: #111111;
}

.btn-procedimenti-icon {
  display: block;
  height: 110px;
  object-fit: contain;
  width: 110px;
}

.btn-procedimenti-text {
  color: #111111;
  font-size: 1.25rem;
  font-weight: 800;
  letter-spacing: 0;
  line-height: 1.1;
}

.procedimento-layout {
  align-items: start;
  display: grid;
  gap: 24px;
  grid-template-columns: minmax(380px, 36vw) minmax(0, 1fr);
}

.fasi-section {
  min-width: 380px;
  padding-bottom: var(--stepper-bottom-gap);
}

.fasi-header {
  align-items: center;
  display: flex;
  gap: 14px;
  justify-content: space-between;
  margin-bottom: 14px;
}

.fasi-stepper-shell {
  background: rgb(var(--v-theme-surface));
  border-radius: 8px;
  box-sizing: border-box;
  display: grid;
  grid-template-columns: 56px minmax(0, 1fr);
  height: var(--stepper-fixed-height);
  max-height: var(--stepper-fixed-height);
  min-height: 280px;
  overflow: hidden;
}

.procedimento-title-rail {
  align-items: center;
  align-self: stretch;
  background: #0d47a1;
  border-radius: 8px 0 0 8px;
  box-sizing: border-box;
  color: white;
  display: flex;
  height: 100%;
  justify-content: center;
  overflow: hidden;
  padding: 12px 6px;
}

.procedimento-title-vertical {
  color: #ff9800;
  font-size: 1.25rem;
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

.fasi-stepper-scroll {
  box-sizing: border-box;
  height: 100%;
  overscroll-behavior: contain;
  overflow-y: auto;
  padding-bottom: 32px;
  padding-left: 12px;
  padding-right: 6px;
}

.fasi-stepper-scroll::-webkit-scrollbar {
  width: 8px;
}

.fasi-stepper-scroll::-webkit-scrollbar-thumb {
  background: rgba(var(--v-theme-on-surface), 0.24);
  border-radius: 999px;
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
  margin-bottom: 0;
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
  align-items: center;
  color: rgba(var(--v-theme-on-surface), 0.7);
  display: flex;
  flex-wrap: wrap;
  font-size: 0.76rem;
  gap: 6px 10px;
  margin-top: 10px;
}

.fase-edit-btn {
  flex: 0 0 auto;
}

.fase-detail-section {
  align-self: start;
  min-width: 0;
  padding-top: 40px;
}

.fase-detail-card {
  max-width: 820px;
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

@media (max-width: 1100px) {
  .procedimento-layout {
    grid-template-columns: minmax(380px, 48vw) minmax(0, 1fr);
  }
}

@media (max-width: 720px) {
  .dettaglio-procedimento-page {
    --stepper-bottom-gap: 32px;
    --stepper-fixed-height: calc(100vh - 242px);
  }

  .page-header,
  .fasi-header {
    align-items: stretch;
    flex-direction: column;
  }

  .btn-torna-procedimenti {
    align-self: flex-start;
  }

  .procedimento-layout {
    grid-template-columns: 1fr;
  }

  .fasi-section {
    min-width: 0;
  }

  .fase-detail-section {
    padding-top: 0;
  }

  .detail-grid {
    grid-template-columns: 1fr;
  }

  .fasi-stepper-shell {
    grid-template-columns: 44px minmax(0, 1fr);
  }

  .procedimento-title-vertical {
    font-size: 1rem;
  }

  .fase-step {
    grid-template-columns: 48px minmax(0, 1fr);
  }

  .step-dot {
    height: 36px;
    width: 36px;
  }
}
</style>
