<template>
  <v-app>
    <v-main class="bg-background">
      <v-container class="d-flex align-center justify-center" style="min-height:100vh">
        <v-card width="400" :loading="auth.loading">
          <v-card-item>
            <div class="d-flex align-center gap-3 py-2">
              <v-icon icon="mdi-fire" color="primary" size="32"/>
              <div>
                <v-card-title class="pa-0">SoluzioniOperative</v-card-title>
                <v-card-subtitle class="pa-0">Modulo AIB 2026 — VVF</v-card-subtitle>
              </div>
            </div>
          </v-card-item>

          <v-divider/>

          <v-card-text>
            <v-alert v-if="auth.error" type="error" variant="tonal"
                     class="mb-4" :text="auth.error" density="compact"/>

            <v-text-field
              v-model="form.username"
              label="Username"
              prepend-inner-icon="mdi-account"
              autocomplete="username"
              class="mb-3"
              @keyup.enter="handleLogin"
            />
            <v-text-field
              v-model="form.password"
              label="Password"
              :type="showPwd ? 'text' : 'password'"
              prepend-inner-icon="mdi-lock"
              :append-inner-icon="showPwd ? 'mdi-eye-off' : 'mdi-eye'"
              @click:append-inner="showPwd = !showPwd"
              autocomplete="current-password"
              @keyup.enter="handleLogin"
            />
          </v-card-text>

          <v-card-actions class="px-4 pb-4">
            <v-btn block color="primary" size="large" :loading="auth.loading"
                   @click="handleLogin">
              Accedi
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-container>
    </v-main>
  </v-app>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth   = useAuthStore()
const router = useRouter()
const showPwd = ref(false)
const form   = ref({ username: '', password: '' })

async function handleLogin() {
  const ok = await auth.login(form.value.username, form.value.password)
  if (ok) router.push('/')
}
</script>
