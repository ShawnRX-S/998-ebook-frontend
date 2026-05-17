<template>
  <div class="container">
    <h2>Orders</h2>

    <div class="actions">
      <button class="btnGhost" @click="refresh">Refresh</button>
      <button class="btnDanger" @click="doClear">Clear Orders</button>
    </div>

    <div v-if="orders.length === 0" class="empty">
      No OT orders yet. Go to Books and complete a Privacy Purchase.
    </div>

    <div v-else class="orderList">
      <div
        class="orderCard card"
        v-for="o in orders"
        :key="o.orderId"
      >
        <div class="orderHeader">
          <div>
            <div class="oid">{{ o.orderId }}</div>
            <div class="meta">
              Time: {{ o.orderTime || o.time }} · Status: {{ o.status }}
            </div>
          </div>

          <div class="right">
            <div class="total">
              Total: ${{ Number(o.total || 0).toFixed(2) }}
            </div>

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
                <th>Privacy Status</th>
              </tr>
            </thead>

            <tbody>
              <tr
                v-for="it in o.items"
                :key="orderItemKey(it)"
              >
                <td>
                  <div class="bookTitle">{{ it.title }}</div>
                  <div class="privacyText">
                    Purchased through the OT privacy-preserving flow.
                  </div>
                </td>

                <td>${{ Number(it.price || 0).toFixed(2) }}</td>
                <td>{{ Number(it.qty || 1) }}</td>

                <td>
                  ${{ (Number(it.price || 0) * Number(it.qty || 1)).toFixed(2) }}
                </td>

                <td>
                  <span class="privacyBadge">
                    OT Protected
                  </span>
                </td>
              </tr>
            </tbody>
          </table>

          <p class="note">
            This order record is stored locally for demonstration purposes. The selected
            book identifier is not sent to the backend as a normal order payload.
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getOrderList, clearOrderList } from '../api/orders'

const orders = ref([])
const openId = ref('')

async function refresh() {
  orders.value = await getOrderList()
}

async function doClear() {
  await clearOrderList()
  await refresh()
  openId.value = ''
}

function toggle(id) {
  openId.value = openId.value === id ? '' : id
}

function orderItemKey(item) {
  return `${item.groupId || 'default'}-${item.choiceIndex}`
}

onMounted(async () => {
  await refresh()
})
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

.privacyBadge {
  display: inline-block;
  padding: 5px 9px;
  border-radius: 999px;
  background: rgba(37, 99, 235, 0.08);
  color: #2563eb;
  font-size: 12px;
  font-weight: 700;
}
</style>