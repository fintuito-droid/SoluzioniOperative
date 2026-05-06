import { createRouter, createWebHistory } from 'vue-router'


// ======================================================
// DEFINIZIONE ROTTE APPLICAZIONE
// ======================================================

const routes = [

  // HOME
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/HomeView.vue'),
    meta: {
      title: 'Home'
    }
  },

  // ======================================================
  // PROTOCOLLO MONITOR
  // ======================================================

  {
    path: '/protocollo-monitor/protocolli',
    name: 'ProtocolloMonitorProtocolli',
    component: () =>
      import('../views/protocollo-monitor/ProtocolliAcquisitiView.vue'),
    meta: {
      title: 'Protocolli acquisiti',
      modulo: 'ProtocolloMonitor'
    }
  },

  {
  path: '/protocollo-monitor/protocolli/:idProtocollo',
  name: 'ProtocolloMonitorDettaglio',
  component: () =>
    import('../views/protocollo-monitor/ProtocolloDettaglioView.vue'),
  meta: {
    title: 'Dettaglio protocollo',
    modulo: 'ProtocolloMonitor'
  }
}

  

]



// ======================================================
// CREAZIONE ROUTER
// ======================================================

const router = createRouter({
  history: createWebHistory(),
  routes
})



// ======================================================
// CAMBIO TITOLO PAGINA AUTOMATICO
// ======================================================

router.afterEach((to) => {
  document.title = to.meta.title || 'SoluzioniOperative'
})





// ======================================================
// EXPORT
// ======================================================

export default router