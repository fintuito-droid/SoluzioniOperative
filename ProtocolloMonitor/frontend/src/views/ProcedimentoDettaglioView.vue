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
                  v-if="workflowConfigurabile"
                  class="workflow-quick-actions"
                >
                  <v-btn
                    color="primary"
                    :variant="workflowIstanzaFineAttivo ? 'flat' : 'tonal'"
                    prepend-icon="mdi-file-import-outline"
                    :loading="operazioneStepInCorso"
                    :disabled="!faseSelezionata || loadingStepOrizzontali"
                    @click="configuraWorkflowRapidoIstanzaFine"
                  >
                    Istanza -> Fine
                  </v-btn>

                  <v-btn
                    color="primary"
                    :variant="workflowPredefinitoAttivo ? 'flat' : 'tonal'"
                    prepend-icon="mdi-format-list-numbered"
                    :loading="operazioneStepInCorso"
                    :disabled="!faseSelezionata || loadingStepOrizzontali"
                    @click="configuraWorkflowPredefinito"
                  >
                    Predefinito
                  </v-btn>
                </div>

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
                        :class="classeStepOrizzontale(step)"
                        @click.stop="gestisciClickStepOrizzontale(step)"
                      >
                        {{ index + 1 }}
                      </div>

                      <div
                        v-if="index < stepOrizzontali.length - 1"
                        class="step-orizzontale-line"
                      />
                    </div>

                    <div
                      class="step-node-actions"
                    >
                      <v-btn
                        icon="mdi-delete-outline"
                        size="x-small"
                        variant="text"
                        color="error"
                        :disabled="operazioneStepInCorso"
                        @click.stop="apriConfermaEliminaStep(step)"
                      />

                      <v-menu location="bottom">
                        <template #activator="{ props }">
                          <v-btn
                            v-bind="props"
                            icon="mdi-plus-circle-outline"
                            size="x-small"
                            variant="text"
                            color="primary"
                            :disabled="operazioneStepInCorso"
                            @click.stop
                          />
                        </template>

                        <v-list density="compact">
                          <v-list-item
                            v-for="opzione in stepInseribili"
                            :key="opzione.codiceStep"
                            @click="inserisciStepDopo(step, opzione)"
                          >
                            <template #prepend>
                              <v-avatar
                                size="28"
                                color="primary"
                                variant="tonal"
                              >
                                <v-icon size="17">
                                  {{ opzione.icona }}
                                </v-icon>
                              </v-avatar>
                            </template>

                            <v-list-item-title>
                              {{ opzione.titoloStep }}
                            </v-list-item-title>
                          </v-list-item>
                        </v-list>
                      </v-menu>
                    </div>

                    <div class="step-orizzontale-title">
                      {{ step.titoloStep }}
                    </div>

                    <button
                      v-if="isIstanzaProtocolloCompletata(step)"
                      type="button"
                      class="step-istanza-linked"
                      title="Apri PDF protocollo collegato"
                      aria-label="Apri PDF protocollo collegato"
                      @click.stop="apriPdfProtocolloIstanza(step)"
                    >
                      <v-icon
                        size="34"
                        color="primary"
                      >
                        mdi-file-document-outline
                      </v-icon>
                      <v-icon
                        size="30"
                        color="success"
                      >
                        mdi-check-circle
                      </v-icon>
                    </button>
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

                <v-card
                  v-if="stepRedigiSelezionato"
                  class="redigi-work-panel"
                  rounded="lg"
                  variant="outlined"
                >
                  <v-card-title class="redigi-panel-title">
                    <div>
                      <div class="text-caption text-medium-emphasis">
                        Step operativo
                      </div>
                      <div class="redigi-panel-heading">
                        Step: Redigi
                      </div>
                    </div>

                    <v-chip
                      :color="coloreStatoStep(stepRedigiSelezionato.statoStep)"
                      variant="tonal"
                    >
                      Stato: {{ statoRedigiSelezionato }}
                    </v-chip>
                  </v-card-title>

                  <v-divider />

                  <v-card-text>
                    <div class="redigi-actions">
                      <v-btn
                        v-if="redigiAvviabile"
                        color="primary"
                        variant="flat"
                        prepend-icon="mdi-play-circle-outline"
                        :loading="operazioneStepInCorso"
                        @click="avviaRedigiSelezionato"
                      >
                        Avvia lavorazione
                      </v-btn>

                      <v-btn
                        v-if="redigiCompletabile"
                        color="success"
                        variant="flat"
                        prepend-icon="mdi-check-circle-outline"
                        :loading="operazioneStepInCorso"
                        @click="completaRedigiSelezionato"
                      >
                        Completa lavorazione
                      </v-btn>
                    </div>

                    <v-alert
                      v-if="erroreDocumentoPrincipaleRedigi"
                      type="warning"
                      variant="tonal"
                      density="compact"
                      class="mt-5"
                    >
                      {{ erroreDocumentoPrincipaleRedigi }}
                    </v-alert>

                    <v-card
                      class="redigi-document-card mt-5"
                      rounded="lg"
                      variant="tonal"
                    >
                      <v-card-text>
                        <div class="redigi-document-header">
                          <v-avatar
                            color="primary"
                            variant="tonal"
                            size="42"
                          >
                            <v-icon size="25">
                              mdi-file-document-outline
                            </v-icon>
                          </v-avatar>

                          <div>
                            <div class="redigi-document-title">
                              Documento Principale
                            </div>
                            <div class="text-caption text-medium-emphasis">
                              Documento operativo principale della sottofase
                            </div>
                          </div>
                        </div>

                        <v-progress-linear
                          v-if="loadingDocumentoPrincipaleRedigi"
                          color="primary"
                          indeterminate
                          rounded
                          class="mt-4"
                        />

                        <div
                          v-else-if="!documentoPrincipaleRedigi"
                          class="redigi-document-empty"
                        >
                          <div class="font-weight-bold">
                            Documento principale: assente
                          </div>
                          <v-btn
                            color="primary"
                            variant="flat"
                            prepend-icon="mdi-file-plus-outline"
                            :loading="creazioneDocumentoPrincipaleInCorso"
                            class="mt-3"
                            @click="creaDocumentoPrincipaleRedigi"
                          >
                            Crea documento principale
                          </v-btn>
                        </div>

                        <div
                          v-else
                          class="redigi-document-detail"
                        >
                          <div class="redigi-document-form">
                            <v-text-field
                              v-model="documentoMetadatiForm.titoloDocumento"
                              label="Titolo documento"
                              variant="outlined"
                              density="compact"
                            />

                            <v-select
                              v-model="documentoMetadatiForm.statoDocumento"
                              :items="statiDocumentoPrincipale"
                              label="Stato documento"
                              variant="outlined"
                              density="compact"
                            />

                            <v-select
                              v-model="documentoMetadatiForm.tipoDocumento"
                              :items="tipiDocumentoPrincipale"
                              label="Tipo documento"
                              variant="outlined"
                              density="compact"
                            />

                            <v-textarea
                              v-model="documentoMetadatiForm.descrizioneDocumento"
                              label="Descrizione documento"
                              variant="outlined"
                              rows="3"
                              auto-grow
                              class="redigi-document-description"
                            />
                          </div>

                          <div class="detail-grid mt-4">
                            <div class="detail-field">
                              <div class="detail-label">Ruolo</div>
                              <div class="detail-value">
                                {{ valoreDettaglio(documentoPrincipaleRedigi.ruoloDocumento) }}
                              </div>
                            </div>

                            <div class="detail-field">
                              <div class="detail-label">Tipo Origine</div>
                              <div class="detail-value">
                                {{ valoreDettaglio(documentoPrincipaleRedigi.tipoOrigine) }}
                              </div>
                            </div>

                            <div class="detail-field">
                              <div class="detail-label">Versione</div>
                              <div class="detail-value">
                                {{ valoreDettaglio(documentoPrincipaleRedigi.versioneDocumento) }}
                              </div>
                            </div>

                            <div class="detail-field">
                              <div class="detail-label">Data creazione</div>
                              <div class="detail-value">
                                {{ valoreDettaglio(documentoPrincipaleRedigi.dataCreazione) }}
                              </div>
                            </div>

                            <div class="detail-field">
                              <div class="detail-label">Data modifica</div>
                              <div class="detail-value">
                                {{ valoreDettaglio(documentoPrincipaleRedigi.dataModifica) }}
                              </div>
                            </div>

                            <div class="detail-field">
                              <div class="detail-label">Percorso</div>
                              <div class="detail-value">
                                {{ valoreDettaglio(documentoPrincipaleRedigi.percorsoDocumento) }}
                              </div>
                            </div>
                          </div>

                          <v-btn
                            color="primary"
                            variant="tonal"
                            prepend-icon="mdi-open-in-new"
                            :loading="aperturaDocumentoPrincipaleInCorso"
                            class="mt-4"
                            @click="apriDocumentoPrincipaleRedigi"
                          >
                            Apri documento
                          </v-btn>

                          <v-btn
                            color="primary"
                            variant="flat"
                            prepend-icon="mdi-content-save-outline"
                            :loading="salvataggioMetadatiDocumentoInCorso"
                            class="mt-4 ml-3"
                            @click="salvaMetadatiDocumentoPrincipaleRedigi"
                          >
                            Salva metadati documento
                          </v-btn>
                        </div>
                      </v-card-text>
                    </v-card>

                    <v-textarea
                      v-model="noteRedigiForm"
                      label="Note operative"
                      variant="outlined"
                      rows="5"
                      auto-grow
                      class="mt-5"
                    />
                  </v-card-text>

                  <v-card-actions class="justify-end">
                    <v-btn
                      color="primary"
                      variant="tonal"
                      prepend-icon="mdi-content-save-outline"
                      :loading="salvataggioNoteRedigiInCorso"
                      @click="salvaNoteRedigiSelezionato"
                    >
                      Salva note
                    </v-btn>
                  </v-card-actions>
                </v-card>

                <div
                  v-else
                  class="work-content-placeholder"
                >
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

    <v-dialog
      v-model="dialogEliminaStep"
      max-width="460"
    >
      <v-card rounded="lg">
        <v-card-title class="text-subtitle-1 font-weight-bold">
          Elimina step
        </v-card-title>

        <v-card-text>
          Confermi l'eliminazione dello step selezionato?
        </v-card-text>

        <v-card-actions class="justify-end">
          <v-btn
            variant="text"
            :disabled="operazioneStepInCorso"
            @click="dialogEliminaStep = false"
          >
            Annulla
          </v-btn>
          <v-btn
            color="error"
            variant="flat"
            :loading="operazioneStepInCorso"
            @click="confermaEliminaStep"
          >
            Elimina
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog
      v-model="dialogProtocolloIstanza"
      max-width="980"
    >
      <v-card rounded="lg">
        <v-card-title class="text-subtitle-1 font-weight-bold">
          Collega protocollo allo step Istanza
        </v-card-title>

        <v-card-text>
          <v-alert
            v-if="protocolloCollegatoCorrente"
            type="info"
            variant="tonal"
            density="compact"
            class="mb-4"
          >
            Protocollo collegato:
            {{ protocolloCollegatoCorrente.numeroProtocollo || protocolloCollegatoCorrente.idProtocollo }}
            -
            {{ protocolloCollegatoCorrente.oggetto || '-' }}
          </v-alert>

          <v-alert
            v-if="erroreProtocolloIstanza"
            type="error"
            variant="tonal"
            density="compact"
            class="mb-4"
          >
            {{ erroreProtocolloIstanza }}
          </v-alert>

          <v-text-field
            v-model="ricercaProtocolloIstanza"
            label="Cerca protocollo"
            variant="outlined"
            density="compact"
            prepend-inner-icon="mdi-magnify"
            clearable
            class="mb-3"
          />

          <v-data-table
            :headers="headersProtocolliIstanza"
            :items="protocolliIstanzaFiltrati"
            :loading="loadingProtocolliIstanza"
            density="compact"
            item-value="idProtocollo"
            hover
          >
            <template #item.dataProtocollo="{ item }">
              {{ valoreDettaglio(item.dataProtocollo) }}
            </template>

            <template #item.oggetto="{ item }">
              <span class="protocollo-oggetto-cell">
                {{ item.oggetto || '-' }}
              </span>
            </template>

            <template #item.actions="{ item }">
              <v-btn
                color="primary"
                variant="flat"
                size="small"
                :loading="collegamentoProtocolloInCorso"
                @click="selezionaProtocolloIstanza(item)"
              >
                Seleziona
              </v-btn>
            </template>

            <template #no-data>
              Nessun protocollo disponibile.
            </template>
          </v-data-table>
        </v-card-text>

        <v-card-actions class="justify-end">
          <v-btn
            variant="text"
            :disabled="collegamentoProtocolloInCorso"
            @click="chiudiDialogProtocolloIstanza"
          >
            Chiudi
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
  apriPdfProtocolloEsterno,
  apriDocumentoSottofase,
  avviaStepRedigi,
  completaStepRedigi,
  configuraStepOrizzontaliIstanzaFine,
  configuraStepOrizzontaliPredefinito,
  collegaProtocolloStepIstanza,
  createDocumentoPrincipaleSottofase,
  createFaseProcedimento,
  eliminaStepOrizzontale,
  getDocumentoPrincipaleSottofase,
  getProcedimento,
  inserisciStepOrizzontaleDopo,
  listFasiProcedimento,
  listProtocolli,
  listStepOrizzontaliFase,
  salvaNoteStepRedigi,
  updateDocumentoPrincipaleMetadatiSottofase,
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
const operazioneStepInCorso = ref(false)
const stepOperativoSelezionatoId = ref(null)
const noteRedigiForm = ref('')
const salvataggioNoteRedigiInCorso = ref(false)
const documentoPrincipaleRedigi = ref(null)
const loadingDocumentoPrincipaleRedigi = ref(false)
const creazioneDocumentoPrincipaleInCorso = ref(false)
const aperturaDocumentoPrincipaleInCorso = ref(false)
const salvataggioMetadatiDocumentoInCorso = ref(false)
const erroreDocumentoPrincipaleRedigi = ref('')
const dialogEliminaStep = ref(false)
const stepDaEliminare = ref(null)
const dialogProtocolloIstanza = ref(false)
const stepIstanzaCorrente = ref(null)
const protocolliIstanza = ref([])
const loadingProtocolliIstanza = ref(false)
const collegamentoProtocolloInCorso = ref(false)
const erroreProtocolloIstanza = ref('')
const ricercaProtocolloIstanza = ref('')
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
const documentoMetadatiForm = reactive({
  titoloDocumento: '',
  descrizioneDocumento: '',
  statoDocumento: 'BOZZA',
  tipoDocumento: 'ALTRO'
})

const regoleFase = {
  titolo: (value) => Boolean(String(value || '').trim()) || 'Titolo fase obbligatorio'
}

const stepInseribili = [
  { codiceStep: 'REDIGI', titoloStep: 'Redigi', icona: 'mdi-pencil' },
  { codiceStep: 'REVISIONA', titoloStep: 'Revisiona', icona: 'mdi-magnify' },
  { codiceStep: 'FIRMA', titoloStep: 'Firma', icona: 'mdi-signature-freehand' },
  {
    codiceStep: 'PROTOCOLLA',
    titoloStep: 'Protocolla',
    icona: 'mdi-file-document-outline'
  },
  { codiceStep: 'ALLEGATI', titoloStep: 'Allegati', icona: 'mdi-paperclip' },
  { codiceStep: 'FINE', titoloStep: 'Fine', icona: 'mdi-flag-checkered' },
  { codiceStep: 'TELEFONA', titoloStep: 'Telefona', icona: 'mdi-phone' },
  { codiceStep: 'MAIL', titoloStep: 'Mail', icona: 'mdi-email-outline' },
  {
    codiceStep: 'APPUNTAMENTO',
    titoloStep: 'Appuntamento',
    icona: 'mdi-calendar-clock'
  }
]

const statiDocumentoPrincipale = [
  'BOZZA',
  'IN_REVISIONE',
  'APPROVATO',
  'FIRMATO',
  'PROTOCOLLATO',
  'ARCHIVIATO'
]

const tipiDocumentoPrincipale = [
  'NOTA',
  'RELAZIONE',
  'VERBALE',
  'RICHIESTA',
  'PARERE',
  'ALTRO'
]

const headersProtocolliIstanza = [
  { title: 'Numero', key: 'numeroProtocollo', sortable: true },
  { title: 'Data', key: 'dataProtocollo', sortable: true },
  { title: 'Oggetto', key: 'oggetto', sortable: true },
  { title: 'Mittente', key: 'comandoMittente', sortable: true },
  { title: '', key: 'actions', sortable: false, align: 'end' }
]

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

const workflowIstanzaFineAttivo = computed(() => {
  const codici = stepOrizzontali.value.map((step) =>
    String(step.codiceStep || '').toUpperCase()
  )
  return codici.length === 2 && codici[0] === 'ISTANZA' && codici[1] === 'FINE'
})

const workflowPredefinitoAttivo = computed(() => {
  const codici = stepOrizzontali.value.map((step) =>
    String(step.codiceStep || '').toUpperCase()
  )
  return (
    codici.length === 5 &&
    codici.join('|') === 'REDIGI|REVISIONA|FIRMA|PROTOCOLLA|FINE'
  )
})

const workflowConfigurabile = computed(() => {
  return stepOrizzontali.value.every((step) => {
    return String(step.statoStep || '').toUpperCase() === 'NON_AVVIATO'
  })
})

const stepOperativoSelezionato = computed(() => {
  return stepOrizzontali.value.find((step) => {
    return Number(step.id) === Number(stepOperativoSelezionatoId.value)
  })
})

const stepRedigiSelezionato = computed(() => {
  const step = stepOperativoSelezionato.value
  return isStepRedigi(step) ? step : null
})

const idSottofaseDocumentaleRedigi = computed(() => {
  return faseSelezionata.value?.idSottofase || faseSelezionata.value?.id || null
})

const statoRedigiSelezionato = computed(() => {
  return String(stepRedigiSelezionato.value?.statoStep || 'NON_AVVIATO').toUpperCase()
})

const redigiAvviabile = computed(() => {
  return statoRedigiSelezionato.value === 'NON_AVVIATO'
})

const redigiCompletabile = computed(() => {
  return statoRedigiSelezionato.value === 'IN_CORSO'
})

const protocolloCollegatoCorrente = computed(() => {
  const step = stepIstanzaCorrente.value
  if (!step?.idProtocolloCollegato) return null

  return {
    idProtocollo: step.idProtocolloCollegato,
    numeroProtocollo: step.numeroProtocolloCollegato,
    dataProtocollo: step.dataProtocolloCollegato,
    oggetto: step.oggettoProtocolloCollegato
  }
})

const protocolliIstanzaFiltrati = computed(() => {
  const filtro = String(ricercaProtocolloIstanza.value || '').trim().toLowerCase()
  if (!filtro) return protocolliIstanza.value

  return protocolliIstanza.value.filter((protocollo) => {
    return [
      protocollo.numeroProtocollo,
      protocollo.dataProtocollo,
      protocollo.oggetto,
      protocollo.comandoMittente,
      protocollo.modalita
    ]
      .map((value) => String(value || '').toLowerCase())
      .some((value) => value.includes(filtro))
  })
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
    idSottofase:
      dato.id_sottofase ??
      dato.IDSottofase ??
      dato.idSottofase ??
      null,
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
      'NON_AVVIATO',
    dataAvvio:
      dato.data_avvio ??
      dato.DataAvvio ??
      dato.dataAvvio ??
      '',
    dataCompletamento:
      dato.data_completamento ??
      dato.DataCompletamento ??
      dato.dataCompletamento ??
      '',
    noteOperative:
      dato.note_operative ??
      dato.NoteOperative ??
      dato.noteOperative ??
      '',
    idProtocolloCollegato:
      dato.id_protocollo_collegato ??
      dato.IDProtocolloCollegato ??
      dato.idProtocolloCollegato ??
      null,
    numeroProtocolloCollegato:
      dato.numero_protocollo_collegato ??
      dato.NumeroProtocolloCollegato ??
      dato.numeroProtocolloCollegato ??
      '',
    dataProtocolloCollegato:
      dato.data_protocollo_collegato ??
      dato.DataProtocolloCollegato ??
      dato.dataProtocolloCollegato ??
      '',
    oggettoProtocolloCollegato:
      dato.oggetto_protocollo_collegato ??
      dato.OggettoProtocolloCollegato ??
      dato.oggettoProtocolloCollegato ??
      ''
  }
}

function normalizzaProtocolloIstanza(dato = {}) {
  return {
    idProtocollo:
      dato.id_protocollo ??
      dato.IDProtocollo ??
      dato.idProtocollo ??
      dato.id,
    numeroProtocollo:
      dato.numero_protocollo ??
      dato.NumeroProtocollo ??
      dato.numeroProtocollo ??
      '',
    dataProtocollo:
      dato.data_protocollo ??
      dato.DataProtocollo ??
      dato.dataProtocollo ??
      '',
    oggetto:
      dato.oggetto ??
      dato.Oggetto ??
      '',
    modalita:
      dato.modalita ??
      dato.Modalita ??
      '',
    comandoMittente:
      dato.comando_mittente ??
      dato.ComandoMittente ??
      dato.comandoMittente ??
      ''
  }
}

function normalizzaDocumentoPrincipale(dato = {}) {
  if (!dato) return null

  return {
    idDocumentoSottofase:
      dato.id_documento_sottofase ??
      dato.IDDocumentoSottofase ??
      dato.idDocumentoSottofase ??
      dato.id,
    idSottofase:
      dato.id_sottofase ??
      dato.IDSottofase ??
      dato.idSottofase ??
      null,
    ruoloDocumento:
      dato.ruolo_documento ??
      dato.RuoloDocumento ??
      dato.ruoloDocumento ??
      '',
    tipoOrigine:
      dato.tipo_origine ??
      dato.TipoOrigine ??
      dato.tipoOrigine ??
      '',
    titoloDocumento:
      dato.titolo_documento ??
      dato.TitoloDocumento ??
      dato.titoloDocumento ??
      '',
    statoDocumento:
      dato.stato_documento ??
      dato.StatoDocumento ??
      dato.statoDocumento ??
      '',
    tipoDocumento:
      dato.tipo_documento ??
      dato.TipoDocumento ??
      dato.tipoDocumento ??
      '',
    descrizioneDocumento:
      dato.descrizione_documento ??
      dato.DescrizioneDocumento ??
      dato.descrizioneDocumento ??
      '',
    versioneDocumento:
      dato.versione_documento ??
      dato.VersioneDocumento ??
      dato.versioneDocumento ??
      '',
    dataCreazione:
      dato.data_creazione ??
      dato.DataCreazione ??
      dato.dataCreazione ??
      '',
    dataModifica:
      dato.data_modifica ??
      dato.DataModifica ??
      dato.dataModifica ??
      '',
    percorsoDocumento:
      dato.percorso_documento ??
      dato.PercorsoDocumento ??
      dato.percorsoDocumento ??
      ''
  }
}

function labelStepOrizzontale(codice) {
  const labels = {
    ISTANZA: 'Istanza',
    REDIGI: 'Redigi',
    REVISIONA: 'Revisiona',
    FIRMA: 'Firma',
    PROTOCOLLA: 'Protocolla',
    ALLEGATI: 'Allegati',
    FINE: 'Fine',
    TELEFONA: 'Telefona',
    MAIL: 'Mail',
    APPUNTAMENTO: 'Appuntamento'
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

  if (
    [
      'ISTANZA',
      'REDIGI',
      'REVISIONA',
      'FIRMA',
      'PROTOCOLLA',
      'ALLEGATI',
      'FINE',
      'TELEFONA',
      'MAIL',
      'APPUNTAMENTO'
    ].includes(titoloUpper)
  ) {
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
    const step = await listStepOrizzontaliFase(idProcedimento.value, fase.id)
    aggiornaStepOrizzontali(step)
  } catch {
    erroreStepOrizzontali.value =
      'Impossibile caricare gli step orizzontali della fase.'
    aggiornaStepOrizzontali([])
  } finally {
    loadingStepOrizzontali.value = false
  }
}

function aggiornaStepOrizzontali(step) {
  stepOrizzontali.value = normalizzaListaStepOrizzontali(step)
  sincronizzaStepOperativoSelezionato()
}

function normalizzaListaStepOrizzontali(step) {
  const normalizzati = Array.isArray(step)
    ? step.map(normalizzaStepOrizzontale).sort(confrontaOrdine)
    : []

  if (normalizzati.length) return normalizzati

  return []
}

async function configuraWorkflowRapidoIstanzaFine() {
  if (!faseSelezionata.value) return

  operazioneStepInCorso.value = true
  erroreStepOrizzontali.value = ''

  try {
    const step = await configuraStepOrizzontaliIstanzaFine(
      idProcedimento.value,
      faseSelezionata.value.id
    )
    aggiornaStepOrizzontali(step)
    messaggioFase.value = 'Workflow rapido Istanza -> Fine applicato.'
    snackbarFase.value = true
  } catch (error) {
    erroreStepOrizzontali.value = messaggioErroreStep(error)
  } finally {
    operazioneStepInCorso.value = false
  }
}

async function configuraWorkflowPredefinito() {
  if (!faseSelezionata.value) return

  operazioneStepInCorso.value = true
  erroreStepOrizzontali.value = ''

  try {
    const step = await configuraStepOrizzontaliPredefinito(
      idProcedimento.value,
      faseSelezionata.value.id
    )
    aggiornaStepOrizzontali(step)
    messaggioFase.value = 'Workflow predefinito applicato.'
    snackbarFase.value = true
  } catch (error) {
    erroreStepOrizzontali.value = messaggioErroreStep(error)
  } finally {
    operazioneStepInCorso.value = false
  }
}

function isStepIstanza(step) {
  return String(step?.codiceStep || '').toUpperCase() === 'ISTANZA'
}

function isStepRedigi(step) {
  return String(step?.codiceStep || '').toUpperCase() === 'REDIGI'
}

function isIstanzaProtocolloCompletata(step) {
  const stato = String(step?.statoStep || '').toUpperCase()
  return isStepIstanza(step) &&
    stato.includes('COMPLET') &&
    Boolean(step?.idProtocolloCollegato)
}

async function gestisciClickStepOrizzontale(step) {
  if (isStepRedigi(step)) {
    stepOperativoSelezionatoId.value = step.id
    noteRedigiForm.value = step.noteOperative || ''
    await caricaDocumentoPrincipaleRedigi()
    return
  }

  if (!isStepIstanza(step)) {
    stepOperativoSelezionatoId.value = null
    noteRedigiForm.value = ''
    documentoPrincipaleRedigi.value = null
    resetFormMetadatiDocumento()
    erroreDocumentoPrincipaleRedigi.value = ''
    return
  }

  stepIstanzaCorrente.value = step
  erroreProtocolloIstanza.value = ''
  ricercaProtocolloIstanza.value = ''
  dialogProtocolloIstanza.value = true
  await caricaProtocolliIstanza()
}

function sincronizzaStepOperativoSelezionato() {
  if (!stepOperativoSelezionatoId.value) return

  const stepAggiornato = stepOrizzontali.value.find((step) => {
    return Number(step.id) === Number(stepOperativoSelezionatoId.value)
  })

  if (!stepAggiornato) {
    stepOperativoSelezionatoId.value = null
    noteRedigiForm.value = ''
    return
  }

  if (isStepRedigi(stepAggiornato)) {
    noteRedigiForm.value = stepAggiornato.noteOperative || ''
  }
}

async function caricaDocumentoPrincipaleRedigi() {
  const idSottofase = idSottofaseDocumentaleRedigi.value
  if (!idSottofase) {
    documentoPrincipaleRedigi.value = null
    erroreDocumentoPrincipaleRedigi.value =
      'Contesto documentale della fase non disponibile.'
    return
  }

  loadingDocumentoPrincipaleRedigi.value = true
  erroreDocumentoPrincipaleRedigi.value = ''

  try {
    const documento = await getDocumentoPrincipaleSottofase(idSottofase)
    documentoPrincipaleRedigi.value = normalizzaDocumentoPrincipale(documento)
    popolaFormMetadatiDocumento(documentoPrincipaleRedigi.value)
  } catch (error) {
    documentoPrincipaleRedigi.value = null
    resetFormMetadatiDocumento()
    erroreDocumentoPrincipaleRedigi.value = messaggioErroreDocumentoPrincipale(error)
  } finally {
    loadingDocumentoPrincipaleRedigi.value = false
  }
}

async function creaDocumentoPrincipaleRedigi() {
  const idSottofase = idSottofaseDocumentaleRedigi.value
  if (!idSottofase) return

  creazioneDocumentoPrincipaleInCorso.value = true
  erroreDocumentoPrincipaleRedigi.value = ''

  try {
    const documento = await createDocumentoPrincipaleSottofase(idSottofase)
    documentoPrincipaleRedigi.value = normalizzaDocumentoPrincipale(documento)
    popolaFormMetadatiDocumento(documentoPrincipaleRedigi.value)
    messaggioFase.value = 'Documento principale creato.'
    snackbarFase.value = true
  } catch (error) {
    erroreDocumentoPrincipaleRedigi.value = messaggioErroreDocumentoPrincipale(error)
  } finally {
    creazioneDocumentoPrincipaleInCorso.value = false
  }
}

async function salvaMetadatiDocumentoPrincipaleRedigi() {
  const idSottofase = idSottofaseDocumentaleRedigi.value
  if (!idSottofase || !documentoPrincipaleRedigi.value) return

  salvataggioMetadatiDocumentoInCorso.value = true
  erroreDocumentoPrincipaleRedigi.value = ''

  try {
    await updateDocumentoPrincipaleMetadatiSottofase(idSottofase, {
      titoloDocumento: documentoMetadatiForm.titoloDocumento,
      descrizioneDocumento: documentoMetadatiForm.descrizioneDocumento,
      statoDocumento: documentoMetadatiForm.statoDocumento,
      tipoDocumento: documentoMetadatiForm.tipoDocumento
    })
    await caricaDocumentoPrincipaleRedigi()
    messaggioFase.value = 'Metadati documento salvati.'
    snackbarFase.value = true
  } catch (error) {
    erroreDocumentoPrincipaleRedigi.value = messaggioErroreDocumentoPrincipale(error)
  } finally {
    salvataggioMetadatiDocumentoInCorso.value = false
  }
}

async function apriDocumentoPrincipaleRedigi() {
  const idDocumento = documentoPrincipaleRedigi.value?.idDocumentoSottofase
  if (!idDocumento) {
    erroreDocumentoPrincipaleRedigi.value =
      'Documento principale non apribile: identificativo mancante.'
    return
  }

  const openedWindow = window.open('', '_blank')
  if (!openedWindow) {
    erroreDocumentoPrincipaleRedigi.value =
      'Il browser ha bloccato l apertura del documento in una nuova scheda.'
    return
  }

  openedWindow.opener = null
  aperturaDocumentoPrincipaleInCorso.value = true
  erroreDocumentoPrincipaleRedigi.value = ''

  try {
    const blob = await apriDocumentoSottofase(idDocumento)
    const blobUrl = URL.createObjectURL(blob)
    openedWindow.location.href = blobUrl

    setTimeout(() => {
      URL.revokeObjectURL(blobUrl)
    }, 60000)
  } catch (error) {
    if (error.status === 404) {
      erroreDocumentoPrincipaleRedigi.value =
        'Documento principale creato, ma file fisico non ancora disponibile.'
    } else {
      erroreDocumentoPrincipaleRedigi.value =
        'Impossibile aprire il documento principale.'
    }

    try {
      openedWindow.close()
    } catch {
      // Scheda aperta solo in risposta al click utente.
    }
  } finally {
    aperturaDocumentoPrincipaleInCorso.value = false
  }
}

function popolaFormMetadatiDocumento(documento) {
  documentoMetadatiForm.titoloDocumento = documento?.titoloDocumento || ''
  documentoMetadatiForm.descrizioneDocumento =
    documento?.descrizioneDocumento || ''
  documentoMetadatiForm.statoDocumento =
    documento?.statoDocumento || 'BOZZA'
  documentoMetadatiForm.tipoDocumento =
    documento?.tipoDocumento || 'ALTRO'
}

function resetFormMetadatiDocumento() {
  documentoMetadatiForm.titoloDocumento = ''
  documentoMetadatiForm.descrizioneDocumento = ''
  documentoMetadatiForm.statoDocumento = 'BOZZA'
  documentoMetadatiForm.tipoDocumento = 'ALTRO'
}

async function avviaRedigiSelezionato() {
  if (!faseSelezionata.value || !stepRedigiSelezionato.value?.id) return

  operazioneStepInCorso.value = true
  erroreStepOrizzontali.value = ''

  try {
    const stepAggiornati = await avviaStepRedigi(
      idProcedimento.value,
      faseSelezionata.value.id,
      stepRedigiSelezionato.value.id
    )
    aggiornaStepOrizzontali(stepAggiornati)
    messaggioFase.value = 'Lavorazione Redigi avviata.'
    snackbarFase.value = true
  } catch (error) {
    erroreStepOrizzontali.value = messaggioErroreStep(error)
  } finally {
    operazioneStepInCorso.value = false
  }
}

async function completaRedigiSelezionato() {
  if (!faseSelezionata.value || !stepRedigiSelezionato.value?.id) return

  operazioneStepInCorso.value = true
  erroreStepOrizzontali.value = ''

  try {
    const stepAggiornati = await completaStepRedigi(
      idProcedimento.value,
      faseSelezionata.value.id,
      stepRedigiSelezionato.value.id
    )
    aggiornaStepOrizzontali(stepAggiornati)
    messaggioFase.value = 'Lavorazione Redigi completata.'
    snackbarFase.value = true
  } catch (error) {
    erroreStepOrizzontali.value = messaggioErroreStep(error)
  } finally {
    operazioneStepInCorso.value = false
  }
}

async function salvaNoteRedigiSelezionato() {
  if (!faseSelezionata.value || !stepRedigiSelezionato.value?.id) return

  salvataggioNoteRedigiInCorso.value = true
  erroreStepOrizzontali.value = ''

  try {
    const stepAggiornati = await salvaNoteStepRedigi(
      idProcedimento.value,
      faseSelezionata.value.id,
      stepRedigiSelezionato.value.id,
      { noteOperative: noteRedigiForm.value }
    )
    aggiornaStepOrizzontali(stepAggiornati)
    messaggioFase.value = 'Note operative salvate.'
    snackbarFase.value = true
  } catch (error) {
    erroreStepOrizzontali.value = messaggioErroreStep(error)
  } finally {
    salvataggioNoteRedigiInCorso.value = false
  }
}

async function caricaProtocolliIstanza() {
  loadingProtocolliIstanza.value = true
  erroreProtocolloIstanza.value = ''

  try {
    const protocolli = await listProtocolli()
    protocolliIstanza.value = Array.isArray(protocolli)
      ? protocolli.map(normalizzaProtocolloIstanza)
      : []
  } catch {
    protocolliIstanza.value = []
    erroreProtocolloIstanza.value = 'Impossibile caricare i protocolli disponibili.'
  } finally {
    loadingProtocolliIstanza.value = false
  }
}

async function selezionaProtocolloIstanza(protocollo) {
  if (!faseSelezionata.value || !stepIstanzaCorrente.value?.id || !protocollo?.idProtocollo) {
    return
  }

  const protocolloGiaCollegato = stepIstanzaCorrente.value.idProtocolloCollegato
  const protocolloDiverso =
    protocolloGiaCollegato &&
    Number(protocolloGiaCollegato) !== Number(protocollo.idProtocollo)

  if (protocolloDiverso) {
    const conferma = window.confirm(
      'Lo step Istanza contiene gia un protocollo collegato. Vuoi sostituirlo?'
    )
    if (!conferma) return
  }

  collegamentoProtocolloInCorso.value = true
  erroreProtocolloIstanza.value = ''

  try {
    const stepAggiornati = await collegaProtocolloStepIstanza(
      idProcedimento.value,
      faseSelezionata.value.id,
      stepIstanzaCorrente.value.id,
      { idProtocollo: protocollo.idProtocollo }
    )
    aggiornaStepOrizzontali(stepAggiornati)
    stepIstanzaCorrente.value = stepOrizzontali.value.find(
      (step) => Number(step.id) === Number(stepIstanzaCorrente.value?.id)
    )
    dialogProtocolloIstanza.value = false
    messaggioFase.value = 'Protocollo collegato allo step Istanza.'
    snackbarFase.value = true
  } catch (error) {
    erroreProtocolloIstanza.value = messaggioErroreStep(error)
  } finally {
    collegamentoProtocolloInCorso.value = false
  }
}

async function apriPdfProtocolloIstanza(step) {
  const idProtocollo = step?.idProtocolloCollegato
  if (!idProtocollo) {
    erroreStepOrizzontali.value = 'Nessun protocollo collegato allo step Istanza.'
    return
  }

  erroreStepOrizzontali.value = ''

  try {
    await apriPdfProtocolloEsterno(idProtocollo)
  } catch (error) {
    erroreStepOrizzontali.value = messaggioErrorePdfProtocollo(error)
  }
}

function chiudiDialogProtocolloIstanza() {
  if (collegamentoProtocolloInCorso.value) return

  dialogProtocolloIstanza.value = false
  erroreProtocolloIstanza.value = ''
}

async function inserisciStepDopo(step, opzione) {
  if (!faseSelezionata.value || !step?.id) return

  operazioneStepInCorso.value = true
  erroreStepOrizzontali.value = ''

  try {
    const stepAggiornati = await inserisciStepOrizzontaleDopo(
      idProcedimento.value,
      faseSelezionata.value.id,
      step.id,
      {
        titoloStep: opzione?.titoloStep || 'Nuovo step',
        codiceStep: opzione?.codiceStep || 'NUOVO_STEP'
      }
    )
    aggiornaStepOrizzontali(stepAggiornati)
    messaggioFase.value = `${opzione?.titoloStep || 'Step'} inserito.`
    snackbarFase.value = true
  } catch (error) {
    erroreStepOrizzontali.value = messaggioErroreStep(error)
  } finally {
    operazioneStepInCorso.value = false
  }
}

function apriConfermaEliminaStep(step) {
  stepDaEliminare.value = step
  dialogEliminaStep.value = true
}

async function confermaEliminaStep() {
  if (!faseSelezionata.value || !stepDaEliminare.value?.id) return

  operazioneStepInCorso.value = true
  erroreStepOrizzontali.value = ''

  try {
    const stepAggiornati = await eliminaStepOrizzontale(
      idProcedimento.value,
      faseSelezionata.value.id,
      stepDaEliminare.value.id
    )
    dialogEliminaStep.value = false
    stepDaEliminare.value = null
    aggiornaStepOrizzontali(stepAggiornati)
    messaggioFase.value = 'Step eliminato.'
    snackbarFase.value = true
  } catch (error) {
    erroreStepOrizzontali.value = messaggioErroreStep(error)
  } finally {
    operazioneStepInCorso.value = false
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

function messaggioErroreStep(error) {
  const dettaglio = error?.payload?.detail
  if (typeof dettaglio === 'string') return dettaglio

  if (error?.status === 404) return 'Fase o step non trovato.'
  return 'Impossibile aggiornare lo stepper.'
}

function messaggioErrorePdfProtocollo(error) {
  const dettaglio = error?.payload?.detail
  if (typeof dettaglio === 'string') return dettaglio

  if (error?.status === 404) {
    return 'Il PDF non e disponibile o non e stato ancora acquisito.'
  }

  return 'Errore apertura PDF protocollo.'
}

function messaggioErroreDocumentoPrincipale(error) {
  const dettaglio = error?.payload?.detail
  if (typeof dettaglio === 'string') return dettaglio

  if (error?.status === 409) {
    return 'Esiste gia un documento principale attivo.'
  }

  if (error?.status === 404) {
    return 'Documento principale non disponibile.'
  }

  return 'Impossibile aggiornare il documento principale.'
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

function classeStepOrizzontale(step) {
  const stato = typeof step === 'string' ? step : step?.statoStep
  const normalizzato = String(stato || '').toUpperCase()
  if (normalizzato === 'NON_AVVIATO') return 'step-orizzontale-non-avviato'
  if (normalizzato.includes('COMPLET')) return 'step-orizzontale-completato'
  if (normalizzato.includes('ANNULL')) return 'step-orizzontale-annullato'
  if (normalizzato.includes('CORSO') || normalizzato === 'ACTIVE') {
    return 'step-orizzontale-in-corso'
  }
  return 'step-orizzontale-non-avviato'
}

function coloreStatoStep(stato) {
  const normalizzato = String(stato || '').toUpperCase()
  if (normalizzato === 'NON_AVVIATO') return 'grey'
  if (normalizzato.includes('COMPLET')) return 'success'
  if (normalizzato.includes('ANNULL')) return 'error'
  if (normalizzato.includes('CORSO') || normalizzato === 'ACTIVE') return 'primary'
  return 'grey'
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

.workflow-quick-actions {
  display: flex;
  flex: 0 0 auto;
  gap: 10px;
  justify-content: flex-start;
  margin-bottom: 26px;
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
  cursor: pointer;
  min-width: 0;
  padding-bottom: 46px;
  position: relative;
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

.step-orizzontale-item:hover .step-orizzontale-node {
  box-shadow:
    0 0 0 1px rgba(var(--v-theme-on-surface), 0.16),
    0 0 0 5px rgba(var(--v-theme-primary), 0.16);
}

.step-node-actions {
  align-items: center;
  display: flex;
  gap: 4px;
  left: 50%;
  opacity: 0;
  pointer-events: none;
  position: absolute;
  top: 58px;
  transform: translateX(-50%);
  transition: opacity 0.12s ease;
  z-index: 2;
}

.step-orizzontale-item:hover .step-node-actions,
.step-node-actions:focus-within {
  opacity: 1;
  pointer-events: auto;
}

.step-orizzontale-non-avviato {
  background: #9e9e9e;
}

.step-orizzontale-completato {
  background: #2e7d32;
}

.step-orizzontale-in-corso {
  background: #1976d2;
}

.step-orizzontale-annullato {
  background: #c62828;
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
  margin-top: 42px;
  overflow-wrap: anywhere;
}

.step-istanza-linked {
  align-items: center;
  background: transparent;
  border: 0;
  cursor: pointer;
  display: flex;
  gap: 6px;
  justify-content: center;
  margin: 4px auto 0;
  padding: 0;
  width: fit-content;
}

.step-istanza-linked:hover {
  filter: drop-shadow(0 0 4px rgba(var(--v-theme-primary), 0.35));
}

.protocollo-oggetto-cell {
  display: inline-block;
  max-width: 360px;
  overflow: hidden;
  text-overflow: ellipsis;
  vertical-align: bottom;
  white-space: nowrap;
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

.redigi-work-panel {
  align-self: center;
  flex: 0 0 auto;
  margin-top: 30px;
  max-width: 860px;
  width: min(100%, 860px);
}

.redigi-panel-title {
  align-items: center;
  display: flex;
  gap: 16px;
  justify-content: space-between;
}

.redigi-panel-heading {
  font-size: 1.32rem;
  font-weight: 900;
  letter-spacing: 0;
}

.redigi-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.redigi-document-card {
  background: rgba(var(--v-theme-primary), 0.045);
}

.redigi-document-header {
  align-items: center;
  display: flex;
  gap: 12px;
}

.redigi-document-title {
  font-size: 1.05rem;
  font-weight: 900;
  letter-spacing: 0;
}

.redigi-document-empty,
.redigi-document-detail {
  margin-top: 16px;
}

.redigi-document-form {
  display: grid;
  gap: 12px;
  grid-template-columns: minmax(0, 1fr) minmax(160px, 220px) minmax(160px, 220px);
}

.redigi-document-description {
  grid-column: 1 / -1;
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

  .redigi-document-form {
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

  .workflow-quick-actions {
    justify-content: stretch;
  }

  .workflow-quick-actions .v-btn {
    width: 100%;
  }

  .step-orizzontale-line {
    display: none;
  }

  .work-content-placeholder {
    min-height: 280px;
  }
}
</style>
