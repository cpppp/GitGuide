import { createRouter, createWebHistory } from 'vue-router'
import Home from '@/views/Home.vue'
import Documentation from '@/views/Documentation.vue'
import Chat from '@/views/Chat.vue'
import Repositories from '@/views/Repositories.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/docs',
    name: 'Documentation',
    component: Documentation
  },
  {
    path: '/chat',
    name: 'Chat',
    component: Chat
  },
  {
    path: '/repositories',
    name: 'Repositories',
    component: Repositories
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router