<template>
  <div class="container" v-if="book">
    <button class="backLink" type="button" @click="goBack">← Back to Books</button>

    <div class="book-card card">
      <div class="cover-column">
        <div class="coverWrap">
          <div class="badge" v-if="book.isPrivacyProtected">Privacy Protected</div>

          <div class="cover" :class="coverClass(book.category)">
            <div class="coverTop">EBOOK</div>
            <div class="coverCode">{{ book.coverText || shortCode(book.title) }}</div>
            <div class="coverBottom">{{ book.category || 'Book' }}</div>
          </div>
        </div>
      </div>

      <div class="details-column">
        <div class="rightTop">
          <h1 class="title">{{ book.title }}</h1>

          <div class="subTop">
            <div class="author">by {{ book.author }}</div>
          </div>
        </div>

        <div class="keyRow">
          <div class="priceWrap">
            <div class="price">
              <el-icon class="securityBadge" aria-label="Security badge">
                <Lock />
              </el-icon>
              ${{ book.price }}
            </div>
            <div class="priceHint">Secure, privacy-preserving delivery</div>
          </div>

          <div class="ratingRow" aria-label="Rating">
            <span class="stars" aria-hidden="true">★★★★★</span>
            <span class="ratingText">{{ book.rating }}</span>
          </div>
        </div>

        <div class="desc">
          <div class="descTitle">About this book</div>
          <p class="descText">{{ book.description || book.summary }}</p>
        </div>

        <div class="bottomActions">
          <template v-if="!adminMode">
            <button class="btn ctaPrimary" @click="privacyPurchaseByOT">
              Privacy Purchase (OT)
            </button>

            <div class="securityInfo">
              <div class="securityTitle">Security Info</div>
              <div class="securityBody">
                This purchase is simulated. In the final system, the backend OT module can deliver
                your ebook while preserving user privacy (minimizing what the server learns about
                your reading choices).
              </div>
            </div>

            <div class="callout calloutSmall simNote">
              “Buy Now” is simulated. In the final system the backend OT module will deliver the ebook
              while preserving user privacy.
            </div>
          </template>

          <template v-else>
            <div class="callout calloutSmall simNote">
              Purchase actions are disabled for admin accounts.
            </div>
          </template>
        </div>
      </div>
    </div>

    <div class="recommended card">
      <div class="recHeader">
        <div class="recTitle">Recommended for you</div>
        <div class="recSub">More privacy and security reads</div>
      </div>

      <div class="recScroll" aria-label="Recommended books">
        <button
          v-for="b in recommendedBooks"
          :key="b.id"
          class="recCard"
          type="button"
          @click="goToBook(b.id)"
        >
          <div class="recCover" :class="coverClass(b.category)">
            <div class="recCoverTop">EBOOK</div>
            <div class="recCoverCode">{{ b.coverText || shortCode(b.title) }}</div>
          </div>

          <div class="recMeta">
            <div class="recName">{{ b.title }}</div>
            <div class="recAuthor">by {{ b.author }}</div>
            <div class="recBottom">
              <span v-if="b.isPrivacyProtected" class="chip recChip">Privacy Protected</span>
              <span class="recPrice">${{ b.price }}</span>
            </div>
          </div>
        </button>
      </div>
    </div>
  </div>

  <div class="container" v-else>
    <div class="notFound card">
      <h2>Book not found</h2>
      <p>The requested book does not exist.</p>
      <button class="btnGhost" @click="goBack">Back</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Lock } from '@element-plus/icons-vue'
import { isAdmin } from '../utils/authStore'
import { getBookDetail } from '../api/books'
import { books } from '../data/books'
import { createOtSession, sendOtStep, getEncryptedPackage } from '../api/ot'
import { OTReceiver } from '../utils/otReceiver'
import { aesGcmDecrypt } from '../utils/aesGcmDecrypt'

const route = useRoute()
const router = useRouter()

const bookId = computed(() => Number(route.params.id))
const book = ref(null)
const adminMode = isAdmin()

async function loadBookDetail() {
  const res = await getBookDetail(bookId.value)
  book.value = res
}

const recommendedBooks = computed(() => {
  return books.filter((b) => b.id !== bookId.value).slice(0, 4)
})

function goBack() {
  router.push('/books')
}

function goToBook(bookId) {
  router.push(`/books/${bookId}`)
}

async function privacyPurchaseByOT() {
  if (!book.value) return

  if (!book.value.isPrivacyProtected) {
    ElMessage.warning('This book is not marked as privacy protected.')
    return
  }

  try {
    const groupId = book.value.groupId || 'default'
    const choiceIndex = book.value.choiceIndex

    if (choiceIndex === undefined || choiceIndex === null) {
      ElMessage.error('OT choice index is missing.')
      return
    }

    const sessionRes = await createOtSession(groupId)
    const session = sessionRes.data

    const receiver = new OTReceiver(choiceIndex, session.l)

    for (let level = 0; level < session.l; level++) {
      const { h0, h1 } = receiver.startLevel(level)

      const stepRes = await sendOtStep({
        sessionId: session.session_id,
        level,
        h0,
        h1
      })

      await receiver.finishLevel(
        level,
        stepRes.data.c0,
        stepRes.data.c1,
        stepRes.data.gy
      )
    }

    const recoveredKey = await receiver.recoverKey(session.masked_keys)

    const packageRes = await getEncryptedPackage(groupId)
    const encryptedBooks = packageRes.data.books || []

    const selectedEncryptedBook = encryptedBooks.find(
      (x) => Number(x.index) === Number(choiceIndex)
    )

    if (!selectedEncryptedBook) {
      ElMessage.error('Selected encrypted book was not found.')
      return
    }

    const aesKey = recoveredKey

    const ebookContent = await aesGcmDecrypt(
      selectedEncryptedBook,
      aesKey
    )

    downloadTextFile(selectedEncryptedBook.filename, ebookContent)

    ElMessage({
      type: 'success',
      showClose: true,
      duration: 6000,
      message:
        'OT privacy purchase completed and ebook decrypted locally. Server did not receive bookId. Key prefix: ' +
        bytesToHex(recoveredKey).slice(0, 16)
    })
  } catch (e) {
      console.error(e)

      ElMessage.error('OT privacy purchase failed.')
  }
}

function shortCode(title) {
  return title
    .split(' ')
    .slice(0, 3)
    .map((x) => x[0])
    .join('')
    .toUpperCase()
}

function bytesToHex(bytes) {
  return Array.from(bytes)
    .map((b) => b.toString(16).padStart(2, '0'))
    .join('')
}

function downloadTextFile(filename, content) {
  const blob = new Blob([content], {
    type: 'text/plain;charset=utf-8'
  })

  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')

  a.href = url
  a.download = filename || 'ebook.txt'
  a.click()

  URL.revokeObjectURL(url)
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

onMounted(async () => {
  await loadBookDetail()
})

watch(bookId, async () => {
  await loadBookDetail()
})
</script>

<style scoped>
.container {
  max-width: 1200px;
  margin: 0 auto;
}

.backLink {
  border: none;
  background: transparent;
  color: var(--muted);
  font-weight: 700;
  padding: 8px 0;
  cursor: pointer;
  transition: color 0.18s ease, transform 0.12s ease;
}

.backLink:hover {
  color: var(--text);
}

.book-card {
  width: 100%;
  max-width: 1200px;
  overflow: hidden;
  display: grid;
  grid-template-columns: 1fr 2fr;
  align-items: stretch;
}

.cover-column {
  padding: 0;
}

.details-column {
  padding: 48px;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.coverWrap {
  position: relative;
  height: 100%;
}

.badge {
  position: absolute;
  top: 14px;
  right: 14px;
  z-index: 2;
  padding: 4px 8px;
  font-size: 12px;
  border: 1px solid rgba(255, 255, 255, 0.7);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.12);
  color: #fff;
  backdrop-filter: blur(4px);
}

.cover {
  aspect-ratio: 3 / 4;
  min-height: 520px;
  border-radius: 22px;
  padding: 18px;
  color: #fff;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  box-shadow: 0 22px 55px rgba(15, 23, 42, 0.18);
  border: 1px solid rgba(255, 255, 255, 0.22);
  margin: 48px;
}

.coverTop {
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 1px;
  opacity: 0.9;
}

.coverCode {
  font-size: 84px;
  font-weight: 800;
  line-height: 1;
}

.coverBottom {
  font-size: 14px;
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

.head {
  margin-bottom: 10px;
}

.title {
  margin: 0;
  font-size: 2.5rem;
  line-height: 1.15;
  letter-spacing: -0.01em;
}

.author {
  margin-top: 0;
  color: #6b7280;
  font-size: 15px;
}

.subTop {
  margin-top: 10px;
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.keyRow {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 14px;
  flex-wrap: wrap;
}

.desc {
  min-width: 0;
}

.price {
  font-size: 30px;
  font-weight: 900;
  color: var(--text);
  display: inline-flex;
  align-items: center;
  gap: 10px;
}

.priceWrap {
  display: grid;
  gap: 6px;
}

.priceHint {
  font-size: 13px;
  color: var(--muted);
  font-weight: 600;
}

.securityBadge {
  width: 18px;
  height: 18px;
  color: var(--accent);
  flex: 0 0 auto;
}

.ratingRow {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #6b7280;
  font-size: 14px;
}

.stars {
  color: #f59e0b;
  letter-spacing: 1px;
}

.descTitle {
  font-weight: 900;
  margin: 0 0 10px 0;
  font-size: 18px;
}

.descText {
  margin: 0;
  line-height: 1.8;
  color: #374151;
  font-size: 14px;
}

.bottomActions {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: auto;
}

.ctaRow {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.ctaRow .ctaPrimary {
  flex: 1 1 220px;
}

.ctaRow .ctaSecondary {
  flex: 0 1 220px;
}

.ctaPrimary {
  padding: 12px 14px;
  border-radius: 14px;
}

.ctaSecondary {
  padding: 12px 14px;
  border-radius: 14px;
}

.simNote {
  margin-top: 4px;
}

.securityInfo {
  margin-top: 18px;
  padding: 16px 18px;
  border-radius: 16px;
  border: 1px solid rgba(37, 99, 235, 0.18);
  background: linear-gradient(180deg, rgba(37, 99, 235, 0.06), rgba(255, 255, 255, 0.8));
}

.securityTitle {
  font-weight: 900;
  margin-bottom: 8px;
}

.securityBody {
  color: #374151;
  line-height: 1.75;
}

.recommended {
  margin-top: 22px;
  padding: 28px;
}

.recHeader {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}

.recTitle {
  font-size: 18px;
  font-weight: 900;
}

.recSub {
  color: var(--muted);
  font-size: 13px;
  font-weight: 600;
}

.recScroll {
  margin-top: 16px;
  display: grid;
  grid-auto-flow: column;
  grid-auto-columns: minmax(240px, 280px);
  gap: 14px;
  overflow-x: auto;
  padding-bottom: 8px;
  scroll-snap-type: x mandatory;
}

.recCard {
  text-align: left;
  border: 1px solid var(--border);
  background: var(--card);
  border-radius: 16px;
  padding: 14px;
  cursor: pointer;
  transition: transform 0.12s ease, box-shadow 0.18s ease, border-color 0.18s ease,
    background 0.18s ease;
  scroll-snap-align: start;
}

.recCard:hover {
  transform: translateY(-2px);
  border-color: rgba(37, 99, 235, 0.25);
  box-shadow: var(--shadow-md);
  background: var(--cardHover);
}

.recCover {
  border-radius: 14px;
  aspect-ratio: 3 / 4;
  min-height: 170px;
  padding: 12px;
  color: #fff;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  box-shadow: 0 14px 30px rgba(15, 23, 42, 0.14);
}

.recCoverTop {
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 1px;
  opacity: 0.9;
}

.recCoverCode {
  font-size: 40px;
  font-weight: 900;
  line-height: 1;
}

.recMeta {
  margin-top: 12px;
  display: grid;
  gap: 6px;
}

.recName {
  font-weight: 900;
  line-height: 1.25;
}

.recAuthor {
  color: var(--muted);
  font-size: 13px;
  font-weight: 600;
}

.recBottom {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.recChip {
  padding: 5px 10px;
}

.recPrice {
  font-weight: 900;
}

.notFound {
  padding: 24px;
}

@media (max-width: 900px) {
  .book-card {
    grid-template-columns: 1fr;
  }

  .cover {
    min-height: 320px;
    margin: 24px;
  }

  .coverCode {
    font-size: 64px;
  }

  .title {
    font-size: 26px;
  }

  .details-column {
    padding: 24px;
  }

  .ctaRow {
    flex-direction: column;
  }
}
</style>