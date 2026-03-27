<template>
  <el-card shadow="never" class="sectionCard">
    <template #header>
      <div class="headerRow">
        <div class="cardHeader">User Management</div>
        <div class="headerHint">Users are loaded from LocalStorage key: <b>users</b></div>
      </div>
    </template>

    <el-table :data="rows" border stripe style="width: 100%" row-key="username">
      <el-table-column prop="username" label="Username" min-width="200" />
      <el-table-column prop="role" label="Role" width="160" />
      <el-table-column prop="source" label="Source" width="180" />
    </el-table>

    <div v-if="rows.length === 0" class="hint">No users found.</div>
  </el-card>
</template>

<script setup>
import { onMounted, onBeforeUnmount, ref } from 'vue'

const rows = ref([])

function safeParseJson(raw) {
  try {
    return raw ? JSON.parse(raw) : null
  } catch {
    return null
  }
}

function loadUsersFromLocalStorage() {
  const parsed = safeParseJson(localStorage.getItem('users'))
  const obj = parsed && typeof parsed === 'object' ? parsed : {}

  const next = []
  for (const [username, value] of Object.entries(obj)) {
    // `authStore` currently normalizes users to: { username: { password, role } }
    const role =
      value && typeof value === 'object' && value.role ? String(value.role) : 'user'
    next.push({
      username: String(username),
      role,
      source: 'localStorage'
    })
  }

  next.sort((a, b) => a.username.localeCompare(b.username))
  rows.value = next
}

function onStorage(e) {
  if (e && e.key && e.key !== 'users') return
  loadUsersFromLocalStorage()
}

function onUsersChanged() {
  loadUsersFromLocalStorage()
}

onMounted(() => {
  loadUsersFromLocalStorage()
  window.addEventListener('storage', onStorage)
  window.addEventListener('users-changed', onUsersChanged)
})

onBeforeUnmount(() => {
  window.removeEventListener('storage', onStorage)
  window.removeEventListener('users-changed', onUsersChanged)
})
</script>

<style scoped>
.headerRow {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 12px;
}

.cardHeader {
  font-weight: 800;
}

.headerHint {
  color: #6b7280;
  font-size: 13px;
}

.hint {
  margin-top: 12px;
  color: #6b7280;
  font-size: 13px;
}
</style>

