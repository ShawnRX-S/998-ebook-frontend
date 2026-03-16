const KEY = 'cart'

function notifyCartChanged() {
  window.dispatchEvent(new CustomEvent('cart-updated'))
}

export function getCart() {
  const raw = localStorage.getItem(KEY)
  if (!raw) return []
  try {
    return JSON.parse(raw)
  } catch (e) {
    return []
  }
}

export function saveCart(list) {
  localStorage.setItem(KEY, JSON.stringify(list))
  notifyCartChanged()
}

export function addToCart(item) {
  const list = getCart()

  const found = list.find((x) => x.bookId === item.bookId)
  if (found) {
    found.qty = found.qty + 1
  } else {
    list.push({
      bookId: item.bookId,
      title: item.title,
      price: item.price,
      qty: 1
    })
  }

  saveCart(list)
}

export function updateQty(bookId, qty) {
  const list = getCart()
  const found = list.find((x) => x.bookId === bookId)
  if (!found) return

  const n = Number(qty)
  if (n <= 0) {
    const next = list.filter((x) => x.bookId !== bookId)
    saveCart(next)
    return
  }

  found.qty = n
  saveCart(list)
}

export function removeItem(bookId) {
  const list = getCart().filter((x) => x.bookId !== bookId)
  saveCart(list)
}

export function clearCart() {
  localStorage.removeItem(KEY)
  notifyCartChanged()
}