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
      <v-card-title class="font-weight-bold">
        Documento protocollato
      </v-card-title>

      <v-divider class="mb-4" />

      <iframe
        v-if="protocollo"
        :src="urlPdf"
        width="100%"
        height="750"
        class="pdf-viewer"
      ></iframe>

      <v-alert v-else type="info" variant="tonal">
        Caricamento PDF in corso...
      </v-alert>
    </v-card>

  </v-container>
</template>

<script setup>
import { ref, onMounted, computed } from "vue"
import { useRoute } from "vue-router"

const route = useRoute()
const protocollo = ref(null)

const urlSorgente = computed(() => {
  return protocollo.value?.UrlSorgente || ""
})

const urlPdf = computed(() => {
  return `http://127.0.0.1:8000/protocollo-monitor/protocolli/${route.params.idProtocollo}/pdf`
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

function apriDocumentoOriginale() {
  if (!urlSorgente.value) return
  window.open(urlSorgente.value, "_blank")
}

onMounted(() => {
  caricaProtocollo()
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