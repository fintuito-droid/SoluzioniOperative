<template>
  <div>
    <div class="mb-6 mt-2">
      <div class="text-h5 font-weight-bold">
        Benvenuto, {{ auth.user?.username }}
      </div>
      <div class="text-body-2 text-medium-emphasis mt-1">
        Seleziona un modulo per iniziare. I moduli con il lucchetto non sono abilitati per il tuo utente.
      </div>
    </div>

    <v-row>
      <v-col v-for="m in MODULI" :key="m.codice" cols="12" sm="6" md="4">
        <v-card
          class="modulo-card h-100"
          :class="{ 'modulo-disabilitato': !apribile(m) }"
          :elevation="apribile(m) ? 2 : 0"
          @click="apri(m)"
        >
          <v-card-item>
            <div class="d-flex align-center ga-3 py-2">
              <v-avatar :color="apribile(m) ? m.colore : 'grey-lighten-1'" size="48" rounded="lg">
                <v-icon :icon="m.icona" color="white" size="28"/>
              </v-avatar>
              <div>
                <v-card-title class="pa-0">{{ m.nome }}</v-card-title>
                <v-card-subtitle class="pa-0">{{ m.descrizione }}</v-card-subtitle>
              </div>
            </div>
          </v-card-item>

          <v-divider/>

          <v-card-actions class="px-4">
            <template v-if="!m.migrato">
              <v-chip size="small" color="grey" variant="tonal" prepend-icon="mdi-progress-wrench">
                In migrazione
              </v-chip>
            </template>
            <template v-else-if="!abilitato(m)">
              <v-chip size="small" color="grey" variant="tonal" prepend-icon="mdi-lock">
                Non abilitato
              </v-chip>
            </template>
            <template v-else>
              <v-btn color="primary" variant="tonal" append-icon="mdi-arrow-right">
                Apri
              </v-btn>
            </template>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { MODULI } from '@/moduli'

const auth   = useAuthStore()
const router = useRouter()

// Abilitazione per utente: dal backend (tabella utenti_moduli, admin = tutti)
function abilitato(m) {
  return auth.hasModulo(m.codice)
}

function apribile(m) {
  return m.migrato && abilitato(m)
}

function apri(m) {
  if (apribile(m)) router.push(m.rotta)
}
</script>

<style scoped>
.modulo-card {
  cursor: pointer;
  transition: transform 120ms ease, box-shadow 120ms ease;
}
.modulo-card:hover:not(.modulo-disabilitato) {
  transform: translateY(-2px);
}
.modulo-disabilitato {
  cursor: default;
  opacity: 0.75;
}
</style>
