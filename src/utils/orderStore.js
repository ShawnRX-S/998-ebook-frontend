const KEY = 'orders'

export function getOrders() {
  const raw = localStorage.getItem(KEY)

  if (!raw) {
    return []
  }

  try {
    return JSON.parse(raw)
  } catch (e) {
    return []
  }
}

export function addOrder(order) {
  const list = getOrders()

  const safeOrder = {
    orderId: order.orderId,
    orderTime: order.orderTime,
    status: order.status || 'Completed by OT',
    total: Number(order.total || 0),
    items: (order.items || []).map((item) => ({
      groupId: item.groupId || 'default',
      choiceIndex: item.choiceIndex,
      title: item.title,
      author: item.author,
      price: Number(item.price || 0),
      qty: Number(item.qty || 1)
    }))
  }

  list.unshift(safeOrder)
  localStorage.setItem(KEY, JSON.stringify(list))
}

export function clearOrders() {
  localStorage.removeItem(KEY)
}