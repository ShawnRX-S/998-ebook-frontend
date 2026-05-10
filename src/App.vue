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
          <router-link v-if="!isAdmin" class="navLink" to="/orders">Orders</router-link>

          <router-link
            v-if="!loggedIn"
            class="navLink navBtn navBtnPrimary"
            to="/login"
          >
            <UserFilled class="navIcon" />
            Login
          </router-link>

          <button v-else class="navLink navBtn navBtnPrimary" type="button" @click="onLogout">
            Logout
          </button>

          <router-link
            v-if="isAdmin"
            class="navLink navBtn navBtnSuccess"
            to="/admin/dashboard"
          >
            <Setting class="navIcon" />
            Admin
          </router-link>
        </nav>
      </div>
    </header>

    <main :class="['page', { pageFull: isAdminRoute }]">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import {
  isAdmin as authIsAdmin,
  isLoggedIn as authIsLoggedIn,
  logout as authLogout
} from './utils/authStore'
import { useRouter } from 'vue-router'

import { Setting, UserFilled } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const loggedIn = ref(authIsLoggedIn())
const isAdmin = ref(authIsAdmin())

const isAdminRoute = computed(() => String(route.path || '').startsWith('/admin'))

function syncAuth() {
  loggedIn.value = authIsLoggedIn()
  isAdmin.value = authIsAdmin()
}

function onLogout() {
  authLogout()
  router.push('/login')
}

onMounted(() => {
  syncAuth()

  window.addEventListener('auth-changed', syncAuth)
})

onUnmounted(() => {
  window.removeEventListener('auth-changed', syncAuth)
})
</script>

<style>
.topbar {
  position: sticky;
  top: 0;
  z-index: 10;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--border);
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
  color: var(--muted);
}

.nav {
  display: flex;
  gap: 10px;
  align-items: center;
}

.navLink {
  text-decoration: none;
  color: var(--text);
  padding: 8px 10px;
  border-radius: 10px;
  font-weight: 700;
  transition: background 0.18s ease, color 0.18s ease, transform 0.12s ease;
}

.navLink:hover {
  background: #f3f4f6;
}

.navLink.router-link-active {
  background: var(--primary);
  color: var(--primaryText);
}

.pill {
  margin-left: 6px;
  padding: 2px 8px;
  border-radius: 999px;
  background: var(--primary);
  color: var(--primaryText);
  font-size: 12px;
  font-weight: 800;
  display: inline-block;
  transition: transform 0.2s ease, background 0.2s ease;
}

.pill.bump {
  transform: scale(1.22);
  background: var(--accent);
}

.navBtn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border: 1px solid transparent;
}

.navIcon {
  width: 16px;
  height: 16px;
  display: inline-block;
}

.navBtnPrimary {
  background: var(--accent);
  color: var(--primaryText);
}

.navBtnSuccess {
  background: var(--success);
  color: var(--primaryText);
}

.navBtnPrimary:hover {
  background: var(--accentHover);
}

.navBtnSuccess:hover {
  background: var(--successHover);
}

.navBtnPrimary.router-link-active {
  background: var(--accent);
  color: var(--primaryText);
}

.navBtnSuccess.router-link-active {
  background: var(--success);
  color: var(--primaryText);
}

.navBtn.router-link-active {
  color: #fff;
}
</style>