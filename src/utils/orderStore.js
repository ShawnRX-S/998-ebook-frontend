const KEY = 'orders'

export function getOrders() {
  const raw = localStorage.getItem(KEY)
  if (!raw) return []
  try {
    return JSON.parse(raw)
  } catch (e) {
    return []
  }
}

export function addOrder(order) {
  const list = getOrders()
  list.unshift(order)
  localStorage.setItem(KEY, JSON.stringify(list))
}

export function clearOrders() {
  localStorage.removeItem(KEY)
}