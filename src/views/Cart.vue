<template>
  <div class="container">
    <h2>Cart</h2>

    <div class="cartCard card">
      <div v-if="items.length === 0" class="empty">
        Your cart is empty.
      </div>

      <template v-else>
        <table class="table">
          <thead>
            <tr>
              <th>Book</th>
              <th>Price</th>
              <th style="width: 120px">Qty</th>
              <th>Total</th>
              <th style="width: 90px">Action</th>
            </tr>
          </thead>

          <tbody>
            <tr
              v-for="it in items"
              :key="cartKey(it)"
            >
              <td>
                <div class="bookTitle">{{ it.title }}</div>
                <div class="privacyText">
                  Local OT selection data is kept in the browser.
                </div>
              </td>

              <td>${{ Number(it.price || 0).toFixed(2) }}</td>

              <td>
                <input
                  class="qty"
                  type="number"
                  min="1"
                  :value="it.qty"
                  @input="onQty(it, $event)"
                />
              </td>

              <td>
                ${{ (Number(it.price || 0) * Number(it.qty || 0)).toFixed(2) }}
              </td>

              <td>
                <button class="btnDanger" @click="remove(it)">
                  Remove
                </button>
              </td>
            </tr>
          </tbody>
        </table>

        <div class="footer">
          <div class="sum">
            Total: <b>${{ grandTotal.toFixed(2) }}</b>
          </div>

          <div class="actions">
            <button class="btnGhost" @click="clear">
              Clear Cart
            </button>

            <button class="btn" @click="goToOtPurchase">
              Go to OT Purchase
            </button>
          </div>
        </div>
      </template>

      <p class="note">
        Note: This cart is only a local reading list for the demo. It does not create
        backend orders or send the selected book identifier to the server. To complete
        a privacy-preserving purchase, open a book detail page and use Privacy Purchase (OT).
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import {
  getCart,
  updateQty,
  removeItem,
  clearCart
} from '../utils/cartStore'

const router = useRouter()
const items = ref(getCart())

const grandTotal = computed(() => {
  return items.value.reduce((sum, x) => {
    return sum + Number(x.price || 0) * Number(x.qty || 0)
  }, 0)
})

function refresh() {
  items.value = getCart()
}

function cartKey(item) {
  return `${item.groupId || 'default'}-${item.choiceIndex}`
}

function onQty(item, e) {
  const qty = Number(e.target.value)

  updateQty(
    item.choiceIndex,
    item.groupId || 'default',
    qty
  )

  refresh()
}

function remove(item) {
  removeItem(
    item.choiceIndex,
    item.groupId || 'default'
  )

  refresh()
}

function clear() {
  clearCart()
  refresh()
}

function goToOtPurchase() {
  alert(
    'For the strict privacy version, please complete the purchase from the book detail page using Privacy Purchase (OT).'
  )

  router.push('/books')
}
</script>

<style>
.container {
  max-width: 980px;
  margin: 0 auto;
}

.cartCard {
  padding: 16px;
}

.qty {
  width: 90px;
  padding: 6px 8px;
  border: 1px solid #ddd;
  border-radius: 8px;
}

.empty {
  margin-top: 14px;
  color: #555;
}

.footer {
  margin-top: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.sum {
  font-size: 15px;
  color: #222;
}

.actions {
  display: flex;
  gap: 10px;
}

.note {
  margin-top: 12px;
  color: #666;
  font-size: 13px;
  line-height: 1.6;
}

.bookTitle {
  font-weight: 600;
  color: #222;
}

.privacyText {
  margin-top: 4px;
  font-size: 12px;
  color: #6b7280;
}
</style>