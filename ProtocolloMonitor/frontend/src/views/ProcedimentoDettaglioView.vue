<template>
  <v-container fluid class="pa-4 dettaglio-procedimento-page">
    <div class="page-header">
      <div>
        <div class="text-overline text-medium-emphasis">
          Protocollo Monitor
        </div>
        <h1 class="page-title">
          Dettaglio procedimento
        </h1>
      </div>

      <v-btn
        class="btn-torna-procedimenti"
        prepend-icon="mdi-arrow-left"
        variant="outlined"
        @click="tornaAElenco"
      >
        Elenco procedimenti
      </v-btn>
    </div>

    <v-alert
      v-if="errore"
      type="warning"
      variant="tonal"
      class="mb-4"
    >
      {{ errore }}
    </v-alert>

    <v-card rounded="lg" elevation="1" class="mb-4 info-card">
      <v-card-title class="text-subtitle-1 font-weight-bold">
        Informazioni procedimento
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
          <v-col cols="12" md="3">
            <div class="label">Codice</div>
            <div class="value">
              {{ procedimento.CodiceProcedimento || '-' }}
            </div>
          </v-col>

          <v-col cols="12" md="3">
            <div class="label">Stato</div>
            <v-chip
              :color="coloreProcedimento(procedimento.StatoProcedimento)"
              size="small"
              variant="tonal"
            >
              {{ procedimento.StatoProcedimento || 'Non definito' }}
            </v-chip>
          </v-col>

          <v-col cols="12" md="3">
            <div class="label">Priorita</div>
            <v-chip
              :color="colorePriorita(procedimento.Priorita)"
              size="small"
              variant="tonal"
            >
              {{ procedimento.Priorita || 'Normale' }}
            </v-chip>
          </v-col>

          <v-col cols="12" md="3">
            <div class="label">Data scadenza</div>
            <div class="value">
              {{ procedimento.DataScadenza || '-' }}
            </div>
          </v-col>

          <v-col cols="12">
            <div class="label">Titolo</div>
            <div class="value titolo-procedimento">
              {{ procedimento.Titolo || '-' }}
            </div>
          </v-col>

          <v-col cols="12" md="4">
            <div class="label">Azienda/Soggetto</div>
            <div class="value">
              {{ procedimento.AziendaSoggetto || '-' }}
            </div>
          </v-col>

          <v-col cols="12" md="4">
            <div class="label">Comando</div>
            <div class="value">
              {{ procedimento.ComandoCompetenza || '-' }}
            </div>
          </v-col>

          <v-col cols="12" md="4">
            <div class="label">Settore</div>
            <div class="value">
              {{ procedimento.SettoreCompetenza || '-' }}
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

    <v-card rounded="lg" elevation="1" class="fasi-card">
      <v-card-title class="fasi-title">
        <div>
          <div class="text-subtitle-1 font-weight-bold">
            Fasi del procedimento
          </div>
          <div class="text-caption text-medium-emphasis">
            Elenco verticale delle fasi configurate
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
      </v-card-title>

      <v-divider />

      <v-card-text>
        <v-alert
          v-if="loadingWorkflow"
          type="info"
          variant="tonal"
          class="mb-4"
        >
          Caricamento fasi in corso...
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
          class="fasi-list"
        >
          <v-card
            v-for="fase in fasiWorkflow"
            :key="fase.id"
            rounded="lg"
            variant="outlined"
            class="fase-row"
            :class="{ 'fase-selezionata': fase.id === faseSelezionataId }"
            @click="selezionaFase(fase.id)"
          >
            <v-card-text class="fase-row-content">
              <div class="fase-order">
                {{ fase.ordine }}
              </div>

              <div class="fase-main">
                <div class="fase-heading">
                  {{ fase.titolo }}
                </div>
                <div class="fase-description">
                  {{ fase.descrizione || 'Nessuna descrizione.' }}
                </div>
              </div>

              <v-chip
                :color="coloreStatoWorkflow(fase.stato)"
                size="small"
                variant="tonal"
              >
                {{ labelStatoWorkflow(fase.stato) }}
              </v-chip>

              <v-btn
                icon="mdi-pencil"
                size="small"
                variant="text"
                class="fase-edit-btn"
                @click.stop="apriDialogModificaFase(fase)"
              />
            </v-card-text>
          </v-card>
        </div>

        <v-alert
          v-else
          type="info"
          variant="tonal"
        >
          Nessuna fase configurata per questo procedimento.
        </v-alert>
      </v-card-text>
    </v-card>

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

const route = useRoute()
const router = useRouter()

const procedimento = ref(null)
const loading = ref(false)
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

const idProcedimento = computed(() => route.params.idProcedimento)

async function caricaDettaglio() {
  loading.value = true
  errore.value = ''

  try {
    const dettaglio = await getProcedimento(idProcedimento.value)
    procedimento.value = normalizzaProcedimento(dettaglio)
  } catch (error) {
    errore.value = error.status === 404
      ? 'Procedimento non trovato.'
      : 'Impossibile caricare il procedimento da FastAPI.'
    procedimento.value = null
  } finally {
    loading.value = false
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
    stato: dato.stato_fase ?? dato.StatoFase ?? 'NON_AVVIATA'
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

onMounted(() => {
  caricaDettaglio()
  caricaWorkflow()
})
</script>

<style scoped>
.dettaglio-procedimento-page {
  margin: 0 auto;
  max-width: 1180px;
}

.page-header {
  align-items: center;
  display: flex;
  gap: 16px;
  justify-content: space-between;
  margin-bottom: 16px;
}

.page-title {
  font-size: 1.55rem;
  font-weight: 800;
  letter-spacing: 0;
  line-height: 1.2;
  margin: 0;
}

.btn-torna-procedimenti {
  background: #eeeeee;
  border: 1px solid #c62828;
  color: #c62828;
  font-weight: 800;
  letter-spacing: 0;
  text-transform: none;
}

.btn-torna-procedimenti:hover {
  background: #ffeb3b;
  border-color: #c62828;
  color: #111111;
}

.info-card,
.fasi-card {
  border-radius: 8px;
}

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

.titolo-procedimento {
  font-size: 1.1rem;
}

.box-testo {
  border: 1px solid rgba(var(--v-theme-on-surface), 0.12);
  border-radius: 8px;
  padding: 12px;
  white-space: pre-wrap;
}

.fasi-title {
  align-items: center;
  display: flex;
  gap: 16px;
  justify-content: space-between;
}

.fasi-list {
  display: grid;
  gap: 12px;
}

.fase-row {
  cursor: pointer;
  transition: border-color 0.16s ease, background-color 0.16s ease;
}

.fase-row:hover,
.fase-selezionata {
  background: rgba(var(--v-theme-primary), 0.04);
  border-color: rgb(var(--v-theme-primary));
}

.fase-row-content {
  align-items: center;
  display: grid;
  gap: 14px;
  grid-template-columns: 44px minmax(0, 1fr) auto 40px;
}

.fase-order {
  align-items: center;
  background: rgb(var(--v-theme-primary));
  border-radius: 999px;
  color: white;
  display: flex;
  font-size: 0.9rem;
  font-weight: 800;
  height: 34px;
  justify-content: center;
  width: 34px;
}

.fase-main {
  min-width: 0;
}

.fase-heading {
  font-size: 0.98rem;
  font-weight: 800;
  overflow-wrap: anywhere;
}

.fase-description {
  color: rgba(var(--v-theme-on-surface), 0.68);
  font-size: 0.84rem;
  margin-top: 2px;
  overflow-wrap: anywhere;
}

.fase-edit-btn {
  justify-self: end;
}

@media (max-width: 720px) {
  .page-header,
  .fasi-title {
    align-items: stretch;
    flex-direction: column;
  }

  .btn-torna-procedimenti {
    align-self: flex-start;
  }

  .fase-row-content {
    grid-template-columns: 40px minmax(0, 1fr) 40px;
  }

  .fase-row-content .v-chip {
    grid-column: 2 / 4;
    justify-self: start;
  }
}
</style>
