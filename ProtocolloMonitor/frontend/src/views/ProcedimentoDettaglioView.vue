<template>
  <v-container
    fluid
    class="procedimento-page"
    :class="{ 'procedimento-page-lavorazione': modalitaVista === 'lavorazione-fase' }"
  >
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
              <div class="lavorazione-sticky-head">
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
                  v-if="workflowVisualPoints.length"
                  class="stepper-orizzontale"
                >
                  <div
                    v-for="(step, index) in workflowVisualPoints"
                    :key="step.id || step.codiceStep"
                    class="step-orizzontale-item"
                    :class="{ 'step-orizzontale-item--locked': !step.attivabile }"
                  >
                    <div class="step-orizzontale-node-wrap">
                      <div
                        class="step-orizzontale-node"
                        :class="classeStepOrizzontale(step)"
                        :aria-disabled="!step.attivabile"
                        @click.stop="gestisciClickStepOrizzontale(step)"
                      >
                        <img
                          :src="workflowAvatarForStep(step)"
                          alt=""
                          class="workflow-avatar-img step-node-avatar-img"
                          :class="{ 'workflow-avatar-img--muted': step.avatarState === 'locked' }"
                        >
                        <span class="step-node-number">
                          {{ index + 1 }}
                        </span>
                      </div>

                      <div
                        v-if="index < workflowVisualPoints.length - 1 && (index + 1) % 6 !== 0"
                        class="step-orizzontale-line"
                      />
                    </div>

                    <div
                      class="step-node-actions"
                    >
                      <v-btn
                        class="step-node-action step-delete-action"
                        icon="mdi-delete-outline"
                        size="small"
                        variant="text"
                        color="error"
                        :disabled="operazioneStepInCorso"
                        @click.stop="apriConfermaEliminaStep(step)"
                      />

                      <v-menu location="bottom">
                        <template #activator="{ props }">
                          <v-btn
                            v-bind="props"
                            class="step-node-action step-add-action"
                            icon="mdi-plus-circle-outline"
                            size="small"
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
                                <img
                                  :src="workflowAvatarForStep(opzione.codiceStep)"
                                  alt=""
                                  class="workflow-avatar-img workflow-menu-avatar-img"
                                >
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

                    <div
                      v-if="step.outputs.length"
                      class="step-node-outputs"
                    >
                      <v-tooltip
                        v-for="output in step.outputs"
                        :key="output.key"
                        location="bottom"
                      >
                        <template #activator="{ props }">
                          <button
                            v-bind="props"
                            type="button"
                            class="step-output-action"
                            :title="output.label"
                            :aria-label="output.label"
                            @click.stop="gestisciClickOutputStep(step, output)"
                          >
                            <v-icon
                              size="26"
                              :color="output.color"
                            >
                              {{ output.icon }}
                            </v-icon>
                          </button>
                        </template>
                        <span>{{ output.label }}</span>
                      </v-tooltip>
                    </div>

                    <v-btn
                      class="step-details-action"
                      size="x-small"
                      variant="text"
                      prepend-icon="mdi-information-outline"
                      @click.stop="apriDettagliStep(step)"
                    >
                      Dettagli
                    </v-btn>
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
              </div>

              <div class="lavorazione-content-card">
                <div class="step-operativo-scroll">
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
                        class="workflow-documentale-card mt-5"
                        rounded="lg"
                        variant="tonal"
                      >
                        <v-card-title class="workflow-documentale-title">
                          <div class="redigi-document-header">
                            <v-avatar
                              color="primary"
                              variant="tonal"
                              size="42"
                            >
                              <img
                                :src="workflowAvatarForStep(stepRedigiSelezionato)"
                                alt=""
                                class="workflow-panel-avatar-img"
                              >
                            </v-avatar>

                            <div>
                              <div class="redigi-document-title">
                                Workflow documentale
                              </div>
                              <div class="text-caption text-medium-emphasis">
                                Redigi
                              </div>
                            </div>
                          </div>

                          <v-chip
                            :color="coloreStatoDocumentoWorkflow(statoWorkflowDocumento)"
                            variant="tonal"
                          >
                            {{ valoreDettaglio(statoWorkflowDocumento) }}
                          </v-chip>
                        </v-card-title>

                        <v-card-text>
                          <v-progress-linear
                            v-if="loadingWorkflowDocumentale"
                            color="primary"
                            indeterminate
                            rounded
                          />

                          <v-alert
                            v-if="erroreWorkflowDocumentale"
                            type="warning"
                            variant="tonal"
                            density="compact"
                            class="mb-4"
                          >
                            {{ erroreWorkflowDocumentale }}
                          </v-alert>

                          <div v-if="canCreaBozzaWorkflow">
                            <v-text-field
                              v-model="workflowBozzaForm.titoloDocumento"
                              label="Titolo documento"
                              variant="outlined"
                              density="compact"
                            />

                            <v-textarea
                              v-model="workflowBozzaForm.descrizioneDocumento"
                              label="Descrizione"
                              variant="outlined"
                              rows="3"
                              auto-grow
                            />

                            <v-btn
                              color="primary"
                              variant="flat"
                              prepend-icon="mdi-file-plus-outline"
                              :loading="operazioneWorkflowDocumentaleInCorso"
                              @click="creaBozzaWorkflowDocumentale"
                            >
                              Crea bozza documento
                            </v-btn>
                          </div>

                          <div v-else>
                            <v-expansion-panels
                              class="technical-details-panel mb-4"
                              variant="accordion"
                            >
                              <v-expansion-panel>
                                <v-expansion-panel-title>
                                  Dettagli documento e workflow
                                </v-expansion-panel-title>

                                <v-expansion-panel-text>
                                  <div class="detail-grid">
                                    <div class="detail-field">
                                      <div class="detail-label">Documento</div>
                                      <div class="detail-value">
                                        {{ valoreDettaglio(documentoWorkflowPrincipale?.titoloDocumento) }}
                                      </div>
                                    </div>
                                    <div class="detail-field">
                                      <div class="detail-label">Messaggio</div>
                                      <div class="detail-value">
                                        {{ workflowDocumentaleReadyMessage }}
                                      </div>
                                    </div>
                                  </div>
                                </v-expansion-panel-text>
                              </v-expansion-panel>
                            </v-expansion-panels>

                            <v-textarea
                              v-if="canCompletaRedazioneWorkflow"
                              v-model="workflowAzioneNote"
                              label="Note redazione"
                              variant="outlined"
                              rows="3"
                              auto-grow
                              class="mt-4"
                            />

                            <v-btn
                              v-if="canCompletaRedazioneWorkflow"
                              color="success"
                              variant="flat"
                              prepend-icon="mdi-check-circle-outline"
                              :loading="operazioneWorkflowDocumentaleInCorso"
                              class="mt-2"
                              @click="eseguiAzioneDocumentale('completa_redazione')"
                            >
                              Completa redazione
                            </v-btn>

                            <v-alert
                              v-else
                              type="info"
                              variant="tonal"
                              density="compact"
                              class="mt-4"
                            >
                              Documento gia redatto o in fase successiva.
                            </v-alert>
                          </div>
                        </v-card-text>
                      </v-card>

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
                          <div class="document-operational-summary">
                            <div>
                              <div class="detail-label">Documento</div>
                              <div class="redigi-document-title">
                                {{ valoreDettaglio(documentoPrincipaleRedigi.titoloDocumento) }}
                              </div>
                            </div>

                            <v-chip
                              :color="coloreStatoDocumentoWorkflow(documentoPrincipaleRedigi.statoDocumento)"
                              variant="tonal"
                              size="small"
                            >
                              {{ valoreDettaglio(documentoPrincipaleRedigi.statoDocumento) }}
                            </v-chip>
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

                          <v-expansion-panels
                            class="technical-details-panel mt-4"
                            variant="accordion"
                          >
                            <v-expansion-panel>
                              <v-expansion-panel-title>
                                Metadati e informazioni tecniche
                              </v-expansion-panel-title>

                              <v-expansion-panel-text>
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
                                  variant="flat"
                                  prepend-icon="mdi-content-save-outline"
                                  :loading="salvataggioMetadatiDocumentoInCorso"
                                  class="mt-4"
                                  @click="salvaMetadatiDocumentoPrincipaleRedigi"
                                >
                                  Salva metadati documento
                                </v-btn>
                              </v-expansion-panel-text>
                            </v-expansion-panel>
                          </v-expansion-panels>
                        </div>
                      </v-card-text>
                    </v-card>

                    <v-expansion-panels
                      class="technical-details-panel mt-5"
                      variant="accordion"
                    >
                      <v-expansion-panel>
                        <v-expansion-panel-title>
                          Note operative interne
                        </v-expansion-panel-title>

                        <v-expansion-panel-text>
                          <v-textarea
                            v-model="noteRedigiForm"
                            label="Note operative"
                            variant="outlined"
                            rows="5"
                            auto-grow
                          />

                          <div class="technical-details-actions">
                            <v-btn
                              color="primary"
                              variant="tonal"
                              prepend-icon="mdi-content-save-outline"
                              :loading="salvataggioNoteRedigiInCorso"
                              @click="salvaNoteRedigiSelezionato"
                            >
                              Salva note
                            </v-btn>
                          </div>
                        </v-expansion-panel-text>
                      </v-expansion-panel>
                    </v-expansion-panels>
                  </v-card-text>
                </v-card>

                <v-card
                  v-else-if="stepDocumentaleSelezionato"
                  class="redigi-work-panel"
                  rounded="lg"
                  variant="outlined"
                >
                  <v-card-title class="redigi-panel-title">
                    <div class="redigi-document-header">
                      <v-avatar
                        color="primary"
                        variant="tonal"
                        size="46"
                      >
                        <img
                          :src="workflowAvatarForStep(stepDocumentaleSelezionato)"
                          alt=""
                          class="workflow-panel-avatar-img"
                        >
                      </v-avatar>

                      <div>
                        <div class="text-caption text-medium-emphasis">
                          Workflow documentale
                        </div>
                        <div class="redigi-panel-heading">
                          {{ stepDocumentaleSelezionato.titolo }}
                        </div>
                      </div>
                    </div>

                    <v-chip
                      :color="coloreStatoDocumentoWorkflow(statoWorkflowDocumento)"
                      variant="tonal"
                    >
                      Stato documento: {{ valoreDettaglio(statoWorkflowDocumento) }}
                    </v-chip>
                  </v-card-title>

                  <v-divider />

                  <v-card-text>
                    <v-progress-linear
                      v-if="loadingWorkflowDocumentale"
                      color="primary"
                      indeterminate
                      rounded
                      class="mb-4"
                    />

                    <v-alert
                      v-if="erroreWorkflowDocumentale"
                      type="warning"
                      variant="tonal"
                      density="compact"
                      class="mb-4"
                    >
                      {{ erroreWorkflowDocumentale }}
                    </v-alert>

                    <v-alert
                      v-if="!documentoWorkflowPrincipale"
                      type="info"
                      variant="tonal"
                      density="compact"
                      class="mb-4"
                    >
                      Documento principale non ancora presente. Crearlo dallo step Redigi.
                    </v-alert>

                    <div
                      v-else
                      class="workflow-documentale-body"
                    >
                      <div class="document-operational-summary">
                        <div>
                          <div class="detail-label">Documento</div>
                          <div class="redigi-document-title">
                            {{ valoreDettaglio(documentoWorkflowPrincipale.titoloDocumento) }}
                          </div>
                        </div>

                        <v-chip
                          :color="coloreStatoDocumentoWorkflow(statoWorkflowDocumento)"
                          variant="tonal"
                          size="small"
                        >
                          {{ valoreDettaglio(statoWorkflowDocumento) }}
                        </v-chip>
                      </div>

                      <v-expansion-panels
                        class="technical-details-panel"
                        variant="accordion"
                      >
                        <v-expansion-panel>
                          <v-expansion-panel-title>
                            Dettagli documento e collegamenti
                          </v-expansion-panel-title>

                          <v-expansion-panel-text>
                            <div class="detail-grid">
                              <div class="detail-field">
                                <div class="detail-label">Titolo documento</div>
                                <div class="detail-value">
                                  {{ valoreDettaglio(documentoWorkflowPrincipale.titoloDocumento) }}
                                </div>
                              </div>

                              <div class="detail-field">
                                <div class="detail-label">Stato</div>
                                <div class="detail-value">
                                  {{ valoreDettaglio(statoWorkflowDocumento) }}
                                </div>
                              </div>

                              <div class="detail-field">
                                <div class="detail-label">Ultima modifica</div>
                                <div class="detail-value">
                                  {{ valoreDettaglio(documentoWorkflowPrincipale.dataModifica) }}
                                </div>
                              </div>

                              <div class="detail-field">
                                <div class="detail-label">Protocollo collegato</div>
                                <div class="detail-value">
                                  {{ valoreDettaglio(documentoWorkflowPrincipale.idProtocolloCollegato) }}
                                </div>
                              </div>
                            </div>

                            <div class="detail-description-box">
                              {{ valoreDettaglio(documentoWorkflowPrincipale.descrizioneDocumento) }}
                            </div>

                            <v-alert
                              type="info"
                              variant="tonal"
                              density="compact"
                              class="mb-0"
                            >
                              {{ workflowDocumentaleReadyMessage }}
                            </v-alert>
                          </v-expansion-panel-text>
                        </v-expansion-panel>
                      </v-expansion-panels>

                      <v-textarea
                        v-if="canApprovaRevisioneWorkflow || canFirmaWorkflow || canProtocollaWorkflow"
                        v-model="workflowAzioneNote"
                        label="Note / motivo"
                        variant="outlined"
                        rows="3"
                        auto-grow
                      />

                      <v-text-field
                        v-if="canProtocollaWorkflow"
                        v-model="workflowProtocolloId"
                        label="ID protocollo"
                        type="number"
                        variant="outlined"
                        density="compact"
                      />

                      <div class="workflow-documentale-actions">
                        <v-btn
                          v-if="canApprovaRevisioneWorkflow"
                          color="success"
                          variant="flat"
                          prepend-icon="mdi-check-circle-outline"
                          :loading="operazioneWorkflowDocumentaleInCorso"
                          @click="eseguiAzioneDocumentale('approva_revisione')"
                        >
                          Approva revisione
                        </v-btn>

                        <v-btn
                          v-if="canApprovaRevisioneWorkflow"
                          color="error"
                          variant="tonal"
                          prepend-icon="mdi-close-circle-outline"
                          :loading="operazioneWorkflowDocumentaleInCorso"
                          @click="eseguiAzioneDocumentale('respingi_revisione')"
                        >
                          Respingi revisione
                        </v-btn>

                        <v-btn
                          v-if="canFirmaWorkflow"
                          color="success"
                          variant="flat"
                          prepend-icon="mdi-draw"
                          :loading="operazioneWorkflowDocumentaleInCorso"
                          @click="eseguiAzioneDocumentale('conferma_firma')"
                        >
                          Conferma firma
                        </v-btn>

                        <v-btn
                          v-if="canFirmaWorkflow"
                          color="error"
                          variant="tonal"
                          prepend-icon="mdi-close-circle-outline"
                          :loading="operazioneWorkflowDocumentaleInCorso"
                          @click="eseguiAzioneDocumentale('respingi_firma')"
                        >
                          Respingi firma
                        </v-btn>

                        <v-btn
                          v-if="canProtocollaWorkflow"
                          color="success"
                          variant="flat"
                          prepend-icon="mdi-file-check-outline"
                          :loading="operazioneWorkflowDocumentaleInCorso"
                          @click="eseguiAzioneDocumentale('conferma_protocollazione')"
                        >
                          Conferma protocollazione
                        </v-btn>
                      </div>

                      <v-alert
                        v-if="
                          isStepRevisiona(stepDocumentaleSelezionato) &&
                          !canApprovaRevisioneWorkflow
                        "
                        type="info"
                        variant="tonal"
                        density="compact"
                        class="mt-4"
                      >
                        Il documento non e ancora pronto per la revisione.
                      </v-alert>

                      <v-alert
                        v-if="
                          isStepFirma(stepDocumentaleSelezionato) &&
                          !canFirmaWorkflow
                        "
                        type="info"
                        variant="tonal"
                        density="compact"
                        class="mt-4"
                      >
                        Il documento non e ancora pronto per la firma.
                      </v-alert>

                      <v-alert
                        v-if="
                          isStepProtocolla(stepDocumentaleSelezionato) &&
                          !canProtocollaWorkflow
                        "
                        type="info"
                        variant="tonal"
                        density="compact"
                        class="mt-4"
                      >
                        Il documento non e ancora pronto per la protocollazione.
                      </v-alert>
                    </div>
                  </v-card-text>
                </v-card>

                <v-card
                  v-else-if="stepAllegatiSelezionato"
                  class="allegati-work-panel"
                  rounded="lg"
                  variant="outlined"
                >
                  <v-card-title class="redigi-panel-title">
                    <div>
                      <div class="text-caption text-medium-emphasis">
                        Step operativo
                      </div>
                      <div class="redigi-panel-heading">
                        Allegati della sottofase
                      </div>
                    </div>

                    <v-chip
                      color="primary"
                      variant="tonal"
                    >
                      {{ allegatiSottofase.length }} allegati
                    </v-chip>
                  </v-card-title>

                  <v-divider />

                  <v-card-text>
                    <div class="allegati-actions">
                      <v-btn
                        color="primary"
                        variant="flat"
                        prepend-icon="mdi-file-link-outline"
                        :loading="loadingAllegatiSottofase"
                        @click="apriDialogProtocolloAllegato"
                      >
                        Collega protocollo
                      </v-btn>

                      <v-btn
                        color="primary"
                        variant="tonal"
                        prepend-icon="mdi-file-upload-outline"
                        :loading="uploadAllegatoInCorso"
                        @click="apriSelettoreFileAllegato"
                      >
                        Carica file
                      </v-btn>

                      <input
                        ref="allegatoFileInput"
                        type="file"
                        class="d-none"
                        :accept="allegatiFileAccept"
                        @change="gestisciSelezioneFileAllegato"
                      >
                    </div>

                    <v-alert
                      v-if="erroreAllegatiSottofase"
                      type="warning"
                      variant="tonal"
                      density="compact"
                      class="mt-5"
                    >
                      {{ erroreAllegatiSottofase }}
                    </v-alert>

                    <v-progress-linear
                      v-if="loadingAllegatiSottofase"
                      color="primary"
                      indeterminate
                      rounded
                      class="mt-5"
                    />

                    <v-list
                      v-else-if="allegatiSottofase.length"
                      class="allegati-list mt-5"
                      density="comfortable"
                      lines="two"
                    >
                      <v-list-item
                        v-for="allegato in allegatiSottofase"
                        :key="allegato.idDocumentoSottofase"
                        class="allegato-item"
                      >
                        <template #prepend>
                          <v-avatar
                            color="primary"
                            variant="tonal"
                          >
                            <v-icon>
                              {{ iconaAllegato(allegato) }}
                            </v-icon>
                          </v-avatar>
                        </template>

                        <v-list-item-title class="font-weight-bold">
                          {{ valoreDettaglio(allegato.titoloDocumento) }}
                        </v-list-item-title>

                        <v-list-item-subtitle>
                          {{ valoreDettaglio(allegato.nomeFile) }}
                        </v-list-item-subtitle>

                        <template #append>
                          <div class="allegato-item-actions">
                            <v-btn
                              color="primary"
                              variant="text"
                              prepend-icon="mdi-open-in-new"
                              :loading="aperturaAllegatoInCorsoId === allegato.idDocumentoSottofase"
                              @click="apriAllegatoSottofase(allegato)"
                            >
                              Apri
                            </v-btn>

                            <v-tooltip text="Elimina allegato">
                              <template #activator="{ props }">
                                <v-btn
                                  v-bind="props"
                                  color="error"
                                  variant="text"
                                  icon="mdi-delete-outline"
                                  :disabled="eliminazioneAllegatoInCorso"
                                  @click="apriDialogEliminaAllegato(allegato)"
                                />
                              </template>
                            </v-tooltip>
                          </div>
                        </template>
                      </v-list-item>
                    </v-list>

                    <v-alert
                      v-else
                      type="info"
                      variant="tonal"
                      class="mt-5"
                    >
                      Nessun allegato collegato alla sottofase.
                    </v-alert>

                    <v-expansion-panels
                      v-if="allegatiSottofase.length"
                      class="technical-details-panel mt-4"
                      variant="accordion"
                    >
                      <v-expansion-panel>
                        <v-expansion-panel-title>
                          Dettagli allegati correnti
                        </v-expansion-panel-title>

                        <v-expansion-panel-text>
                          <div class="attachment-detail-list">
                            <div
                              v-for="allegato in allegatiSottofase"
                              :key="`dettagli-${allegato.idDocumentoSottofase}`"
                              class="attachment-detail-item"
                            >
                              <div class="font-weight-bold">
                                {{ valoreDettaglio(allegato.titoloDocumento) }}
                              </div>
                              <div class="detail-grid mt-3">
                                <div class="detail-field">
                                  <div class="detail-label">Tipo origine</div>
                                  <div class="detail-value">
                                    {{ valoreDettaglio(allegato.tipoOrigine) }}
                                  </div>
                                </div>

                                <div class="detail-field">
                                  <div class="detail-label">Nome file</div>
                                  <div class="detail-value">
                                    {{ valoreDettaglio(allegato.nomeFile) }}
                                  </div>
                                </div>

                                <div class="detail-field">
                                  <div class="detail-label">Data creazione</div>
                                  <div class="detail-value">
                                    {{ valoreDettaglio(allegato.dataCreazione) }}
                                  </div>
                                </div>

                                <div class="detail-field">
                                  <div class="detail-label">Data modifica</div>
                                  <div class="detail-value">
                                    {{ valoreDettaglio(allegato.dataModifica) }}
                                  </div>
                                </div>

                                <div class="detail-field">
                                  <div class="detail-label">Protocollo collegato</div>
                                  <div class="detail-value">
                                    {{ valoreDettaglio(allegato.idProtocolloCollegato) }}
                                  </div>
                                </div>

                                <div class="detail-field">
                                  <div class="detail-label">Percorso</div>
                                  <div class="detail-value">
                                    {{ valoreDettaglio(allegato.percorsoDocumento) }}
                                  </div>
                                </div>
                              </div>
                            </div>
                          </div>
                        </v-expansion-panel-text>
                      </v-expansion-panel>
                    </v-expansion-panels>

                    <v-expansion-panels
                      v-model="pannelloAllegatiEliminatiAperto"
                      class="allegati-eliminati-panel mt-5"
                      variant="accordion"
                    >
                      <v-expansion-panel :value="true">
                        <v-expansion-panel-title>
                          <div class="allegati-eliminati-title">
                            <div>
                              <div class="text-subtitle-2 font-weight-bold">
                                Allegati eliminati
                              </div>
                              <div class="text-caption text-medium-emphasis">
                                Storico eliminazioni e possibilita di ripristino.
                              </div>
                            </div>

                            <v-chip
                              color="warning"
                              variant="tonal"
                              size="small"
                            >
                              {{ allegatiEliminatiSottofase.length }} eliminati
                            </v-chip>
                          </div>
                        </v-expansion-panel-title>

                        <v-expansion-panel-text>
                          <v-alert
                            v-if="erroreAllegatiEliminati"
                            type="warning"
                            variant="tonal"
                            density="compact"
                            class="mb-4"
                          >
                            {{ erroreAllegatiEliminati }}
                          </v-alert>

                          <v-progress-linear
                            v-if="loadingAllegatiEliminati"
                            color="warning"
                            indeterminate
                            rounded
                            class="mb-4"
                          />

                          <v-list
                            v-else-if="allegatiEliminatiSottofase.length"
                            class="allegati-eliminati-list"
                            density="comfortable"
                            lines="three"
                          >
                            <v-list-item
                              v-for="allegato in allegatiEliminatiSottofase"
                              :key="allegato.idDocumentoSottofase"
                              class="allegato-eliminato-item"
                            >
                              <template #prepend>
                                <v-avatar
                                  color="warning"
                                  variant="tonal"
                                >
                                  <v-icon>
                                    {{ iconaAllegato(allegato) }}
                                  </v-icon>
                                </v-avatar>
                              </template>

                              <v-list-item-title class="font-weight-bold">
                                {{ valoreDettaglio(allegato.titoloDocumento) }}
                              </v-list-item-title>

                              <v-list-item-subtitle>
                                {{ valoreDettaglio(allegato.nomeFile) }}
                                <span class="mx-1">|</span>
                                {{ valoreDettaglio(allegato.tipoOrigine) }}
                              </v-list-item-subtitle>

                              <div class="allegato-audit-info mt-2">
                                <v-chip
                                  size="x-small"
                                  color="error"
                                  variant="tonal"
                                >
                                  Eliminato: {{ valoreDettaglio(allegato.dataEliminazione) }}
                                </v-chip>
                                <v-chip
                                  size="x-small"
                                  color="secondary"
                                  variant="tonal"
                                >
                                  Utente: {{ valoreDettaglio(allegato.utenteEliminazione) }}
                                </v-chip>
                              </div>

                              <div class="text-caption text-medium-emphasis mt-2">
                                Motivo: {{ valoreDettaglio(allegato.motivoEliminazione) }}
                              </div>

                              <template #append>
                                <v-tooltip text="Ripristina allegato">
                                  <template #activator="{ props }">
                                    <v-btn
                                      v-bind="props"
                                      color="success"
                                      variant="text"
                                      prepend-icon="mdi-restore"
                                      :disabled="ripristinoAllegatoInCorso"
                                      @click="apriDialogRipristinaAllegato(allegato)"
                                    >
                                      Ripristina
                                    </v-btn>
                                  </template>
                                </v-tooltip>
                              </template>
                            </v-list-item>
                          </v-list>

                          <v-alert
                            v-else
                            type="info"
                            variant="tonal"
                            density="compact"
                          >
                            Nessun allegato eliminato.
                          </v-alert>
                        </v-expansion-panel-text>
                      </v-expansion-panel>
                    </v-expansion-panels>
                  </v-card-text>
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

    <v-dialog
      v-model="dialogProtocolloAllegato"
      max-width="980"
    >
      <v-card rounded="lg">
        <v-card-title class="text-subtitle-1 font-weight-bold">
          Collega protocollo come allegato
        </v-card-title>

        <v-card-text>
          <v-alert
            v-if="erroreProtocolloAllegato"
            type="error"
            variant="tonal"
            density="compact"
            class="mb-4"
          >
            {{ erroreProtocolloAllegato }}
          </v-alert>

          <v-text-field
            v-model="ricercaProtocolloAllegato"
            label="Cerca protocollo"
            variant="outlined"
            density="compact"
            prepend-inner-icon="mdi-magnify"
            clearable
            class="mb-3"
          />

          <v-data-table
            :headers="headersProtocolliIstanza"
            :items="protocolliAllegatoFiltrati"
            :loading="loadingProtocolliAllegato"
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
                :loading="collegamentoProtocolloAllegatoInCorso"
                @click="selezionaProtocolloAllegato(item)"
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
            :disabled="collegamentoProtocolloAllegatoInCorso"
            @click="chiudiDialogProtocolloAllegato"
          >
            Chiudi
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog
      v-model="dialogEliminaAllegato"
      max-width="560"
      persistent
    >
      <v-card rounded="lg">
        <v-card-title class="text-subtitle-1 font-weight-bold">
          Elimina allegato
        </v-card-title>

        <v-card-text>
          <v-alert
            v-if="erroreEliminazioneAllegato"
            type="error"
            variant="tonal"
            density="compact"
            class="mb-4"
          >
            {{ erroreEliminazioneAllegato }}
          </v-alert>

          <p class="mb-3">
            Confermi l'eliminazione logica dell'allegato
            <strong>{{ titoloAllegatoDaEliminare }}</strong>?
          </p>

          <v-alert
            type="info"
            variant="tonal"
            density="compact"
            class="mb-4"
          >
            Il file non verra cancellato fisicamente e restera disponibile per audit.
          </v-alert>

          <v-textarea
            v-model="motivoEliminazioneAllegato"
            label="Motivo eliminazione"
            variant="outlined"
            rows="3"
            auto-grow
            counter="500"
          />
        </v-card-text>

        <v-card-actions class="justify-end">
          <v-btn
            variant="text"
            :disabled="eliminazioneAllegatoInCorso"
            @click="chiudiDialogEliminaAllegato"
          >
            Annulla
          </v-btn>

          <v-btn
            color="error"
            variant="flat"
            prepend-icon="mdi-delete-outline"
            :loading="eliminazioneAllegatoInCorso"
            @click="confermaEliminaAllegato"
          >
            Elimina
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog
      v-model="dialogRipristinaAllegato"
      max-width="520"
      persistent
    >
      <v-card rounded="lg">
        <v-card-title class="text-subtitle-1 font-weight-bold">
          Ripristina allegato
        </v-card-title>

        <v-card-text>
          <v-alert
            v-if="erroreRipristinoAllegato"
            type="error"
            variant="tonal"
            density="compact"
            class="mb-4"
          >
            {{ erroreRipristinoAllegato }}
          </v-alert>

          <p class="mb-0">
            L'allegato
            <strong>{{ titoloAllegatoDaRipristinare }}</strong>
            tornera disponibile nella sottofase.
          </p>
        </v-card-text>

        <v-card-actions class="justify-end">
          <v-btn
            variant="text"
            :disabled="ripristinoAllegatoInCorso"
            @click="chiudiDialogRipristinaAllegato"
          >
            Annulla
          </v-btn>

          <v-btn
            color="success"
            variant="flat"
            prepend-icon="mdi-restore"
            :loading="ripristinoAllegatoInCorso"
            @click="confermaRipristinaAllegato"
          >
            Ripristina
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog
      v-model="dialogDettagliStep"
      max-width="760"
    >
      <v-card rounded="lg">
        <v-card-title class="text-subtitle-1 font-weight-bold">
          Dettagli step
        </v-card-title>

        <v-card-text v-if="stepDettagliSelezionato">
          <div class="detail-grid">
            <div class="detail-field">
              <div class="detail-label">Titolo</div>
              <div class="detail-value">
                {{ valoreDettaglio(stepDettagliSelezionato.titoloStep) }}
              </div>
            </div>

            <div class="detail-field">
              <div class="detail-label">Codice</div>
              <div class="detail-value">
                {{ valoreDettaglio(stepDettagliSelezionato.codiceStep) }}
              </div>
            </div>

            <div class="detail-field">
              <div class="detail-label">Stato step</div>
              <div class="detail-value">
                {{ valoreDettaglio(stepDettagliSelezionato.statoStep) }}
              </div>
            </div>

            <div class="detail-field">
              <div class="detail-label">Stato visuale</div>
              <div class="detail-value">
                {{ valoreDettaglio(labelVisualState(stepDettagliSelezionato.visualState)) }}
              </div>
            </div>

            <div class="detail-field">
              <div class="detail-label">Ordine</div>
              <div class="detail-value">
                {{ valoreDettaglio(stepDettagliSelezionato.ordine) }}
              </div>
            </div>

            <div class="detail-field">
              <div class="detail-label">Attivabile</div>
              <div class="detail-value">
                {{ stepDettagliSelezionato.attivabile ? 'Si' : 'No' }}
              </div>
            </div>

            <div class="detail-field">
              <div class="detail-label">Data avvio</div>
              <div class="detail-value">
                {{ valoreDettaglio(stepDettagliSelezionato.dataAvvio) }}
              </div>
            </div>

            <div class="detail-field">
              <div class="detail-label">Data completamento</div>
              <div class="detail-value">
                {{ valoreDettaglio(stepDettagliSelezionato.dataCompletamento) }}
              </div>
            </div>

            <div class="detail-field">
              <div class="detail-label">Sottofase documentale</div>
              <div class="detail-value">
                {{ stepDettagliSelezionato.hasSottofaseDocumentale ? 'Presente' : 'Assente' }}
              </div>
            </div>

            <div class="detail-field">
              <div class="detail-label">ID sottofase</div>
              <div class="detail-value">
                {{ valoreDettaglio(stepDettagliSelezionato.sottofaseAttiva?.idSottofase) }}
              </div>
            </div>

            <div class="detail-field">
              <div class="detail-label">Stato sottofase</div>
              <div class="detail-value">
                {{ valoreDettaglio(stepDettagliSelezionato.sottofaseAttiva?.statoSottofase) }}
              </div>
            </div>

            <div class="detail-field">
              <div class="detail-label">Protocollo collegato</div>
              <div class="detail-value">
                {{ valoreDettaglio(stepDettagliSelezionato.numeroProtocolloCollegato) }}
              </div>
            </div>

            <div class="detail-field detail-field-wide">
              <div class="detail-label">Oggetto protocollo</div>
              <div class="detail-value">
                {{ valoreDettaglio(stepDettagliSelezionato.oggettoProtocolloCollegato) }}
              </div>
            </div>

            <div class="detail-field detail-field-wide">
              <div class="detail-label">Note operative</div>
              <div class="detail-value">
                {{ valoreDettaglio(stepDettagliSelezionato.noteOperative) }}
              </div>
            </div>
          </div>
        </v-card-text>

        <v-card-actions class="justify-end">
          <v-btn
            variant="text"
            @click="dialogDettagliStep = false"
          >
            Chiudi
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-snackbar
      v-model="snackbarFase"
      :color="snackbarFaseColor"
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
  collegaProtocolloAllegatoSottofase,
  collegaProtocolloStepIstanza,
  createDocumentoPrincipaleSottofase,
  createFaseProcedimento,
  creaBozzaDocumentoPrincipale,
  eliminaAllegatoSottofase,
  eliminaStepOrizzontale,
  eseguiAzioneWorkflowDocumentale,
  getAllegatiEliminati,
  getDocumentoPrincipaleSottofase,
  getProcedimento,
  getWorkflowDocumentaleSottofase,
  inserisciStepOrizzontaleDopo,
  listAllegatiSottofase,
  listFasiProcedimento,
  listProtocolli,
  listStepOrizzontaliFase,
  ripristinaAllegatoSottofase,
  salvaNoteStepRedigi,
  updateDocumentoPrincipaleMetadatiSottofase,
  updateFaseProcedimento,
  uploadAllegatoFileSottofase
} from '../services/procedimentoApi'
import { statiWorkflow } from '../mock/procedimentoWorkflowMock'
import elencoProcedimentoIcon from '../assets/ElencoProcedimentoICO.png'
import allegatiSvg from '../assets/workflow/allegati.svg'
import appuntamentoSvg from '../assets/workflow/appuntamento.svg'
import fineSvg from '../assets/workflow/fine.svg'
import firmaSvg from '../assets/workflow/firma.svg'
import mailSvg from '../assets/workflow/mail.svg'
import protocollaSvg from '../assets/workflow/protocolla.svg'
import redigiSvg from '../assets/workflow/redigi.svg'
import revisionaSvg from '../assets/workflow/revisiona.svg'
import telefonaSvg from '../assets/workflow/telefona.svg'

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
const dialogDettagliStep = ref(false)
const stepDettagliSelezionato = ref(null)
const noteRedigiForm = ref('')
const salvataggioNoteRedigiInCorso = ref(false)
const documentoPrincipaleRedigi = ref(null)
const loadingDocumentoPrincipaleRedigi = ref(false)
const creazioneDocumentoPrincipaleInCorso = ref(false)
const aperturaDocumentoPrincipaleInCorso = ref(false)
const salvataggioMetadatiDocumentoInCorso = ref(false)
const erroreDocumentoPrincipaleRedigi = ref('')
const workflowDocumentale = ref(null)
const loadingWorkflowDocumentale = ref(false)
const erroreWorkflowDocumentale = ref('')
const operazioneWorkflowDocumentaleInCorso = ref(false)
const workflowBozzaForm = reactive({
  titoloDocumento: '',
  descrizioneDocumento: ''
})
const workflowAzioneNote = ref('')
const workflowProtocolloId = ref('')
const allegatiSottofase = ref([])
const allegatiEliminatiSottofase = ref([])
const loadingAllegatiSottofase = ref(false)
const loadingAllegatiEliminati = ref(false)
const erroreAllegatiSottofase = ref('')
const erroreAllegatiEliminati = ref('')
const pannelloAllegatiEliminatiAperto = ref(false)
const dialogProtocolloAllegato = ref(false)
const protocolliAllegato = ref([])
const loadingProtocolliAllegato = ref(false)
const collegamentoProtocolloAllegatoInCorso = ref(false)
const erroreProtocolloAllegato = ref('')
const ricercaProtocolloAllegato = ref('')
const aperturaAllegatoInCorsoId = ref(null)
const allegatoFileInput = ref(null)
const uploadAllegatoInCorso = ref(false)
const dialogEliminaAllegato = ref(false)
const allegatoDaEliminare = ref(null)
const motivoEliminazioneAllegato = ref('')
const eliminazioneAllegatoInCorso = ref(false)
const erroreEliminazioneAllegato = ref('')
const dialogRipristinaAllegato = ref(false)
const allegatoDaRipristinare = ref(null)
const ripristinoAllegatoInCorso = ref(false)
const erroreRipristinoAllegato = ref('')
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
const snackbarFaseColor = ref('success')
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

const workflowStepAvatarMap = {
  redigi: redigiSvg,
  revisiona: revisionaSvg,
  firma: firmaSvg,
  protocolla: protocollaSvg,
  allegati: allegatiSvg,
  fine: fineSvg,
  telefona: telefonaSvg,
  mail: mailSvg,
  appuntamento: appuntamentoSvg
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
  'REDATTO',
  'IN_REVISIONE',
  'REVISIONATO',
  'DA_FIRMARE',
  'APPROVATO',
  'FIRMATO',
  'PROTOCOLLATO',
  'DA_PROTOCOLLARE',
  'ARCHIVIATO',
  'RESPINTO',
  'ANNULLATO'
]

const tipiDocumentoPrincipale = [
  'NOTA',
  'RELAZIONE',
  'VERBALE',
  'RICHIESTA',
  'PARERE',
  'ALTRO'
]

const allegatiFileAccept = [
  '.pdf',
  '.doc',
  '.docx',
  '.xls',
  '.xlsx',
  '.ppt',
  '.pptx',
  '.jpg',
  '.jpeg',
  '.png',
  '.txt'
].join(',')

const titoloAllegatoDaEliminare = computed(() => {
  const allegato = allegatoDaEliminare.value
  return (
    allegato?.titoloDocumento ||
    allegato?.nomeFile ||
    `Allegato ${allegato?.idDocumentoSottofase || ''}`.trim()
  )
})

const titoloAllegatoDaRipristinare = computed(() => {
  const allegato = allegatoDaRipristinare.value
  return (
    allegato?.titoloDocumento ||
    allegato?.nomeFile ||
    `Allegato ${allegato?.idDocumentoSottofase || ''}`.trim()
  )
})

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

const workflowVisualPoints = computed(() => {
  return stepOrizzontali.value.map((step, index, steps) => {
    const previousStep = index > 0 ? steps[index - 1] : null
    const visualState = getVisualState(step, previousStep)

    return {
      ...step,
      visualState,
      attivabile: isStepAttivabile(step, previousStep),
      outputs: getStepOutputs(step),
      avatarState: getAvatarState(step, previousStep)
    }
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

const stepDocumentaleSelezionato = computed(() => {
  const step = stepOperativoSelezionato.value
  return isStepDocumentale(step) ? step : null
})

const stepAllegatiSelezionato = computed(() => {
  const step = stepOperativoSelezionato.value
  return isStepAllegati(step) ? step : null
})

const idSottofaseDocumentaleRedigi = computed(() => {
  return (
    idSottofaseDaStep(stepRedigiSelezionato.value) ||
    faseSelezionata.value?.idSottofase ||
    faseSelezionata.value?.id ||
    null
  )
})

const idSottofaseDocumentaleWorkflow = computed(() => {
  return (
    idSottofaseDaStep(stepDocumentaleSelezionato.value) ||
    faseSelezionata.value?.idSottofase ||
    faseSelezionata.value?.id ||
    null
  )
})

const idSottofaseDocumentaleAllegati = computed(() => {
  return (
    idSottofaseDaStep(stepAllegatiSelezionato.value) ||
    faseSelezionata.value?.idSottofase ||
    faseSelezionata.value?.id ||
    null
  )
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

const documentoWorkflowPrincipale = computed(() => {
  return workflowDocumentale.value?.documento || null
})

const statoWorkflowDocumento = computed(() => {
  return String(documentoWorkflowPrincipale.value?.statoDocumento || '').toUpperCase()
})

const azioniWorkflowDocumentaleDisponibili = computed(() => {
  return Array.isArray(workflowDocumentale.value?.azioniDisponibili)
    ? workflowDocumentale.value.azioniDisponibili
    : []
})

const workflowDocumentaleReadyMessage = computed(() => {
  return workflowDocumentale.value?.message || 'Workflow documentale non caricato.'
})

const canCreaBozzaWorkflow = computed(() => {
  return isStepRedigi(stepDocumentaleSelezionato.value) && !documentoWorkflowPrincipale.value
})

const canCompletaRedazioneWorkflow = computed(() => {
  return (
    isStepRedigi(stepDocumentaleSelezionato.value) &&
    azioniWorkflowDocumentaleDisponibili.value.includes('completa_redazione')
  )
})

const canApprovaRevisioneWorkflow = computed(() => {
  return (
    isStepRevisiona(stepDocumentaleSelezionato.value) &&
    azioniWorkflowDocumentaleDisponibili.value.includes('approva_revisione')
  )
})

const canFirmaWorkflow = computed(() => {
  return (
    isStepFirma(stepDocumentaleSelezionato.value) &&
    azioniWorkflowDocumentaleDisponibili.value.includes('conferma_firma')
  )
})

const canProtocollaWorkflow = computed(() => {
  return (
    isStepProtocolla(stepDocumentaleSelezionato.value) &&
    azioniWorkflowDocumentaleDisponibili.value.includes('conferma_protocollazione')
  )
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

const protocolliAllegatoFiltrati = computed(() => {
  const filtro = String(ricercaProtocolloAllegato.value || '').trim().toLowerCase()
  if (!filtro) return protocolliAllegato.value

  return protocolliAllegato.value.filter((protocollo) => {
    return [
      protocollo.numeroProtocollo,
      protocollo.dataProtocollo,
      protocollo.oggetto,
      protocollo.comandoMittente
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
  const sottofaseAttiva = normalizzaSottofaseAttivaStep(
    dato.sottofase_attiva ??
      dato.sottofaseAttiva ??
      dato.SottofaseAttiva ??
      null
  )

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
      '',
    sottofaseAttiva,
    hasSottofaseDocumentale: Boolean(
      dato.has_sottofase_documentale ??
        dato.hasSottofaseDocumentale ??
        dato.HasSottofaseDocumentale ??
        sottofaseAttiva
    )
  }
}

function normalizzaSottofaseAttivaStep(dato = null) {
  if (!dato) return null

  return {
    idSottofase:
      dato.id_sottofase ??
      dato.IDSottofase ??
      dato.idSottofase ??
      dato.id,
    idFase:
      dato.id_fase ??
      dato.IDFase ??
      dato.idFase ??
      null,
    idStepOrizzontale:
      dato.id_step_orizzontale ??
      dato.IDStepOrizzontale ??
      dato.idStepOrizzontale ??
      null,
    titolo:
      dato.titolo ??
      dato.Titolo ??
      dato.titoloSottofase ??
      dato.TitoloSottofase ??
      'Fascicolo documentale',
    statoSottofase:
      dato.stato_sottofase ??
      dato.StatoSottofase ??
      dato.statoSottofase ??
      '',
    tipoAggancio:
      dato.tipo_aggancio ??
      dato.TipoAggancio ??
      dato.tipoAggancio ??
      '',
    sottofasePrincipale:
      dato.sottofase_principale ??
      dato.SottofasePrincipale ??
      dato.sottofasePrincipale ??
      null,
    attivo:
      dato.attivo ??
      dato.Attivo ??
      true
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

function normalizzaAllegatoSottofase(dato = {}) {
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
    titoloDocumento:
      dato.titolo_documento ??
      dato.TitoloDocumento ??
      dato.titoloDocumento ??
      '',
    tipoOrigine:
      dato.tipo_origine ??
      dato.TipoOrigine ??
      dato.tipoOrigine ??
      '',
    nomeFile:
      dato.nome_file ??
      dato.NomeFile ??
      dato.nomeFile ??
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
    dataEliminazione:
      dato.data_eliminazione ??
      dato.DataEliminazione ??
      dato.dataEliminazione ??
      '',
    utenteEliminazione:
      dato.utente_eliminazione ??
      dato.UtenteEliminazione ??
      dato.utenteEliminazione ??
      '',
    motivoEliminazione:
      dato.motivo_eliminazione ??
      dato.MotivoEliminazione ??
      dato.motivoEliminazione ??
      '',
    statoDocumento:
      dato.stato_documento ??
      dato.StatoDocumento ??
      dato.statoDocumento ??
      '',
    attivo:
      dato.attivo ??
      dato.Attivo ??
      true,
    idProtocolloCollegato:
      dato.id_protocollo_collegato ??
      dato.IDProtocolloCollegato ??
      dato.idProtocolloCollegato ??
      null,
    percorsoDocumento:
      dato.percorso_documento ??
      dato.PercorsoDocumento ??
      dato.percorsoDocumento ??
      ''
  }
}

function normalizzaChiaveWorkflowStep(stepOrCode) {
  const value = typeof stepOrCode === 'object' && stepOrCode !== null
    ? stepOrCode.codiceStep ??
      stepOrCode.codice_step ??
      stepOrCode.CodiceStep ??
      stepOrCode.titoloStep ??
      stepOrCode.titolo_step ??
      stepOrCode.TitoloStep
    : stepOrCode

  const normalized = String(value || '')
    .trim()
    .toLowerCase()
    .replace(/\s+/g, '_')
    .replace(/-/g, '_')

  const aliases = {
    redazione: 'redigi',
    revisione: 'revisiona',
    firma_digitale: 'firma',
    protocollo: 'protocolla',
    protocollazione: 'protocolla',
    allegato: 'allegati',
    allegati_documento: 'allegati',
    chiusura: 'fine',
    telefono: 'telefona',
    telefonata: 'telefona',
    email: 'mail',
    e_mail: 'mail',
    appuntamenti: 'appuntamento'
  }

  return aliases[normalized] || normalized
}

function workflowAvatarForStep(stepOrCode) {
  const key = normalizzaChiaveWorkflowStep(stepOrCode)
  return workflowStepAvatarMap[key] || workflowStepAvatarMap.fine
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
    mostraSnackbarFase('Workflow rapido Istanza -> Fine applicato.', 'success')
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
    mostraSnackbarFase('Workflow predefinito applicato.', 'success')
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

function isStepRevisiona(step) {
  return String(step?.codiceStep || '').toUpperCase() === 'REVISIONA'
}

function isStepFirma(step) {
  return String(step?.codiceStep || '').toUpperCase() === 'FIRMA'
}

function isStepProtocolla(step) {
  return String(step?.codiceStep || '').toUpperCase() === 'PROTOCOLLA'
}

function isStepDocumentale(step) {
  return (
    isStepRedigi(step) ||
    isStepRevisiona(step) ||
    isStepFirma(step) ||
    isStepProtocolla(step)
  )
}

function isStepAllegati(step) {
  return String(step?.codiceStep || '').toUpperCase() === 'ALLEGATI'
}

function isIstanzaProtocolloCompletata(step) {
  const stato = String(step?.statoStep || '').toUpperCase()
  return isStepIstanza(step) &&
    stato.includes('COMPLET') &&
    Boolean(step?.idProtocolloCollegato)
}

function isStepCompletato(step) {
  const stato = String(step?.statoStep || '').toUpperCase()
  return stato.includes('COMPLET')
}

function isStepInLavorazione(step) {
  const stato = String(step?.statoStep || '').toUpperCase()
  return stato.includes('CORSO') || stato === 'ACTIVE'
}

function isStepAttivabile(step, previousStep = null) {
  if (isStepCompletato(step)) return true
  if (!previousStep) return true
  return isStepCompletato(previousStep)
}

function getVisualState(step, previousStep = null) {
  if (!isStepAttivabile(step, previousStep)) return 'locked'
  if (isStepCompletato(step)) return 'completed'
  if (isStepInLavorazione(step)) return 'active'
  return 'idle'
}

function getStepOutputs(step) {
  const outputs = []

  if (isIstanzaProtocolloCompletata(step)) {
    outputs.push({
      key: 'protocollo',
      icon: 'mdi-file-document-check-outline',
      color: 'success',
      label: 'Apri PDF protocollo collegato',
      action: 'apri-protocollo'
    })
  }

  if (step?.hasSottofaseDocumentale) {
    outputs.push({
      key: 'sottofase-documentale',
      icon: 'mdi-folder-file-outline',
      color: 'primary',
      label: step.sottofaseAttiva?.titolo || 'Fascicolo documentale collegato',
      action: 'dettagli'
    })
  }

  return outputs
}

function getAvatarState(step, previousStep = null) {
  return getVisualState(step, previousStep)
}

function idSottofaseDaStep(step) {
  return step?.sottofaseAttiva?.idSottofase || step?.idSottofase || null
}

function labelVisualState(visualState) {
  const labels = {
    idle: 'Non avviato',
    active: 'In lavorazione',
    completed: 'Completato',
    locked: 'Non attivabile'
  }
  return labels[visualState] || visualState
}

function apriDettagliStep(step) {
  stepDettagliSelezionato.value = step
  dialogDettagliStep.value = true
}

function gestisciClickOutputStep(step, output) {
  if (output?.action === 'apri-protocollo') {
    apriPdfProtocolloIstanza(step)
    return
  }

  apriDettagliStep(step)
}

async function gestisciClickStepOrizzontale(step) {
  if (step?.attivabile === false) {
    mostraSnackbarFase(
      'Questo step sara attivabile dopo il completamento del precedente.',
      'warning'
    )
    return
  }

  if (isStepDocumentale(step)) {
    stepOperativoSelezionatoId.value = step.id
    noteRedigiForm.value = isStepRedigi(step) ? step.noteOperative || '' : ''
    allegatiSottofase.value = []
    allegatiEliminatiSottofase.value = []
    resetFormMetadatiDocumento()
    if (isStepRedigi(step)) {
      await Promise.all([
        caricaWorkflowDocumentale(),
        caricaDocumentoPrincipaleRedigi()
      ])
    } else {
      documentoPrincipaleRedigi.value = null
      await caricaWorkflowDocumentale()
    }
    return
  }

  if (isStepAllegati(step)) {
    stepOperativoSelezionatoId.value = step.id
    noteRedigiForm.value = ''
    documentoPrincipaleRedigi.value = null
    resetFormMetadatiDocumento()
    await aggiornaListeAllegatiSottofase()
    return
  }

  if (!isStepIstanza(step)) {
    stepOperativoSelezionatoId.value = null
    noteRedigiForm.value = ''
    documentoPrincipaleRedigi.value = null
    resetFormMetadatiDocumento()
    erroreDocumentoPrincipaleRedigi.value = ''
    workflowDocumentale.value = null
    erroreWorkflowDocumentale.value = ''
    allegatiSottofase.value = []
    allegatiEliminatiSottofase.value = []
    erroreAllegatiSottofase.value = ''
    erroreAllegatiEliminati.value = ''
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

async function caricaWorkflowDocumentale() {
  const idSottofase = idSottofaseDocumentaleWorkflow.value
  if (!idSottofase) {
    workflowDocumentale.value = null
    erroreWorkflowDocumentale.value =
      'Contesto documentale della fase non disponibile.'
    return
  }

  loadingWorkflowDocumentale.value = true
  erroreWorkflowDocumentale.value = ''

  try {
    workflowDocumentale.value = await getWorkflowDocumentaleSottofase(idSottofase)
    sincronizzaDocumentoPrincipaleDaWorkflow()
  } catch (error) {
    workflowDocumentale.value = null
    erroreWorkflowDocumentale.value = messaggioErroreWorkflowDocumentale(error)
  } finally {
    loadingWorkflowDocumentale.value = false
  }
}

async function creaBozzaWorkflowDocumentale() {
  const idSottofase = idSottofaseDocumentaleWorkflow.value
  if (!idSottofase) return

  operazioneWorkflowDocumentaleInCorso.value = true
  erroreWorkflowDocumentale.value = ''

  try {
    workflowDocumentale.value = await creaBozzaDocumentoPrincipale(idSottofase, {
      titoloDocumento: workflowBozzaForm.titoloDocumento,
      descrizioneDocumento: workflowBozzaForm.descrizioneDocumento,
      utente: 'operatore'
    })
    sincronizzaDocumentoPrincipaleDaWorkflow()
    workflowBozzaForm.titoloDocumento = ''
    workflowBozzaForm.descrizioneDocumento = ''
    mostraSnackbarFase('Bozza documento creata.', 'success')
  } catch (error) {
    erroreWorkflowDocumentale.value = messaggioErroreWorkflowDocumentale(error)
    mostraSnackbarFase(erroreWorkflowDocumentale.value, 'error')
  } finally {
    operazioneWorkflowDocumentaleInCorso.value = false
  }
}

async function eseguiAzioneDocumentale(azione) {
  const idSottofase = idSottofaseDocumentaleWorkflow.value
  const idDocumento = documentoWorkflowPrincipale.value?.idDocumento
  if (!idSottofase || !idDocumento) return

  operazioneWorkflowDocumentaleInCorso.value = true
  erroreWorkflowDocumentale.value = ''

  try {
    const payload = {
      azione,
      note: workflowAzioneNote.value,
      utente: 'operatore'
    }
    if (azione === 'conferma_protocollazione') {
      payload.idProtocollo = workflowProtocolloId.value
    }

    const result = await eseguiAzioneWorkflowDocumentale(
      idSottofase,
      idDocumento,
      payload
    )
    workflowDocumentale.value = result.workflow
    sincronizzaDocumentoPrincipaleDaWorkflow()
    workflowAzioneNote.value = ''
    workflowProtocolloId.value = ''
    mostraSnackbarFase('Stato documentale aggiornato.', 'success')
  } catch (error) {
    erroreWorkflowDocumentale.value = messaggioErroreWorkflowDocumentale(error)
    mostraSnackbarFase(erroreWorkflowDocumentale.value, 'error')
  } finally {
    operazioneWorkflowDocumentaleInCorso.value = false
  }
}

function sincronizzaDocumentoPrincipaleDaWorkflow() {
  const documento = workflowDocumentale.value?.documento
  if (!documento) {
    documentoPrincipaleRedigi.value = null
    resetFormMetadatiDocumento()
    return
  }

  const normalizzato = normalizzaDocumentoPrincipale({
    ...documento,
    idDocumentoSottofase:
      documento.idDocumentoSottofase ??
      documento.idDocumento,
    statoDocumento: documento.statoDocumento,
    titoloDocumento: documento.titoloDocumento,
    descrizioneDocumento: documento.descrizioneDocumento,
    tipoDocumento: documento.tipoDocumento,
    dataCreazione: documento.dataCreazione,
    dataModifica: documento.dataModifica,
    versioneDocumento: documento.versioneDocumento
  })
  documentoPrincipaleRedigi.value = normalizzato
  popolaFormMetadatiDocumento(normalizzato)
}

async function aggiornaListeAllegatiSottofase() {
  await Promise.all([
    caricaAllegatiSottofase(),
    caricaAllegatiEliminatiSottofase()
  ])
}

async function caricaAllegatiSottofase() {
  const idSottofase = idSottofaseDocumentaleAllegati.value
  if (!idSottofase) {
    allegatiSottofase.value = []
    allegatiEliminatiSottofase.value = []
    erroreAllegatiSottofase.value =
      'Contesto documentale della fase non disponibile.'
    return
  }

  loadingAllegatiSottofase.value = true
  erroreAllegatiSottofase.value = ''

  try {
    const allegati = await listAllegatiSottofase(idSottofase)
    allegatiSottofase.value = Array.isArray(allegati)
      ? allegati.map(normalizzaAllegatoSottofase)
      : []
  } catch (error) {
    allegatiSottofase.value = []
    erroreAllegatiSottofase.value = messaggioErroreAllegati(error)
  } finally {
    loadingAllegatiSottofase.value = false
  }
}

async function caricaAllegatiEliminatiSottofase() {
  const idSottofase = idSottofaseDocumentaleAllegati.value
  if (!idSottofase) {
    allegatiEliminatiSottofase.value = []
    erroreAllegatiEliminati.value =
      'Contesto documentale della fase non disponibile.'
    return
  }

  loadingAllegatiEliminati.value = true
  erroreAllegatiEliminati.value = ''

  try {
    const response = await getAllegatiEliminati(idSottofase)
    const items = Array.isArray(response)
      ? response
      : Array.isArray(response?.items)
        ? response.items
        : []
    allegatiEliminatiSottofase.value = items.map(normalizzaAllegatoSottofase)
  } catch (error) {
    allegatiEliminatiSottofase.value = []
    erroreAllegatiEliminati.value = messaggioErroreAllegati(error)
  } finally {
    loadingAllegatiEliminati.value = false
  }
}

async function apriDialogProtocolloAllegato() {
  erroreProtocolloAllegato.value = ''
  ricercaProtocolloAllegato.value = ''
  dialogProtocolloAllegato.value = true
  await caricaProtocolliAllegato()
}

async function caricaProtocolliAllegato() {
  loadingProtocolliAllegato.value = true
  erroreProtocolloAllegato.value = ''

  try {
    const protocolli = await listProtocolli()
    protocolliAllegato.value = Array.isArray(protocolli)
      ? protocolli.map(normalizzaProtocolloIstanza)
      : []
  } catch {
    protocolliAllegato.value = []
    erroreProtocolloAllegato.value =
      'Impossibile caricare i protocolli disponibili.'
  } finally {
    loadingProtocolliAllegato.value = false
  }
}

async function selezionaProtocolloAllegato(protocollo) {
  const idSottofase = idSottofaseDocumentaleAllegati.value
  if (!idSottofase || !protocollo?.idProtocollo) return

  collegamentoProtocolloAllegatoInCorso.value = true
  erroreProtocolloAllegato.value = ''

  try {
    await collegaProtocolloAllegatoSottofase(idSottofase, {
      idProtocollo: protocollo.idProtocollo
    })
    await aggiornaListeAllegatiSottofase()
    dialogProtocolloAllegato.value = false
    mostraSnackbarFase('Protocollo collegato come allegato.', 'success')
  } catch (error) {
    erroreProtocolloAllegato.value = messaggioErroreAllegati(error)
  } finally {
    collegamentoProtocolloAllegatoInCorso.value = false
  }
}

function apriSelettoreFileAllegato() {
  erroreAllegatiSottofase.value = ''
  allegatoFileInput.value?.click()
}

async function gestisciSelezioneFileAllegato(event) {
  const input = event?.target
  const file = input?.files?.[0]
  if (!file) return

  await caricaFileAllegato(file)

  if (input) {
    input.value = ''
  }
}

async function caricaFileAllegato(file) {
  const idSottofase = idSottofaseDocumentaleAllegati.value
  if (!idSottofase || !file) return

  uploadAllegatoInCorso.value = true
  erroreAllegatiSottofase.value = ''

  try {
    await uploadAllegatoFileSottofase(idSottofase, file)
    await aggiornaListeAllegatiSottofase()
    mostraSnackbarFase('File allegato caricato.', 'success')
  } catch (error) {
    erroreAllegatiSottofase.value = messaggioErroreAllegati(error)
  } finally {
    uploadAllegatoInCorso.value = false
  }
}

function chiudiDialogProtocolloAllegato() {
  if (collegamentoProtocolloAllegatoInCorso.value) return

  dialogProtocolloAllegato.value = false
  erroreProtocolloAllegato.value = ''
}

async function apriAllegatoSottofase(allegato) {
  if (allegato?.tipoOrigine === 'PROTOCOLLO' && allegato?.idProtocolloCollegato) {
    erroreAllegatiSottofase.value = ''
    try {
      await apriPdfProtocolloEsterno(allegato.idProtocolloCollegato)
    } catch (error) {
      erroreAllegatiSottofase.value = messaggioErrorePdfProtocollo(error)
    }
    return
  }

  const idDocumento = allegato?.idDocumentoSottofase
  if (!idDocumento) {
    erroreAllegatiSottofase.value = 'Allegato non apribile: identificativo mancante.'
    return
  }

  const openedWindow = window.open('', '_blank')
  if (!openedWindow) {
    erroreAllegatiSottofase.value =
      'Il browser ha bloccato l apertura dell allegato in una nuova scheda.'
    return
  }

  openedWindow.opener = null
  aperturaAllegatoInCorsoId.value = idDocumento
  erroreAllegatiSottofase.value = ''

  try {
    const blob = await apriDocumentoSottofase(idDocumento)
    const blobUrl = URL.createObjectURL(blob)
    openedWindow.location.href = blobUrl

    setTimeout(() => {
      URL.revokeObjectURL(blobUrl)
    }, 60000)
  } catch (error) {
    erroreAllegatiSottofase.value = messaggioErroreAllegati(error)

    try {
      openedWindow.close()
    } catch {
      // Scheda aperta solo in risposta al click utente.
    }
  } finally {
    aperturaAllegatoInCorsoId.value = null
  }
}

function apriDialogEliminaAllegato(allegato) {
  allegatoDaEliminare.value = allegato
  motivoEliminazioneAllegato.value = ''
  erroreEliminazioneAllegato.value = ''
  dialogEliminaAllegato.value = true
}

function chiudiDialogEliminaAllegato() {
  if (eliminazioneAllegatoInCorso.value) return

  dialogEliminaAllegato.value = false
  allegatoDaEliminare.value = null
  motivoEliminazioneAllegato.value = ''
  erroreEliminazioneAllegato.value = ''
}

async function confermaEliminaAllegato() {
  const idSottofase = idSottofaseDocumentaleAllegati.value
  const idDocumento = allegatoDaEliminare.value?.idDocumentoSottofase
  if (!idSottofase || !idDocumento) {
    erroreEliminazioneAllegato.value =
      'Allegato non eliminabile: contesto non disponibile.'
    return
  }

  eliminazioneAllegatoInCorso.value = true
  erroreEliminazioneAllegato.value = ''

  try {
    await eliminaAllegatoSottofase(idSottofase, idDocumento, {
      motivoEliminazione: motivoEliminazioneAllegato.value,
      utenteEliminazione: 'operatore'
    })
    await aggiornaListeAllegatiSottofase()
    eliminazioneAllegatoInCorso.value = false
    chiudiDialogEliminaAllegato()
    mostraSnackbarFase('Allegato eliminato logicamente.', 'success')
  } catch (error) {
    erroreEliminazioneAllegato.value = messaggioErroreEliminazioneAllegato(error)
    mostraSnackbarFase(erroreEliminazioneAllegato.value, 'error')
  } finally {
    eliminazioneAllegatoInCorso.value = false
  }
}

function apriDialogRipristinaAllegato(allegato) {
  allegatoDaRipristinare.value = allegato
  erroreRipristinoAllegato.value = ''
  dialogRipristinaAllegato.value = true
}

function chiudiDialogRipristinaAllegato() {
  if (ripristinoAllegatoInCorso.value) return

  dialogRipristinaAllegato.value = false
  allegatoDaRipristinare.value = null
  erroreRipristinoAllegato.value = ''
}

async function confermaRipristinaAllegato() {
  const idSottofase = idSottofaseDocumentaleAllegati.value
  const idDocumento = allegatoDaRipristinare.value?.idDocumentoSottofase
  if (!idSottofase || !idDocumento) {
    erroreRipristinoAllegato.value =
      'Allegato non ripristinabile: contesto non disponibile.'
    return
  }

  ripristinoAllegatoInCorso.value = true
  erroreRipristinoAllegato.value = ''

  try {
    await ripristinaAllegatoSottofase(idSottofase, idDocumento, {
      utenteRipristino: 'operatore'
    })
    await aggiornaListeAllegatiSottofase()
    ripristinoAllegatoInCorso.value = false
    chiudiDialogRipristinaAllegato()
    mostraSnackbarFase('Allegato ripristinato.', 'success')
  } catch (error) {
    erroreRipristinoAllegato.value = messaggioErroreRipristinoAllegato(error)
    mostraSnackbarFase(erroreRipristinoAllegato.value, 'error')
  } finally {
    ripristinoAllegatoInCorso.value = false
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
    mostraSnackbarFase('Documento principale creato.', 'success')
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
    mostraSnackbarFase('Metadati documento salvati.', 'success')
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
    mostraSnackbarFase('Lavorazione Redigi avviata.', 'success')
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
    mostraSnackbarFase('Lavorazione Redigi completata.', 'success')
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
    mostraSnackbarFase('Note operative salvate.', 'success')
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
    mostraSnackbarFase('Protocollo collegato allo step Istanza.', 'success')
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
    mostraSnackbarFase(`${opzione?.titoloStep || 'Step'} inserito.`, 'success')
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
    mostraSnackbarFase('Step eliminato.', 'success')
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
    mostraSnackbarFase(
      faseDialogMode.value === 'create' ? 'Fase creata.' : 'Fase aggiornata.',
      'success'
    )
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

function messaggioErroreWorkflowDocumentale(error) {
  const dettaglio = error?.payload?.detail
  if (typeof dettaglio === 'string') return dettaglio

  if (error?.status === 400) {
    return 'Azione documentale non consentita.'
  }

  if (error?.status === 404) {
    return 'Documento principale non trovato.'
  }

  if (error?.status === 409) {
    return 'Esiste gia un documento principale attivo.'
  }

  return 'Impossibile aggiornare il workflow documentale.'
}

function messaggioErroreAllegati(error) {
  const dettaglio = error?.payload?.detail
  if (typeof dettaglio === 'string') return dettaglio

  if (error?.status === 409) {
    return 'Protocollo gia collegato alla sottofase.'
  }

  if (error?.status === 404) {
    return 'Allegato o protocollo non disponibile.'
  }

  return 'Impossibile aggiornare gli allegati della sottofase.'
}

function messaggioErroreEliminazioneAllegato(error) {
  const dettaglio = error?.payload?.detail
  if (typeof dettaglio === 'string') return dettaglio

  if (error?.status === 400) {
    return 'Allegato non eliminabile.'
  }

  if (error?.status === 404) {
    return 'Allegato non trovato o non appartenente alla sottofase.'
  }

  if (error?.status === 410) {
    return 'Allegato gia eliminato.'
  }

  if (error?.status === 500) {
    return 'Errore imprevisto durante eliminazione allegato.'
  }

  return 'Impossibile eliminare allegato.'
}

function messaggioErroreRipristinoAllegato(error) {
  const dettaglio = error?.payload?.detail
  if (typeof dettaglio === 'string') return dettaglio

  if (error?.status === 400) {
    return 'Allegato non ripristinabile.'
  }

  if (error?.status === 404) {
    return 'Allegato non trovato o non appartenente alla sottofase.'
  }

  if (error?.status === 500) {
    return 'Errore imprevisto durante ripristino allegato.'
  }

  return 'Impossibile ripristinare allegato.'
}

function mostraSnackbarFase(messaggio, color = 'success') {
  messaggioFase.value = messaggio
  snackbarFaseColor.value = color
  snackbarFase.value = true
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

function iconaAllegato(allegato) {
  const tipoOrigine = String(allegato?.tipoOrigine || '').toUpperCase()
  if (tipoOrigine === 'PROTOCOLLO') return 'mdi-file-document-outline'
  if (tipoOrigine === 'FILE') return 'mdi-file-upload-outline'
  if (tipoOrigine === 'GENERATO') return 'mdi-file-cog-outline'
  return 'mdi-file-document-outline'
}

function classeStepOrizzontale(step) {
  if (typeof step === 'object' && step?.visualState) {
    const classi = {
      idle: 'step-orizzontale-non-avviato',
      locked: 'step-orizzontale-non-avviato step-orizzontale-locked',
      completed: 'step-orizzontale-completato',
      active: 'step-orizzontale-in-corso'
    }
    return classi[step.visualState] || 'step-orizzontale-non-avviato'
  }

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

function coloreStatoDocumentoWorkflow(stato) {
  const normalizzato = String(stato || '').toUpperCase()
  if (normalizzato === 'BOZZA') return 'grey'
  if (normalizzato === 'REDATTO') return 'info'
  if (normalizzato === 'REVISIONATO') return 'primary'
  if (normalizzato === 'FIRMATO') return 'success'
  if (normalizzato === 'PROTOCOLLATO') return 'success'
  if (normalizzato === 'RESPINTO') return 'error'
  if (normalizzato === 'ANNULLATO') return 'error'
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

.procedimento-page-lavorazione {
  height: auto;
  min-height: calc(100vh - 112px);
  overflow: visible;
}

.procedimento-page-lavorazione .procedimento-shell {
  align-items: start;
  height: auto;
  min-height: calc(100vh - 112px);
  overflow: visible;
}

.procedimento-page-lavorazione .procedimento-rail {
  height: calc(100vh - 112px);
  position: sticky;
  top: 0;
}

.procedimento-page-lavorazione .work-area,
.procedimento-page-lavorazione .work-window,
.procedimento-page-lavorazione .work-window :deep(.v-window__container),
.procedimento-page-lavorazione .work-window :deep(.v-window-item) {
  height: auto;
  min-height: calc(100vh - 112px);
  overflow: visible;
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

.detail-field-wide {
  grid-column: 1 / -1;
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

.technical-details-panel {
  border: 1px solid rgba(var(--v-theme-on-surface), 0.1);
  border-radius: 8px;
  overflow: hidden;
}

.technical-details-panel :deep(.v-expansion-panel-title) {
  font-size: 0.86rem;
  font-weight: 850;
  letter-spacing: 0;
  min-height: 42px;
  padding: 10px 16px;
}

.technical-details-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 12px;
}

.document-operational-summary {
  align-items: center;
  border: 1px solid rgba(var(--v-theme-on-surface), 0.1);
  border-radius: 8px;
  display: flex;
  gap: 12px;
  justify-content: space-between;
  margin-bottom: 14px;
  padding: 12px 14px;
}

.attachment-detail-list {
  display: grid;
  gap: 16px;
}

.attachment-detail-item + .attachment-detail-item {
  border-top: 1px solid rgba(var(--v-theme-on-surface), 0.1);
  padding-top: 16px;
}

.lavorazione-view {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 0;
  overflow: hidden;
  padding: 12px 38px 28px 26px;
}

.procedimento-page-lavorazione .lavorazione-view {
  height: auto;
  min-height: calc(100vh - 112px);
  overflow: visible;
  padding-bottom: 80px;
}

.lavorazione-sticky-head {
  background: rgb(var(--v-theme-surface));
  flex: 0 0 auto;
  padding-top: 4px;
  position: sticky;
  top: 0;
  z-index: 20;
}

.lavorazione-toolbar {
  align-items: flex-start;
  display: flex;
  flex: 0 0 auto;
  justify-content: center;
  min-height: 78px;
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
  padding: 8px 28px 12px;
  text-align: center;
}

.lavorazione-content-card {
  border: 1px dashed rgba(var(--v-theme-on-surface), 0.18);
  border-radius: 8px;
  display: flex;
  flex: 0 0 auto;
  flex-direction: column;
  min-height: 0;
  overflow: visible;
  padding: 0 40px 48px;
}

.workflow-quick-actions {
  display: flex;
  flex: 0 0 auto;
  gap: 10px;
  justify-content: flex-start;
  margin-bottom: 10px;
}

.stepper-orizzontale {
  align-items: start;
  display: flex;
  flex: 0 0 auto;
  flex-wrap: wrap;
  justify-content: space-between;
  margin: 0;
  row-gap: 10px;
  width: 100%;
}

.step-orizzontale-item {
  cursor: pointer;
  flex: 1 0 16.666%;
  min-width: 0;
  padding-bottom: 26px;
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
  border: 1px solid white;
  border-radius: 999px;
  box-shadow: 0 0 0 2px rgba(var(--v-theme-on-surface), 0.12);
  color: white;
  display: flex;
  font-weight: 900;
  height: 104px;
  justify-content: center;
  padding: 0;
  position: relative;
  width: 104px;
  z-index: 1;
}

.workflow-avatar-img {
  display: block;
  object-fit: contain;
}

.step-node-avatar-img {
  filter: drop-shadow(0 1px 1px rgba(0, 0, 0, 0.18));
  height: 94px;
  width: 94px;
}

.step-node-number {
  align-items: center;
  background: rgba(255, 255, 255, 0.96);
  border: 1px solid rgba(var(--v-theme-on-surface), 0.16);
  border-radius: 999px;
  color: rgba(var(--v-theme-on-surface), 0.78);
  display: flex;
  font-size: 0.8rem;
  font-weight: 900;
  height: 28px;
  justify-content: center;
  left: -8px;
  min-width: 28px;
  padding: 0 7px;
  position: absolute;
  top: -8px;
}

.workflow-menu-avatar-img {
  height: 22px;
  width: 22px;
}

.step-orizzontale-item:hover .step-orizzontale-node {
  box-shadow:
    0 0 0 2px rgba(var(--v-theme-on-surface), 0.12),
    0 0 0 4px rgba(var(--v-theme-primary), 0.14);
}

.step-orizzontale-item--locked {
  cursor: not-allowed;
  filter: grayscale(1);
  opacity: 0.58;
}

.step-orizzontale-item--locked .step-orizzontale-title,
.step-orizzontale-item--locked .step-details-action {
  color: rgba(var(--v-theme-on-surface), 0.58);
}

.step-orizzontale-item--locked:hover .step-orizzontale-node {
  box-shadow: 0 0 0 2px rgba(var(--v-theme-on-surface), 0.12);
}

.step-node-actions {
  align-items: center;
  display: flex;
  gap: 0;
  justify-content: space-between;
  left: 50%;
  opacity: 0;
  pointer-events: none;
  position: absolute;
  top: 73px;
  transform: translateX(-50%);
  transition: opacity 0.12s ease;
  width: 198px;
  z-index: 2;
}

.step-node-action {
  height: 49px;
  min-width: 49px;
  width: 49px;
}

.step-node-action :deep(.v-icon) {
  font-size: 34px;
}

.step-delete-action {
  margin-left: 4px;
}

.step-add-action {
  margin-right: 4px;
}

.step-orizzontale-item:hover .step-node-actions,
.step-node-actions:focus-within {
  opacity: 1;
  pointer-events: auto;
}

.step-orizzontale-non-avviato {
  background: #9e9e9e;
}

.step-orizzontale-locked {
  background: #b0b0b0;
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
  left: calc(50% + 54px);
  position: absolute;
  right: calc(-50% + 54px);
  top: 50%;
  transform: translateY(-50%);
}

.step-orizzontale-title {
  font-size: 1rem;
  font-weight: 900;
  margin-bottom: 4px;
  margin-top: 24px;
  overflow-wrap: anywhere;
}

.workflow-avatar-img--muted {
  filter: grayscale(1);
  opacity: 0.52;
}

.step-node-outputs {
  align-items: center;
  display: flex;
  gap: 6px;
  justify-content: center;
  min-height: 32px;
}

.step-output-action {
  align-items: center;
  background: rgba(var(--v-theme-surface), 0.92);
  border: 1px solid rgba(var(--v-theme-on-surface), 0.14);
  border-radius: 999px;
  cursor: pointer;
  display: inline-flex;
  height: 32px;
  justify-content: center;
  padding: 0;
  width: 32px;
}

.step-output-action:hover {
  background: rgba(var(--v-theme-primary), 0.08);
  border-color: rgba(var(--v-theme-primary), 0.28);
}

.step-details-action {
  font-weight: 800;
  letter-spacing: 0;
  margin-top: 6px;
  min-height: 28px;
  text-transform: none;
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
  flex: 0 0 auto;
  margin: 0 auto;
  max-width: 620px;
}

.step-operativo-scroll {
  display: flex;
  flex: 0 0 auto;
  flex-direction: column;
  min-height: 0;
  overflow: visible;
  padding: 34px 8px 36px;
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
  max-width: 860px;
  width: min(100%, 860px);
}

.allegati-work-panel {
  align-self: center;
  flex: 0 0 auto;
  max-width: 920px;
  width: min(100%, 920px);
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

.allegati-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.allegati-list {
  border: 1px solid rgba(var(--v-theme-on-surface), 0.12);
  border-radius: 8px;
}

.allegati-eliminati-panel {
  border: 1px solid rgba(var(--v-theme-warning), 0.22);
  border-radius: 8px;
  overflow: hidden;
}

.allegati-eliminati-title {
  align-items: center;
  display: flex;
  gap: 16px;
  justify-content: space-between;
  width: 100%;
}

.allegati-eliminati-list {
  border: 1px dashed rgba(var(--v-theme-warning), 0.34);
  border-radius: 8px;
}

.allegato-eliminato-item {
  background: rgba(var(--v-theme-warning), 0.045);
}

.allegato-eliminato-item + .allegato-eliminato-item {
  border-top: 1px solid rgba(var(--v-theme-warning), 0.16);
}

.allegato-audit-info {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.allegato-item + .allegato-item {
  border-top: 1px solid rgba(var(--v-theme-on-surface), 0.08);
}

.allegato-item-actions {
  align-items: center;
  display: flex;
  gap: 6px;
}

.redigi-document-card {
  background: rgba(var(--v-theme-primary), 0.045);
}

.workflow-documentale-card {
  background: rgba(var(--v-theme-primary), 0.045);
}

.workflow-documentale-title {
  align-items: center;
  display: flex;
  gap: 16px;
  justify-content: space-between;
}

.workflow-panel-avatar-img {
  height: 34px;
  object-fit: contain;
  width: 34px;
}

.workflow-documentale-body {
  display: grid;
  gap: 16px;
}

.workflow-documentale-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
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
    overflow: visible;
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
    padding: 10px 18px;
  }

  .lavorazione-content-card {
    margin-top: 18px;
    padding: 28px 16px;
  }

  .step-operativo-scroll {
    flex: 0 0 auto;
    overflow: visible;
    padding: 22px 2px 16px;
  }

  .stepper-orizzontale {
    gap: 18px;
    max-width: 420px;
  }

  .step-orizzontale-item {
    flex-basis: 100%;
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
