<template>
  <v-app>
    <v-navigation-drawer v-model="drawer" app>
      <v-list nav density="comfortable">
        <v-list-item
          prepend-icon="mdi-clipboard-check"
          title="Checklist XR33"
          @click="goTo('/xr33')"
        />
      </v-list>
    </v-navigation-drawer>

    <v-app-bar color="primary">
      <v-app-bar-nav-icon @click="drawer = !drawer" />
      <v-app-bar-title>XR33 - Ricognizione VVF</v-app-bar-title>
      <v-spacer />
      <v-btn variant="text" @click="logout">Logout</v-btn>
    </v-app-bar>

    <v-main>
      <v-container fluid class="pa-4">
        <router-view />
      </v-container>
    </v-main>
  </v-app>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";

const drawer = ref(true);
const router = useRouter();

function logout() {
  localStorage.removeItem("token");
  router.push("/");
}

function goTo(path) {
  router.push(path);
}
</script>