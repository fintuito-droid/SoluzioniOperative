<template>
  <v-container fluid class="pa-4">

    <v-card class="mb-4" rounded="xl" elevation="2">
      <v-card-title class="text-subtitle-1 font-weight-bold">
        Filtri
      </v-card-title>

      <v-card-text>
        <v-row>
          <v-col cols="12" md="4">
            <v-text-field
              v-model="filtri.testo"
              label="Cerca per oggetto, protocollo, mittente o comando"
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
            <v-btn color="primary" variant="flat" block @click="caricaProtocolli">
              Aggiorna
            </v-btn>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <v-row>
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
            fixed-header
            class="tabella-protocolli"
            @click:row="selezionaProtocollo"
          >
            <template #item="{ item, columns, index }">

              <tr
                :class="classeRigaProtocollo(index)"
                @mouseenter="hoverIndex = index"
                @mouseleave="hoverIndex = null"
              >
                <td>{{ item.numero_protocollo }}</td>

                <td>{{ item.data_protocollo }}</td>

                <td>
                  <div class="cella-modalita">
                    <span>{{ item.modalita }}</span>

                    <v-chip
                      v-if="item.comando_mittente"
                      color="indigo"
                      size="x-small"
                      variant="tonal"
                      class="chip-comando"
                    >
                      {{ item.comando_mittente }}
                    </v-chip>
                  </div>
                </td>

                <td>
                  <v-chip
                    v-if="item.da_lavorare"
                    color="orange"
                    size="x-small"
                    variant="tonal"
                  >
                    Da lavorare
                  </v-chip>

                  <v-chip
                    v-else
                    color="grey"
                    size="x-small"
                    variant="tonal"
                  >
                    No
                  </v-chip>
                </td>

                <td>
                  <v-chip
                    :color="colorePriorita(item.priorita)"
                    size="x-small"
                    variant="tonal"
                  >
                    {{ item.priorita || 'Normale' }}
                  </v-chip>
                </td>

                <td>
                  <v-chip color="blue" size="x-small" variant="tonal">
                    {{ item.stato_pratica || 'NUOVA' }}
                  </v-chip>
                </td>

                <td>
                  <v-btn
                    size="x-small"
                    color="primary"
                    variant="tonal"
                    class="btn-compatto"
                    @click.stop="visualizzaProtocollo(item)"
                  >
                    Visualizza
                  </v-btn>

                  <v-btn
                    size="x-small"
                    color="deep-purple"
                    variant="flat"
                    class="ml-2 btn-compatto btn-pdf"
                    @click.stop="apriPdfEsterno(item)"
                  >
                    PDF
                  </v-btn>
                </td>
              </tr>

              <tr
                :class="classeRigaProtocollo(index, true)"
                @mouseenter="hoverIndex = index"
                @mouseleave="hoverIndex = null"
                @click="protocolloSelezionato = { ...item }"
              >
                <td :colspan="columns.length">
                  <div class="testo-oggetto" :title="item.oggetto">
                    <span class="label-oggetto">Oggetto:</span>
                    {{ item.oggetto }}
                  </div>
                </td>
              </tr>

            </template>
          </v-data-table>
        </v-card>
      </v-col>

      <v-col cols="12" lg="4">
        <v-card rounded="xl" elevation="2" class="card-dettaglio">
          <v-card-title class="text-subtitle-1 font-weight-bold">
            Dettaglio pratica
          </v-card-title>

          <v-card-text v-if="protocolloSelezionato">
            <div class="mb-3">
              <div class="text-caption text-grey">Protocollo</div>
              <div class="font-weight-bold">
                {{ protocolloSelezionato.numero_protocollo }}
              </div>
            </div>

            <div class="mb-3">
              <div class="text-caption text-grey">Data protocollo</div>
              <div>{{ protocolloSelezionato.data_protocollo }}</div>
            </div>

            <div class="mb-3">
              <div class="text-caption text-grey">Modalità</div>
              <div>
                {{ protocolloSelezionato.modalita }}
                <span v-if="protocolloSelezionato.comando_mittente">
                  - {{ protocolloSelezionato.comando_mittente }}
                </span>
              </div>
            </div>

            <div class="mb-3">
              <div class="text-caption text-grey">Oggetto</div>
              <div>{{ protocolloSelezionato.oggetto }}</div>
            </div>

            <div class="mb-3">
              <div class="text-caption text-grey">Tipologia documento</div>
              <div>{{ protocolloSelezionato.tipologia_documento || '-' }}</div>
            </div>

            <div class="mb-3">
              <div class="text-caption text-grey">Scadenza</div>
              <div>{{ protocolloSelezionato.data_scadenza || '-' }}</div>
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
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const protocolli = ref([])
const protocolloSelezionato = ref(null)
const hoverIndex = ref(null)

const filtri = reactive({
  testo: '',
  stato: null,
  priorita: null,
  soloDaLavorare: false
})

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

const headers = [
  { title: 'Protocollo', key: 'numero_protocollo' },
  { title: 'Data', key: 'data_protocollo' },
  { title: 'Modalità', key: 'modalita' },
  { title: 'Da lavorare', key: 'da_lavorare' },
  { title: 'Priorità', key: 'priorita' },
  { title: 'Stato', key: 'stato_pratica' },
  { title: 'Azioni', key: 'azioni', sortable: false }
]

const protocolliFiltrati = computed(() => {
  return protocolli.value.filter((p) => {
    const testo = (filtri.testo || '').toLowerCase()

    const matchTesto =
      !testo ||
      String(p.numero_protocollo || '').toLowerCase().includes(testo) ||
      String(p.oggetto || '').toLowerCase().includes(testo) ||
      String(p.mittente || '').toLowerCase().includes(testo) ||
      String(p.comando_mittente || '').toLowerCase().includes(testo)

    const matchStato =
      !filtri.stato || p.stato_pratica === filtri.stato

    const matchPriorita =
      !filtri.priorita || p.priorita === filtri.priorita

    const matchDaLavorare =
      !filtri.soloDaLavorare || p.da_lavorare === true

    return matchTesto && matchStato && matchPriorita && matchDaLavorare
  })
})

function classeRigaProtocollo(index, oggetto = false) {
  return [
    oggetto ? 'riga-oggetto' : '',
    index % 2 === 0 ? 'riga-grigio-chiaro' : 'riga-grigio-scuro',
    hoverIndex.value === index ? 'riga-hover-paglierino' : ''
  ]
}

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

function selezionaProtocollo(event, row) {
  protocolloSelezionato.value = { ...row.item }
}

async function salvaDettaglio() {
  if (!protocolloSelezionato.value) return

  const index = protocolli.value.findIndex(
    p => p.id_protocollo === protocolloSelezionato.value.id_protocollo
  )

  if (index !== -1) {
    protocolli.value[index] = { ...protocolloSelezionato.value }
  }

  alert('Modifiche salvate localmente. Nel prossimo step collegheremo FastAPI.')
}

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

function visualizzaProtocollo(item) {
  const id =
    item.id_protocollo ||
    item.IDProtocollo ||
    item.idProtocollo

  router.push(`/protocollo-monitor/protocolli/${id}`)
}

const apriPdfEsterno = async (item) => {
  try {
    const response = await fetch(
      `http://127.0.0.1:8000/protocollo-monitor/protocolli/${item.id_protocollo}/apri-pdf`
    )

    if (!response.ok) {
      const errore = await response.json()
      alert(errore.detail || 'Errore apertura PDF')
    }
  } catch (err) {
    console.error(err)
    alert('Errore comunicazione backend')
  }
}

onMounted(() => {
  caricaProtocolli()
})
</script>

<style scoped>
.card-protocolli {
  height: 760px;
  display: flex;
  flex-direction: column;
}

.card-dettaglio {
  height: 760px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.tabella-protocolli {
  flex: 1;
  width: 100% !important;
  overflow-y: auto;
}

.tabella-protocolli :deep(table) {
  width: 100% !important;
  table-layout: fixed;
}

:deep(thead th) {
  color: #42a5f5 !important;
  font-weight: 800 !important;
  font-size: 0.78rem !important;
  letter-spacing: 0.4px;
  text-transform: uppercase;
}

.riga-grigio-chiaro td {
  background-color: #f3f4f6 !important;
  color: #000000 !important;
}

.riga-grigio-scuro td {
  background-color: #d9dde3 !important;
  color: #000000 !important;
}

.riga-hover-paglierino td {
  background-color: #fff8c6 !important;
}

.riga-oggetto {
  cursor: pointer;
}

.riga-oggetto td {
  padding: 0px 12px 3px 12px !important;
  font-size: 0.70rem;
  line-height: 1.05;
  white-space: nowrap;
  border-top: none !important;
}

.testo-oggetto {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  width: 100%;
  color: #000000 !important;
}

.label-oggetto {
  color: #c62828;
  font-weight: 700;
  text-decoration: underline;
  margin-right: 6px;
}

.cella-modalita {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 6px;
  width: 100%;
}

.chip-comando {
  font-weight: 700;
  letter-spacing: 0.3px;
}

.btn-compatto {
  min-height: 16px !important;
  height: 16px !important;
  font-size: 0.64rem !important;
  padding-left: 7px !important;
  padding-right: 7px !important;
}

.btn-pdf:hover {
  background-color: orange !important;
}

:deep(.v-chip) {
  min-height: 15px !important;
  height: 15px !important;
  font-size: 0.56rem !important;
  padding-left: 5px !important;
  padding-right: 5px !important;
}

.riga-oggetto td {
  padding: 0px 12px 3px 12px !important;
  font-size: 0.70rem;
  line-height: 1.05;
  white-space: nowrap;
  border-top: none !important;
}

:deep(.v-btn__content) {
  line-height: 1 !important;
}

:deep(tr) {
  height: auto !important;
}

</style>