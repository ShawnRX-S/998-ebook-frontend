import { createRouter, createWebHistory } from 'vue-router'
import Books from '../views/Books.vue'
import BookDetail from '../views/BookDetail.vue'
import Orders from '../views/Orders.vue'
import Login from '../views/Login.vue'
import { ElMessage } from 'element-plus'
import { isLoggedIn } from '../utils/authStore'

const routes = [
  { path: '/', redirect: '/books' },
  { path: '/books', component: Books },
  { path: '/books/:id', component: BookDetail },
  { path: '/orders', component: Orders, meta: { requiresAuth: true } },
  { path: '/login', component: Login }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  if (to.meta && to.meta.requiresAuth && !isLoggedIn()) {
    ElMessage.warning('Please login first!')
    next({ path: '/login', query: { redirect: to.fullPath } })
    return
  }

  next()
})

export default router