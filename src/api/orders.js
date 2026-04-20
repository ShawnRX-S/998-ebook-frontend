import { getOrders, addOrder, clearOrders } from '../utils/orderStore'

export function getOrderList() {
  return Promise.resolve(getOrders())
}

export function createOrder(order) {
  addOrder(order)
  return Promise.resolve({
    success: true,
    order
  })
}

export function clearOrderList() {
  clearOrders()
  return Promise.resolve({
    success: true
  })
}