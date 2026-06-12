<template>
  <v-card rounded="lg" variant="outlined" class="sottofase-documentale-card">
    <v-card-title class="d-flex flex-wrap align-center justify-space-between ga-3">
      <span class="text-subtitle-1 font-weight-bold">
        Stato documentale
      </span>

      <v-chip
        :color="documentoPresente ? 'green' : 'grey'"
        variant="tonal"
        size="small"
      >
        Documento {{ documentoPresente ? 'presente' : 'assente' }}
      </v-chip>
    </v-card-title>

    <v-divider />

    <v-card-text>
      <v-skeleton-loader
        v-if="loading"
        type="article, list-item-two-line, actions"
      />

      <v-alert
        v-else-if="errore"
        type="warning"
        variant="tonal"
        density="compact"
      >
        {{ errore }}
      </v-alert>

      <template v-else-if="quadro">
        <v-row dense>
          <v-col cols="12" sm="6" lg="3">
            <div class="label-documentale">Documento collegato</div>
            <v-chip
              :color="documentoPresente ? 'green' : 'grey'"
              variant="flat"
              size="small"
            >
              {{ documentoPresente ? 'Presente' : 'Assente' }}
            </v-chip>
          </v-col>

          <v-col cols="12" sm="6" lg="3">
            <div class="label-documentale">Versione</div>
            <div class="value-documentale">
              {{ versioneCorrente }}
            </div>
          </v-col>

          <v-col cols="12" sm="6" lg="3">
            <div class="label-documentale">Ultima azione</div>
            <div class="value-documentale">
              {{ formattaDataOra(quadro.dataUltimaAzione) }}
            </div>
          </v-col>

          <v-col cols="12" sm="6" lg="3">
            <div class="label-documentale">Operatore</div>
            <div class="value-documentale">
              {{ quadro.utenteUltimaAzione || '-' }}
            </div>
          </v-col>

          <v-col cols="12" sm="6" lg="3">
            <div class="label-documentale">Step corrente</div>
            <v-chip color="primary" variant="tonal" size="small">
              {{ labelStep(quadro.stepCorrente) }}
            </v-chip>
          </v-col>

          <v-col cols="12">
            <v-textarea
              :model-value="quadro.testoOperatore || 'Nessun testo operatore registrato.'"
              label="Testo operatore"
              readonly
              auto-grow
              rows="2"
              density="compact"
              variant="outlined"
              hide-details
            />
          </v-col>
        </v-row>

        <v-divider class="my-4" />

        <section>
          <div class="text-subtitle-2 font-weight-bold mb-3">
            Documento corrente
          </div>

          <v-card
            v-if="quadro.documentoCorrente"
            rounded="lg"
            variant="tonal"
            class="documento-corrente-card"
          >
            <v-card-text>
              <div class="d-flex flex-wrap align-center justify-space-between ga-3">
                <div class="d-flex align-center ga-3">
                  <v-avatar color="blue" variant="tonal" size="42">
                    <v-icon color="blue">
                      {{ iconaDocumento(quadro.documentoCorrente) }}
                    </v-icon>
                  </v-avatar>

                  <div>
                    <div class="font-weight-bold">
                      {{ quadro.documentoCorrente.nomeFile || 'Documento senza nome' }}
                    </div>
                    <div class="text-caption text-medium-emphasis">
                      {{ formattaVersione(quadro.documentoCorrente.versioneDocumento) }}
                      · Collegato il {{ formattaDataOra(quadro.documentoCorrente.dataCollegamento) }}
                    </div>
                  </div>
                </div>

                <div class="azioni-documento">
                  <v-tooltip
                    location="top"
                    :text="tooltipAperturaDocumento(quadro.documentoCorrente)"
                  >
                    <template #activator="{ props: tooltipProps }">
                      <span v-bind="tooltipProps" class="azione-documento-wrapper">
                        <v-btn
                          color="primary"
                          variant="tonal"
                          size="small"
                          prepend-icon="mdi-open-in-new"
                          :disabled="azioneDocumentoInCorso"
                          :loading="aperturaInCorsoId === quadro.documentoCorrente.idDocumentoSottofase"
                          @click="apriDocumento(quadro.documentoCorrente)"
                        >
                          Apri
                        </v-btn>
                      </span>
                    </template>
                  </v-tooltip>

                  <v-tooltip
                    location="top"
                    :text="tooltipScaricaDocumento(quadro.documentoCorrente)"
                  >
                    <template #activator="{ props: tooltipProps }">
                      <span v-bind="tooltipProps" class="azione-documento-wrapper">
                        <v-btn
                          color="primary"
                          variant="outlined"
                          size="small"
                          prepend-icon="mdi-download-outline"
                          :disabled="azioneDocumentoInCorso"
                          :loading="downloadInCorsoId === quadro.documentoCorrente.idDocumentoSottofase"
                          @click="scaricaDocumento(quadro.documentoCorrente)"
                        >
                          Scarica
                        </v-btn>
                      </span>
                    </template>
                  </v-tooltip>

                  <v-tooltip
                    v-if="isDocumentoWord(quadro.documentoCorrente)"
                    location="top"
                    :text="tooltipApriConWord(quadro.documentoCorrente)"
                  >
                    <template #activator="{ props: tooltipProps }">
                      <span v-bind="tooltipProps" class="azione-documento-wrapper">
                        <v-btn
                          color="indigo"
                          variant="text"
                          size="small"
                          prepend-icon="mdi-microsoft-word"
                          :disabled="azioneDocumentoInCorso"
                          :loading="wordInCorsoId === quadro.documentoCorrente.idDocumentoSottofase"
                          @click="apriConWord(quadro.documentoCorrente)"
                        >
                          Apri con Word
                        </v-btn>
                      </span>
                    </template>
                  </v-tooltip>
                </div>
              </div>
            </v-card-text>
          </v-card>

          <v-alert
            v-else
            type="info"
            variant="tonal"
            density="compact"
          >
            Nessun documento corrente collegato a questa sottofase.
          </v-alert>

          <v-alert
            v-if="erroreApertura"
            type="warning"
            variant="tonal"
            density="compact"
            class="mt-3"
          >
            {{ erroreApertura }}
          </v-alert>

          <v-alert
            v-if="messaggioAzioneDocumento"
            type="success"
            variant="tonal"
            density="compact"
            class="mt-3"
          >
            {{ messaggioAzioneDocumento }}
          </v-alert>
        </section>

        <v-divider class="my-4" />

        <section>
          <div class="text-subtitle-2 font-weight-bold mb-3">
            Storico documenti
          </div>

          <v-list
            v-if="quadro.documenti.length"
            density="compact"
            lines="two"
            class="lista-documenti"
          >
            <v-list-item
              v-for="documento in quadro.documenti"
              :key="documento.idDocumentoSottofase"
            >
              <template #prepend>
                <v-icon color="blue">
                  {{ iconaDocumento(documento) }}
                </v-icon>
              </template>

              <v-list-item-title>
                {{ formattaVersione(documento.versioneDocumento) }}
                {{ documento.nomeFile || 'Documento senza nome' }}
              </v-list-item-title>

              <v-list-item-subtitle>
                {{ documento.tipoDocumento || 'Documento' }}
                · {{ formattaDataOra(documento.dataCollegamento) }}
              </v-list-item-subtitle>

              <template #append>
                <div class="azioni-documento">
                  <v-tooltip
                    location="top"
                    :text="tooltipAperturaDocumento(documento)"
                  >
                    <template #activator="{ props: tooltipProps }">
                      <span v-bind="tooltipProps" class="azione-documento-wrapper">
                        <v-btn
                          color="primary"
                          variant="text"
                          size="small"
                          prepend-icon="mdi-open-in-new"
                          :disabled="azioneDocumentoInCorso"
                          :loading="aperturaInCorsoId === documento.idDocumentoSottofase"
                          @click="apriDocumento(documento)"
                        >
                          Apri
                        </v-btn>
                      </span>
                    </template>
                  </v-tooltip>

                  <v-tooltip
                    location="top"
                    :text="tooltipScaricaDocumento(documento)"
                  >
                    <template #activator="{ props: tooltipProps }">
                      <span v-bind="tooltipProps" class="azione-documento-wrapper">
                        <v-btn
                          color="primary"
                          variant="text"
                          size="small"
                          prepend-icon="mdi-download-outline"
                          :disabled="azioneDocumentoInCorso"
                          :loading="downloadInCorsoId === documento.idDocumentoSottofase"
                          @click="scaricaDocumento(documento)"
                        >
                          Scarica
                        </v-btn>
                      </span>
                    </template>
                  </v-tooltip>

                  <v-tooltip
                    v-if="isDocumentoWord(documento)"
                    location="top"
                    :text="tooltipApriConWord(documento)"
                  >
                    <template #activator="{ props: tooltipProps }">
                      <span v-bind="tooltipProps" class="azione-documento-wrapper">
                        <v-btn
                          color="indigo"
                          variant="text"
                          size="small"
                          prepend-icon="mdi-microsoft-word"
                          :disabled="azioneDocumentoInCorso"
                          :loading="wordInCorsoId === documento.idDocumentoSottofase"
                          @click="apriConWord(documento)"
                        >
                          Apri con Word
                        </v-btn>
                      </span>
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
            density="compact"
          >
            Nessuno storico documentale registrato.
          </v-alert>
        </section>

        <v-divider class="my-4" />

        <section v-if="quadro.assegnazioniAutoReport">
          <SottofaseAssegnazioniReport
            :report="quadro.assegnazioniAutoReport"
          />
        </section>

        <v-divider
          v-if="quadro.assegnazioniAutoReport"
          class="my-4"
        />

        <section>
          <div class="text-subtitle-2 font-weight-bold mb-3">
            Step operativi
          </div>

          <v-alert
            v-if="messaggioPartecipanti"
            type="success"
            variant="tonal"
            density="compact"
            class="mb-3"
          >
            {{ messaggioPartecipanti }}
          </v-alert>

          <v-alert
            v-if="errorePartecipanti"
            type="warning"
            variant="tonal"
            density="compact"
            class="mb-3"
          >
            {{ errorePartecipanti }}
          </v-alert>

          <SottofaseTimelineOperativa
            :steps="quadro.stepOperativi"
            :partecipanti-per-step="partecipantiPerStep"
            :loading-partecipanti="loadingPartecipanti"
            :completamento-partecipante-in-corso="completamentoPartecipanteInCorso"
            @completa-partecipante="completaPartecipante"
          />
        </section>
      </template>

      <v-alert
        v-else
        type="info"
        variant="tonal"
        density="compact"
      >
        Seleziona una sottofase per leggere lo stato documentale.
      </v-alert>
    </v-card-text>
  </v-card>
</template>

<script setup>
import { computed, ref, watch } from 'vue'

import {
  apriDocumentoSottofase,
  apriDocumentoConWord,
  completaPartecipanteStepSottofase,
  getSottofaseDocumentale,
  listPartecipantiStepSottofase,
  scaricaDocumentoSottofase
} from '../../services/procedimentoApi'
import SottofaseAssegnazioniReport from './SottofaseAssegnazioniReport.vue'
import SottofaseTimelineOperativa from './SottofaseTimelineOperativa.vue'

const props = defineProps({
  idSottofase: {
    type: [Number, String],
    default: null
  }
})

const loading = ref(false)
const errore = ref('')
const quadro = ref(null)
const erroreApertura = ref('')
const messaggioAzioneDocumento = ref('')
const aperturaInCorsoId = ref(null)
const downloadInCorsoId = ref(null)
const wordInCorsoId = ref(null)
const partecipantiPerStep = ref({})
const loadingPartecipanti = ref(false)
const errorePartecipanti = ref('')
const messaggioPartecipanti = ref('')
const completamentoPartecipanteInCorso = ref(null)

const documentoPresente = computed(() => {
  return Boolean(
    quadro.value?.haDocumentoCollegato ||
    quadro.value?.documentoCorrente ||
    quadro.value?.documenti?.length
  )
})

const versioneCorrente = computed(() => {
  return formattaVersione(
    quadro.value?.versioneDocumento ??
    quadro.value?.documentoCorrente?.versioneDocumento
  )
})

const azioneDocumentoInCorso = computed(() => {
  return aperturaInCorsoId.value !== null ||
    downloadInCorsoId.value !== null ||
    wordInCorsoId.value !== null
})

watch(
  () => props.idSottofase,
  () => {
    caricaSottofaseDocumentale()
  },
  { immediate: true }
)

async function caricaSottofaseDocumentale() {
  erroreApertura.value = ''
  messaggioAzioneDocumento.value = ''
  errorePartecipanti.value = ''
  messaggioPartecipanti.value = ''

  if (!props.idSottofase) {
    quadro.value = null
    errore.value = ''
    partecipantiPerStep.value = {}
    return
  }

  loading.value = true
  errore.value = ''

  try {
    const response = await getSottofaseDocumentale(props.idSottofase)
    quadro.value = normalizzaQuadroDocumentale(response)
    await caricaPartecipantiStepOperativi()
  } catch (error) {
    quadro.value = null
    partecipantiPerStep.value = {}
    errore.value =
      error.status === 404
        ? 'Sottofase non trovata.'
        : 'Impossibile caricare lo stato documentale della sottofase.'
  } finally {
    loading.value = false
  }
}

function normalizzaQuadroDocumentale(dato = {}) {
  return {
    idSottofase: pick(dato, 'id_sottofase', 'IDSottofase', 'idSottofase'),
    titolo: pick(dato, 'titolo', 'Titolo') || 'Sottofase',
    stepCorrente: pick(dato, 'step_corrente', 'StepCorrente', 'stepCorrente'),
    testoOperatore: pick(
      dato,
      'testo_operatore',
      'TestoOperatore',
      'testoOperatore'
    ),
    haDocumentoCollegato: normalizzaBoolean(
      pick(
        dato,
        'ha_documento_collegato',
        'HaDocumentoCollegato',
        'haDocumentoCollegato'
      )
    ),
    idDocumentoCorrente: pick(
      dato,
      'id_documento_corrente',
      'IDDocumentoCorrente',
      'idDocumentoCorrente'
    ),
    dataUltimaAzione: pick(
      dato,
      'data_ultima_azione',
      'DataUltimaAzione',
      'dataUltimaAzione'
    ),
    utenteUltimaAzione: pick(
      dato,
      'utente_ultima_azione',
      'UtenteUltimaAzione',
      'utenteUltimaAzione'
    ),
    versioneDocumento: pick(
      dato,
      'versione_documento',
      'VersioneDocumento',
      'versioneDocumento'
    ),
    documentoCorrente: normalizzaDocumento(
      pick(dato, 'documento_corrente', 'documentoCorrente', 'DocumentoCorrente')
    ),
    documenti: normalizzaLista(
      pick(dato, 'documenti', 'Documenti')
    )
      .map(normalizzaDocumento)
      .filter(Boolean)
      .sort(confrontaVersioneDiscendente),
    stepOperativi: normalizzaLista(
      pick(dato, 'step_operativi', 'stepOperativi', 'StepOperativi')
    )
      .map(normalizzaStepOperativo)
      .filter(Boolean)
      .sort(confrontaOrdine),
    assegnazioniAutoReport: pick(
      dato,
      'assegnazioni_auto_report',
      'assegnazioniAutoReport',
      'AssegnazioniAutoReport'
    )
  }
}

function normalizzaDocumento(dato) {
  if (!dato) return null

  return {
    idDocumentoSottofase: pick(
      dato,
      'id_documento_sottofase',
      'IDDocumentoSottofase',
      'idDocumentoSottofase'
    ),
    tipoDocumento: pick(dato, 'tipo_documento', 'TipoDocumento', 'tipoDocumento'),
    nomeFile: pick(dato, 'nome_file', 'NomeFile', 'nomeFile'),
    estensione: pick(dato, 'estensione', 'Estensione'),
    mimeType: pick(dato, 'mime_type', 'MimeType', 'mimeType'),
    percorsoDocumento: pick(
      dato,
      'percorso_documento',
      'PercorsoDocumento',
      'percorsoDocumento'
    ),
    versioneDocumento: pick(
      dato,
      'versione_documento',
      'VersioneDocumento',
      'versioneDocumento'
    ),
    dataCollegamento: pick(
      dato,
      'data_collegamento',
      'DataCollegamento',
      'dataCollegamento'
    )
  }
}

function normalizzaStepOperativo(dato) {
  if (!dato) return null

  return {
    idStepSottofase: pick(
      dato,
      'id_step_sottofase',
      'IDStepSottofase',
      'idStepSottofase'
    ),
    codiceStep: pick(dato, 'codice_step', 'CodiceStep', 'codiceStep'),
    ordine: pick(dato, 'ordine', 'Ordine') ?? 0,
    statoStep: pick(dato, 'stato_step', 'StatoStep', 'statoStep'),
    dataCompletamento: pick(
      dato,
      'data_completamento',
      'DataCompletamento',
      'dataCompletamento'
    ),
    utenteAssegnato: pick(
      dato,
      'utente_assegnato',
      'UtenteAssegnato',
      'utenteAssegnato'
    )
  }
}

function normalizzaPartecipante(dato) {
  if (!dato) return null

  return {
    idPartecipante: pick(
      dato,
      'id_partecipante',
      'IDPartecipante',
      'idPartecipante'
    ),
    idSottofase: pick(dato, 'id_sottofase', 'IDSottofase', 'idSottofase'),
    idStepOperativo: pick(
      dato,
      'id_step_operativo',
      'IDStepOperativo',
      'idStepOperativo'
    ),
    nomeVisualizzato: pick(
      dato,
      'nome_visualizzato',
      'NomeVisualizzato',
      'nomeVisualizzato'
    ),
    email: pick(dato, 'email', 'Email'),
    ruolo: pick(dato, 'ruolo', 'Ruolo'),
    statoPartecipante: pick(
      dato,
      'stato_partecipante',
      'StatoPartecipante',
      'statoPartecipante'
    ),
    partecipanteObbligatorio: normalizzaBoolean(
      pick(
        dato,
        'partecipante_obbligatorio',
        'PartecipanteObbligatorio',
        'partecipanteObbligatorio'
      ) ?? true
    ),
    ordine: pick(dato, 'ordine', 'Ordine') ?? 0,
    coloreAvatar: pick(dato, 'colore_avatar', 'ColoreAvatar', 'coloreAvatar'),
    iniziali: pick(dato, 'iniziali', 'Iniziali'),
    dataAzione: pick(dato, 'data_azione', 'DataAzione', 'dataAzione'),
    notePartecipante: pick(
      dato,
      'note_partecipante',
      'NotePartecipante',
      'notePartecipante'
    )
  }
}

async function caricaPartecipantiStepOperativi() {
  const steps = quadro.value?.stepOperativi || []
  const idSottofase = props.idSottofase
  partecipantiPerStep.value = {}

  if (!idSottofase || !steps.length) return

  loadingPartecipanti.value = true
  errorePartecipanti.value = ''

  try {
    const entries = await Promise.all(
      steps.map(async (step) => {
        if (!step.idStepSottofase) return [null, []]

        const response = await listPartecipantiStepSottofase(
          idSottofase,
          step.idStepSottofase
        )
        const partecipanti = normalizzaLista(response)
          .map(normalizzaPartecipante)
          .filter(Boolean)
          .sort(confrontaOrdine)

        return [step.idStepSottofase, partecipanti]
      })
    )

    partecipantiPerStep.value = Object.fromEntries(
      entries.filter(([idStep]) => idStep !== null)
    )
  } catch {
    errorePartecipanti.value =
      'Impossibile caricare i partecipanti collegati agli step.'
  } finally {
    loadingPartecipanti.value = false
  }
}

async function completaPartecipante(step, partecipante) {
  const idStep = step?.idStepSottofase
  const idPartecipante = partecipante?.idPartecipante

  if (!props.idSottofase || !idStep || !idPartecipante) {
    errorePartecipanti.value =
      'Partecipante non completabile: identificativi mancanti.'
    return
  }

  errorePartecipanti.value = ''
  messaggioPartecipanti.value = ''
  completamentoPartecipanteInCorso.value = idPartecipante

  try {
    const response = await completaPartecipanteStepSottofase(
      props.idSottofase,
      idStep,
      idPartecipante
    )
    aggiornaPartecipanteStep(idStep, idPartecipante, response?.partecipante)

    if (response?.step_completato || response?.stepCompletato) {
      step.statoStep = 'COMPLETATO'
      step.dataCompletamento = step.dataCompletamento || new Date().toISOString()
      messaggioPartecipanti.value =
        'Partecipante completato e step chiuso automaticamente.'
    } else {
      messaggioPartecipanti.value = 'Partecipante completato.'
    }
  } catch (error) {
    errorePartecipanti.value = messaggioErroreCompletaPartecipante(error)
  } finally {
    completamentoPartecipanteInCorso.value = null
  }
}

function aggiornaPartecipanteStep(idStep, idPartecipante, datoPartecipante) {
  const partecipanti = partecipantiPerStep.value[idStep] || []
  const index = partecipanti.findIndex(
    (item) => String(item.idPartecipante) === String(idPartecipante)
  )
  const aggiornato = normalizzaPartecipante(datoPartecipante) || {
    ...partecipanti[index],
    statoPartecipante: 'COMPLETATO',
    dataAzione: new Date().toISOString()
  }

  if (index === -1) return

  partecipantiPerStep.value = {
    ...partecipantiPerStep.value,
    [idStep]: [
      ...partecipanti.slice(0, index),
      aggiornato,
      ...partecipanti.slice(index + 1)
    ]
  }
}

function pick(source, ...keys) {
  if (!source) return null

  for (const key of keys) {
    if (source[key] !== undefined && source[key] !== null) {
      return source[key]
    }
  }

  return null
}

function normalizzaLista(value) {
  return Array.isArray(value) ? value : []
}

function normalizzaBoolean(value) {
  return value === true || value === 1 || value === '1' || value === 'true' || value === 'True'
}

function confrontaOrdine(a, b) {
  return Number(a?.ordine ?? 0) - Number(b?.ordine ?? 0)
}

function confrontaVersioneDiscendente(a, b) {
  return Number(b?.versioneDocumento ?? 0) - Number(a?.versioneDocumento ?? 0)
}

function formattaVersione(value) {
  if (value === null || value === undefined || value === '') return '-'

  const number = Number(value)

  if (Number.isFinite(number)) {
    return `V${String(number).padStart(3, '0')}`
  }

  return String(value)
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

function iconaDocumento(documento) {
  if (isDocumentoWord(documento)) return 'mdi-file-word-outline'
  if (isDocumentoPdf(documento)) return 'mdi-file-pdf-box'

  return 'mdi-file-document-outline'
}

function tooltipAperturaDocumento(documento) {
  if (!documento?.idDocumentoSottofase) {
    return 'Documento non disponibile.'
  }

  if (azioneDocumentoInCorso.value) {
    return 'Operazione documento in corso.'
  }

  if (isDocumentoWord(documento)) {
    return 'Apre il documento Word nel browser o nel visualizzatore associato.'
  }

  if (isDocumentoPdf(documento)) {
    return 'Visualizza il PDF in una nuova scheda.'
  }

  return 'Apre il documento in una nuova scheda.'
}

function tooltipScaricaDocumento(documento) {
  if (!documento?.idDocumentoSottofase) {
    return 'Documento non disponibile.'
  }

  if (azioneDocumentoInCorso.value) {
    return 'Operazione documento in corso.'
  }

  return 'Scarica una copia del file.'
}

function tooltipApriConWord(documento) {
  if (!documento?.idDocumentoSottofase) {
    return 'Documento non disponibile.'
  }

  if (azioneDocumentoInCorso.value) {
    return 'Operazione documento in corso.'
  }

  return 'Apre il documento con Word tramite helper locale Windows.'
}

function isDocumentoWord(documento) {
  const type = documentoTypeSignature(documento)

  return type.includes('.docx') ||
    type.includes('word') ||
    type.includes('officedocument.wordprocessingml')
}

function isDocumentoPdf(documento) {
  return documentoTypeSignature(documento).includes('pdf')
}

function documentoTypeSignature(documento) {
  return [
    documento?.estensione,
    documento?.nomeFile,
    documento?.tipoDocumento,
    documento?.mimeType
  ]
    .filter(Boolean)
    .join(' ')
    .toLowerCase()
}

async function apriDocumento(documento) {
  erroreApertura.value = ''
  messaggioAzioneDocumento.value = ''

  const idDocumento = documento?.idDocumentoSottofase

  if (!idDocumento) {
    erroreApertura.value = 'Documento non apribile: identificativo mancante.'
    return
  }

  const openedWindow = window.open('', '_blank')

  if (!openedWindow) {
    erroreApertura.value =
      'Il browser ha bloccato l apertura del documento in una nuova scheda.'
    return
  }

  openedWindow.opener = null
  aperturaInCorsoId.value = idDocumento

  try {
    const blob = await apriDocumentoSottofase(idDocumento)
    const blobUrl = URL.createObjectURL(blob)
    openedWindow.location.href = blobUrl

    setTimeout(() => {
      URL.revokeObjectURL(blobUrl)
    }, 60000)
  } catch (error) {
    if (error.status === 404) {
      erroreApertura.value =
        'Documento non disponibile o file fisico non trovato.'
    } else if (error.status === 500) {
      erroreApertura.value =
        'Errore tecnico durante l apertura del documento.'
    } else {
      erroreApertura.value =
        'Impossibile aprire il documento collegato alla sottofase.'
    }

    try {
      openedWindow.close()
    } catch {
      // La scheda e stata aperta solo per rispettare il gesto utente.
    }
  } finally {
    aperturaInCorsoId.value = null
  }
}

async function scaricaDocumento(documento) {
  erroreApertura.value = ''
  messaggioAzioneDocumento.value = ''

  const idDocumento = documento?.idDocumentoSottofase

  if (!idDocumento) {
    erroreApertura.value = 'Documento non scaricabile: identificativo mancante.'
    return
  }

  downloadInCorsoId.value = idDocumento

  try {
    const blob = await scaricaDocumentoSottofase(idDocumento)
    const blobUrl = URL.createObjectURL(blob)
    const link = document.createElement('a')

    link.href = blobUrl
    link.download = documento?.nomeFile || `documento-${idDocumento}`
    link.style.display = 'none'
    document.body.appendChild(link)
    link.click()
    link.remove()

    setTimeout(() => {
      URL.revokeObjectURL(blobUrl)
    }, 60000)
  } catch (error) {
    if (error.status === 404) {
      erroreApertura.value =
        'Documento non disponibile o file fisico non trovato.'
    } else if (error.status === 500) {
      erroreApertura.value =
        'Errore tecnico durante il download del documento.'
    } else {
      erroreApertura.value =
        'Impossibile scaricare il documento collegato alla sottofase.'
    }
  } finally {
    downloadInCorsoId.value = null
  }
}

async function apriConWord(documento) {
  erroreApertura.value = ''
  messaggioAzioneDocumento.value = ''

  const idDocumento = documento?.idDocumentoSottofase

  if (!idDocumento) {
    erroreApertura.value =
      'Documento non apribile con Word: identificativo mancante.'
    return
  }

  wordInCorsoId.value = idDocumento

  try {
    await apriDocumentoConWord(idDocumento)
    messaggioAzioneDocumento.value = 'Apertura con Word avviata.'
  } catch (error) {
    erroreApertura.value = messaggioErroreApriConWord(error)
  } finally {
    wordInCorsoId.value = null
  }
}

function messaggioErroreApriConWord(error) {
  const dettaglio = error?.payload?.error || error?.payload?.detail

  if (error?.status === 0) {
    return 'Helper locale Word non avviato: avvia open_word_helper.py e riprova.'
  }

  if (error?.status === 400) {
    return dettaglio || 'Documento non valido per apertura con Word.'
  }

  if (error?.status === 403) {
    return dettaglio || 'Documento fuori dalla cartella autorizzata.'
  }

  if (error?.status === 404) {
    return dettaglio || 'Documento Word non disponibile o file fisico mancante.'
  }

  if (error?.status === 500) {
    return dettaglio || 'Errore tecnico nel helper locale Word.'
  }

  return 'Impossibile aprire il documento con Word.'
}

function messaggioErroreCompletaPartecipante(error) {
  const dettaglio = error?.payload?.detail || error?.payload?.error

  if (error?.status === 400) {
    return dettaglio || 'Partecipante gia completato o non completabile.'
  }

  if (error?.status === 404) {
    return dettaglio || 'Partecipante non coerente con lo step selezionato.'
  }

  if (error?.status >= 500) {
    return dettaglio || 'Errore backend durante il completamento partecipante.'
  }

  return 'Impossibile completare il partecipante.'
}
</script>

<style scoped>
.sottofase-documentale-card {
  background: #ffffff;
}

.label-documentale {
  color: #6b7280;
  font-size: 0.74rem;
  margin-bottom: 4px;
}

.value-documentale {
  font-size: 0.92rem;
  font-weight: 700;
}

.documento-corrente-card {
  border: 1px solid rgba(25, 118, 210, 0.16);
}

.lista-documenti {
  border: 1px solid rgba(0, 0, 0, 0.06);
  border-radius: 8px;
}

.azione-documento-wrapper {
  display: inline-flex;
}

.azioni-documento {
  align-items: center;
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  justify-content: flex-end;
}

</style>
