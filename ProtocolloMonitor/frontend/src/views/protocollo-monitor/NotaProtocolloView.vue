<template>
  <v-container fluid class="pa-6">

    <v-card rounded="xl" elevation="2" class="pa-6 mb-5">
      <div class="d-flex justify-space-between align-center mb-4">
        <div>
          <div class="text-h5 font-weight-bold">
            Nota protocollata
          </div>
          <div class="text-caption text-medium-emphasis">
            Scheda sintetica della nota acquisita
          </div>
        </div>

        <v-btn
          color="primary"
          variant="tonal"
          prepend-icon="mdi-open-in-new"
          :disabled="!urlSorgente"
          @click="apriDocumentoOriginale"
        >
          Apri documento originale
        </v-btn>
      </div>

      <v-divider class="mb-5" />

      <v-row v-if="protocollo">
        <v-col cols="12" md="4">
          <div class="label">Numero protocollo</div>
          <div class="value">{{ protocollo.NumeroProtocollo }}</div>
        </v-col>

        <v-col cols="12" md="4">
          <div class="label">Data protocollo</div>
          <div class="value">{{ protocollo.DataProtocollo }}</div>
        </v-col>

        <v-col cols="12" md="4">
          <div class="label">Modalità</div>
          <div class="value">{{ protocollo.Modalita }}</div>
        </v-col>

        <v-col cols="12">
          <div class="label">Oggetto</div>
          <div class="oggetto">
            {{ protocollo.Oggetto }}
          </div>
        </v-col>

        <v-col cols="12" md="4">
          <div class="label">Da lavorare</div>
          <v-chip
            :color="protocollo.DaLavorare ? 'orange' : 'grey'"
            variant="tonal"
          >
            {{ protocollo.DaLavorare ? 'Sì' : 'No' }}
          </v-chip>
        </v-col>

        <v-col cols="12" md="4">
          <div class="label">Tipologia documento</div>
          <div class="value">{{ protocollo.TipologiaDocumento || '-' }}</div>
        </v-col>

        <v-col cols="12" md="4">
          <div class="label">Scadenza</div>
          <div class="value">{{ protocollo.dataScadenza || '-' }}</div>
        </v-col>

        <v-col cols="12">
          <div class="label">URL sorgente</div>
          <div class="url">
            {{ urlSorgente || 'Non disponibile' }}
          </div>
        </v-col>
      </v-row>

      <v-alert v-else type="info" variant="tonal">
        Caricamento della nota in corso...
      </v-alert>
    </v-card>

    <v-card rounded="xl" elevation="2" class="pa-4 mb-5">
      <v-card-title class="d-flex justify-space-between align-center">
        <span class="font-weight-bold">
          Procedimenti collegati
        </span>

        <v-btn
          color="primary"
          variant="flat"
          prepend-icon="mdi-link-variant-plus"
          :loading="procedimentiDisponibiliLoading"
          :disabled="!protocollo"
          @click="apriDialogCollegamento"
        >
          Collega a procedimento
        </v-btn>
      </v-card-title>

      <v-divider class="mb-4" />

      <v-alert
        v-if="procedimentiErrore"
        type="warning"
        variant="tonal"
        class="mb-4"
      >
        {{ procedimentiErrore }}
      </v-alert>

      <v-alert
        v-if="collegamentoMessaggio"
        type="success"
        variant="tonal"
        class="mb-4"
      >
        {{ collegamentoMessaggio }}
      </v-alert>

      <v-data-table
        :headers="procedimentiHeaders"
        :items="procedimentiCollegatiNormalizzati"
        :loading="procedimentiLoading"
        item-value="idProcedimento"
        density="compact"
        hover
      >
        <template #no-data>
          <div class="pa-6 text-medium-emphasis">
            Nessun procedimento collegato.
          </div>
        </template>

        <template #item.Stato="{ item }">
          <v-chip
            :color="coloreStatoProcedimento(item.Stato)"
            size="x-small"
            variant="tonal"
          >
            {{ item.Stato || 'Non definito' }}
          </v-chip>
        </template>

        <template #item.Priorita="{ item }">
          <v-chip
            :color="colorePrioritaProcedimento(item.Priorita)"
            size="x-small"
            variant="tonal"
          >
            {{ item.Priorita || 'Normale' }}
          </v-chip>
        </template>

        <template #item.Principale="{ item }">
          <v-chip
            :color="item.Principale ? 'green' : 'grey'"
            size="x-small"
            variant="tonal"
          >
            {{ item.Principale ? 'Si' : 'No' }}
          </v-chip>
        </template>
      </v-data-table>
    </v-card>

    <v-card rounded="xl" elevation="2" class="pa-4">
      <v-card-title class="d-flex justify-space-between align-center">
        <span class="font-weight-bold">
          Documento protocollato
        </span>

        <v-btn
          v-if="!metadataLoading && pdfDisponibile"
          color="deep-purple"
          variant="flat"
          prepend-icon="mdi-file-pdf-box"
          :loading="pdfLoading"
          @click="visualizzaPdf"
        >
          Visualizza PDF
        </v-btn>

        <v-chip
          v-else-if="!metadataLoading"
          color="grey"
          variant="tonal"
        >
          PDF non disponibile
        </v-chip>
      </v-card-title>

      <v-divider class="mb-4" />

      <v-alert
        v-if="metadataLoading"
        type="info"
        variant="tonal"
        class="mb-4"
      >
        Verifica disponibilita PDF in corso...
      </v-alert>

      <v-alert
        v-else-if="pdfErrore"
        type="warning"
        variant="tonal"
        class="mb-4"
      >
        {{ pdfErrore }}
      </v-alert>

      <iframe
        v-if="pdfViewerUrl"
        :src="pdfViewerUrl"
        width="100%"
        height="750"
        class="pdf-viewer"
      ></iframe>

      <v-alert
        v-else-if="protocollo && !metadataLoading && !pdfDisponibile"
        type="info"
        variant="tonal"
      >
        Il PDF non e disponibile o non e stato ancora acquisito.
      </v-alert>

      <v-alert
        v-else-if="protocollo && pdfDisponibile"
        type="info"
        variant="tonal"
      >
        PDF disponibile.
      </v-alert>

      <v-alert v-else type="info" variant="tonal">
        Caricamento informazioni documento in corso...
      </v-alert>
    </v-card>

    <v-dialog v-model="dialogCollegamento" max-width="760">
      <v-card rounded="xl">
        <v-card-title class="d-flex align-center justify-space-between">
          <span class="font-weight-bold">
            Collega a procedimento
          </span>

          <v-btn
            icon="mdi-close"
            variant="text"
            @click="chiudiDialogCollegamento"
          />
        </v-card-title>

        <v-divider />

        <v-card-text>
          <v-alert
            v-if="collegamentoErrore"
            type="warning"
            variant="tonal"
            class="mb-4"
          >
            {{ collegamentoErrore }}
          </v-alert>

          <v-row>
            <v-col cols="12">
              <v-autocomplete
                v-model="procedimentoSelezionatoId"
                :items="procedimentiSelezionabili"
                item-title="label"
                item-value="idProcedimento"
                label="Procedimento"
                variant="outlined"
                density="compact"
                clearable
                :loading="procedimentiDisponibiliLoading"
                :disabled="procedimentiDisponibiliLoading"
                no-data-text="Nessun procedimento disponibile"
              />
            </v-col>

            <v-col cols="12" md="6">
              <v-text-field
                v-model="formCollegamento.RuoloProtocollo"
                label="Ruolo protocollo"
                variant="outlined"
                density="compact"
              />
            </v-col>

            <v-col cols="12" md="6" class="d-flex align-center">
              <v-checkbox
                v-model="formCollegamento.Principale"
                label="Principale"
                density="compact"
                hide-details
              />
            </v-col>

            <v-col cols="12">
              <v-textarea
                v-model="formCollegamento.NoteCollegamento"
                label="Note collegamento"
                variant="outlined"
                density="compact"
                rows="3"
                auto-grow
                clearable
              />
            </v-col>
          </v-row>
        </v-card-text>

        <v-card-actions class="px-6 pb-5">
          <v-spacer />

          <v-btn
            variant="text"
            @click="chiudiDialogCollegamento"
          >
            Annulla
          </v-btn>

          <v-btn
            color="primary"
            variant="flat"
            :loading="collegamentoLoading"
            :disabled="!procedimentoSelezionatoId"
            @click="confermaCollegamento"
          >
            Collega
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

  </v-container>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, computed } from "vue"
import { useRoute } from "vue-router"

import {
  linkProtocolloToProcedimento,
  listProcedimenti,
  listProcedimentiByProtocollo
} from "../../services/procedimentoApi"

const route = useRoute()
const protocollo = ref(null)
const metadata = ref(null)
const metadataLoading = ref(false)
const pdfLoading = ref(false)
const pdfErrore = ref("")
const pdfViewerUrl = ref("")
const procedimentiCollegati = ref([])
const procedimentiDisponibili = ref([])
const procedimentiLoading = ref(false)
const procedimentiDisponibiliLoading = ref(false)
const procedimentiErrore = ref("")
const dialogCollegamento = ref(false)
const collegamentoLoading = ref(false)
const collegamentoErrore = ref("")
const collegamentoMessaggio = ref("")
const procedimentoSelezionatoId = ref(null)
const formCollegamento = ref({
  RuoloProtocollo: "COLLEGATO",
  Principale: false,
  NoteCollegamento: null
})

const urlSorgente = computed(() => {
  return protocollo.value?.UrlSorgente || ""
})

const urlPdf = computed(() => {
  return `http://127.0.0.1:8000/protocollo-monitor/protocolli/${route.params.idProtocollo}/pdf`
})

const pdfDisponibile = computed(() => {
  return metadata.value?.pdf_disponibile === true
})

const procedimentiHeaders = [
  { title: "Codice procedimento", key: "Codice" },
  { title: "Titolo", key: "Titolo" },
  { title: "Stato", key: "Stato" },
  { title: "Priorita", key: "Priorita" },
  { title: "Ruolo collegamento", key: "Ruolo" },
  { title: "Principale", key: "Principale" }
]

const procedimentiCollegatiNormalizzati = computed(() => {
  return procedimentiCollegati.value.map(normalizzaProcedimentoCollegato)
})

const procedimentiSelezionabili = computed(() => {
  const collegati = new Set(
    procedimentiCollegatiNormalizzati.value.map((item) => item.idProcedimento)
  )

  return procedimentiDisponibili.value
    .map(normalizzaProcedimentoDisponibile)
    .filter((item) => item.idProcedimento && !collegati.has(item.idProcedimento))
})

async function caricaProtocollo() {
  const idProtocollo = route.params.idProtocollo

  const response = await fetch(
    `http://127.0.0.1:8000/protocollo-monitor/protocolli/${idProtocollo}`
  )

  if (!response.ok) {
    console.error("Errore nel caricamento del protocollo")
    return
  }

  const dati = await response.json()
  protocollo.value = dati.protocollo
}

async function caricaProcedimentiCollegati() {
  const idProtocollo = route.params.idProtocollo
  procedimentiLoading.value = true
  procedimentiErrore.value = ""

  try {
    procedimentiCollegati.value = await listProcedimentiByProtocollo(idProtocollo)
  } catch (error) {
    if (error.status === 404) {
      procedimentiErrore.value = "Protocollo non trovato."
    } else {
      procedimentiErrore.value = "Impossibile caricare i procedimenti collegati."
    }

    procedimentiCollegati.value = []
  } finally {
    procedimentiLoading.value = false
  }
}

async function caricaProcedimentiDisponibili() {
  procedimentiDisponibiliLoading.value = true
  collegamentoErrore.value = ""

  try {
    procedimentiDisponibili.value = await listProcedimenti()
  } catch {
    collegamentoErrore.value = "Impossibile caricare l'elenco procedimenti."
    procedimentiDisponibili.value = []
  } finally {
    procedimentiDisponibiliLoading.value = false
  }
}

async function caricaMetadata() {
  const idProtocollo = route.params.idProtocollo
  metadataLoading.value = true
  pdfErrore.value = ""

  try {
    const response = await fetch(
      `http://127.0.0.1:8000/protocollo-monitor/protocolli/${idProtocollo}/metadata`
    )

    if (response.status === 404) {
      metadata.value = { pdf_disponibile: false }
      return
    }

    if (!response.ok) {
      throw new Error("Errore HTTP " + response.status)
    }

    metadata.value = await response.json()
  } catch (error) {
    console.error("Errore nel caricamento dei metadata:", error)
    metadata.value = { pdf_disponibile: false }
    pdfErrore.value = "Impossibile verificare la disponibilita del PDF."
  } finally {
    metadataLoading.value = false
  }
}

async function visualizzaPdf() {
  if (!pdfDisponibile.value) return

  pdfLoading.value = true
  pdfErrore.value = ""

  try {
    const response = await fetch(urlPdf.value)

    if (response.status === 404) {
      revocaPdfViewerUrl()
      pdfErrore.value = "Il PDF non e disponibile o non e stato ancora acquisito."
      metadata.value = {
        ...(metadata.value || {}),
        pdf_disponibile: false
      }
      return
    }

    if (!response.ok) {
      throw new Error("Errore HTTP " + response.status)
    }

    const pdfBlob = await response.blob()
    revocaPdfViewerUrl()
    pdfViewerUrl.value = URL.createObjectURL(pdfBlob)
  } catch (error) {
    console.error("Errore apertura PDF:", error)
    revocaPdfViewerUrl()
    pdfErrore.value = "Il PDF non e disponibile o non e stato ancora acquisito."
  } finally {
    pdfLoading.value = false
  }
}

function revocaPdfViewerUrl() {
  if (pdfViewerUrl.value) {
    URL.revokeObjectURL(pdfViewerUrl.value)
    pdfViewerUrl.value = ""
  }
}

function apriDocumentoOriginale() {
  if (!urlSorgente.value) return
  window.open(urlSorgente.value, "_blank")
}

function normalizzaProcedimentoCollegato(item) {
  return {
    idProcedimento:
      item.id_procedimento ??
      item.IDProcedimento ??
      item.idProcedimento,
    Codice:
      item.codice_procedimento ??
      item.CodiceProcedimento ??
      "",
    Titolo:
      item.titolo ??
      item.Titolo ??
      "",
    Stato:
      item.stato_procedimento ??
      item.StatoProcedimento ??
      "",
    Priorita:
      item.priorita ??
      item.Priorita ??
      "",
    Ruolo:
      item.ruolo_protocollo ??
      item.RuoloProtocollo ??
      "COLLEGATO",
    Principale:
      item.principale ??
      item.Principale ??
      false
  }
}

function normalizzaProcedimentoDisponibile(item) {
  const idProcedimento =
    item.id_procedimento ??
    item.IDProcedimento ??
    item.idProcedimento

  const codice =
    item.codice_procedimento ??
    item.CodiceProcedimento ??
    ""

  const titolo =
    item.titolo ??
    item.Titolo ??
    ""

  return {
    idProcedimento,
    codice,
    titolo,
    label: `${codice || "Senza codice"} - ${titolo || "Senza titolo"}`
  }
}

function resetFormCollegamento() {
  procedimentoSelezionatoId.value = null
  formCollegamento.value = {
    RuoloProtocollo: "COLLEGATO",
    Principale: false,
    NoteCollegamento: null
  }
  collegamentoErrore.value = ""
}

async function apriDialogCollegamento() {
  resetFormCollegamento()
  dialogCollegamento.value = true
  await caricaProcedimentiDisponibili()
}

function chiudiDialogCollegamento() {
  if (collegamentoLoading.value) return
  dialogCollegamento.value = false
}

async function confermaCollegamento() {
  if (!procedimentoSelezionatoId.value) return

  collegamentoLoading.value = true
  collegamentoErrore.value = ""
  collegamentoMessaggio.value = ""

  try {
    await linkProtocolloToProcedimento(
      route.params.idProtocollo,
      procedimentoSelezionatoId.value,
      {
        RuoloProtocollo: formCollegamento.value.RuoloProtocollo || "COLLEGATO",
        Principale: formCollegamento.value.Principale === true,
        NoteCollegamento: formCollegamento.value.NoteCollegamento || null
      }
    )

    dialogCollegamento.value = false
    collegamentoMessaggio.value = "Protocollo collegato al procedimento."
    await caricaProcedimentiCollegati()
  } catch (error) {
    if (error.status === 404) {
      collegamentoErrore.value = "Protocollo o procedimento non trovato."
    } else if (error.status === 409) {
      collegamentoErrore.value = "Il protocollo e gia collegato al procedimento selezionato."
    } else {
      collegamentoErrore.value = "Impossibile creare il collegamento."
    }
  } finally {
    collegamentoLoading.value = false
  }
}

function colorePrioritaProcedimento(valore) {
  switch (valore) {
    case "Urgente":
    case "URGENTE":
      return "red"
    case "Alta":
    case "ALTA":
    case "MEDIA":
      return "orange"
    case "Bassa":
    case "BASSA":
      return "grey"
    default:
      return "green"
  }
}

function coloreStatoProcedimento(valore) {
  switch (valore) {
    case "Chiuso":
    case "CHIUSO":
      return "green"
    case "Sospeso":
    case "SOSPESO":
      return "orange"
    case "Aperto":
    case "APERTO":
      return "blue"
    default:
      return "grey"
  }
}

onMounted(() => {
  caricaProtocollo()
  caricaMetadata()
  caricaProcedimentiCollegati()
})

onBeforeUnmount(() => {
  revocaPdfViewerUrl()
})
</script>

<style scoped>
.label {
  font-size: 0.78rem;
  color: #6b7280;
  margin-bottom: 4px;
}

.value {
  font-size: 1rem;
  font-weight: 600;
}

.oggetto {
  font-size: 1.05rem;
  line-height: 1.6;
  background: #f5f7fb;
  padding: 16px;
  border-radius: 16px;
  font-weight: 500;
}

.url {
  font-size: 0.85rem;
  color: #475569;
  word-break: break-all;
  background: #f8fafc;
  padding: 12px;
  border-radius: 12px;
}

.pdf-viewer {
  border: none;
  border-radius: 16px;
  background: #f8fafc;
}
</style>
