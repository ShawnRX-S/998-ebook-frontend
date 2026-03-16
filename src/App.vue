<template>
  <div>
    <header class="topbar">
      <div class="topbarInner">
        <div class="logo">
          <div class="logoMark">998</div>
          <div class="logoText">
            <div class="logoTitle">Ebook Store</div>
            <div class="logoSub">Privacy-preserving ebook demo</div>
          </div>
        </div>

        <nav class="nav">
          <router-link class="navLink" to="/books">Books</router-link>
          <router-link class="navLink" to="/orders">Orders</router-link>
          <router-link class="navLink" to="/cart">
            Cart
            <span class="pill" :class="{ bump: cartBump }">{{ cartCount }}</span>
          </router-link>
        </nav>
      </div>
    </header>

    <main class="page">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { getCart } from './utils/cartStore'

const cartCount = ref(0)
const cartBump = ref(false)

let timerId = null
let bumpTimerId = null

function refreshCartCount() {
  const list = getCart()
  cartCount.value = list.reduce((sum, x) => sum + Number(x.qty || 0), 0)
}

function playCartBump() {
  cartBump.value = false

  if (bumpTimerId) {
    clearTimeout(bumpTimerId)
  }

  setTimeout(() => {
    cartBump.value = true
    bumpTimerId = setTimeout(() => {
      cartBump.value = false
    }, 260)
  }, 10)
}

function handleCartUpdated() {
  refreshCartCount()
  playCartBump()
}

onMounted(() => {
  refreshCartCount()

  timerId = setInterval(refreshCartCount, 500)
  window.addEventListener('cart-updated', handleCartUpdated)
})

onUnmounted(() => {
  if (timerId) clearInterval(timerId)
  if (bumpTimerId) clearTimeout(bumpTimerId)
  window.removeEventListener('cart-updated', handleCartUpdated)
})
</script>

<style>
.topbar {
  position: sticky;
  top: 0;
  z-index: 10;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid #e5e7eb;
}

.topbarInner {
  max-width: 1040px;
  margin: 0 auto;
  padding: 12px 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
}

.logoMark {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  background: #111827;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
}

.logoTitle {
  font-weight: 800;
  line-height: 1;
}

.logoSub {
  margin-top: 2px;
  font-size: 12px;
  color: #6b7280;
}

.nav {
  display: flex;
  gap: 10px;
  align-items: center;
}

.navLink {
  text-decoration: none;
  color: #111827;
  padding: 8px 10px;
  border-radius: 10px;
  font-weight: 700;
}

.navLink:hover {
  background: #f3f4f6;
}

.navLink.router-link-active {
  background: #111827;
  color: #fff;
}

.pill {
  margin-left: 6px;
  padding: 2px 8px;
  border-radius: 999px;
  background: #111827;
  color: #fff;
  font-size: 12px;
  font-weight: 800;
  display: inline-block;
  transition: transform 0.2s ease, background 0.2s ease;
}

.pill.bump {
  transform: scale(1.22);
  background: #2563eb;
}
</style>