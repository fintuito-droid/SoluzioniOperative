<template>
  <div>
    <h1>Login XR33</h1>

    <input v-model="username" placeholder="username" />
    <input v-model="password" type="password" placeholder="password" />

    <button @click="login">Accedi</button>

    <p v-if="error">{{ error }}</p>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import api from "../api";

const username = ref("");
const password = ref("");
const error = ref("");
const router = useRouter();

async function login() {
  try {
    const res = await api.post("/login", {
      username: username.value,
      password: password.value,
    });

    localStorage.setItem("token", res.data.access_token);
    router.push("/xr33");
  } catch (e) {
    error.value = "Login fallito";
  }
}
</script>