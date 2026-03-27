import { createRouter, createWebHistory } from 'vue-router'
import Books from '../views/Books.vue'
import BookDetail from '../views/BookDetail.vue'
import Orders from '../views/Orders.vue'
import Cart from '../views/Cart.vue'
import Login from '../views/Login.vue'
import AdminPanel from '../views/AdminPanel.vue'
import { ElMessage } from 'element-plus'
import { hasRole, isLoggedIn } from '../utils/authStore'

const routes = [
  { path: '/', redirect: '/books' },
  { path: '/books', component: Books },
  { path: '/books/:id', component: BookDetail },
  { path: '/orders', component: Orders, meta: { requiresAuth: true } },
  { path: '/cart', component: Cart, meta: { requiresAuth: true } },
  { path: '/login', component: Login },
  { path: '/admin', redirect: '/admin/dashboard' },
  { path: '/admin/dashboard', component: AdminPanel, meta: { requiresAuth: true, requiresRole: 'admin' } },
  { path: '/admin/books', component: AdminPanel, meta: { requiresAuth: true, requiresRole: 'admin' } },
  { path: '/admin/users', component: AdminPanel, meta: { requiresAuth: true, requiresRole: 'admin' } },
  { path: '/admin/orders', component: AdminPanel, meta: { requiresAuth: true, requiresRole: 'admin' } }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  if (isLoggedIn() && hasRole('admin')) {
    const blockedForAdmin = new Set(['/cart', '/checkout'])
    if (blockedForAdmin.has(to.path)) {
      ElMessage.warning('Admin account cannot access purchasing pages')
      next('/admin/dashboard')
      return
    }
  }

  if (to.meta && to.meta.requiresAuth && !isLoggedIn()) {
    ElMessage.warning('Please login first!')
    next({ path: '/login', query: { redirect: to.fullPath } })
    return
  }

  const requiredRole = to.meta?.requiresRole
  if (requiredRole && !hasRole(requiredRole)) {
    ElMessage.error('Access denied: admin role required')
    next('/books')
    return
  }

  next()
})

export default router