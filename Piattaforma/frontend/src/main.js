// main.js — Entry point piattaforma SoluzioniOperative
// Vue + Vuetify 4 + Pinia. Le rotte di ogni modulo vivono sotto il suo
// namespace (/servizi/..., /protocollo-monitor/..., /xr33/...).
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'

import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import 'vuetify/styles'
import '@mdi/font/css/materialdesignicons.css'

import App from './App.vue'
import { useAuthStore } from './stores/auth'

// ── Vuetify tema VF ──────────────────────────────────────────────────────
const vuetify = createVuetify({
  components,
  directives,
  theme: {
    defaultTheme: 'vf',
    themes: {
      vf: {
        dark: false,
        colors: {
          primary:    '#c0392b',   // rosso VF
          secondary:  '#2c3e50',   // blu scuro istituzionale
          accent:     '#e74c3c',
          surface:    '#ffffff',
          background: '#f5f5f5',
          'on-primary': '#ffffff',
          programmato: '#1976D2',
          confermato:  '#388E3C',
          modificato:  '#F57C00',
          assente:     '#D32F2F',
        }
      }
    }
  },
  defaults: {
    VBtn:   { variant: 'tonal', rounded: 'lg' },
    VCard:  { rounded: 'lg', elevation: 1 },
    VTextField: { variant: 'outlined', density: 'comfortable' },
    VSelect:    { variant: 'outlined', density: 'comfortable' },
    VDataTable: {
      loadingText: 'Caricamento dati…',
      noDataText:  'Nessun dato disponibile',
      itemsPerPageText: 'Righe per pagina',
      hover: true,
    },
    VDialog: { transition: 'dialog-bottom-transition' },
  }
})

// ── Router ───────────────────────────────────────────────────────────────
const routes = [
  { path: '/login', component: () => import('./views/LoginView.vue'), meta: { public: true } },

  {
    path: '/',
    component: () => import('./views/LayoutView.vue'),
    meta: { requiresAuth: true },
    children: [
      // Home piattaforma: launcher dei moduli
      { path: '', component: () => import('./views/HomeView.vue') },

      // ── Modulo Servizi (AIB) ────────────────────────────────────────────
      { path: 'servizi', redirect: '/servizi/presenze' },
      { path: 'servizi/presenze',   component: () => import('./modules/servizi/views/PresenzeView.vue'),   meta: { modulo: 'servizi' } },
      { path: 'servizi/calendario', component: () => import('./modules/servizi/views/CalendarioView.vue'), meta: { modulo: 'servizi' } },
      { path: 'servizi/monte-ore',  component: () => import('./modules/servizi/views/MonteOreView.vue'),   meta: { modulo: 'servizi' } },
      { path: 'servizi/anagrafica', component: () => import('./modules/servizi/views/AnagraficaView.vue'), meta: { modulo: 'servizi', roles: ['admin','responsabile'] } },
      { path: 'servizi/report',     component: () => import('./modules/servizi/views/ReportView.vue'),     meta: { modulo: 'servizi', roles: ['admin'] } },
      { path: 'servizi/report/designer/:id', component: () => import('./modules/servizi/views/ReportDesignerView.vue'), meta: { modulo: 'servizi', roles: ['admin'] } },
      { path: 'servizi/impostazioni', component: () => import('./modules/servizi/views/ImpostazioniView.vue'), meta: { modulo: 'servizi', roles: ['admin'] } },

      // ── Modulo ProtocolloMonitor ────────────────────────────────────────
      { path: 'protocollo-monitor', redirect: '/protocollo-monitor/protocolli' },
      { path: 'protocollo-monitor/protocolli',
        component: () => import('./modules/protocollo-monitor/views/protocollo-monitor/ProtocolliAcquisitiView.vue'),
        meta: { modulo: 'protocollo-monitor' } },
      { path: 'protocollo-monitor/protocolli/:idProtocollo',
        component: () => import('./modules/protocollo-monitor/views/protocollo-monitor/NotaProtocolloView.vue'),
        meta: { modulo: 'protocollo-monitor' } },
      { path: 'protocollo-monitor/procedimenti',
        component: () => import('./modules/protocollo-monitor/views/ProcedimentiView.vue'),
        meta: { modulo: 'protocollo-monitor' } },
      { path: 'protocollo-monitor/procedimenti/:idProcedimento',
        component: () => import('./modules/protocollo-monitor/views/ProcedimentoDettaglioView.vue'),
        meta: { modulo: 'protocollo-monitor' } },

      // ── Modulo XR33 ─────────────────────────────────────────────────────
      { path: 'xr33',
        component: () => import('./modules/xr33/views/ChecklistXR33View.vue'),
        meta: { modulo: 'xr33' } },
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Guard globale: autenticazione + abilitazione modulo + ruoli
router.beforeEach((to, from, next) => {
  const auth = useAuthStore()
  if (to.meta.public) return next()
  if (!auth.isAuth)   return next('/login')
  if (to.meta.modulo && !auth.hasModulo(to.meta.modulo)) return next('/')
  if (to.meta.roles && !to.meta.roles.includes(auth.user?.ruolo)) return next('/')
  next()
})

// ── App ──────────────────────────────────────────────────────────────────
const app = createApp(App)
app.use(createPinia())
app.use(router)
app.use(vuetify)

// Valida la sessione salvata prima del mount: se il token è scaduto
// l'utente viene rimandato al login invece di vedere errori 401
const auth = useAuthStore()
auth.verificaSessione().finally(() => app.mount('#app'))
