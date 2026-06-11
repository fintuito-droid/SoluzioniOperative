<template>
  <v-app>
    <!-- Nav drawer -->
    <v-navigation-drawer v-model="drawer" :rail="rail" permanent>
      <v-list-item
        prepend-icon="mdi-fire"
        title="SoluzioniOperative"
        :subtitle="`Servizi — AIB ${presenze.campagnaAttiva?.anno || ''}`"
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
          v-for="item in navItems"
          :key="item.to"
          :prepend-icon="item.icon"
          :title="item.title"
          :to="item.to"
          :value="item.to"
          color="primary"
          rounded="lg"
        />
      </v-list>

      <template #append>
        <v-list density="compact" nav>
          <v-list-item
            prepend-icon="mdi-logout"
            title="Esci"
            @click="handleLogout"
            color="error"
            rounded="lg"
          />
        </v-list>
        <div v-if="!rail" class="px-4 pb-3 text-caption text-disabled">
          Campagna attiva: {{ presenze.campagnaAttiva?.anno || '—' }}
        </div>
      </template>
    </v-navigation-drawer>

    <!-- App bar mobile -->
    <v-app-bar :elevation="1" color="primary" v-if="mobile">
      <v-app-bar-nav-icon @click="drawer = !drawer"/>
      <v-app-bar-title>SoluzioniOperative — Servizi</v-app-bar-title>
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
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useDisplay } from 'vuetify'
import { useAuthStore } from '@/stores/auth'
import { usePresenzeStore } from '@/stores/presenze'

const auth     = useAuthStore()
const presenze = usePresenzeStore()
const router   = useRouter()
const { mobile } = useDisplay()
const drawer   = ref(true)
const rail     = ref(false)

const navItems = computed(() => {
  const items = [
    { to: '/presenze',   icon: 'mdi-calendar-check', title: 'Presenze' },
    { to: '/calendario', icon: 'mdi-calendar-month',  title: 'Calendario' },
    { to: '/monte-ore',  icon: 'mdi-chart-bar',        title: 'Monte ore' },
  ]
  if (auth.canPlanificare) {
    items.push({ to: '/anagrafica', icon: 'mdi-account-group', title: 'Anagrafica' })
  }
  if (auth.isAdmin) {
    items.push({ to: '/impostazioni', icon: 'mdi-cog', title: 'Impostazioni' })
  }
  return items
})

async function handleLogout() {
  await auth.logout()
  router.push('/login')
}

onMounted(() => presenze.caricaLookup())
</script>
