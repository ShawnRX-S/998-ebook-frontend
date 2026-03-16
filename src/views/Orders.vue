<template>
  <div class="container">
    <h2>Orders</h2>

    <div class="actions">
      <button class="btnGhost" @click="refresh">Refresh</button>
      <button class="btnDanger" @click="doClear">Clear Orders</button>
    </div>

    <div v-if="orders.length === 0" class="empty">
      No orders yet. Go to Books and checkout from Cart.
    </div>

    <div v-else class="orderList">
      <div class="orderCard card" v-for="o in orders" :key="o.orderId">
        <div class="orderHeader">
          <div>
            <div class="oid">{{ o.orderId }}</div>
            <div class="meta">Time: {{ o.time }} · Status: {{ o.status }}</div>
          </div>

          <div class="right">
            <div class="total">Total: ${{ o.total }}</div>
            <button class="btn" @click="toggle(o.orderId)">
              {{ openId === o.orderId ? 'Hide' : 'View' }}
            </button>
          </div>
        </div>

        <div v-if="openId === o.orderId" class="orderBody">
          <table class="table">
            <thead>
              <tr>
                <th>Book</th>
                <th>Price</th>
                <th>Qty</th>
                <th>Line Total</th>
                <th>Action</th>
              </tr>
            </thead>

            <tbody>
              <tr v-for="it in o.items" :key="it.bookId">
                <td>{{ it.title }}</td>
                <td>${{ it.price }}</td>
                <td>{{ it.qty }}</td>
                <td>${{ (it.price * it.qty).toFixed(2) }}</td>
                <td>
                  <button class="btnGhost" @click="download(o, it)">Download</button>
                </td>
              </tr>
            </tbody>
          </table>

          <p class="note">
            Note: Download is simulated. Later the backend OT module will provide the real ebook.
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { getOrders, clearOrders } from '../utils/orderStore'

const orders = ref(getOrders())
const openId = ref('')

function refresh() {
  orders.value = getOrders()
}

function doClear() {
  clearOrders()
  refresh()
  openId.value = ''
}

function toggle(id) {
  openId.value = openId.value === id ? '' : id
}

function download(order, item) {
  alert('Simulated download: ' + item.title + ' (Order: ' + order.orderId + ')')
}
</script>

<style>
.container {
  max-width: 980px;
  margin: 0 auto;
}

.actions {
  margin: 10px 0 14px 0;
  display: flex;
  gap: 10px;
}

.orderList {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.orderCard {
  border: 1px solid #e7e7e7;
  border-radius: 14px;
  background: #fff;
  padding: 14px;
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.03);
}

.orderHeader {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.oid {
  font-weight: 700;
  color: #222;
}

.meta {
  margin-top: 4px;
  color: #666;
  font-size: 13px;
}

.right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.total {
  font-weight: 700;
}

.orderBody {
  margin-top: 12px;
}

.empty {
  margin-top: 14px;
  color: #555;
}

.note {
  margin-top: 10px;
  color: #666;
  font-size: 13px;
}
</style>