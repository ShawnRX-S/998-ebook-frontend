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
            <tr v-for="it in items" :key="it.bookId">
              <td>{{ it.title }}</td>
              <td>${{ it.price }}</td>
              <td>
                <input
                  class="qty"
                  type="number"
                  min="1"
                  :value="it.qty"
                  @input="onQty(it.bookId, $event)"
                />
              </td>
              <td>${{ (it.price * it.qty).toFixed(2) }}</td>
              <td>
                <button class="btnDanger" @click="remove(it.bookId)">Remove</button>
              </td>
            </tr>
          </tbody>
        </table>

        <div class="footer">
          <div class="sum">
            Total: <b>${{ grandTotal.toFixed(2) }}</b>
          </div>

          <div class="actions">
            <button class="btnGhost" @click="clear">Clear Cart</button>
            <button class="btn" @click="checkout">Checkout</button>
          </div>
        </div>
      </template>

      <p class="note">
        Note: Checkout is simulated. Later you can connect it to backend purchase + OT.
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { getCart, updateQty, removeItem, clearCart } from '../utils/cartStore'
import { addOrder } from '../utils/orderStore'

const router = useRouter()
const items = ref(getCart())

const grandTotal = computed(() => {
  return items.value.reduce((sum, x) => sum + Number(x.price) * Number(x.qty), 0)
})

function refresh() {
  items.value = getCart()
}

function onQty(bookId, e) {
  updateQty(bookId, e.target.value)
  refresh()
}

function remove(bookId) {
  removeItem(bookId)
  refresh()
}

function clear() {
  clearCart()
  refresh()
}

function checkout() {
  const cartItems = getCart()

  if (cartItems.length === 0) {
    alert('Your cart is empty.')
    return
  }

  const total = cartItems.reduce((sum, x) => {
    return sum + Number(x.price) * Number(x.qty)
  }, 0)

  const order = {
    orderId: 'ORD-' + Date.now(),
    time: new Date().toLocaleString(),
    status: 'PAID',
    items: cartItems.map((x) => ({
      bookId: x.bookId,
      title: x.title,
      price: x.price,
      qty: x.qty
    })),
    total: Number(total.toFixed(2))
  }

  addOrder(order)
  clearCart()
  refresh()
  router.push('/orders')
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
}
</style>