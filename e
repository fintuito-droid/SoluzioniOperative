[35mbackend/main.py[m[36m:[m# Esporre tramite API web i [1;31mprotocolli[m già acquisiti da Vigilia/Grisù
[35mbackend/main.py[m[36m:[m@app.get("/protocollo-monitor/[1;31mprotocolli[m")
[35mbackend/main.py[m[36m:[mdef get_[1;31mprotocolli[m():
[35mbackend/main.py[m[36m:[m    Restituisce l'elenco dei [1;31mprotocolli[m acquisiti da Vigilia.
[35mfrontend/src/App.vue[m[36m:[m          Gestione [1;31mprotocolli[m, pratiche e documenti
[35mfrontend/src/App.vue[m[36m:[m          to="/protocollo-monitor/[1;31mprotocolli[m"
[35mfrontend/src/App.vue[m[36m:[m                Piattaforma operativa per la gestione dei [1;31mprotocolli[m acquisiti da Vigilia.
[35mfrontend/src/router/index.js[m[36m:[m    path: '/protocollo-monitor/[1;31mprotocolli[m',
[35mfrontend/src/views/protocollo-monitor/ProtocolliAcquisitiView.vue[m[36m:[m        <v-card rounded="xl" elevation="2" class="card-[1;31mprotocolli[m">
[35mfrontend/src/views/protocollo-monitor/ProtocolliAcquisitiView.vue[m[36m:[m              {{ [1;31mprotocolli[mFiltrati.length }} record
[35mfrontend/src/views/protocollo-monitor/ProtocolliAcquisitiView.vue[m[36m:[m  :items="[1;31mprotocolli[mFiltrati"
[35mfrontend/src/views/protocollo-monitor/ProtocolliAcquisitiView.vue[m[36m:[m  class="elevation-0 tabella-[1;31mprotocolli[m"
[35mfrontend/src/views/protocollo-monitor/ProtocolliAcquisitiView.vue[m[36m:[m// Mostra i [1;31mprotocolli[m acquisiti da Vigilia tramite Grisù.
[35mfrontend/src/views/protocollo-monitor/ProtocolliAcquisitiView.vue[m[36m:[mconst [1;31mprotocolli[m = ref([])
[35mfrontend/src/views/protocollo-monitor/ProtocolliAcquisitiView.vue[m[36m:[mconst [1;31mprotocolli[mFiltrati = computed(() => {
[35mfrontend/src/views/protocollo-monitor/ProtocolliAcquisitiView.vue[m[36m:[m  return [1;31mprotocolli[m.value.filter((p) => {
[35mfrontend/src/views/protocollo-monitor/ProtocolliAcquisitiView.vue[m[36m:[m      'http://127.0.0.1:8000/protocollo-monitor/[1;31mprotocolli[m'
[35mfrontend/src/views/protocollo-monitor/ProtocolliAcquisitiView.vue[m[36m:[m    [1;31mprotocolli[m.value = await response.json()
[35mfrontend/src/views/protocollo-monitor/ProtocolliAcquisitiView.vue[m[36m:[m    console.error('Errore durante il caricamento dei [1;31mprotocolli[m:', error)
[35mfrontend/src/views/protocollo-monitor/ProtocolliAcquisitiView.vue[m[36m:[m    alert('Errore durante il caricamento dei [1;31mprotocolli[m da FastAPI.')
[35mfrontend/src/views/protocollo-monitor/ProtocolliAcquisitiView.vue[m[36m:[m    const index = [1;31mprotocolli[m.value.findIndex(
[35mfrontend/src/views/protocollo-monitor/ProtocolliAcquisitiView.vue[m[36m:[m      [1;31mprotocolli[m.value[index] = { ...protocolloSelezionato.value }
[35mfrontend/src/views/protocollo-monitor/ProtocolliAcquisitiView.vue[m[36m:[m.card-[1;31mprotocolli[m {
[35mfrontend/src/views/protocollo-monitor/ProtocolliAcquisitiView.vue[m[36m:[m.tabella-[1;31mprotocolli[m {
