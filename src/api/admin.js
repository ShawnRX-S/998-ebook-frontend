import { books } from '../data/books'
import { getOrders } from '../utils/orderStore'

export function getAdminDashboard() {
  const orders = getOrders()

  return Promise.resolve({
    totalBooks: books.length,
    activeUsers: 128,
    privacySecurityLevel: 'High',
    totalOrders: orders.length
  })
}

export function getAdminBooks() {
  return Promise.resolve([...books])
}

export function getAdminOrders() {
  return Promise.resolve(getOrders())
}

export function getAdminUsers() {
  return Promise.resolve([
    { id: 1, username: 'admin', role: 'admin' },
    { id: 2, username: 'alice', role: 'user' },
    { id: 3, username: 'bob', role: 'user' }
  ])
}