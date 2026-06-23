import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/Home.vue'),
  },
  {
    path: '/upload',
    name: 'UploadResume',
    component: () => import('../views/UploadResume.vue'),
  },
  {
    path: '/configure',
    name: 'ConfigureInterview',
    component: () => import('../views/ConfigureInterview.vue'),
  },
  {
    path: '/interview',
    name: 'InterviewSession',
    component: () => import('../views/InterviewSession.vue'),
  },
  {
    path: '/results',
    name: 'Results',
    component: () => import('../views/Results.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
