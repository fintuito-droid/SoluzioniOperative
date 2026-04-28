import 'vuetify/styles'
import '@mdi/font/css/materialdesignicons.css'
import { createVuetify } from 'vuetify'

const vuetify = createVuetify({
  theme: {
    defaultTheme: 'light',
    themes: {
      light: {
        colors: {
          primary: '#B71C1C',
          secondary: '#37474F',
          success: '#2E7D32',
          warning: '#ED6C02',
          error: '#D32F2F',
          info: '#0288D1',
          background: '#F5F7FA',
          surface: '#FFFFFF',
        },
      },
    },
  },
})

export default vuetify