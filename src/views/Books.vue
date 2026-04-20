<template>
  <div class="container">
    <div class="pageTitle">
      <h2>Books</h2>
      <p class="sub">Browse ebooks and simulate purchase (OT handled by backend later).</p>
    </div>

    <div class="filterBar card">
      <div class="filterLeft">
        <div class="inputWrap">
          <span class="icon">🔎</span>
          <input
            class="searchInput"
            type="text"
            v-model="keyword"
            placeholder="Search by title / author / summary..."
          />
        </div>

        <div class="chipRow">
          <button
            class="chip"
            :class="{ active: category === 'ALL' }"
            @click="setCategory('ALL')"
          >
            All
          </button>

          <button
            v-for="c in categories"
            :key="c"
            class="chip"
            :class="{ active: category === c }"
            @click="setCategory(c)"
          >
            {{ c }}
          </button>
        </div>
      </div>

      <div class="filterRight">
        <select class="select" v-model="sortBy">
          <option value="NONE">Sort: Default</option>
          <option value="PRICE_ASC">Price: Low → High</option>
          <option value="PRICE_DESC">Price: High → Low</option>
        </select>

        <select class="select" v-model="pageSize">
          <option :value="6">6 / page</option>
          <option :value="9">9 / page</option>
          <option :value="12">12 / page</option>
        </select>

        <button class="btnGhost" @click="resetAll">Reset</button>
      </div>
    </div>

    <div class="resultRow">
      <div class="resultText">
        Showing <b>{{ pagedList.length }}</b> of <b>{{ totalCount }}</b>
        (Total: {{ totalCount }})
      </div>

      <div class="pageText" v-if="totalPages > 1">
        Page {{ page }} / {{ totalPages }}
      </div>
    </div>

    <div class="grid">
      <div class="card bookCard" v-for="b in pagedList" :key="b.id">
        <div class="badge" v-if="b.isPrivacyProtected">Privacy Protected</div>

        <div class="cover" :class="coverClass(b.category)">
          <div class="coverTop">EBOOK</div>
          <div class="coverCode">{{ shortCode(b.title) }}</div>
          <div class="coverBottom">{{ b.category || 'Book' }}</div>
        </div>

        <h3 class="title">{{ b.title }}</h3>
        <div class="rating">
          ⭐ {{ b.rating }}
        </div>
        <p class="meta">Author: {{ b.author }}</p>
        <p class="meta">Price: ${{ b.price }}</p>
        <p class="summary">{{ b.description || b.summary }}</p>

        <div class="actions">
          <button class="btnGhost" @click="goDetail(b.id)">View Detail</button>

          <el-button v-if="!adminMode" type="success" :icon="ShoppingCart" @click="addToCart(b)">
            Add to Cart
          </el-button>

          <el-button v-if="b.isPrivacyProtected" type="primary" @click="privacyEncryptTest(b)">
            Privacy Encryption Test
          </el-button>
        </div>
      </div>
    </div>

    <div v-if="pagedList.length === 0" class="empty">
      No matching books. Try another keyword/category.
    </div>

    <div class="pager" v-if="totalPages > 1">
      <button class="pagerBtn" :disabled="page === 1" @click="toFirst">First</button>
      <button class="pagerBtn" :disabled="page === 1" @click="prevPage">Prev</button>

      <button
        class="pagerNum"
        v-for="p in pageButtons"
        :key="p"
        :class="{ active: p === page, dots: p === '...' }"
        :disabled="p === '...'"
        @click="goPage(p)"
      >
        {{ p }}
      </button>

      <button class="pagerBtn" :disabled="page === totalPages" @click="nextPage">Next</button>
      <button class="pagerBtn" :disabled="page === totalPages" @click="toLast">Last</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import { ShoppingCart } from '@element-plus/icons-vue'
import { addToCart as addToCartStore } from '../utils/cartStore'
import { aesEncryptString } from '../utils/cryptoHelper'
import { isAdmin, isLoggedIn } from '../utils/authStore'
import { getBooks } from '../api/books'

const router = useRouter()
const list = ref([])
const adminMode = isAdmin()

// Demo-only passphrase for encrypting book title payloads.
// In the real system, the secret should come from backend / key management.
const AES_SECRET = 'ebook-privacy-demo-secret'

const keyword = ref('')
const category = ref('ALL')
const sortBy = ref('NONE')

const page = ref(1)
const pageSize = ref(9)
const totalCount = ref(0)

async function loadBooks() {
  const res = await getBooks({
    page: page.value,
    pageSize: pageSize.value,
    category: category.value,
    keyword: keyword.value,
    sort: sortBy.value
  })

  list.value = res.list
  totalCount.value = res.total
}

const categories = computed(() => {
  const set = new Set()
  list.value.forEach((b) => {
    if (b.category) set.add(b.category)
  })
  return Array.from(set).sort()
})

const totalPages = computed(() => {
  const n = Math.ceil(totalCount.value / Number(pageSize.value))
  return n <= 0 ? 1 : n
})

const pagedList = computed(() => list.value)

function goDetail(id) {
  router.push('/books/' + id)
}

function addToCart(book) {
  if (adminMode) {
    ElMessage.warning('Admin account cannot add items to cart')
    return
  }

  if (!isLoggedIn()) {
    ElMessage.warning('Please login first!')
    router.push('/login')
    return
  }

  addToCartStore({
    bookId: book.id,
    title: book.title,
    price: book.price,
    qty: 1
  })

  alert('Added to cart: ' + book.title)
}

function privacyEncryptTest(book) {
  if (!book?.isPrivacyProtected) {
    ElMessage.error('Standard Mode: Encryption is disabled for this item.')
    return
  }

  const cipherText = aesEncryptString(book.title, AES_SECRET)
  ElMessage({
    type: 'success',
    showClose: true,
    duration: 5000,
    // Encryption result display (demo)
    message: `Encryption result (AES): ${cipherText}`
  })
}

function setCategory(c) {
  category.value = c
}

function resetAll() {
  keyword.value = ''
  category.value = 'ALL'
  sortBy.value = 'NONE'
  pageSize.value = 9
  page.value = 1
}

function goPage(p) {
  if (p === '...') return
  page.value = Number(p)
}

function prevPage() {
  page.value = Math.max(1, page.value - 1)
}

function nextPage() {
  page.value = Math.min(totalPages.value, page.value + 1)
}

function toFirst() {
  page.value = 1
}

function toLast() {
  page.value = totalPages.value
}

const pageButtons = computed(() => {
  const total = totalPages.value
  const cur = page.value

  if (total <= 7) {
    return Array.from({ length: total }, (_, i) => i + 1)
  }

  const result = []
  result.push(1)

  const left = Math.max(2, cur - 1)
  const right = Math.min(total - 1, cur + 1)

  if (left > 2) result.push('...')

  for (let i = left; i <= right; i++) result.push(i)

  if (right < total - 1) result.push('...')

  result.push(total)
  return result
})

function shortCode(title) {
  return title
    .split(' ')
    .slice(0, 3)
    .map((x) => x[0])
    .join('')
    .toUpperCase()
}

function coverClass(categoryName) {
  if (categoryName === 'Privacy') return 'coverPrivacy'
  if (categoryName === 'Cryptography') return 'coverCrypto'
  if (categoryName === 'E-commerce') return 'coverCommerce'
  if (categoryName === 'Security') return 'coverSecurity'
  if (categoryName === 'Blockchain') return 'coverBlock'
  if (categoryName === 'Systems') return 'coverSystems'
  return 'coverDefault'
}

watch([keyword, category, sortBy, pageSize], async () => {
  page.value = 1
  await loadBooks()
})

watch(page, async () => {
  await loadBooks()
})

onMounted(async () => {
  await loadBooks()
})
</script>

<style scoped>
.container {
  max-width: 1040px;
  margin: 0 auto;
}

.pageTitle {
  margin-bottom: 10px;
}

.pageTitle h2 {
  margin: 0;
}

.sub {
  margin: 6px 0 0 0;
  color: #666;
  font-size: 13px;
}

.filterBar {
  display: flex;
  justify-content: space-between;
  gap: 14px;
  padding: 14px;
}

.filterLeft {
  flex: 1;
  min-width: 360px;
}

.inputWrap {
  display: flex;
  align-items: center;
  border: 1px solid #e2e2e2;
  border-radius: 12px;
  padding: 10px 12px;
  gap: 8px;
}

.icon {
  font-size: 14px;
}

.searchInput {
  border: none;
  outline: none;
  width: 100%;
  font-size: 14px;
}

.chipRow {
  margin-top: 10px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.chip {
  padding: 6px 10px;
  font-size: 13px;
  border: 1px solid #e2e2e2;
  border-radius: 999px;
  background: #fff;
  cursor: pointer;
}

.chip.active {
  border-color: #222;
  background: #222;
  color: #fff;
}

.filterRight {
  display: flex;
  gap: 10px;
  align-items: flex-start;
}

.select {
  padding: 10px 12px;
  border: 1px solid #e2e2e2;
  border-radius: 12px;
  background: #fff;
  font-size: 14px;
}

.resultRow {
  margin: 12px 2px;
  display: flex;
  justify-content: space-between;
  color: #555;
  font-size: 13px;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 32px;
  margin-top: 10px;
}

.bookCard {
  position: relative;
  padding: 16px;
  display: flex;
  flex-direction: column;
  border: 1px solid transparent;
  transition: transform 0.22s ease, box-shadow 0.22s ease, border-color 0.22s ease;
}

.bookCard:hover {
  transform: translateY(-6px);
  box-shadow: 0 18px 35px rgba(0, 0, 0, 0.08);
  border-color: rgba(37, 99, 235, 0.35);
}

.cover {
  aspect-ratio: 3 / 2;
  max-height: 170px;
  border-radius: 14px;
  margin-bottom: 12px;
  padding: 12px;
  color: #fff;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  overflow: hidden;
  transition: transform 0.22s ease;
}

.bookCard:hover .cover {
  transform: scale(1.02);
}

.coverTop {
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 1px;
  opacity: 0.9;
}

.coverCode {
  font-size: 30px;
  font-weight: 800;
  line-height: 1;
}

.coverBottom {
  font-size: 12px;
  opacity: 0.95;
}

.coverPrivacy {
  background: linear-gradient(135deg, #0f172a, #2563eb);
}

.coverCrypto {
  background: linear-gradient(135deg, #3b0764, #9333ea);
}

.coverCommerce {
  background: linear-gradient(135deg, #14532d, #10b981);
}

.coverSecurity {
  background: linear-gradient(135deg, #3f3f46, #ef4444);
}

.coverBlock {
  background: linear-gradient(135deg, #78350f, #f59e0b);
}

.coverSystems {
  background: linear-gradient(135deg, #164e63, #06b6d4);
}

.coverDefault {
  background: linear-gradient(135deg, #374151, #6b7280);
}

.badge {
  position: absolute;
  top: 24px;
  right: 24px;
  padding: 4px 8px;
  font-size: 12px;
  border: 1px solid rgba(255, 255, 255, 0.7);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.12);
  color: #fff;
  backdrop-filter: blur(4px);
}

.title {
  margin: 0 0 8px 0;
  min-height: 48px;
}

.meta {
  margin: 4px 0;
  color: #555;
  font-size: 14px;
}

.summary {
  margin-top: 8px;
  color: #333;
  font-size: 13px;
  line-height: 1.5;
  min-height: 40px;
  flex: 1 1 auto;
}

.actions {
  margin-top: 12px;
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.actions .btn,
.actions .btnGhost {
  transition: transform 0.18s ease, opacity 0.18s ease;
}

.actions .btn:hover,
.actions .btnGhost:hover {
  transform: translateY(-1px);
}

.empty {
  margin-top: 14px;
  color: #555;
}

.pager {
  margin: 18px 0 10px 0;
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 8px;
}

.pagerBtn,
.pagerNum {
  padding: 8px 10px;
  border: 1px solid #e2e2e2;
  border-radius: 10px;
  background: #fff;
  cursor: pointer;
  font-size: 13px;
}

.pagerBtn:disabled,
.pagerNum:disabled {
  cursor: not-allowed;
  opacity: 0.5;
}

.pagerNum.active {
  border-color: #222;
  background: #222;
  color: #fff;
}

.pagerNum.dots {
  border-color: transparent;
}

@media (max-width: 980px) {
  .filterBar {
    flex-direction: column;
  }

  .filterLeft {
    min-width: auto;
  }

  .filterRight {
    align-items: center;
    justify-content: flex-start;
    flex-wrap: wrap;
  }

  .grid {
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  }
}
</style>

