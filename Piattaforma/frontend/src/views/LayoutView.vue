<template>
  <v-app>
    <!-- Nav drawer -->
    <v-navigation-drawer v-model="drawer" :rail="rail" permanent>
      <v-list-item
        :prepend-icon="moduloCorrente?.icona || 'mdi-apps'"
        title="SoluzioniOperative"
        :subtitle="sottotitolo"
        nav
      >
        <template #append>
          <v-btn :icon="rail ? 'mdi-chevron-right' : 'mdi-chevron-left'"
                 variant="text" @click="rail = !rail"/>
        </template>
      </v-list-item>

      <v-list-item
        v-if="!rail"
        prepend-icon="mdi-account-circle"
        :title="auth.user?.username"
        :subtitle="auth.user?.ruolo"
        density="compact"
      />

      <v-divider/>

      <v-list density="compact" nav>
        <v-list-item
          prepend-icon="mdi-home-outline"
          title="Home moduli"
          to="/"
          exact
          color="primary"
          rounded="lg"
        />

        <template v-if="navItems.length">
          <v-divider class="my-2"/>
          <v-list-subheader v-if="!rail">{{ moduloCorrente?.nome?.toUpperCase() }}</v-list-subheader>
          <v-list-item
            v-for="item in navItems"
            :key="item.to"
            :prepend-icon="item.icon"
            :title="item.title"
            :to="item.to"
            :value="item.to"
            color="primary"
            rounded="lg"
          />
        </template>
      </v-list>

      <template #append>
        <v-list density="compact" nav>
          <v-list-item
            prepend-icon="mdi-key-variant"
            title="Cambia password"
            @click="dialogPassword = true"
            rounded="lg"
          />
          <v-list-item
            prepend-icon="mdi-logout"
            title="Esci"
            @click="handleLogout"
            color="error"
            rounded="lg"
          />
        </v-list>
        <div v-if="!rail && moduloAttivo === 'servizi'" class="px-4 pb-3 text-caption text-disabled">
          Campagna attiva: {{ presenze.campagnaAttiva?.anno || '—' }}
        </div>
      </template>
    </v-navigation-drawer>

    <!-- ── Dialog cambio password ── -->
    <v-dialog v-model="dialogPassword" max-width="440" persistent>
      <v-card>
        <v-card-title class="text-subtitle-1 font-weight-medium pa-4 pb-2">
          Cambia password
        </v-card-title>
        <v-divider/>
        <v-card-text class="pt-4">
          <v-text-field
            v-model="pwd.vecchia"
            label="Password attuale *"
            type="password"
            density="compact"
            class="mb-2"
          />
          <v-text-field
            v-model="pwd.nuova"
            label="Nuova password *"
            type="password"
            density="compact"
            :rules="[v => !v || v.length >= 6 || 'Minimo 6 caratteri']"
            class="mb-2"
          />
          <v-text-field
            v-model="pwd.conferma"
            label="Conferma nuova password *"
            type="password"
            density="compact"
            :error-messages="pwd.conferma && pwd.conferma !== pwd.nuova ? 'Le password non coincidono' : ''"
          />
        </v-card-text>
        <v-divider/>
        <v-card-actions>
          <v-btn variant="text" @click="chiudiDialogPassword">Annulla</v-btn>
          <v-spacer/>
          <v-btn
            color="primary"
            :loading="cambiandoPassword"
            :disabled="!pwd.vecchia || pwd.nuova.length < 6 || pwd.nuova !== pwd.conferma"
            @click="salvaPassword"
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

    <!-- App bar mobile -->
    <v-app-bar :elevation="1" color="primary" v-if="mobile">
      <v-app-bar-nav-icon @click="drawer = !drawer"/>
      <v-app-bar-title>{{ titoloMobile }}</v-app-bar-title>
    </v-app-bar>

    <!-- Contenuto -->
    <v-main>
      <v-container fluid class="pa-4">
        <router-view v-slot="{ Component }">
          <transition name="vista-fade" mode="out-in">
            <component :is="Component"/>
          </transition>
        </router-view>
      </v-container>
    </v-main>
  </v-app>
</template>

<style scoped>
.vista-fade-enter-active,
.vista-fade-leave-active {
  transition: opacity 150ms ease;
}
.vista-fade-enter-from,
.vista-fade-leave-to {
  opacity: 0;
}
</style>

<script setup>
import { ref, computed, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useDisplay } from 'vuetify'
import { useAuthStore } from '@/stores/auth'
import { usePresenzeStore } from '@/stores/presenze'
import { authApi } from '@/api/api'
import { MODULI } from '@/moduli'

const auth     = useAuthStore()
const presenze = usePresenzeStore()
const route    = useRoute()
const router   = useRouter()
const { mobile } = useDisplay()
const drawer   = ref(true)
const rail     = ref(false)

// ── Modulo attivo (dalla meta della rotta) ─────────────────────────────────
const moduloAttivo   = computed(() => route.meta.modulo || null)
const moduloCorrente = computed(() => MODULI.find(m => m.codice === moduloAttivo.value) || null)

const sottotitolo = computed(() => {
  if (moduloAttivo.value === 'servizi') {
    return `Servizi — AIB ${presenze.campagnaAttiva?.anno || ''}`
  }
  return moduloCorrente.value?.nome || 'Piattaforma'
})

const titoloMobile = computed(() =>
  moduloCorrente.value ? `SoluzioniOperative — ${moduloCorrente.value.nome}` : 'SoluzioniOperative'
)

// ── Cambio password ────────────────────────────────────────────────────────
const dialogPassword    = ref(false)
const cambiandoPassword = ref(false)
const pwd   = reactive({ vecchia: '', nuova: '', conferma: '' })
const snack = ref({ show: false, text: '', color: 'success' })

function chiudiDialogPassword() {
  dialogPassword.value = false
  pwd.vecchia = pwd.nuova = pwd.conferma = ''
}

async function salvaPassword() {
  cambiandoPassword.value = true
  const { error } = await authApi.cambiaPassword(pwd.vecchia, pwd.nuova)
  cambiandoPassword.value = false
  if (error) {
    snack.value = { show: true, text: error, color: 'error' }
  } else {
    chiudiDialogPassword()
    snack.value = { show: true, text: 'Password aggiornata', color: 'success' }
  }
}

// ── Voci di navigazione per modulo ─────────────────────────────────────────
const navServizi = computed(() => {
  const items = [
    { to: '/servizi/presenze',   icon: 'mdi-calendar-check', title: 'Presenze' },
    { to: '/servizi/calendario', icon: 'mdi-calendar-month', title: 'Calendario' },
    { to: '/servizi/monte-ore',  icon: 'mdi-chart-bar',      title: 'Monte ore' },
  ]
  if (auth.isAdmin) {
    items.push({ to: '/servizi/report', icon: 'mdi-file-chart', title: 'Report' })
  }
  if (auth.canPlanificare) {
    items.push({ to: '/servizi/anagrafica', icon: 'mdi-account-group', title: 'Anagrafica' })
  }
  if (auth.isAdmin) {
    items.push({ to: '/servizi/impostazioni', icon: 'mdi-cog', title: 'Impostazioni' })
  }
  return items
})

const navProtocolloMonitor = [
  { to: '/protocollo-monitor/protocolli',   icon: 'mdi-file-document-outline',  title: 'Protocolli acquisiti' },
  { to: '/protocollo-monitor/procedimenti', icon: 'mdi-folder-table-outline',   title: 'Procedimenti' },
]

const navXr33 = [
  { to: '/xr33', icon: 'mdi-clipboard-check-outline', title: 'Checklist XR33' },
]

const navItems = computed(() => {
  if (moduloAttivo.value === 'servizi')             return navServizi.value
  if (moduloAttivo.value === 'protocollo-monitor')  return navProtocolloMonitor
  if (moduloAttivo.value === 'xr33')                return navXr33
  return []
})

async function handleLogout() {
  await auth.logout()
  router.push('/login')
}

onMounted(() => presenze.caricaLookup())
</script>
