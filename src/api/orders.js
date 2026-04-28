import axios from 'axios'
import { getOrders, clearOrders } from '../utils/orderStore'

// Backend create order
export async function createOrder(bookIds) {
  const user_id = 1

  const res = await axios.post('/api/orders', {
    user_id,
    book_ids: bookIds
  })

  return res.data
}

// Temporary local order list, because backend currently only has POST /api/orders
export function getOrderList() {
  return Promise.resolve(getOrders())
}

export function clearOrderList() {
  clearOrders()
  return Promise.resolve({
    success: true
  })
}