import { createRouter, createWebHistory } from "vue-router";
import LoginView from "../views/LoginView.vue";
import ChecklistXR33View from "../views/ChecklistXR33View.vue";
import MainLayout from "../layouts/MainLayout.vue";

const routes = [
  {
    path: "/",
    component: LoginView,
  },
  {
    path: "/",
    component: MainLayout,
    children: [
      {
        path: "xr33",
        component: ChecklistXR33View,
      },
    ],
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;