const KEY = 'cart'

function notifyCartChanged() {
  window.dispatchEvent(new CustomEvent('cart-updated'))
}

export function getCart() {
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

export function saveCart(list) {
  localStorage.setItem(KEY, JSON.stringify(list))
  notifyCartChanged()
}

export function addToCart(item) {
  const list = getCart()
  const groupId = item.groupId || 'default'
  const choiceIndex = Number(item.choiceIndex)

  const found = list.find((x) => {
    return (
      Number(x.choiceIndex) === choiceIndex &&
      (x.groupId || 'default') === groupId
    )
  })

  if (found) {
    found.qty = Number(found.qty || 0) + 1
  } else {
    list.push({
      choiceIndex,
      groupId,
      title: item.title,
      author: item.author,
      price: Number(item.price || 0),
      coverText: item.coverText,
      qty: 1
    })
  }

  saveCart(list)
}

export function updateQty(choiceIndex, groupId, qty) {
  const targetChoiceIndex = Number(choiceIndex)
  const targetGroupId = groupId || 'default'
  const newQty = Number(qty)

  const list = getCart()
  const next = []

  for (let i = 0; i < list.length; i++) {
    const item = list[i]

    const sameItem =
      Number(item.choiceIndex) === targetChoiceIndex &&
      (item.groupId || 'default') === targetGroupId

    if (sameItem) {
      if (newQty > 0) {
        item.qty = newQty
        next.push(item)
      }
    } else {
      next.push(item)
    }
  }

  saveCart(next)
}

export function removeItem(choiceIndex, groupId) {
  const targetChoiceIndex = Number(choiceIndex)
  const targetGroupId = groupId || 'default'

  const list = getCart().filter((item) => {
    return !(
      Number(item.choiceIndex) === targetChoiceIndex &&
      (item.groupId || 'default') === targetGroupId
    )
  })

  saveCart(list)
}

export function removeFromCart(choiceIndex, groupId) {
  removeItem(choiceIndex, groupId)
}

export function clearCart() {
  saveCart([])
}

export function getCartCount() {
  return getCart().reduce((sum, item) => {
    return sum + Number(item.qty || 0)
  }, 0)
}

export function getCartTotal() {
  return getCart().reduce((sum, item) => {
    return sum + Number(item.price || 0) * Number(item.qty || 0)
  }, 0)
}