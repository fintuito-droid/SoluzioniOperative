<template>
  <v-container fluid>

    <v-card rounded="xl" class="pa-4">

      <v-card-title class="text-h5">
        Dettaglio Protocollo
      </v-card-title>

      <v-card-text v-if="protocollo">

        <v-row>

          <v-col cols="12" md="6">
            <strong>Numero Protocollo:</strong>
            {{ protocollo.NumeroProtocollo }}
          </v-col>

          <v-col cols="12" md="6">
            <strong>Data Protocollo:</strong>
            {{ protocollo.DataProtocollo }}
          </v-col>

          <v-col cols="12">
            <strong>Oggetto:</strong>
            <br>
            {{ protocollo.Oggetto }}
          </v-col>

          <v-col cols="12" md="4">
            <strong>Modalità:</strong>
            {{ protocollo.Modalita }}
          </v-col>

          <v-col cols="12" md="4">
            <strong>Operatore:</strong>
            {{ protocollo.Operatore }}
          </v-col>

          <v-col cols="12" md="4">
            <strong>Riservatezza:</strong>
            {{ protocollo.LivelloRiservatezza }}
          </v-col>

        </v-row>

      </v-card-text>

    </v-card>

    <v-card rounded="xl" class="pa-4 mt-4">

  <v-card-title>
    Assegnazioni
  </v-card-title>

  <v-data-table
    :items="assegnazioni"
    density="compact"
    hover
  />

</v-card>

<v-card rounded="xl" class="pa-4 mt-4">

  <v-card-title>
    Destinatari / Mittenti
  </v-card-title>

  <v-data-table
    :items="destinatari"
    density="compact"
    hover
  />

</v-card>

<v-card rounded="xl" class="pa-4 mt-4">

  <v-card-title>
    Firmatari
  </v-card-title>

  <v-data-table
    :items="firmatari"
    density="compact"
    hover
  />

</v-card>




  </v-container>
</template>

<script setup>
const assegnazioni = ref([])
const destinatari = ref([])
const firmatari = ref([])
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getToken } from '@/api/api'

const route = useRoute()

const idProtocollo = route.params.idProtocollo

const protocollo = ref(null)

async function caricaDettaglio() {

  try {

    const response = await fetch(
      `http://127.0.0.1:8000/protocollo-monitor/protocolli/${idProtocollo}`,
      { headers: { Authorization: `Bearer ${getToken()}` } }
    )

    const data = await response.json()

    protocollo.value = data.protocollo

    assegnazioni.value = data.assegnazioni || []
    destinatari.value = data.destinatari || []
    firmatari.value = data.firmatari || []

  } catch (error) {

    console.error(error)

    alert('Errore caricamento dettaglio protocollo')

  }

}

onMounted(() => {
  caricaDettaglio()
})
</script>