<template>
  <v-app>
    <v-main class="stage">

      <div
        class="grisu-zone"
        :class="stato"
        @click="attivaGrisu"
      >
        <img
          :src="stato === 'idle'
            ? baseUrl + 'img/grisu_piccolo.png'
            : baseUrl + 'img/grisu_fly.png'"
          class="grisu-img"
        />
      </div>

      <v-card
        v-if="pannelloVisibile"
        class="panel"
        :class="{ exiting: stato === 'exiting' }"
        elevation="12"
      >
        <v-card-text class="panel-content">

          <div class="check-area">
            <v-checkbox
              v-model="daLavorare"
              label="Da lavorare"
              density="compact"
              hide-details
              class="compact-check"
            />

            <v-checkbox
              v-model="usaScadenza"
              label="Scadenza"
              density="compact"
              hide-details
              class="compact-check"
            />
          </div>

          <div class="field-area">
            <v-text-field
              v-if="usaScadenza"
              v-model="dataScadenza"
              type="date"
              density="compact"
              variant="outlined"
              hide-details
              class="date-field"
            />

            <v-select
              v-if="mostraTipoDocumento"
              v-model="tipoDocumento"
              :items="valoriTipoDocumento"
              label="Tipo documento"
              density="compact"
              variant="outlined"
              hide-details
              class="type-field"
            />
          </div>

          <v-btn
            size="small"
            color="primary"
            class="acquisisci-btn"
            @click="acquisisci"
          >
            Acquisisci
          </v-btn>

        </v-card-text>
      </v-card>

    </v-main>
  </v-app>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const baseUrl = import.meta.env.BASE_URL

const stato = ref('idle')
const pannelloVisibile = ref(false)

const daLavorare = ref(false)
const usaScadenza = ref(false)
const dataScadenza = ref('')

const mostraTipoDocumento = ref(false)
const valoriTipoDocumento = ref([])
const tipoDocumento = ref('')

onMounted(() => {
  window.addEventListener('message', (event) => {
    if (!event.data) return
    if (event.data.source !== 'protocollo-monitor') return
    if (event.data.type !== 'CONFIG_GRISU') return

    mostraTipoDocumento.value = event.data.mostraTipoDocumento === true
    valoriTipoDocumento.value = event.data.valoriTipoDocumento || []
  })
})

function attivaGrisu() {
  if (stato.value !== 'idle') return

  stato.value = 'flying'

  setTimeout(() => {
    stato.value = 'arrived'
    pannelloVisibile.value = true
  }, 850)
}

async function acquisisci() {
  const dati = {
    daLavorare: daLavorare.value,
    dataScadenza: usaScadenza.value ? dataScadenza.value : null,
    tipoDocumento: mostraTipoDocumento.value ? tipoDocumento.value : null
  }

  window.parent.postMessage({
    source: 'grisu-v2',
    type: 'ACQUISISCI_PROTOCOLLO',
    dati
  }, '*')

  stato.value = 'exiting'

  setTimeout(() => {
    pannelloVisibile.value = false
    stato.value = 'idle'
  }, 1200)
}
</script>

<style scoped>

:global(html),
:global(body),
:global(#app),
:global(.v-application),
:global(.v-main),
:global(.v-main__wrap) {
  background: transparent !important;
  background-color: transparent !important;
}
.stage {
  --grisu-size-idle: clamp(80px, 6vw, 105px);
  --grisu-size-active: clamp(105px, 8vw, 140px);

  --zona-alta: 6vh;

  --zona-sinistra-nascosta: 10px;
  --zona-sinistra-visibile: 30px;

  --zona-centro: 34vw;
  --zona-pannello: calc(var(--zona-centro) + var(--grisu-size-active) + 1.5vw);

  --zona-uscita-destra: 125vw;

  min-height: 100vh;
  background: transparent !important;
  background-color: transparent !important;
  position: relative;
  overflow: visible;

  pointer-events: auto;
}

.grisu-zone {
  position: fixed;
  z-index: 1000;
  cursor: pointer;
  pointer-events: auto;
}

.grisu-img {
  width: 100%;
  height: auto;
  filter: drop-shadow(0 6px 10px rgba(0,0,0,0.25));
}

.grisu-zone.idle {
  top: var(--zona-alta);
  left: var(--zona-sinistra-nascosta);
  width: var(--grisu-size-idle);
  height: var(--grisu-size-idle);
  animation: peek 5s ease-in-out infinite;
}

.grisu-zone.flying {
  animation: flyToCenter 0.85s ease-out forwards;
}

.grisu-zone.arrived {
  top: var(--zona-alta);
  left: var(--zona-centro);
  width: var(--grisu-size-active);
  height: var(--grisu-size-active);
}

.grisu-zone.arrived .grisu-img {
  animation: floaty 1.7s ease-in-out infinite;
}

.grisu-zone.exiting {
  top: var(--zona-alta);
  left: var(--zona-centro);
  width: var(--grisu-size-active);
  height: var(--grisu-size-active);
  animation: pushOut 1.15s cubic-bezier(0.45, 0, 0.55, 1) forwards;
}

.panel {
  position: fixed;
  top: var(--zona-alta);
  left: var(--zona-pannello);

  width: auto;
  min-width: 520px;
  max-width: 720px;

  border-radius: 18px;
  z-index: 999;
  pointer-events: auto;

  opacity: 0;
  transform: translateX(-2vw) scale(0.94);
  animation: panelIn 0.45s ease-out forwards;
}

.panel-content {
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  gap: 12px;
  padding: 8px 10px !important;
}

.check-area {
  display: flex;
  align-items: center;
  gap: 8px;
}

.field-area {
  display: flex;
  align-items: center;
  gap: 8px;
}

.compact-check {
  margin: 0 !important;
  white-space: nowrap;
}

.date-field {
  width: 145px;
}

.type-field {
  width: 180px;
}

.acquisisci-btn {
  white-space: nowrap;
}


.panel.exiting {
  animation: panelPushOut 1.15s cubic-bezier(0.45, 0, 0.55, 1) forwards;
}

@keyframes peek {
  0%,72%,100% {
    left: var(--zona-sinistra-nascosta);
  }

  80%,100% {
    left: var(--zona-sinistra-visibile);
  }
}

@keyframes flyToCenter {
  from {
    top: var(--zona-alta);
    left: var(--zona-sinistra-visibile);
    width: var(--grisu-size-idle);
    height: var(--grisu-size-idle);
  }

  to {
    top: var(--zona-alta);
    left: var(--zona-centro);
    width: var(--grisu-size-active);
    height: var(--grisu-size-active);
  }
}

@keyframes pushOut {
  from {
    transform: translateX(0);
  }

  to {
    transform: translateX(var(--zona-uscita-destra));
  }
}

@keyframes panelIn {
  to {
    opacity: 1;
    transform: translateX(0) scale(1);
  }
}

@keyframes panelPushOut {
  from {
    opacity: 1;
    transform: translateX(0) scale(1);
  }

  to {
    opacity: 0;
    transform: translateX(var(--zona-uscita-destra)) scale(0.96);
  }
}

@keyframes floaty {
  0%,100% {
    transform: translateY(0) rotate(-2deg);
  }

  50% {
    transform: translateY(-0.8vh) rotate(2deg);
  }
}
</style>