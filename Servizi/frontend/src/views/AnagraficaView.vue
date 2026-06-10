<template>
  <div>
    <!-- Intestazione -->
    <div class="d-flex align-center mb-4 flex-wrap gap-2">
      <div class="flex-1">
        <h1 class="text-h5 font-weight-medium">Anagrafica Personale</h1>
        <p class="text-caption text-medium-emphasis mb-0">Gestione dipendenti e specialità</p>
      </div>
      <v-btn
        v-if="auth.canPlanificare"
        color="primary"
        prepend-icon="mdi-plus"
        @click="apriNuovo"
      >
        Nuovo dipendente
      </v-btn>
    </div>

    <!-- Filtro ricerca -->
    <v-card class="mb-4" variant="outlined">
      <v-card-text class="py-2">
        <v-row dense align="center">
          <v-col cols="12" sm="5">
            <v-text-field
              v-model="ricerca"
              prepend-inner-icon="mdi-magnify"
              label="Cerca per cognome o nome"
              clearable
              density="compact"
              hide-details
            />
          </v-col>
          <v-col cols="12" sm="4">
            <v-select
              v-model="filtroComando"
              :items="comandi"
              item-title="codice"
              item-value="id"
              label="Comando"
              clearable
              density="compact"
              hide-details
            />
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- Tabella -->
    <v-card :loading="caricando">
      <v-data-table
        :headers="headers"
        :items="personaleFiltrato"
        :items-per-page="20"
        density="compact"
        hover
      >
        <!-- Cognome + Nome -->
        <template #item.cognome="{ item }">
          <span class="font-weight-medium">{{ item.cognome }} {{ item.nome }}</span>
        </template>

        <!-- Qualifica -->
        <template #item.qualifica_cod="{ item }">
          <v-chip v-if="item.qualifica_cod" size="x-small" variant="tonal" color="primary">
            {{ item.qualifica_cod }}
          </v-chip>
        </template>

        <!-- Specialità come chips -->
        <template #item.specialita="{ item }">
          <div class="d-flex flex-wrap gap-1 py-1">
            <v-chip
              v-for="s in item.specialita"
              :key="s.id"
              size="x-small"
              variant="tonal"
              color="secondary"
            >
              {{ s.codice }}
            </v-chip>
            <span v-if="!item.specialita?.length" class="text-medium-emphasis text-caption">—</span>
          </div>
        </template>

        <!-- Stato attivo -->
        <template #item.attivo="{ item }">
          <v-icon :color="item.attivo ? 'success' : 'error'" size="small">
            {{ item.attivo ? 'mdi-check-circle' : 'mdi-close-circle' }}
          </v-icon>
        </template>

        <!-- Azioni -->
        <template #item.azioni="{ item }">
          <v-btn
            icon="mdi-pencil"
            size="x-small"
            variant="text"
            color="primary"
            @click="apriModifica(item)"
          />
          <v-btn
            v-if="auth.isAdmin && item.attivo"
            icon="mdi-account-off"
            size="x-small"
            variant="text"
            color="error"
            title="Disattiva"
            @click="disattiva(item)"
          />
        </template>
      </v-data-table>
    </v-card>

    <!-- ── Dialog: crea / modifica dipendente ── -->
    <v-dialog v-model="dialog" max-width="700" persistent scrollable>
      <v-card>
        <v-card-title class="text-subtitle-1 font-weight-medium pa-4 pb-2">
          {{ isNuovo ? 'Nuovo dipendente' : 'Modifica dipendente' }}
        </v-card-title>
        <v-divider/>
        <v-card-text>
          <v-form ref="formRef">
            <v-row dense>
              <!-- Cognome -->
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="form.cognome"
                  label="Cognome *"
                  :rules="[v => !!v || 'Obbligatorio']"
                  density="compact"
                />
              </v-col>
              <!-- Nome -->
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="form.nome"
                  label="Nome *"
                  :rules="[v => !!v || 'Obbligatorio']"
                  density="compact"
                />
              </v-col>
              <!-- Matricola -->
              <v-col cols="12" sm="4">
                <v-text-field
                  v-model="form.matricola"
                  label="Matricola"
                  density="compact"
                />
              </v-col>
              <!-- Qualifica -->
              <v-col cols="12" sm="4">
                <v-select
                  v-model="form.qualifica_id"
                  :items="qualifiche"
                  item-title="codice"
                  item-value="id"
                  label="Qualifica"
                  clearable
                  density="compact"
                />
              </v-col>
              <!-- Comando -->
              <v-col cols="12" sm="4">
                <v-select
                  v-model="form.comando_id"
                  :items="comandi"
                  item-title="codice"
                  item-value="id"
                  label="Comando"
                  clearable
                  density="compact"
                />
              </v-col>
              <!-- Telefono -->
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="form.telefono"
                  label="Telefono"
                  density="compact"
                />
              </v-col>
              <!-- Email -->
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="form.email"
                  label="Email"
                  density="compact"
                />
              </v-col>
              <!-- Note -->
              <v-col cols="12">
                <v-textarea
                  v-model="form.note"
                  label="Note"
                  rows="2"
                  density="compact"
                  auto-grow
                />
              </v-col>
              <!-- Attivo -->
              <v-col cols="12" sm="4">
                <v-switch
                  v-model="form.attivo"
                  label="Attivo"
                  color="success"
                  density="compact"
                  hide-details
                />
              </v-col>
            </v-row>

            <!-- Specialità -->
            <v-divider class="my-3"/>
            <div class="text-subtitle-2 font-weight-medium mb-2">Specialità</div>
            <div class="specialita-grid">
              <v-checkbox
                v-for="s in tutteSpecialita"
                :key="s.id"
                v-model="form.specialita_ids"
                :value="s.id"
                :label="s.codice"
                density="compact"
                hide-details
                color="primary"
              />
            </div>
          </v-form>
        </v-card-text>
        <v-divider/>
        <v-card-actions>
          <v-btn variant="text" @click="dialog = false">Annulla</v-btn>
          <v-spacer/>
          <v-btn
            color="primary"
            :loading="salvando"
            @click="salva"
          >
            Salva
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Snackbar -->
    <v-snackbar v-model="snack.show" :color="snack.color" timeout="4000">
      {{ snack.text }}
    </v-snackbar>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { personaleApi, lookupApi } from '@/api/api'

const auth = useAuthStore()

// ── Stato ─────────────────────────────────────────────────────────────────────
const personaleList    = ref([])
const tutteSpecialita  = ref([])
const qualifiche       = ref([])
const comandi          = ref([])
const caricando        = ref(false)
const salvando         = ref(false)
const ricerca          = ref('')
const filtroComando    = ref(null)
const dialog           = ref(false)
const isNuovo          = ref(true)
const formRef          = ref(null)
const snack            = ref({ show: false, text: '', color: 'success' })

const form = reactive({
  id:           null,
  cognome:      '',
  nome:         '',
  matricola:    '',
  qualifica_id: null,
  comando_id:   null,
  telefono:     '',
  email:        '',
  note:         '',
  attivo:       true,
  specialita_ids: [],
})

// ── Headers tabella ───────────────────────────────────────────────────────────
const headers = [
  { title: 'Cognome / Nome',  key: 'cognome',      sortable: true },
  { title: 'Matricola',       key: 'matricola',    sortable: true },
  { title: 'Qualifica',       key: 'qualifica_cod', sortable: true },
  { title: 'Comando',         key: 'comando_cod',  sortable: true },
  { title: 'Specialità',      key: 'specialita',   sortable: false },
  { title: 'Attivo',          key: 'attivo',       sortable: true },
  { title: '',                key: 'azioni',       sortable: false, align: 'end' },
]

// ── Filtro ────────────────────────────────────────────────────────────────────
const personaleFiltrato = computed(() => {
  let lista = personaleList.value
  if (ricerca.value) {
    const q = ricerca.value.toLowerCase()
    lista = lista.filter(p =>
      p.cognome?.toLowerCase().includes(q) || p.nome?.toLowerCase().includes(q)
    )
  }
  if (filtroComando.value) {
    lista = lista.filter(p => p.comando_id === filtroComando.value)
  }
  return lista
})

// ── Caricamento dati ──────────────────────────────────────────────────────────
async function carica() {
  caricando.value = true
  const [rp, rs, rq, rc] = await Promise.all([
    personaleApi.lista(),
    lookupApi.specialita(),
    lookupApi.qualifiche(),
    lookupApi.comandi(),
  ])
  if (rp.data) personaleList.value   = rp.data
  if (rs.data) tutteSpecialita.value = rs.data
  if (rq.data) qualifiche.value      = rq.data
  if (rc.data) comandi.value         = rc.data
  caricando.value = false
}

onMounted(carica)

// ── Dialog ────────────────────────────────────────────────────────────────────
function apriNuovo() {
  isNuovo.value = true
  Object.assign(form, {
    id: null, cognome: '', nome: '', matricola: '',
    qualifica_id: null, comando_id: null,
    telefono: '', email: '', note: '', attivo: true,
    specialita_ids: [],
  })
  dialog.value = true
}

function apriModifica(item) {
  isNuovo.value = false
  Object.assign(form, {
    id:           item.id,
    cognome:      item.cognome      || '',
    nome:         item.nome         || '',
    matricola:    item.matricola    || '',
    qualifica_id: item.qualifica_id || null,
    comando_id:   item.comando_id   || null,
    telefono:     item.telefono     || '',
    email:        item.email        || '',
    note:         item.note         || '',
    attivo:       item.attivo       ?? true,
    specialita_ids: (item.specialita || []).map(s => s.id),
  })
  dialog.value = true
}

async function salva() {
  const { valid } = await formRef.value.validate()
  if (!valid) return
  salvando.value = true

  const payload = {
    cognome:      form.cognome,
    nome:         form.nome,
    matricola:    form.matricola || null,
    qualifica_id: form.qualifica_id,
    comando_id:   form.comando_id,
    telefono:     form.telefono  || null,
    email:        form.email     || null,
    note:         form.note      || null,
    attivo:       form.attivo,
  }

  let error = null

  if (isNuovo.value) {
    const { data, error: err } = await personaleApi.crea(payload)
    error = err
    if (data && form.specialita_ids.length) {
      await personaleApi.aggiornaSpecialita(data.id, form.specialita_ids)
    }
  } else {
    const { error: err } = await personaleApi.aggiorna(form.id, payload)
    error = err
    if (!err) {
      await personaleApi.aggiornaSpecialita(form.id, form.specialita_ids)
    }
  }

  salvando.value = false
  if (error) {
    showSnack(error, 'error')
  } else {
    showSnack(isNuovo.value ? 'Dipendente creato' : 'Dati aggiornati', 'success')
    dialog.value = false
    await carica()
  }
}

async function disattiva(item) {
  const { error } = await personaleApi.disattiva(item.id)
  if (error) showSnack(error, 'error')
  else { showSnack('Dipendente disattivato', 'success'); await carica() }
}

function showSnack(text, color = 'success') {
  snack.value = { show: true, text, color }
}
</script>

<style scoped>
.specialita-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
  gap: 0 8px;
}
</style>
