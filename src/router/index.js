import { createRouter, createWebHistory } from 'vue-router'
import Books from '../views/Books.vue'
import BookDetail from '../views/BookDetail.vue'
import Orders from '../views/Orders.vue'
import Cart from '../views/Cart.vue'

const routes = [
  { path: '/', redirect: '/books' },
  { path: '/books', component: Books },
  { path: '/books/:id', component: BookDetail },
  { path: '/orders', component: Orders },
  { path:'/cart', component: Cart}
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router