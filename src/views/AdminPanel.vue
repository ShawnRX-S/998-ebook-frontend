<template>
  <el-container class="adminLayout">
    <el-aside class="sidebar" width="240px">
      <div class="sidebarTitle">AdminPanel</div>
      <el-menu
        :default-active="activeKey"
        class="sidebarMenu"
        background-color="var(--adminSidebarBg)"
        text-color="var(--adminSidebarText)"
        active-text-color="var(--adminSidebarActive)"
        @select="onMenuSelect"
      >
        <el-menu-item index="books">Book Management</el-menu-item>
        <el-menu-item index="users">User Management</el-menu-item>
        <el-menu-item index="orders">Order Overview</el-menu-item>
      </el-menu>
    </el-aside>

    <el-main class="content">
      <div class="adminContentInner">
        <div class="adminTopActions">
          <el-button type="text" class="logoutBtn" @click="onLogout">
            Logout
          </el-button>
        </div>

        <div v-if="activeKey === 'orders'">
          <el-row :gutter="16" class="statRow">
            <el-col :span="8">
              <el-card shadow="never" class="statCard">
                <div class="statLabel">Total Books</div>
                <div class="statValue">{{ totalBooks }}</div>
              </el-card>
            </el-col>
            <el-col :span="8">
              <el-card shadow="never" class="statCard">
                <div class="statLabel">Active Users</div>
                <div class="statValue">{{ activeUsers }}</div>
              </el-card>
            </el-col>
            <el-col :span="8">
              <el-card shadow="never" class="statCard">
                <div class="statLabel">Privacy Security Level</div>
                <div class="statValue">
                  <el-tag type="success">High</el-tag>
                </div>
              </el-card>
            </el-col>
          </el-row>

          <el-card shadow="never" class="chartCard">
            <template #header>
              <div class="cardHeader">Monthly Sales</div>
            </template>
            <div class="chartPlaceholder" aria-label="Monthly Sales chart placeholder">
              <div class="bars">
                <div v-for="(v, i) in salesBars" :key="i" class="barWrap">
                  <div class="bar" :style="{ height: v + '%' }" />
                </div>
              </div>
              <div class="chartHint">Placeholder chart (connect to backend later).</div>
            </div>
          </el-card>

          <el-card shadow="never" class="chartCard">
            <template #header>
              <div class="cardHeader">Recent Transactions</div>
            </template>

            <el-table
              :data="recentTransactions"
              border
              stripe
              style="width: 100%"
              row-key="id"
            >
              <el-table-column prop="time" label="Time" min-width="160" />
              <el-table-column prop="user" label="User" min-width="160" />
              <el-table-column prop="book" label="Book" min-width="220" />
              <el-table-column prop="coins" label="Coins" width="120" />
            </el-table>

            <div v-if="recentTransactions.length === 0" class="logsHint">
              No transactions yet. Generate demo orders from Books/Cart.
            </div>
          </el-card>
        </div>

        <div v-else-if="activeKey === 'books'">
          <el-card shadow="never" class="sectionCard">
            <template #header>
              <div class="headerRow">
                <div class="cardHeader">Book Management</div>
                <div class="headerActions">
                  <el-button type="primary" @click="addDialogVisible = true">
                    Add New Book
                  </el-button>
                </div>
              </div>
            </template>

            <el-table :data="localBooks" border stripe style="width: 100%">
              <el-table-column prop="id" label="ID" width="80" />
              <el-table-column prop="title" label="Title" min-width="240" />
              <el-table-column prop="author" label="Author" min-width="160" />
              <el-table-column prop="category" label="Category" min-width="140" />
              <el-table-column
                prop="price"
                label="Price"
                width="120"
                :formatter="(row) => `$${Number(row.price).toFixed(2)}`"
              />
              <el-table-column label="Encryption Status" width="180">
                <template #default="scope">
                  <el-tag v-if="scope.row.isPrivacyProtected" type="success">Protected</el-tag>
                  <el-tag v-else type="info">Not Protected</el-tag>
                </template>
              </el-table-column>
              <el-table-column label="Encryption" width="220">
                <template #default="scope">
                  <el-switch
                    :model-value="!!scope.row.isPrivacyProtected"
                    active-text="Encryption"
                    inactive-text="Encryption"
                    @update:model-value="(val) => onToggleEncryption(scope.row, val)"
                  />
                </template>
              </el-table-column>
              <el-table-column label="Action" width="180">
                <template #default="scope">
                  <el-button type="primary" size="small" @click="onEdit(scope.row)">
                    Edit
                  </el-button>
                  <el-button
                    type="danger"
                    size="small"
                    plain
                    @click="onDelete(scope.row)"
                  >
                    Delete
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-card>

          <el-dialog v-model="editDialogVisible" title="Edit Book" width="520px">
            <el-form :model="editForm" label-position="top">
              <el-form-item label="Title">
                <el-input v-model="editForm.title" />
              </el-form-item>
              <el-form-item label="Author">
                <el-input v-model="editForm.author" />
              </el-form-item>
              <el-form-item label="Category">
                <el-input v-model="editForm.category" />
              </el-form-item>
              <el-form-item label="Price">
                <el-input-number v-model="editForm.price" :min="0" :step="0.1" />
              </el-form-item>
              <el-form-item label="Description">
                <el-input v-model="editForm.description" type="textarea" :rows="4" />
              </el-form-item>
              <el-form-item label="Cover Image URL (optional)">
                <el-input v-model="editForm.coverImage" placeholder="https://..." />
              </el-form-item>
              <el-form-item label="Privacy Protected">
                <el-switch v-model="editForm.isPrivacyProtected" active-text="Yes" inactive-text="No" />
              </el-form-item>
            </el-form>

            <template #footer>
              <span class="dialogFooter">
                <el-button @click="editDialogVisible = false">Cancel</el-button>
                <el-button type="primary" :loading="saving" @click="onSaveEdit">
                  Save
                </el-button>
              </span>
            </template>
          </el-dialog>

          <el-dialog v-model="addDialogVisible" title="Add New Book" width="520px">
            <el-form :model="addForm" label-position="top">
              <el-form-item label="Title">
                <el-input v-model="addForm.title" />
              </el-form-item>
              <el-form-item label="Author">
                <el-input v-model="addForm.author" />
              </el-form-item>
              <el-form-item label="Category">
                <el-input v-model="addForm.category" />
              </el-form-item>
              <el-form-item label="Price">
                <el-input-number v-model="addForm.price" :min="0" :step="0.1" />
              </el-form-item>
              <el-form-item label="Description">
                <el-input v-model="addForm.description" type="textarea" :rows="4" />
              </el-form-item>
              <el-form-item label="Cover Image URL (optional)">
                <el-input v-model="addForm.coverImage" placeholder="https://..." />
              </el-form-item>
              <el-form-item label="Privacy Protected">
                <el-switch v-model="addForm.isPrivacyProtected" active-text="Yes" inactive-text="No" />
              </el-form-item>
            </el-form>

            <template #footer>
              <span class="dialogFooter">
                <el-button @click="addDialogVisible = false">Cancel</el-button>
                <el-button type="primary" :loading="adding" @click="onAddBook">
                  Add
                </el-button>
              </span>
            </template>
          </el-dialog>
        </div>

        <div v-else-if="activeKey === 'users'">
          <UserManagement />
        </div>
      </div>
    </el-main>
  </el-container>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getOrders } from '../utils/orderStore'
import { useRoute, useRouter } from 'vue-router'
import { logout as authLogout } from '../utils/authStore'
import UserManagement from './UserManagement.vue'
import { addBook, deleteBook, updateBook, useBooks } from '../utils/bookStore'

const router = useRouter()
const route = useRoute()

const { books: booksRef, stop: stopBooksSync } = useBooks()
const localBooks = computed(() => booksRef.value || [])
const totalBooks = computed(() => localBooks.value.length)
const activeUsers = ref(0)

const activeKey = computed(() => {
  if (route.path === '/admin/books') return 'books'
  if (route.path === '/admin/users') return 'users'
  return 'orders'
})

const salesBars = computed(() => {
  // Simple deterministic placeholder bars.
  return [20, 35, 28, 45, 50, 40, 60, 55, 48, 62, 70, 65]
})

const editDialogVisible = ref(false)
const saving = ref(false)
const editForm = reactive({
  id: null,
  title: '',
  author: '',
  category: '',
  price: 0,
  description: '',
  coverImage: '',
  isPrivacyProtected: true
})

const addDialogVisible = ref(false)
const adding = ref(false)
const addForm = reactive({
  title: '',
  author: '',
  category: '',
  price: 0,
  description: '',
  coverImage: '',
  isPrivacyProtected: true
})

const auditLogs = ref([
  {
    time: '10:00',
    event: 'Book ID #101 encrypted via AES-256'
  },
  {
    time: '10:05',
    event: "User 'Alice' verified via Zero-Knowledge Proof"
  }
])

let logTimer = null
let txTimer = null

function safeParseJson(raw) {
  try {
    return raw ? JSON.parse(raw) : null
  } catch {
    return null
  }
}

function refreshActiveUsers() {
  const parsed = safeParseJson(localStorage.getItem('users'))
  const obj = parsed && typeof parsed === 'object' ? parsed : {}
  activeUsers.value = Object.keys(obj).length
}

function onUsersChanged() {
  refreshActiveUsers()
}

function onStorage(e) {
  if (e && e.key && e.key !== 'users') return
  refreshActiveUsers()
}

const recentTransactions = ref([])
const coinRate = 10
const mockUsers = ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve', 'Frank', 'Grace', 'Heidi']

function pad2(n) {
  return String(n).padStart(2, '0')
}

function getNowTime() {
  const now = new Date()
  return `${pad2(now.getHours())}:${pad2(now.getMinutes())}`
}

function addAuditLog(event) {
  const time = getNowTime()
  auditLogs.value = [{ time, event }, ...auditLogs.value].slice(0, 12)
}

function pickUser(orderId) {
  let sum = 0
  const s = String(orderId || '')
  for (let i = 0; i < s.length; i++) sum += s.charCodeAt(i)
  return mockUsers[sum % mockUsers.length]
}

function refreshRecentTransactions() {
  const orders = getOrders()
  const rows = []

  for (const o of orders) {
    const user = pickUser(o.orderId)
    for (const it of o.items || []) {
      const amount = Number(it.price) * Number(it.qty)
      rows.push({
        id: `${o.orderId}-${it.bookId}`,
        time: o.time,
        user,
        book: it.title,
        coins: Math.round(amount * coinRate)
      })
    }
  }

  recentTransactions.value = rows.slice(0, 8)
}

function onMenuSelect(key) {
  router.push('/admin/' + key)
}

function onEdit(row) {
  editForm.id = row.id
  editForm.title = row.title
  editForm.author = row.author
  editForm.category = row.category
  editForm.price = Number(row.price)
  editForm.description = row.description || row.summary || ''
  editForm.coverImage = row.coverImage || ''
  editForm.isPrivacyProtected = !!row.isPrivacyProtected
  editDialogVisible.value = true
}

async function onDelete(row) {
  try {
    await ElMessageBox.confirm(
      `Delete book "${row.title}"? This will remove it from the Shop too (LocalStorage).`,
      'Confirm',
      { type: 'warning' }
    )
    deleteBook(row.id)
    ElMessage.success('Book deleted')
  } catch {
    // User cancelled.
  }
}

function onSaveEdit() {
  if (!editForm.title.trim()) {
    ElMessage.warning('Title is required')
    return
  }

  saving.value = true
  setTimeout(() => {
    updateBook(editForm.id, {
      title: editForm.title,
      author: editForm.author,
      category: editForm.category,
      price: editForm.price,
      description: editForm.description || '',
      coverImage: editForm.coverImage || '',
      isPrivacyProtected: !!editForm.isPrivacyProtected
    })

    saving.value = false
    editDialogVisible.value = false
    ElMessage.success('Book updated')
  }, 300)
}

function onToggleEncryption(row, enabled) {
  const next = !!enabled
  updateBook(row.id, { isPrivacyProtected: next })

  if (next) {
    ElMessage.success(`Book [${row.title}] is now protected by AES-256.`)
    addAuditLog(`Book [${row.title}] protected by AES-256`)
  } else {
    addAuditLog(`Book [${row.title}] encryption disabled (demo)`)
  }
}

function resetAddForm() {
  addForm.title = ''
  addForm.author = ''
  addForm.category = ''
  addForm.price = 0
  addForm.description = ''
  addForm.coverImage = ''
  addForm.isPrivacyProtected = true
}

function onAddBook() {
  const title = addForm.title.trim()
  if (!title) {
    ElMessage.warning('Title is required')
    return
  }
  if (!addForm.author.trim()) {
    ElMessage.warning('Author is required')
    return
  }
  adding.value = true
  setTimeout(() => {
    const nextCategory = addForm.category.trim() || (addForm.isPrivacyProtected ? 'Privacy' : '')
    addBook({
      title: addForm.title.trim(),
      author: addForm.author.trim(),
      category: nextCategory,
      price: Number(addForm.price),
      description: addForm.description || '',
      coverImage: addForm.coverImage || '',
      isPrivacyProtected: !!addForm.isPrivacyProtected,
      rating: 4.6,
      coverText: 'NEW',
      encrypted: !!addForm.isPrivacyProtected
    })

    addAuditLog(`Book added to catalog`)
    adding.value = false
    addDialogVisible.value = false
    resetAddForm()
    ElMessage.success('Book added')
  }, 300)
}

function addRandomAuditLog() {
  const templates = [
    () => {
      const id = 100 + Math.floor(Math.random() * 50)
      return `Book ID #${id} encrypted via AES-256`
    },
    () => {
      const names = ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve']
      const name = names[Math.floor(Math.random() * names.length)]
      return `User '${name}' verified via Zero-Knowledge Proof`
    },
    () => {
      return 'Privacy access policy validated (demo)'
    }
  ]

  const pick = templates[Math.floor(Math.random() * templates.length)]
  addAuditLog(pick())
}

onMounted(() => {
  refreshActiveUsers()
  window.addEventListener('users-changed', onUsersChanged)
  window.addEventListener('storage', onStorage)
  logTimer = setInterval(addRandomAuditLog, 5000)
  refreshRecentTransactions()
  txTimer = setInterval(refreshRecentTransactions, 5000)
})

onBeforeUnmount(() => {
  if (logTimer) clearInterval(logTimer)
  if (txTimer) clearInterval(txTimer)
  window.removeEventListener('users-changed', onUsersChanged)
  window.removeEventListener('storage', onStorage)
  stopBooksSync?.()
})

function onLogout() {
  authLogout()
  router.push('/login')
}
</script>

<style scoped>
.adminLayout {
  min-height: calc(100vh - 64px);
}

.adminTopActions {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 14px;
}

.logoutBtn {
  color: #ef4444;
  font-weight: 700;
}

.sidebar {
  background: var(--adminSidebarBg);
  color: #e5e7eb;
  padding: 18px 12px;
}

.sidebarTitle {
  font-weight: 800;
  color: #ffffff;
  margin-bottom: 12px;
}

.sidebarMenu {
  border-right: 0;
}

.content {
  padding: 22px 18px;
  background: var(--bg);
}

.adminContentInner {
  max-width: 1120px;
  margin: 0 auto;
}

.headerRow {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.headerActions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.statRow {
  margin-bottom: 16px;
}

.statCard {
  background: var(--card);
  border-radius: var(--radius);
}

.statLabel {
  color: #6b7280;
  font-size: 13px;
  font-weight: 700;
}

.statValue {
  margin-top: 10px;
  font-size: 30px;
  font-weight: 900;
}

.chartCard {
  margin-top: 16px;
}

.cardHeader {
  font-weight: 800;
}

.chartPlaceholder {
  padding: 18px 16px 6px 16px;
}

.bars {
  display: flex;
  align-items: flex-end;
  gap: 10px;
  height: 160px;
}

.barWrap {
  flex: 1;
  display: flex;
  justify-content: center;
}

.bar {
  width: 100%;
  max-width: 28px;
  border-radius: 8px 8px 0 0;
  background: linear-gradient(180deg, #409eff, #67c23a);
}

.chartHint {
  margin-top: 10px;
  color: #6b7280;
  font-size: 13px;
}

.sectionCard {
  min-height: 420px;
}

.logsHint {
  margin-top: 12px;
  color: #6b7280;
  font-size: 13px;
}

.dialogFooter {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>

