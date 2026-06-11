<template>
  <div>
    <div class="d-flex align-center mb-4">
      <div>
        <h1 class="text-h5 font-weight-medium">Impostazioni</h1>
        <p class="text-caption text-medium-emphasis mb-0">Configurazione modulo Servizi</p>
      </div>
    </div>

    <v-card>
      <v-tabs v-model="tab" color="primary" density="comfortable">
        <v-tab value="campagne"   prepend-icon="mdi-calendar-range">Campagne</v-tab>
        <v-tab value="postazioni" prepend-icon="mdi-map-marker">Postazioni</v-tab>
        <v-tab value="specialita" prepend-icon="mdi-certificate">Specialità</v-tab>
        <v-tab value="utenti"     prepend-icon="mdi-account-key">Utenti</v-tab>
      </v-tabs>
      <v-divider/>

      <v-window v-model="tab">

        <!-- ══ TAB CAMPAGNE ══════════════════════════════════════════════════ -->
        <v-window-item value="campagne">
          <v-card-text>
            <div class="d-flex justify-end mb-3">
              <v-btn color="primary" prepend-icon="mdi-plus" size="small" @click="apriCampagna()">
                Nuova campagna
              </v-btn>
            </div>
            <v-data-table
              :headers="hCampagne"
              :items="store.campagne"
              density="compact"
              items-per-page="-1"
              hide-default-footer
            >
              <template #item.anno="{ item }">
                <span class="font-weight-medium">AIB {{ item.anno }}</span>
              </template>
              <template #item.data_inizio="{ item }">{{ fmtData(item.data_inizio) }}</template>
              <template #item.data_fine="{ item }">{{ fmtData(item.data_fine) }}</template>
              <template #item.attiva="{ item }">
                <v-chip :color="item.attiva ? 'success' : 'grey'" size="x-small" variant="tonal">
                  {{ item.attiva ? 'ATTIVA' : 'chiusa' }}
                </v-chip>
              </template>
              <template #item.azioni="{ item }">
                <v-btn icon="mdi-pencil" size="x-small" variant="text" color="primary"
                       @click="apriCampagna(item)"/>
              </template>
            </v-data-table>
          </v-card-text>
        </v-window-item>

        <!-- ══ TAB POSTAZIONI ════════════════════════════════════════════════ -->
        <v-window-item value="postazioni">
          <v-card-text>
            <div class="d-flex justify-end mb-3">
              <v-btn color="primary" prepend-icon="mdi-plus" size="small" @click="apriPostazione()">
                Nuova postazione
              </v-btn>
            </div>
            <v-data-table
              :headers="hPostazioni"
              :items="store.postazioni"
              density="compact"
              items-per-page="-1"
              hide-default-footer
            >
              <template #item.codice="{ item }">
                <span class="font-weight-medium">{{ item.codice }}</span>
              </template>
              <template #item.composizione="{ item }">
                <div class="d-flex flex-wrap gap-1 py-1">
                  <v-chip v-if="item.slot_funzionario > 0" size="x-small" variant="tonal" color="primary">
                    {{ item.slot_funzionario }} Funzionario
                  </v-chip>
                  <v-chip v-if="item.slot_tas2 > 0" size="x-small" variant="tonal" color="secondary">
                    {{ item.slot_tas2 }} TAS 2
                  </v-chip>
                  <v-chip v-if="item.slot_addetto > 0" size="x-small" variant="tonal" color="info">
                    {{ item.slot_addetto }} Addetto
                  </v-chip>
                  <span v-if="!item.slot_funzionario && !item.slot_tas2 && !item.slot_addetto"
                        class="text-caption text-medium-emphasis">non configurata</span>
                </div>
              </template>
              <template #item.turni_multipli="{ item }">
                <v-icon :color="item.turni_multipli ? 'success' : 'grey-lighten-1'" size="small">
                  {{ item.turni_multipli ? 'mdi-check' : 'mdi-minus' }}
                </v-icon>
              </template>
              <template #item.attiva="{ item }">
                <v-icon :color="item.attiva ? 'success' : 'error'" size="small">
                  {{ item.attiva ? 'mdi-check-circle' : 'mdi-close-circle' }}
                </v-icon>
              </template>
              <template #item.azioni="{ item }">
                <v-btn icon="mdi-pencil" size="x-small" variant="text" color="primary"
                       @click="apriPostazione(item)"/>
              </template>
            </v-data-table>
          </v-card-text>
        </v-window-item>

        <!-- ══ TAB SPECIALITÀ ════════════════════════════════════════════════ -->
        <v-window-item value="specialita">
          <v-card-text>
            <div class="d-flex justify-end mb-3">
              <v-btn color="primary" prepend-icon="mdi-plus" size="small" @click="apriSpecialita()">
                Nuova specialità
              </v-btn>
            </div>
            <v-data-table
              :headers="hSpecialita"
              :items="specialitaList"
              density="compact"
              items-per-page="-1"
              hide-default-footer
            >
              <template #item.codice="{ item }">
                <v-chip size="small" variant="tonal" color="secondary">{{ item.codice }}</v-chip>
              </template>
              <template #item.azioni="{ item }">
                <v-btn icon="mdi-pencil" size="x-small" variant="text" color="primary"
                       @click="apriSpecialita(item)"/>
                <v-btn icon="mdi-delete-outline" size="x-small" variant="text" color="error"
                       @click="chiediEliminaSpecialita(item)"/>
              </template>
            </v-data-table>
          </v-card-text>
        </v-window-item>

        <!-- ══ TAB UTENTI ════════════════════════════════════════════════════ -->
        <v-window-item value="utenti">
          <v-card-text>
            <div class="d-flex justify-end mb-3">
              <v-btn color="primary" prepend-icon="mdi-plus" size="small" @click="apriUtente()">
                Nuovo utente
              </v-btn>
            </div>
            <v-data-table
              :headers="hUtenti"
              :items="utentiList"
              density="compact"
              items-per-page="-1"
              hide-default-footer
            >
              <template #item.username="{ item }">
                <span class="font-weight-medium">{{ item.username }}</span>
              </template>
              <template #item.ruolo="{ item }">
                <v-chip :color="coloreRuolo(item.ruolo)" size="x-small" variant="tonal">
                  {{ item.ruolo }}
                </v-chip>
              </template>
              <template #item.ultimo_accesso="{ item }">
                <span class="text-caption">{{ fmtDataOra(item.ultimo_accesso) }}</span>
              </template>
              <template #item.attivo="{ item }">
                <v-icon :color="item.attivo ? 'success' : 'error'" size="small">
                  {{ item.attivo ? 'mdi-check-circle' : 'mdi-close-circle' }}
                </v-icon>
              </template>
              <template #item.azioni="{ item }">
                <v-btn icon="mdi-pencil" size="x-small" variant="text" color="primary"
                       title="Modifica" @click="apriUtente(item)"/>
                <v-btn icon="mdi-key-variant" size="x-small" variant="text" color="warning"
                       title="Reset password" @click="apriResetPassword(item)"/>
              </template>
            </v-data-table>
          </v-card-text>
        </v-window-item>

      </v-window>
    </v-card>

    <!-- ── Dialog utente ── -->
    <v-dialog v-model="dlgUtente" max-width="480" persistent>
      <v-card>
        <v-card-title class="text-subtitle-1 font-weight-medium pa-4 pb-2">
          {{ formUtente.id ? 'Modifica utente' : 'Nuovo utente' }}
        </v-card-title>
        <v-divider/>
        <v-card-text class="pt-4">
          <v-row dense>
            <v-col cols="12" sm="6">
              <v-text-field v-model="formUtente.username" label="Username *"
                            :disabled="!!formUtente.id" density="compact"/>
            </v-col>
            <v-col cols="12" sm="6">
              <v-text-field v-if="!formUtente.id" v-model="formUtente.password"
                            label="Password *" type="password" density="compact"/>
            </v-col>
            <v-col cols="12" sm="6">
              <v-select v-model="formUtente.ruolo" :items="ruoliDisponibili"
                        label="Ruolo *" density="compact"/>
            </v-col>
            <v-col cols="12" sm="6">
              <v-select v-model="formUtente.comando_id" :items="store.comandi"
                        item-title="codice" item-value="id"
                        label="Comando" clearable density="compact"/>
            </v-col>
            <v-col cols="12">
              <v-autocomplete v-model="formUtente.personale_id" :items="store.personale"
                              :item-title="p => `${p.cognome} ${p.nome}`" item-value="id"
                              label="Dipendente collegato" clearable density="compact"/>
            </v-col>
            <v-col cols="12">
              <v-switch v-model="formUtente.attivo" label="Attivo" color="success"
                        density="compact" hide-details/>
            </v-col>
          </v-row>
        </v-card-text>
        <v-divider/>
        <v-card-actions>
          <v-btn variant="text" @click="dlgUtente = false">Annulla</v-btn>
          <v-spacer/>
          <v-btn color="primary" :loading="salvando" :disabled="!utenteValido" @click="salvaUtente">
            Salva
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- ── Dialog reset password ── -->
    <v-dialog v-model="dlgResetPwd" max-width="420" persistent>
      <v-card>
        <v-card-title class="text-subtitle-1 font-weight-medium pa-4 pb-2">
          Reset password — {{ utenteReset?.username }}
        </v-card-title>
        <v-divider/>
        <v-card-text class="pt-4">
          <v-text-field v-model="nuovaPwd" label="Nuova password *" type="password"
                        :rules="[v => !v || v.length >= 6 || 'Minimo 6 caratteri']"
                        density="compact"/>
          <p class="text-caption text-medium-emphasis">
            Le sessioni attive dell'utente verranno chiuse.
          </p>
        </v-card-text>
        <v-divider/>
        <v-card-actions>
          <v-btn variant="text" @click="dlgResetPwd = false">Annulla</v-btn>
          <v-spacer/>
          <v-btn color="warning" variant="tonal" :loading="salvando"
                 :disabled="nuovaPwd.length < 6" @click="salvaResetPassword">
            Reset
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- ── Dialog campagna ── -->
    <v-dialog v-model="dlgCampagna" max-width="480" persistent>
      <v-card>
        <v-card-title class="text-subtitle-1 font-weight-medium pa-4 pb-2">
          {{ formCampagna.id ? 'Modifica campagna' : 'Nuova campagna' }}
        </v-card-title>
        <v-divider/>
        <v-card-text class="pt-4">
          <v-row dense>
            <v-col cols="12" sm="4">
              <v-text-field v-model.number="formCampagna.anno" label="Anno *" type="number" density="compact"/>
            </v-col>
            <v-col cols="12" sm="4">
              <v-text-field v-model="formCampagna.data_inizio" label="Inizio *" type="date" density="compact"/>
            </v-col>
            <v-col cols="12" sm="4">
              <v-text-field v-model="formCampagna.data_fine" label="Fine *" type="date" density="compact"/>
            </v-col>
            <v-col cols="12">
              <v-text-field v-model="formCampagna.descrizione" label="Descrizione" density="compact"/>
            </v-col>
            <v-col cols="12">
              <v-switch v-model="formCampagna.attiva" label="Campagna attiva" color="success"
                        density="compact" hide-details/>
              <p v-if="formCampagna.attiva" class="text-caption text-medium-emphasis mt-1">
                Attivando questa campagna le altre verranno disattivate.
              </p>
            </v-col>
          </v-row>
        </v-card-text>
        <v-divider/>
        <v-card-actions>
          <v-btn variant="text" @click="dlgCampagna = false">Annulla</v-btn>
          <v-spacer/>
          <v-btn color="primary" :loading="salvando" :disabled="!campagnaValida" @click="salvaCampagna">
            Salva
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- ── Dialog postazione ── -->
    <v-dialog v-model="dlgPostazione" max-width="560" persistent>
      <v-card>
        <v-card-title class="text-subtitle-1 font-weight-medium pa-4 pb-2">
          {{ formPostazione.id ? 'Modifica postazione' : 'Nuova postazione' }}
        </v-card-title>
        <v-divider/>
        <v-card-text class="pt-4">
          <v-row dense>
            <v-col cols="12" sm="4">
              <v-text-field v-model="formPostazione.codice" label="Codice *" density="compact"/>
            </v-col>
            <v-col cols="12" sm="8">
              <v-text-field v-model="formPostazione.nome" label="Nome *" density="compact"/>
            </v-col>
            <v-col cols="12">
              <v-text-field v-model="formPostazione.note" label="Note" density="compact"/>
            </v-col>
          </v-row>

          <v-divider class="my-3"/>
          <div class="text-subtitle-2 font-weight-medium mb-2">Regole di composizione turno</div>
          <v-row dense>
            <v-col cols="4">
              <v-text-field v-model.number="formPostazione.slot_funzionario" label="Funzionari"
                            type="number" min="0" max="5" density="compact"/>
            </v-col>
            <v-col cols="4">
              <v-text-field v-model.number="formPostazione.slot_tas2" label="TAS 2"
                            type="number" min="0" max="5" density="compact"/>
            </v-col>
            <v-col cols="4">
              <v-text-field v-model.number="formPostazione.slot_addetto" label="Addetti"
                            type="number" min="0" max="5" density="compact"/>
            </v-col>
            <v-col cols="12" sm="6">
              <v-switch v-model="formPostazione.turni_multipli" label="Consenti doppio turno (M/P)"
                        color="primary" density="compact" hide-details/>
            </v-col>
            <v-col cols="12" sm="6">
              <v-switch v-model="formPostazione.attiva" label="Attiva" color="success"
                        density="compact" hide-details/>
            </v-col>
          </v-row>
        </v-card-text>
        <v-divider/>
        <v-card-actions>
          <v-btn variant="text" @click="dlgPostazione = false">Annulla</v-btn>
          <v-spacer/>
          <v-btn color="primary" :loading="salvando"
                 :disabled="!formPostazione.codice || !formPostazione.nome"
                 @click="salvaPostazione">
            Salva
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- ── Dialog specialità ── -->
    <v-dialog v-model="dlgSpecialita" max-width="440" persistent>
      <v-card>
        <v-card-title class="text-subtitle-1 font-weight-medium pa-4 pb-2">
          {{ formSpecialita.id ? 'Modifica specialità' : 'Nuova specialità' }}
        </v-card-title>
        <v-divider/>
        <v-card-text class="pt-4">
          <v-text-field v-model="formSpecialita.codice" label="Codice *" density="compact" class="mb-2"/>
          <v-text-field v-model="formSpecialita.descrizione" label="Descrizione" density="compact"/>
        </v-card-text>
        <v-divider/>
        <v-card-actions>
          <v-btn variant="text" @click="dlgSpecialita = false">Annulla</v-btn>
          <v-spacer/>
          <v-btn color="primary" :loading="salvando" :disabled="!formSpecialita.codice"
                 @click="salvaSpecialita">
            Salva
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- ── Dialog conferma eliminazione ── -->
    <v-dialog v-model="dlgConferma" max-width="420">
      <v-card>
        <v-card-title class="text-subtitle-1 font-weight-medium pa-4 pb-2">Conferma eliminazione</v-card-title>
        <v-card-text>
          Eliminare la specialità <strong>{{ specialitaDaEliminare?.codice }}</strong>?
        </v-card-text>
        <v-card-actions>
          <v-btn variant="text" @click="dlgConferma = false">Annulla</v-btn>
          <v-spacer/>
          <v-btn color="error" variant="tonal" :loading="salvando" @click="eseguiEliminaSpecialita">
            Elimina
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
import { ref, computed, reactive, onMounted } from 'vue'
import { usePresenzeStore } from '@/stores/presenze'
import { lookupApi, utentiApi } from '@/api/api'
import { formatDataOraIT } from '@/utils/format'

const store = usePresenzeStore()

const tab       = ref('campagne')
const salvando  = ref(false)
const snack     = ref({ show: false, text: '', color: 'success' })

// ── Headers ───────────────────────────────────────────────────────────────────
const hCampagne = [
  { title: 'Campagna',  key: 'anno',        sortable: true },
  { title: 'Inizio',    key: 'data_inizio', sortable: true },
  { title: 'Fine',      key: 'data_fine',   sortable: true },
  { title: 'Descrizione', key: 'descrizione', sortable: false },
  { title: 'Stato',     key: 'attiva',      sortable: true },
  { title: '',          key: 'azioni',      sortable: false, align: 'end' },
]
const hPostazioni = [
  { title: 'Codice',       key: 'codice',          sortable: true },
  { title: 'Nome',         key: 'nome',            sortable: true },
  { title: 'Composizione', key: 'composizione',    sortable: false },
  { title: 'Doppio turno', key: 'turni_multipli',  sortable: false },
  { title: 'Attiva',       key: 'attiva',          sortable: true },
  { title: '',             key: 'azioni',          sortable: false, align: 'end' },
]
const hSpecialita = [
  { title: 'Codice',      key: 'codice',      sortable: true },
  { title: 'Descrizione', key: 'descrizione', sortable: true },
  { title: '',            key: 'azioni',      sortable: false, align: 'end' },
]

// ── Campagne ──────────────────────────────────────────────────────────────────
const dlgCampagna  = ref(false)
const formCampagna = reactive({ id: null, anno: null, data_inizio: '', data_fine: '', descrizione: '', attiva: false })

const campagnaValida = computed(() =>
  !!formCampagna.anno && !!formCampagna.data_inizio && !!formCampagna.data_fine
)

function apriCampagna(item = null) {
  Object.assign(formCampagna, item
    ? { id: item.id, anno: item.anno, descrizione: item.descrizione || '',
        data_inizio: normData(item.data_inizio), data_fine: normData(item.data_fine),
        attiva: !!item.attiva }
    : { id: null, anno: new Date().getFullYear(), data_inizio: '', data_fine: '', descrizione: '', attiva: false })
  dlgCampagna.value = true
}

async function salvaCampagna() {
  salvando.value = true
  const body = {
    anno: formCampagna.anno,
    data_inizio: formCampagna.data_inizio,
    data_fine: formCampagna.data_fine,
    descrizione: formCampagna.descrizione || null,
    attiva: formCampagna.attiva,
  }
  const { error } = formCampagna.id
    ? await lookupApi.aggiornaCampagna(formCampagna.id, body)
    : await lookupApi.creaCampagna(body)
  salvando.value = false
  if (error) return showSnack(error, 'error')
  dlgCampagna.value = false
  showSnack('Campagna salvata')
  await store.caricaLookup()
}

// ── Postazioni ────────────────────────────────────────────────────────────────
const dlgPostazione  = ref(false)
const formPostazione = reactive({
  id: null, codice: '', nome: '', note: '', attiva: true,
  turni_multipli: false, slot_funzionario: 0, slot_tas2: 0, slot_addetto: 0,
})

function apriPostazione(item = null) {
  Object.assign(formPostazione, item
    ? { id: item.id, codice: item.codice, nome: item.nome, note: item.note || '',
        attiva: !!item.attiva, turni_multipli: !!item.turni_multipli,
        slot_funzionario: item.slot_funzionario ?? 0,
        slot_tas2: item.slot_tas2 ?? 0,
        slot_addetto: item.slot_addetto ?? 0 }
    : { id: null, codice: '', nome: '', note: '', attiva: true,
        turni_multipli: false, slot_funzionario: 0, slot_tas2: 0, slot_addetto: 0 })
  dlgPostazione.value = true
}

async function salvaPostazione() {
  salvando.value = true
  const body = { ...formPostazione }
  delete body.id
  const { error } = formPostazione.id
    ? await store.aggiornaPostazione(formPostazione.id, body)
    : await store.creaPostazione(body)
  salvando.value = false
  if (error) return showSnack(error, 'error')
  dlgPostazione.value = false
  showSnack('Postazione salvata')
  await store.caricaLookup()
}

// ── Specialità ────────────────────────────────────────────────────────────────
const specialitaList = ref([])
const dlgSpecialita  = ref(false)
const dlgConferma    = ref(false)
const specialitaDaEliminare = ref(null)
const formSpecialita = reactive({ id: null, codice: '', descrizione: '' })

async function caricaSpecialita() {
  const { data } = await lookupApi.specialita()
  if (data) specialitaList.value = data
}

function apriSpecialita(item = null) {
  Object.assign(formSpecialita, item
    ? { id: item.id, codice: item.codice, descrizione: item.descrizione || '' }
    : { id: null, codice: '', descrizione: '' })
  dlgSpecialita.value = true
}

async function salvaSpecialita() {
  salvando.value = true
  const body = { codice: formSpecialita.codice, descrizione: formSpecialita.descrizione || null }
  const { error } = formSpecialita.id
    ? await lookupApi.aggiornaSpecialita(formSpecialita.id, body)
    : await lookupApi.creaSpecialita(body)
  salvando.value = false
  if (error) return showSnack(error, 'error')
  dlgSpecialita.value = false
  showSnack('Specialità salvata')
  await caricaSpecialita()
}

function chiediEliminaSpecialita(item) {
  specialitaDaEliminare.value = item
  dlgConferma.value = true
}

async function eseguiEliminaSpecialita() {
  salvando.value = true
  const { error } = await lookupApi.eliminaSpecialita(specialitaDaEliminare.value.id)
  salvando.value = false
  dlgConferma.value = false
  if (error) return showSnack(error, 'error')
  showSnack('Specialità eliminata')
  await caricaSpecialita()
}

// ── Utenti ────────────────────────────────────────────────────────────────────
const utentiList  = ref([])
const dlgUtente   = ref(false)
const dlgResetPwd = ref(false)
const utenteReset = ref(null)
const nuovaPwd    = ref('')
const ruoliDisponibili = ['admin', 'responsabile', 'dipendente']

const hUtenti = [
  { title: 'Username',       key: 'username',       sortable: true },
  { title: 'Ruolo',          key: 'ruolo',          sortable: true },
  { title: 'Dipendente',     key: 'nominativo',     sortable: true },
  { title: 'Ultimo accesso', key: 'ultimo_accesso', sortable: true },
  { title: 'Attivo',         key: 'attivo',         sortable: true },
  { title: '',               key: 'azioni',         sortable: false, align: 'end' },
]

const formUtente = reactive({
  id: null, username: '', password: '', ruolo: 'dipendente',
  personale_id: null, comando_id: null, attivo: true,
})

const utenteValido = computed(() => {
  if (!formUtente.username || !formUtente.ruolo) return false
  if (!formUtente.id && formUtente.password.length < 6) return false
  return true
})

async function caricaUtenti() {
  const { data } = await utentiApi.lista()
  if (data) utentiList.value = data
}

function apriUtente(item = null) {
  Object.assign(formUtente, item
    ? { id: item.id, username: item.username, password: '',
        ruolo: item.ruolo, personale_id: item.personale_id || null,
        comando_id: item.comando_id || null, attivo: !!item.attivo }
    : { id: null, username: '', password: '', ruolo: 'dipendente',
        personale_id: null, comando_id: null, attivo: true })
  dlgUtente.value = true
}

async function salvaUtente() {
  salvando.value = true
  const body = {
    ruolo:        formUtente.ruolo,
    personale_id: formUtente.personale_id,
    comando_id:   formUtente.comando_id,
    attivo:       formUtente.attivo,
  }
  let error
  if (formUtente.id) {
    ({ error } = await utentiApi.aggiorna(formUtente.id, body))
  } else {
    ({ error } = await utentiApi.crea({ ...body, username: formUtente.username, password: formUtente.password }))
  }
  salvando.value = false
  if (error) return showSnack(error, 'error')
  dlgUtente.value = false
  showSnack('Utente salvato')
  await caricaUtenti()
}

function apriResetPassword(item) {
  utenteReset.value = item
  nuovaPwd.value = ''
  dlgResetPwd.value = true
}

async function salvaResetPassword() {
  salvando.value = true
  const { error } = await utentiApi.resetPassword(utenteReset.value.id, nuovaPwd.value)
  salvando.value = false
  dlgResetPwd.value = false
  if (error) return showSnack(error, 'error')
  showSnack('Password resettata')
}

function coloreRuolo(r) {
  return { admin: 'error', responsabile: 'warning', dipendente: 'info' }[r] || 'grey'
}

function fmtDataOra(v) {
  return formatDataOraIT(v)
}

// ── Utilità ───────────────────────────────────────────────────────────────────
function normData(v) {
  if (!v) return ''
  return String(v).slice(0, 10)
}
function fmtData(v) {
  const s = normData(v)
  if (!s) return '—'
  const [y, m, d] = s.split('-')
  return `${d}/${m}/${y}`
}
function showSnack(text, color = 'success') {
  snack.value = { show: true, text, color }
}

onMounted(() => {
  // Tutto in parallelo: nessuna tab aspetta le altre
  caricaSpecialita()
  caricaUtenti()
  if (!store.postazioni.length) store.caricaLookup()
})
</script>
