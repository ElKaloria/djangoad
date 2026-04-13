import { createRouter, createWebHistory } from "vue-router";
import { isAuthenticated, isSuperuser } from "../auth";

const LoginView = () => import("../views/LoginView.vue");
const EventsView = () => import("../views/EventsView.vue");
const PlacesView = () => import("../views/PlacesView.vue");

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/login",
      name: "login",
      component: LoginView,
      meta: { guestOnly: true },
    },
    {
      path: "/events",
      name: "events",
      component: EventsView,
      meta: { requiresAuth: true },
    },
    {
      path: "/places",
      name: "places",
      component: PlacesView,
      meta: { requiresAuth: true, requiresSuperuser: true },
    },
    { path: "/", redirect: "/events" },
    { path: "/:pathMatch(.*)*", redirect: "/events" },
  ],
});

router.beforeEach((to) => {
  if (to.meta.requiresAuth && !isAuthenticated()) {
    return { name: "login", query: { redirect: to.fullPath } };
  }
  if (to.meta.requiresSuperuser && !isSuperuser()) {
    return { name: "events" };
  }
  if (to.meta.guestOnly && isAuthenticated()) {
    return { name: "events" };
  }
  return true;
});

export default router;
