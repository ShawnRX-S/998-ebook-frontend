import { getOrders, addOrder, clearOrders } from '../utils/orderStore'

export async function createOrder() {
  throw new Error(
    'Direct order creation with bookIds is disabled in the strict OT version.'
  )
}

export function addLocalOtOrder(order) {
  addOrder({
    orderId: order.orderId || createLocalOrderId(),
    orderTime: order.orderTime || new Date().toLocaleString(),
    status: order.status || 'Completed by OT',
    total: Number(order.total || 0),
    items: order.items || []
  })

  return Promise.resolve({
    success: true
  })
}

export function getOrderList() {
  return Promise.resolve(getOrders())
}

export function clearOrderList() {
  clearOrders()

  return Promise.resolve({
    success: true
  })
}

function createLocalOrderId() {
  return 'OT-' + Date.now()
}