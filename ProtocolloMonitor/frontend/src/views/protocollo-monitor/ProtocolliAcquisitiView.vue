<template>
  <v-container fluid class="pa-4">

    <!-- =========================================================
         TITOLO PAGINA
         ========================================================= -->



    <!-- =========================================================
         FILTRI RAPIDI
         ========================================================= -->
    <v-card class="mb-4" rounded="xl" elevation="2">
      <v-card-title class="text-subtitle-1 font-weight-bold">
        Filtri
      </v-card-title>

      <v-card-text>
        <v-row>

          <v-col cols="12" md="4">
            <v-text-field
              v-model="filtri.testo"
              label="Cerca per oggetto, protocollo o mittente"
              variant="outlined"
              density="compact"
              clearable
            />
          </v-col>

          <v-col cols="12" md="2">
            <v-select
              v-model="filtri.stato"
              :items="statiPratica"
              label="Stato pratica"
              variant="outlined"
              density="compact"
              clearable
            />
          </v-col>

          <v-col cols="12" md="2">
            <v-select
              v-model="filtri.priorita"
              :items="priorita"
              label="Priorità"
              variant="outlined"
              density="compact"
              clearable
            />
          </v-col>

          <v-col cols="12" md="2">
            <v-checkbox
              v-model="filtri.soloDaLavorare"
              label="Solo da lavorare"
              density="compact"
              hide-details
            />
          </v-col>

          <v-col cols="12" md="2" class="d-flex align-center">
            <v-btn
              color="primary"
              variant="flat"
              block
              @click="caricaProtocolli"
            >
              Aggiorna
            </v-btn>
          </v-col>

        </v-row>
      </v-card-text>
    </v-card>


    <!-- =========================================================
         AREA PRINCIPALE: TABELLA + DETTAGLIO
         ========================================================= -->
    <v-row>

      <!-- TABELLA PROTOCOLLI -->
      <v-col cols="12" lg="8">
        <v-card rounded="xl" elevation="2" class="card-protocolli">

          <v-card-title class="d-flex justify-space-between align-center">
            <span class="text-subtitle-1 font-weight-bold">
              Protocolli acquisiti
            </span>

            <v-chip color="primary" variant="tonal">
              {{ protocolliFiltrati.length }} record
            </v-chip>
          </v-card-title>

          <v-data-table
  :headers="headers"
  :items="protocolliFiltrati"
  item-value="id_protocollo"
  density="compact"
  hover
  class="elevation-0 tabella-protocolli"
  @click:row="selezionaProtocollo"
>
  <template #item="{ item, columns }">
    <tr>
      <td>{{ item.numero_protocollo }}</td>
      <td>{{ item.data_protocollo }}</td>
      <td>{{ item.modalita }}</td>

      <td>
        <v-chip
          v-if="item.da_lavorare"
          color="orange"
          size="small"
          variant="tonal"
        >
          Da lavorare
        </v-chip>

        <v-chip
          v-else
          color="grey"
          size="small"
          variant="tonal"
        >
          No
        </v-chip>
      </td>

      <td>
        <v-chip
          :color="colorePriorita(item.priorita)"
          size="small"
          variant="tonal"
        >
          {{ item.priorita || 'Normale' }}
        </v-chip>
      </td>

      <td>
        <v-chip color="blue" size="small" variant="tonal">
          {{ item.stato_pratica || 'NUOVA' }}
        </v-chip>
      </td>
    </tr>

      <tr
        class="riga-oggetto"
        @click="protocolloSelezionato = { ...item }"
      >
        <td :colspan="columns.length">
          <div class="testo-oggetto" :title="item.oggetto">
            {{ item.oggetto }}
          </div>
        </td>
      </tr>

  </template>
</v-data-table>

        </v-card>
      </v-col>


      <!-- DETTAGLIO PROTOCOLLO -->
      <v-col cols="12" lg="4">
        <v-card
          rounded="xl"
          elevation="2"
          class="card-dettaglio"
        >

          <v-card-title class="text-subtitle-1 font-weight-bold">
            Dettaglio pratica
          </v-card-title>

          <v-card-text v-if="protocolloSelezionato">

            <div class="mb-3">
              <div class="text-caption text-grey">
                Protocollo
              </div>
              <div class="font-weight-bold">
                {{ protocolloSelezionato.numero_protocollo }}
              </div>
            </div>

            <div class="mb-3">
              <div class="text-caption text-grey">
                Data protocollo
              </div>
              <div>
                {{ protocolloSelezionato.data_protocollo }}
              </div>
            </div>

            <div class="mb-3">
              <div class="text-caption text-grey">
                Oggetto
              </div>
              <div>
                {{ protocolloSelezionato.oggetto }}
              </div>
            </div>

            <div class="mb-3">
              <div class="text-caption text-grey">
                Modalità
              </div>
              <div>
                {{ protocolloSelezionato.modalita }}
              </div>
            </div>

            <div class="mb-3">
              <div class="text-caption text-grey">
                Tipologia documento
              </div>
              <div>
                {{ protocolloSelezionato.tipologia_documento || '-' }}
              </div>
            </div>

            <div class="mb-3">
              <div class="text-caption text-grey">
                Scadenza
              </div>
              <div>
                {{ protocolloSelezionato.data_scadenza || '-' }}
              </div>
            </div>

            <v-divider class="my-4" />

            <v-row>
              <v-col cols="12" md="6">
                <v-select
                  v-model="protocolloSelezionato.priorita"
                  :items="priorita"
                  label="Priorità"
                  variant="outlined"
                  density="compact"
                />
              </v-col>

              <v-col cols="12" md="6">
                <v-select
                  v-model="protocolloSelezionato.stato_pratica"
                  :items="statiPratica"
                  label="Stato"
                  variant="outlined"
                  density="compact"
                />
              </v-col>
            </v-row>

            <v-textarea
              v-model="protocolloSelezionato.note_interne"
              label="Note interne"
              variant="outlined"
              rows="4"
              auto-grow
            />

            <v-btn
              color="primary"
              variant="flat"
              block
              class="mt-2"
              @click="salvaDettaglio"
            >
              Salva modifiche
            </v-btn>

          </v-card-text>

          <v-card-text v-else class="text-grey">
            Seleziona un protocollo dalla tabella per visualizzarne il dettaglio.
          </v-card-text>

        </v-card>
      </v-col>

    </v-row>

  </v-container>
</template>


<script setup>
// ==========================================================================================
// ProtocolliAcquisitiView.vue
//
// Prima Form web di ProtocolloMonitor.
// Mostra i protocolli acquisiti da Vigilia tramite Grisù.
//
// Architettura prevista:
// Vue.js + Vuetify
//        ↓
// FastAPI
//        ↓
// Access ora / PostgreSQL domani
// ==========================================================================================

import { computed, onMounted, reactive, ref } from 'vue'


// ==========================================================================================
// DATI PRINCIPALI
// ==========================================================================================

const protocolli = ref([])
const protocolloSelezionato = ref(null)


// ==========================================================================================
// FILTRI FORM
// ==========================================================================================

const filtri = reactive({
  testo: '',
  stato: null,
  priorita: null,
  soloDaLavorare: false
})


// ==========================================================================================
// LISTE VALORI
// ==========================================================================================

const statiPratica = [
  'NUOVA',
  'DA_ASSEGNARE',
  'ASSEGNATA',
  'IN_LAVORAZIONE',
  'DOCUMENTO_GENERATO',
  'CHIUSA'
]

const priorita = [
  'Bassa',
  'Normale',
  'Alta',
  'Urgente'
]


// ==========================================================================================
// INTESTAZIONI TABELLA
// ==========================================================================================

const headers = [
  { title: 'Protocollo', key: 'numero_protocollo' },
  { title: 'data', key: 'data_protocollo' },
  { title: 'modalità', key: 'modalita' },
  { title: 'da lavorare', key: 'da_lavorare' },
  { title: 'priorità', key: 'priorita' },
  { title: 'stato', key: 'stato_pratica' }
]


// ==========================================================================================
// FILTRO LOCALE DEI PROTOCOLLI
// ==========================================================================================

const protocolliFiltrati = computed(() => {
  return protocolli.value.filter((p) => {
    const testo = (filtri.testo || '').toLowerCase()

    const matchTesto =
      !testo ||
      String(p.numero_protocollo || '').toLowerCase().includes(testo) ||
      String(p.oggetto || '').toLowerCase().includes(testo) ||
      String(p.mittente || '').toLowerCase().includes(testo)

    const matchStato =
      !filtri.stato || p.stato_pratica === filtri.stato

    const matchPriorita =
      !filtri.priorita || p.priorita === filtri.priorita

    const matchDaLavorare =
      !filtri.soloDaLavorare || p.da_lavorare === true

    return matchTesto && matchStato && matchPriorita && matchDaLavorare
  })
})


// ==========================================================================================
// CARICAMENTO DATI
// ==========================================================================================

async function caricaProtocolli() {
  try {
    const response = await fetch(
      'http://127.0.0.1:8000/protocollo-monitor/protocolli'
    )

    if (!response.ok) {
      throw new Error('Errore HTTP ' + response.status)
    }

    protocolli.value = await response.json()
  } catch (error) {
    console.error('Errore durante il caricamento dei protocolli:', error)
    alert('Errore durante il caricamento dei protocolli da FastAPI.')
  }
}


// ==========================================================================================
// SELEZIONE RIGA TABELLA
// ==========================================================================================

function selezionaProtocollo(event, row) {
  protocolloSelezionato.value = { ...row.item }
}


// ==========================================================================================
// SALVATAGGIO DETTAGLIO
// ==========================================================================================

async function salvaDettaglio() {
  if (!protocolloSelezionato.value) return

  try {
    // Per ora aggiorniamo solo localmente.
    // Nello step successivo chiameremo FastAPI con PUT/PATCH.

    const index = protocolli.value.findIndex(
      p => p.id_protocollo === protocolloSelezionato.value.id_protocollo
    )

    if (index !== -1) {
      protocolli.value[index] = { ...protocolloSelezionato.value }
    }

    alert('Modifiche salvate localmente. Nel prossimo step collegheremo FastAPI.')
  } catch (error) {
    console.error('Errore durante il salvataggio:', error)
  }
}


// ==========================================================================================
// COLORE PRIORITÀ
// ==========================================================================================

function colorePriorita(valore) {
  switch (valore) {
    case 'Urgente':
      return 'red'
    case 'Alta':
      return 'orange'
    case 'Bassa':
      return 'grey'
    default:
      return 'green'
  }
}


// ==========================================================================================
// AVVIO PAGINA
// ==========================================================================================

onMounted(() => {
  caricaProtocolli()
})
</script>
<style scoped>

.riga-oggetto td {
  padding: 4px 16px 12px 16px;
  font-size: 0.82rem;
  line-height: 1.35;
  color: rgba(255, 255, 255, 0.90);
  white-space: normal;
  border-top: none !important;
  border-bottom: 1px solid rgba(255,255,255,0.10);
}

.riga-oggetto {
  cursor: pointer;
  border-top: none !important;
}

.riga-oggetto td {
  border-top: 0 !important;
}

.riga-oggetto + tr td {
  border-top: 0 !important;
}

tbody tr.riga-oggetto td {
  border-top: none !important;
}

tbody tr:has(+ .riga-oggetto) td {
  border-bottom: none !important;
}

:deep(thead th) {
  color: #42a5f5 !important;
  font-weight: 800 !important;
  font-size: 0.82rem !important;
  letter-spacing: 0.5px;
  text-transform: uppercase;
}

.testo-oggetto {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;

  overflow: hidden;
  text-overflow: ellipsis;

  line-height: 1.35;
  max-height: 2.7em;
  width: 100%;
}

.card-protocolli {
  height: 760px;
  display: flex;
  flex-direction: column;
}

.tabella-protocolli {
  flex: 1;
  overflow-y: auto;
}

.card-dettaglio {
  height: 760px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

</style>