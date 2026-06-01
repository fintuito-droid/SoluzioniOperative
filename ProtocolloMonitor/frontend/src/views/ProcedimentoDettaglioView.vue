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

        <template v-if="!modalitaLavorazione">
          <v-col cols="12" md="4" class="workflow-column">
            <div class="pa-4">
              <div class="d-flex flex-wrap align-center justify-space-between ga-2 mb-4">
                <div class="text-subtitle-1 font-weight-bold">
                  Fasi del procedimento
                </div>

                <div class="d-flex align-center ga-2">
                  <v-chip color="primary" variant="tonal" size="small">
                    Dati reali
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
                            color="indigo"
                            size="x-small"
                            variant="tonal"
                          >
                            {{ fase.sottofasi.length }}
                          </v-chip>

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
                  {{ faseSelezionata.descrizione }}
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

                  <v-col cols="12" md="6">
                    <div class="label">Obbligatoria</div>
                    <div class="value">{{ faseSelezionata.obbligatoria ? 'Si' : 'No' }}</div>
                  </v-col>

                  <v-col cols="12" md="6">
                    <div class="label">Bloccante</div>
                    <div class="value">{{ faseSelezionata.bloccante ? 'Si' : 'No' }}</div>
                  </v-col>
                </v-row>

                <v-divider class="my-4" />

                <div class="d-flex flex-wrap ga-2">
                  <v-btn
                    color="primary"
                    variant="flat"
                    prepend-icon="mdi-play-circle-outline"
                    @click="apriLavorazioneFase"
                  >
                    Avvia / lavora fase
                  </v-btn>

                  <v-tooltip
                    v-if="faseHaSottofasiNonCompletate(faseSelezionata)"
                    text="Completa prima tutte le sottofasi"
                    location="top"
                  >
                    <template #activator="{ props }">
                      <span v-bind="props">
                        <v-btn
                          color="green"
                          variant="tonal"
                          prepend-icon="mdi-check-circle-outline"
                          disabled
                        >
                          Completa fase
                        </v-btn>
                      </span>
                    </template>
                  </v-tooltip>

                  <v-btn
                    v-else
                    color="green"
                    variant="tonal"
                    prepend-icon="mdi-check-circle-outline"
                    @click="aggiornaStatoFase('COMPLETATA')"
                  >
                    Completa fase
                  </v-btn>

                  <v-btn
                    color="red"
                    variant="tonal"
                    prepend-icon="mdi-lock-outline"
                    @click="aggiornaStatoFase('BLOCCATA')"
                  >
                    Blocca fase
                  </v-btn>
                </div>

                <v-alert
                  v-if="faseHaSottofasiNonCompletate(faseSelezionata)"
                  type="info"
                  variant="tonal"
                  density="compact"
                  class="mt-4"
                >
                  Completa prima tutte le sottofasi.
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
        </template>

        <template v-else>
          <v-col cols="12" md="11" class="lavorazione-column">
            <div class="pa-4">
              <div class="fase-intestazione">
                {{ faseSelezionata?.descrizione }}
              </div>

              <div class="d-flex flex-wrap align-center justify-space-between ga-4 mb-6">
                <v-btn
                  color="grey"
                  variant="tonal"
                  prepend-icon="mdi-arrow-left"
                  @click="chiudiLavorazioneFase"
                >
                  Torna alle fasi
                </v-btn>

                <v-autocomplete
                  v-model="sottofaseDaAggiungere"
                  :items="catalogoSottofasi"
                  item-title="titolo"
                  item-value="codice"
                  label="Aggiungi sottofase"
                  return-object
                  clearable
                  variant="outlined"
                  density="comfortable"
                  hide-details
                  class="combo-sottofase"
                  :loading="loadingCatalogo"
                  :disabled="!catalogoSottofasi.length"
                  @update:model-value="aggiungiSottofaseDaCatalogo"
                >
                  <template #item="{ props, item }">
                    <v-list-item v-bind="props">
                      <template #prepend>
                        <v-avatar
                          size="38"
                          :color="catalogoItem(item).colore"
                          class="mr-3"
                        >
                          <v-icon color="white" size="22">
                            {{ catalogoItem(item).icona }}
                          </v-icon>
                        </v-avatar>
                      </template>

                      <v-list-item-title>
                        {{ catalogoItem(item).titolo }}
                      </v-list-item-title>

                      <v-list-item-subtitle>
                        {{ catalogoItem(item).descrizione }}
                      </v-list-item-subtitle>
                    </v-list-item>
                  </template>

                  <template #selection="{ item }">
                    <div class="d-flex align-center">
                      <v-avatar
                        size="28"
                        :color="catalogoItem(item).colore"
                        class="mr-2"
                      >
                        <v-icon color="white" size="18">
                          {{ catalogoItem(item).icona }}
                        </v-icon>
                      </v-avatar>

                      {{ catalogoItem(item).titolo }}
                    </div>
                  </template>
                </v-autocomplete>
              </div>

              <v-card class="pa-4" rounded="xl" elevation="1">
                <v-card-title class="text-subtitle-1 font-weight-bold">
                  Sottofasi della fase: {{ faseSelezionata?.titolo }}
                </v-card-title>

                <v-divider class="mb-4" />

                <div
                  v-if="faseSelezionata?.sottofasi.length"
                  class="sottofasi-stepper-wrapper"
                >
                  <div
                    v-for="(sottofase, index) in faseSelezionata.sottofasi"
                    :key="sottofase.id"
                    class="sottofase-step"
                  >
                    <div class="sottofase-avatar-area">
                      <v-avatar
                        class="sottofase-avatar"
                        :class="{ 'avatar-selezionato': sottofase.id === sottofaseSelezionataId }"
                        :color="coloreStatoWorkflow(sottofase.stato)"
                        size="56"
                        @click="selezionaSottofase(sottofase.id)"
                      >
                        <v-icon color="white" size="30">
                          {{ sottofase.icona }}
                        </v-icon>
                      </v-avatar>

                      <div
                        v-if="index < faseSelezionata.sottofasi.length - 1"
                        class="sottofase-linea"
                      />
                    </div>

                    <div class="sottofase-titolo">
                      {{ sottofase.titolo }}
                    </div>

                    <v-chip
                      size="x-small"
                      :color="coloreStatoWorkflow(sottofase.stato)"
                      variant="flat"
                      class="mt-2"
                    >
                      {{ labelStatoWorkflow(sottofase.stato) }}
                    </v-chip>
                  </div>
                </div>

                <v-alert
                  v-else
                  type="info"
                  variant="tonal"
                  class="mt-2"
                >
                  Questa fase non ha ancora sottofasi. Puoi aggiungerne una dal catalogo:
                  l'operazione resta locale finche il backend workflow rimane read-only.
                </v-alert>

                <v-divider class="my-4" />

                <v-card
                  v-if="sottofaseSelezionata"
                  class="pa-4"
                  rounded="lg"
                  variant="tonal"
                >
                  <div class="d-flex flex-wrap justify-space-between align-center ga-3">
                    <h3 class="mb-0">
                      {{ sottofaseSelezionata.ordine }}.
                      {{ sottofaseSelezionata.titolo }}
                    </h3>

                    <v-chip
                      :color="coloreStatoWorkflow(sottofaseSelezionata.stato)"
                      variant="flat"
                    >
                      {{ labelStatoWorkflow(sottofaseSelezionata.stato) }}
                    </v-chip>
                  </div>

                  <p class="mt-3">
                    {{ sottofaseSelezionata.descrizione }}
                  </p>

                  <div class="d-flex flex-wrap ga-2">
                    <v-btn
                      size="small"
                      color="blue"
                      variant="tonal"
                      @click="aggiornaStatoSottofase('IN_CORSO')"
                    >
                      In corso
                    </v-btn>

                    <v-btn
                      size="small"
                      color="green"
                      variant="tonal"
                      @click="aggiornaStatoSottofase('COMPLETATA')"
                    >
                      Completa
                    </v-btn>

                    <v-btn
                      size="small"
                      color="red"
                      variant="tonal"
                      @click="aggiornaStatoSottofase('BLOCCATA')"
                    >
                      Blocca
                    </v-btn>

                    <v-btn
                      size="small"
                      color="red"
                      variant="text"
                      prepend-icon="mdi-delete-outline"
                      @click="richiediEliminazioneSottofase(sottofaseSelezionata)"
                    >
                      Elimina locale
                    </v-btn>
                  </div>

                  <SottofaseDocumentaleCard
                    :key="`documentale-${sottofaseSelezionata.id}-${refreshSottofaseKey}`"
                    :id-sottofase="sottofaseSelezionata.id"
                    class="mt-4"
                  />

                  <WorkflowSottofaseCard
                    :id-sottofase="sottofaseSelezionata.id"
                    :titolo-sottofase="sottofaseSelezionata.titolo"
                    class="mt-4"
                    @workflow-aggiornato="gestisciWorkflowAggiornato"
                  />
                </v-card>
              </v-card>
            </div>
          </v-col>
        </template>
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

    <v-dialog
      v-model="dialogEliminaSottofase"
      max-width="460"
    >
      <v-card rounded="lg">
        <v-card-title class="text-subtitle-1 font-weight-bold">
          Elimina sottofase locale
        </v-card-title>

        <v-card-text>
          Vuoi eliminare
          <strong>{{ sottofaseDaEliminare?.titolo || 'questa sottofase' }}</strong>
          dalla fase corrente?
          <div class="text-caption text-medium-emphasis mt-2">
            L'operazione modifica solo la vista locale e non salva nulla sul backend.
          </div>
        </v-card-text>

        <v-card-actions>
          <v-spacer />

          <v-btn
            variant="text"
            @click="annullaEliminazioneSottofase"
          >
            Annulla
          </v-btn>

          <v-btn
            color="red"
            variant="flat"
            @click="confermaEliminazioneSottofase"
          >
            Elimina
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import {
  countProtocolliProcedimento,
  createFaseProcedimento,
  getProcedimento,
  listCatalogoSottofasi,
  listFasiProcedimento,
  listProtocolliProcedimento,
  listSottofasiFase,
  updateFaseProcedimento
} from '../services/procedimentoApi'
import SottofaseDocumentaleCard from '../components/procedimenti/SottofaseDocumentaleCard.vue'
import WorkflowSottofaseCard from '../components/procedimenti/WorkflowSottofaseCard.vue'
import { statiWorkflow } from '../mock/procedimentoWorkflowMock'

const route = useRoute()
const router = useRouter()

const procedimento = ref(null)
const protocolli = ref([])
const numeroProtocolliApi = ref(null)
const loading = ref(false)
const loadingProtocolli = ref(false)
const loadingWorkflow = ref(false)
const loadingCatalogo = ref(false)
const errore = ref('')
const erroreWorkflow = ref('')

const fasiWorkflow = ref([])
const catalogoSottofasi = ref([])
const faseSelezionataId = ref(null)
const sottofaseSelezionataId = ref(null)
const sottofaseDaAggiungere = ref(null)
const sottofaseDaEliminare = ref(null)
const dialogEliminaSottofase = ref(false)
const modalitaLavorazione = ref(false)
const refreshSottofaseKey = ref(0)
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

const sottofaseSelezionata = computed(() => {
  return faseSelezionata.value?.sottofasi.find(
    (sottofase) => sottofase.id === sottofaseSelezionataId.value
  )
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
  loadingCatalogo.value = true
  erroreWorkflow.value = ''

  try {
    const [fasiApi, catalogoApi] = await Promise.all([
      listFasiProcedimento(idProcedimento.value),
      listCatalogoSottofasi(true)
    ])

    catalogoSottofasi.value = catalogoApi.map(normalizzaCatalogoSottofase)

    const fasiNormalizzate = await Promise.all(
      fasiApi.map(async (fase) => {
        const faseNormalizzata = normalizzaFaseWorkflow(fase)

        try {
          const sottofasi = await listSottofasiFase(faseNormalizzata.id)
          faseNormalizzata.sottofasi = sottofasi
            .map(normalizzaSottofaseWorkflow)
            .sort(confrontaOrdine)
        } catch {
          faseNormalizzata.sottofasi = []
        }

        return faseNormalizzata
      })
    )

    fasiWorkflow.value = fasiNormalizzate.sort(confrontaOrdine)
    faseSelezionataId.value = fasiNormalizzate[0]?.id ?? null
    sottofaseSelezionataId.value = null
    modalitaLavorazione.value = false
  } catch (error) {
    erroreWorkflow.value = 'Impossibile caricare il workflow da FastAPI.'
    fasiWorkflow.value = []
    catalogoSottofasi.value = []
    faseSelezionataId.value = null
    sottofaseSelezionataId.value = null
  } finally {
    loadingWorkflow.value = false
    loadingCatalogo.value = false
  }
}

async function ricaricaSottofasiFaseCorrente() {
  if (!faseSelezionata.value) return

  const idFase = faseSelezionata.value.id
  const idSottofaseCorrente = sottofaseSelezionataId.value

  try {
    const sottofasi = await listSottofasiFase(idFase)
    faseSelezionata.value.sottofasi = sottofasi
      .map(normalizzaSottofaseWorkflow)
      .sort(confrontaOrdine)

    if (
      idSottofaseCorrente &&
      faseSelezionata.value.sottofasi.some(
        (sottofase) => sottofase.id === idSottofaseCorrente
      )
    ) {
      sottofaseSelezionataId.value = idSottofaseCorrente
    } else {
      sottofaseSelezionataId.value = faseSelezionata.value.sottofasi[0]?.id ?? null
    }
  } catch {
    erroreWorkflow.value =
      'Workflow aggiornato, ma non e stato possibile ricaricare le sottofasi.'
  }
}

async function gestisciWorkflowAggiornato() {
  refreshSottofaseKey.value += 1
  await ricaricaSottofasiFaseCorrente()
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
    obbligatoria: Boolean(dato.obbligatoria ?? dato.Obbligatoria),
    bloccante: Boolean(dato.bloccante ?? dato.Bloccante),
    responsabile: dato.responsabile ?? dato.Responsabile ?? '-',
    dataScadenza: dato.data_scadenza ?? dato.DataScadenza ?? '-',
    sottofasi: []
  }
}

function normalizzaSottofaseWorkflow(dato) {
  return {
    id: dato.id_sottofase ?? dato.IDSottofase,
    ordine: dato.ordine ?? dato.Ordine ?? 0,
    titolo: dato.titolo ?? dato.Titolo ?? 'Sottofase',
    descrizione: dato.descrizione ?? dato.Descrizione ?? '',
    stato: dato.stato_sottofase ?? dato.StatoSottofase ?? 'NON_AVVIATA',
    icona: dato.icona ?? dato.Icona ?? 'mdi-checkbox-blank-circle-outline'
  }
}

function normalizzaCatalogoSottofase(dato = {}) {
  const sorgente = dato?.raw ?? dato?.value ?? dato ?? {}

  return {
    id: sorgente.id ?? sorgente.id_catalogo_sottofase ?? sorgente.IDCatalogoSottofase,
    codice: sorgente.codice ?? sorgente.codice_sottofase ?? sorgente.CodiceSottofase ?? '',
    titolo: sorgente.titolo ?? sorgente.Titolo ?? 'Sottofase',
    descrizione: sorgente.descrizione ?? sorgente.Descrizione ?? '',
    icona:
      sorgente.icona ??
      sorgente.Icona ??
      'mdi-checkbox-blank-circle-outline',
    colore: sorgente.colore ?? sorgente.Colore ?? 'grey',
    categoria: sorgente.categoria ?? sorgente.Categoria ?? '',
    ordineDefault: sorgente.ordineDefault ?? sorgente.ordine_default ?? sorgente.OrdineDefault ?? 0
  }
}

function catalogoItem(item) {
  return normalizzaCatalogoSottofase(item)
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
    sottofaseSelezionataId.value = null
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
  sottofaseSelezionataId.value = null
}

function apriLavorazioneFase() {
  modalitaLavorazione.value = true

  if (faseSelezionata.value?.sottofasi.length) {
    sottofaseSelezionataId.value = faseSelezionata.value.sottofasi[0].id
  }
}

function chiudiLavorazioneFase() {
  modalitaLavorazione.value = false
}

function selezionaSottofase(idSottofase) {
  sottofaseSelezionataId.value = idSottofase
}

function aggiungiSottofaseDaCatalogo(template) {
  if (!template || !faseSelezionata.value) return

  const sottofaseCatalogo = normalizzaCatalogoSottofase(template)

  if (!sottofaseCatalogo.codice && !sottofaseCatalogo.titolo) {
    sottofaseDaAggiungere.value = null
    return
  }

  const nuovaSottofase = {
    id: Date.now(),
    ordine: faseSelezionata.value.sottofasi.length + 1,
    codice: sottofaseCatalogo.codice,
    titolo: sottofaseCatalogo.titolo,
    descrizione: sottofaseCatalogo.descrizione,
    stato: 'NON_AVVIATA',
    icona: sottofaseCatalogo.icona,
    colore: sottofaseCatalogo.colore
  }

  faseSelezionata.value.sottofasi.push(nuovaSottofase)
  faseSelezionata.value.sottofasi.sort(confrontaOrdine)
  sottofaseSelezionataId.value = nuovaSottofase.id

  setTimeout(() => {
    sottofaseDaAggiungere.value = null
  }, 100)
}

function aggiornaStatoFase(stato) {
  if (!faseSelezionata.value) return
  if (stato === 'COMPLETATA' && faseHaSottofasiNonCompletate(faseSelezionata.value)) {
    return
  }
  faseSelezionata.value.stato = stato
}

function aggiornaStatoSottofase(stato) {
  if (!sottofaseSelezionata.value) return
  sottofaseSelezionata.value.stato = stato
}

function faseHaSottofasiNonCompletate(fase) {
  if (!fase?.sottofasi?.length) return false

  return fase.sottofasi.some(
    (sottofase) => sottofase.stato !== 'COMPLETATA'
  )
}

function richiediEliminazioneSottofase(sottofase) {
  if (!sottofase) return

  sottofaseDaEliminare.value = sottofase
  dialogEliminaSottofase.value = true
}

function annullaEliminazioneSottofase() {
  dialogEliminaSottofase.value = false
  sottofaseDaEliminare.value = null
}

function confermaEliminazioneSottofase() {
  if (!faseSelezionata.value || !sottofaseDaEliminare.value) {
    annullaEliminazioneSottofase()
    return
  }

  faseSelezionata.value.sottofasi = faseSelezionata.value.sottofasi
    .filter((sottofase) => sottofase.id !== sottofaseDaEliminare.value.id)
    .map((sottofase, index) => ({
      ...sottofase,
      ordine: index + 1
    }))

  sottofaseSelezionataId.value =
    faseSelezionata.value.sottofasi[0]?.id ?? null

  annullaEliminazioneSottofase()
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

function colorePriorita(valore) {
  switch (valore) {
    case 'Urgente':
    case 'URGENTE':
      return 'red'
    case 'Alta':
    case 'ALTA':
    case 'MEDIA':
      return 'orange'
    case 'Bassa':
    case 'BASSA':
      return 'grey'
    default:
      return 'green'
  }
}

function coloreProcedimento(valore) {
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
  caricaWorkflow()
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

.workflow-card {
  overflow: hidden;
}

.procedimento-side {
  align-items: center;
  background: #111827;
  display: flex;
  justify-content: center;
  min-height: 620px;
}

.procedimento-verticale {
  color: #38bdf8;
  font-size: 1.35rem;
  font-weight: 700;
  letter-spacing: 0;
  line-height: 1.25;
  max-height: 560px;
  text-align: center;
  transform: rotate(180deg);
  writing-mode: vertical-rl;
}

.workflow-column,
.workflow-detail-column,
.lavorazione-column {
  min-height: 620px;
}

.timeline-scroll {
  --timeline-circle-size: 28px;
  --timeline-line-width: 3px;
  max-height: 540px;
  overflow-y: auto;
  padding-right: 8px;
}

.timeline-item {
  display: grid;
  column-gap: 20px;
  grid-template-columns: var(--timeline-circle-size) minmax(0, 1fr);
  position: relative;
}

.timeline-item:not(:last-child)::before {
  background: #d1d5db;
  bottom: -8px;
  content: '';
  left: calc((var(--timeline-circle-size) - var(--timeline-line-width)) / 2);
  position: absolute;
  top: 34px;
  width: var(--timeline-line-width);
}

.timeline-marker {
  display: flex;
  justify-content: center;
  padding-top: 14px;
  position: relative;
  width: var(--timeline-circle-size);
  z-index: 1;
}

.timeline-number {
  color: white;
  font-size: 0.78rem;
  font-weight: 800;
}

.fase-card {
  cursor: pointer;
  margin-bottom: 14px;
  min-height: 126px;
}

.fase-selezionata {
  outline: 2px solid #1976d2;
}

.scadenza-scaduta {
  color: #b91c1c;
  font-weight: 800;
}

.scadenza-vicina {
  color: #c2410c;
  font-weight: 800;
}

.scadenza-standard {
  color: inherit;
}

.fase-intestazione {
  color: #b91c1c;
  font-size: 1.45rem;
  font-weight: 600;
  line-height: 1.35;
  margin-bottom: 24px;
  text-align: center;
}

.combo-sottofase {
  max-width: 520px;
  min-width: min(420px, 100%);
}

.sottofasi-stepper-wrapper {
  align-items: flex-start;
  background: white;
  display: flex;
  overflow-x: auto;
  overflow-y: hidden;
  padding: 28px 20px 36px;
}

.sottofase-step {
  flex-shrink: 0;
  max-width: 170px;
  min-width: 170px;
  position: relative;
  text-align: center;
}

.sottofase-avatar-area {
  align-items: center;
  display: flex;
  height: 70px;
  justify-content: center;
  position: relative;
}

.sottofase-avatar {
  border: 3px solid white;
  box-shadow: 0 0 0 2px #d1d5db;
  cursor: pointer;
  z-index: 2;
}

.avatar-selezionato {
  box-shadow: 0 0 0 4px #1976d2;
}

.sottofase-linea {
  background: #d1d5db;
  height: 4px;
  left: 50%;
  position: absolute;
  right: -50%;
  top: 50%;
  transform: translateY(-50%);
  z-index: 1;
}

.sottofase-titolo {
  font-size: 0.86rem;
  font-weight: 700;
  line-height: 1.25;
  margin-top: 12px;
  min-height: 40px;
}

:deep(thead th) {
  color: #42a5f5 !important;
  font-size: 0.72rem !important;
  font-weight: 800 !important;
  letter-spacing: 0;
}

:deep(tbody tr:hover td) {
  background-color: #fff8c6 !important;
}

@media (max-width: 959px) {
  .procedimento-side {
    min-height: 96px;
  }

  .procedimento-verticale {
    max-height: none;
    transform: none;
    writing-mode: horizontal-tb;
  }
}
</style>
