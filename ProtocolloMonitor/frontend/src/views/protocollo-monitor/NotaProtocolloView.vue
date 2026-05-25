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

  </v-container>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, computed } from "vue"
import { useRoute } from "vue-router"

const route = useRoute()
const protocollo = ref(null)
const metadata = ref(null)
const metadataLoading = ref(false)
const pdfLoading = ref(false)
const pdfErrore = ref("")
const pdfViewerUrl = ref("")

const urlSorgente = computed(() => {
  return protocollo.value?.UrlSorgente || ""
})

const urlPdf = computed(() => {
  return `http://127.0.0.1:8000/protocollo-monitor/protocolli/${route.params.idProtocollo}/pdf`
})

const pdfDisponibile = computed(() => {
  return metadata.value?.pdf_disponibile === true
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

onMounted(() => {
  caricaProtocollo()
  caricaMetadata()
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
