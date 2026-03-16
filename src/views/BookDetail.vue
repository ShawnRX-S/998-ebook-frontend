<template>
  <div class="container" v-if="book">
    <div class="detailGrid">
      <!-- Left -->
      <div class="left card">
        <div class="coverWrap">
          <div class="badge" v-if="book.category">{{ book.category }}</div>

          <div class="cover" :class="coverClass(book.category)">
            <div class="coverTop">EBOOK</div>
            <div class="coverCode">{{ book.coverText || shortCode(book.title) }}</div>
            <div class="coverBottom">{{ book.category || 'Book' }}</div>
          </div>
        </div>
      </div>

      <!-- Right -->
      <div class="right card">

        <h1 class="title">{{ book.title }}</h1>
        <div class="author">by {{ book.author }}</div>

        <div class="metaRow">
          <span class="tag">{{ book.category }}</span>
          <span class="price">${{ book.price }}</span>
        </div>

        <div class="ratingRow">
          <span class="stars">★★★★★</span>
          <span class="ratingText">{{ book.rating }}</span>
        </div>

        <div class="desc">
          <h3>About this book</h3>
          <p>{{ book.summary }}</p>
        </div>

        <div class="actions">
          <button class="btnGhost" @click="goBack">Back</button>
          <button class="btnGhost" @click="addCart">Add to Cart</button>
          <button class="btn" @click="buyNow">Buy Now</button>
        </div>

        <p class="note">
          “Buy Now” is simulated. In the final system the backend OT module
          will deliver the ebook while preserving user privacy.
        </p>

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
import { useRoute, useRouter } from 'vue-router'
import { books } from '../data/books'
import { addToCart as addToCartStore, clearCart } from '../utils/cartStore'
import { addOrder } from '../utils/orderStore'

const route = useRoute()
const router = useRouter()

const id = Number(route.params.id)
const book = books.find((b) => b.id === id)

function goBack() {
  router.push('/books')
}

function addCart() {
  addToCartStore({
    bookId: book.id,
    title: book.title,
    price: book.price,
    qty: 1
  })

  alert('Added to cart: ' + book.title)
}

function buyNow() {
  const order = {
    orderId: 'ORD-' + Date.now(),
    time: new Date().toLocaleString(),
    status: 'PAID',
    items: [
      {
        bookId: book.id,
        title: book.title,
        price: book.price,
        qty: 1
      }
    ],
    total: Number(book.price)
  }

  addOrder(order)
  clearCart()
  router.push('/orders')
}

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
</script>

<style>
.container {
  max-width: 1040px;
  margin: 0 auto;
}

.detailGrid {
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: 22px;
}

.left,
.right {
  padding: 18px;
}

.coverWrap {
  position: relative;
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
  height: 420px;
  border-radius: 18px;
  padding: 18px;
  color: #fff;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.coverTop {
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 1px;
  opacity: 0.9;
}

.coverCode {
  font-size: 72px;
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
  font-size: 26px;
  line-height: 1.3;
}

.author {
  margin-top: 8px;
  color: #6b7280;
  font-size: 15px;
}

.metaRow {
  margin-top: 14px;
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.tag {
  padding: 6px 10px;
  border: 1px solid #e5e7eb;
  border-radius: 999px;
  background: #f9fafb;
  font-size: 13px;
  color: #374151;
}

.desc {
  margin-top: 18px;
  padding: 16px;
  border-radius: 12px;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
}

.desc h3 {
  margin-bottom: 8px;
}

.desc p {
  line-height: 1.7;
  color: #374151;
}

.price {
  font-size: 28px;
  font-weight: 800;
  color: #111827;
}

.ratingRow {
  margin-top: 12px;
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

.desc {
  margin-top: 18px;
}

.cardSoft {
  padding: 16px;
  border: 1px solid #e5e7eb;
  border-radius: 14px;
  background: #fafafa;
}

.desc h3 {
  margin: 0 0 10px 0;
  font-size: 18px;
}

.desc p {
  margin: 0;
  line-height: 1.8;
  color: #374151;
}

.actions {
  margin-top: 18px;
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.note {
  margin-top: 14px;
  color: #6b7280;
  font-size: 13px;
  line-height: 1.6;
}

.notFound {
  padding: 24px;
}

@media (max-width: 900px) {
  .detailGrid {
    grid-template-columns: 1fr;
  }

  .cover {
    height: 300px;
  }

  .coverCode {
    font-size: 54px;
  }

  .title {
    font-size: 24px;
  }
}
</style>