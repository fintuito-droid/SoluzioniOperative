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

                <v-btn
                  color="primary"
                  variant="tonal"
                  size="small"
                  prepend-icon="mdi-eye-outline"
                  :loading="aperturaInCorsoId === quadro.documentoCorrente.idDocumentoSottofase"
                  @click="apriDocumento(quadro.documentoCorrente)"
                >
                  Visualizza
                </v-btn>
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
                <v-btn
                  color="primary"
                  variant="text"
                  size="small"
                  prepend-icon="mdi-open-in-new"
                  :loading="aperturaInCorsoId === documento.idDocumentoSottofase"
                  @click="apriDocumento(documento)"
                >
                  Apri
                </v-btn>
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

        <section>
          <div class="text-subtitle-2 font-weight-bold mb-3">
            Step operativi
          </div>

          <div
            v-if="quadro.stepOperativi.length"
            class="step-operativi-list"
          >
            <div
              v-for="step in quadro.stepOperativi"
              :key="step.idStepSottofase || step.codiceStep"
              class="step-operativo-row"
            >
              <v-avatar
                :color="coloreStep(step.statoStep)"
                size="28"
              >
                <v-icon color="white" size="18">
                  {{ iconaStep(step.statoStep) }}
                </v-icon>
              </v-avatar>

              <div class="step-operativo-text">
                <div class="font-weight-bold">
                  {{ labelStep(step.codiceStep) }}
                </div>
                <div class="text-caption text-medium-emphasis">
                  {{ labelStatoStep(step.statoStep) }}
                  <span v-if="step.utenteAssegnato">
                    · {{ step.utenteAssegnato }}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <v-alert
            v-else
            type="info"
            variant="tonal"
            density="compact"
          >
            Nessuno step operativo documentale registrato.
          </v-alert>
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
  getSottofaseDocumentale
} from '../../services/procedimentoApi'

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
const aperturaInCorsoId = ref(null)

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

watch(
  () => props.idSottofase,
  () => {
    caricaSottofaseDocumentale()
  },
  { immediate: true }
)

async function caricaSottofaseDocumentale() {
  erroreApertura.value = ''

  if (!props.idSottofase) {
    quadro.value = null
    errore.value = ''
    return
  }

  loading.value = true
  errore.value = ''

  try {
    const response = await getSottofaseDocumentale(props.idSottofase)
    quadro.value = normalizzaQuadroDocumentale(response)
  } catch (error) {
    quadro.value = null
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
      .sort(confrontaOrdine)
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
    utenteAssegnato: pick(
      dato,
      'utente_assegnato',
      'UtenteAssegnato',
      'utenteAssegnato'
    )
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

  return `v${value}`
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

function labelStatoStep(value) {
  const labels = {
    NON_AVVIATO: 'Non avviato',
    IN_CORSO: 'In corso',
    COMPLETATO: 'Completato',
    BLOCCATO: 'Bloccato'
  }

  return labels[value] || value || 'Non definito'
}

function coloreStep(value) {
  switch (value) {
    case 'COMPLETATO':
      return 'green'
    case 'IN_CORSO':
      return 'blue'
    case 'BLOCCATO':
      return 'red'
    default:
      return 'grey'
  }
}

function iconaStep(value) {
  switch (value) {
    case 'COMPLETATO':
      return 'mdi-check'
    case 'IN_CORSO':
      return 'mdi-progress-clock'
    case 'BLOCCATO':
      return 'mdi-lock-outline'
    default:
      return 'mdi-circle-outline'
  }
}

function iconaDocumento(documento) {
  const estensione = String(documento?.estensione || '').toLowerCase()

  if (estensione.includes('doc')) return 'mdi-file-word-outline'
  if (estensione.includes('pdf')) return 'mdi-file-pdf-box'

  return 'mdi-file-document-outline'
}

async function apriDocumento(documento) {
  erroreApertura.value = ''

  const idDocumento = documento?.idDocumentoSottofase

  if (!idDocumento) {
    erroreApertura.value = 'Documento non apribile: identificativo mancante.'
    return
  }

  aperturaInCorsoId.value = idDocumento

  try {
    const blob = await apriDocumentoSottofase(idDocumento)
    const blobUrl = URL.createObjectURL(blob)
    const openedWindow = window.open(blobUrl, '_blank')

    if (!openedWindow) {
      URL.revokeObjectURL(blobUrl)
      erroreApertura.value =
        'Il browser ha bloccato l apertura del documento in una nuova scheda.'
      return
    }

    openedWindow.opener = null

    setTimeout(() => {
      URL.revokeObjectURL(blobUrl)
    }, 60000)
  } catch (error) {
    if (error.status === 404) {
      erroreApertura.value =
        'Documento non disponibile o file fisico non trovato.'
    } else {
      erroreApertura.value =
        'Impossibile aprire il documento collegato alla sottofase.'
    }
  } finally {
    aperturaInCorsoId.value = null
  }
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

.step-operativi-list {
  display: grid;
  gap: 10px;
}

.step-operativo-row {
  align-items: center;
  border: 1px solid rgba(0, 0, 0, 0.07);
  border-radius: 8px;
  display: flex;
  gap: 12px;
  padding: 10px 12px;
}

.step-operativo-text {
  min-width: 0;
}
</style>
