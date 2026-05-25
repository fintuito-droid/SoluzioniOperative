<template>
  <v-app>

    <!-- BARRA SUPERIORE -->
    <v-app-bar
      color="primary"
      elevation="2"
      height="64"
    >
      <v-app-bar-nav-icon @click="drawer = !drawer" />

      <v-toolbar-title class="font-weight-bold">
        SoluzioniOperative
      </v-toolbar-title>

      <v-spacer />

      <v-chip
        color="white"
        variant="tonal"
        class="mr-3"
      >
        ProtocolloMonitor
      </v-chip>

      <v-btn icon>
        <v-icon>mdi-account-circle-outline</v-icon>
      </v-btn>
    </v-app-bar>


    <!-- MENU LATERALE -->
    <v-navigation-drawer
      v-model="drawer"
      width="310"
      color="grey-lighten-5"
    >
      <div class="pa-4">

        <div class="text-h6 font-weight-bold">
          ProtocolloMonitor
        </div>

        <div class="text-caption text-grey-darken-1">
          Gestione protocolli, pratiche e documenti
        </div>

      </div>

      <v-divider />

      <v-list nav density="comfortable">

        <v-list-subheader>
          AREA OPERATIVA
        </v-list-subheader>

        <v-list-item
          title="Home"
          subtitle="Pagina iniziale"
          prepend-icon="mdi-home-outline"
          to="/"
        />

        <v-list-item
          title="Protocolli acquisiti"
          subtitle="Note importate da Vigilia"
          prepend-icon="mdi-file-document-outline"
          to="/protocollo-monitor/protocolli"
        />

        <v-list-item
          title="Procedimenti"
          subtitle="Fascicoli operativi"
          prepend-icon="mdi-folder-table-outline"
          to="/protocollo-monitor/procedimenti"
        />

        <v-list-item
          title="Assegnazioni"
          subtitle="Smistamento pratiche"
          prepend-icon="mdi-account-arrow-right-outline"
          disabled
        />

        <v-list-item
          title="Gruppi di lavoro"
          subtitle="Team e responsabilità"
          prepend-icon="mdi-account-group-outline"
          disabled
        />

        <v-list-item
          title="Documenti generati"
          subtitle="Atti prodotti dalla pratica"
          prepend-icon="mdi-file-sign-outline"
          disabled
        />

        <v-list-item
          title="Monitoraggio pratiche"
          subtitle="Stati, scadenze e avanzamento"
          prepend-icon="mdi-chart-timeline-variant"
          disabled
        />

        <v-divider class="my-3" />

        <v-list-subheader>
          SISTEMA
        </v-list-subheader>

        <v-list-item
          title="Impostazioni"
          subtitle="Configurazione modulo"
          prepend-icon="mdi-cog-outline"
          disabled
        />

      </v-list>
    </v-navigation-drawer>


    <!-- CONTENUTO PRINCIPALE -->
    <v-main class="app-background">

      <v-container fluid class="pa-6">

        <!-- HEADER PAGINA -->
        <v-card
          class="mb-5 header-card"
          rounded="xl"
          elevation="1"
        >
          <v-card-text class="d-flex align-center justify-space-between">

            <div>
              <div class="text-h5 font-weight-bold">
                {{ titoloPagina }}
              </div>

              <div class="text-body-2 text-grey-darken-1 mt-1">
                Piattaforma operativa per la gestione dei protocolli acquisiti da Vigilia.
              </div>
            </div>

            <v-chip
              color="primary"
              variant="tonal"
              size="large"
            >
              Ambiente sviluppo
            </v-chip>

          </v-card-text>
        </v-card>

        <router-view />

      </v-container>

    </v-main>

  </v-app>
</template>


<script setup>
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'

const drawer = ref(true)
const route = useRoute()

const titoloPagina = computed(() => {
  return route.meta.title || 'SoluzioniOperative'
})
</script>


<style scoped>
.app-background {
  background:
    linear-gradient(180deg, #f5f7fb 0%, #eef2f7 100%);
  min-height: 100vh;
}

.header-card {
  border: 1px solid rgba(0, 0, 0, 0.06);
}
</style>
