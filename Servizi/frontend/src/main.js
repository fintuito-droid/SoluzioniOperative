// main.js — Entry point Vue + Vuetify 4 + Pinia
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'

// Vuetify 3
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
      { path: '',          redirect: '/presenze' },
      { path: 'presenze',  component: () => import('./views/PresenzeView.vue') },
      { path: 'calendario',component: () => import('./views/CalendarioView.vue') },
      { path: 'monte-ore', component: () => import('./views/MonteOreView.vue') },
      { path: 'anagrafica',component: () => import('./views/AnagraficaView.vue'), meta: { roles: ['admin','responsabile'] } },
      { path: 'impostazioni', component: () => import('./views/ImpostazioniView.vue'), meta: { roles: ['admin'] } },
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Guard globale
router.beforeEach((to, from, next) => {
  const auth = useAuthStore()
  if (to.meta.public) return next()
  if (!auth.isAuth)   return next('/login')
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
