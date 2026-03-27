import { ref } from 'vue'
import { books as defaultBooks } from '../data/books'

const STORAGE_KEY = 'books'
const BOOKS_UPDATED_EVENT = 'books-updated'

// Singleton reactive ref shared across all components using this store.
// This ensures immediate UI updates even if an event listener timing is off.
let booksSingleton = ref([])
let syncAttached = false

function safeParseJson(raw) {
  try {
    return raw ? JSON.parse(raw) : null
  } catch {
    return null
  }
}

function normalizeBook(raw) {
  const obj = raw && typeof raw === 'object' ? raw : {}

  const title = String(obj.title || '').trim()
  const author = String(obj.author || '').trim()

  // Accept both `description` and legacy `summary`.
  const description = String(obj.description ?? obj.summary ?? '').trim()

  const id = Number(obj.id)
  const price = Number(obj.price)

  const coverImage = obj.coverImage ? String(obj.coverImage) : ''
  const isPrivacyProtected = Boolean(obj.isPrivacyProtected ?? obj.encrypted ?? obj.category === 'Privacy')

  // Keep legacy fields if present for existing UI, but ensure required fields exist.
  const category = obj.category ? String(obj.category) : isPrivacyProtected ? 'Privacy' : ''
  const rating = obj.rating != null ? Number(obj.rating) : 4.6
  const coverText = obj.coverText ? String(obj.coverText) : 'EBOOK'

  return {
    id: Number.isFinite(id) ? id : 0,
    title,
    author,
    price: Number.isFinite(price) ? price : 0,
    description,
    coverImage,
    isPrivacyProtected,
    // legacy / UI convenience
    category,
    rating,
    summary: description,
    coverText
  }
}

function seedDefaults() {
  const seeded = defaultBooks.map((b) =>
    normalizeBook({
      id: b.id,
      title: b.title,
      author: b.author,
      price: b.price,
      description: b.summary,
      coverImage: '',
      isPrivacyProtected: b.category === 'Privacy',
      category: b.category,
      rating: b.rating,
      coverText: b.coverText,
      encrypted: true
    })
  )

  localStorage.setItem(STORAGE_KEY, JSON.stringify(seeded))
  window.dispatchEvent(new CustomEvent(BOOKS_UPDATED_EVENT))
  return seeded
}

export function getBooks() {
  const parsed = safeParseJson(localStorage.getItem(STORAGE_KEY))
  if (!Array.isArray(parsed) || parsed.length === 0) return seedDefaults()

  const normalized = parsed.map(normalizeBook).filter((b) => b.id > 0 && b.title)
  if (normalized.length === 0) return seedDefaults()
  return normalized
}

export function setBooks(next) {
  const arr = Array.isArray(next) ? next : []
  const normalized = arr.map(normalizeBook).filter((b) => b.id > 0 && b.title)
  localStorage.setItem(STORAGE_KEY, JSON.stringify(normalized))

  // Update the shared reactive source immediately.
  booksSingleton.value = normalized

  window.dispatchEvent(new CustomEvent(BOOKS_UPDATED_EVENT))
  return normalized
}

export function addBook(partial) {
  const list = getBooks()
  const maxId = list.reduce((max, b) => Math.max(max, Number(b.id) || 0), 0)
  const nextId = maxId + 1

  const created = normalizeBook({
    ...partial,
    id: nextId
  })

  return setBooks([created, ...list])
}

export function updateBook(id, patch) {
  const list = getBooks()
  const next = list.map((b) => (b.id === Number(id) ? normalizeBook({ ...b, ...patch }) : b))
  return setBooks(next)
}

export function deleteBook(id) {
  const list = getBooks()
  return setBooks(list.filter((b) => b.id !== Number(id)))
}

function ensureBooksSingletonInit() {
  if (booksSingleton.value && booksSingleton.value.length > 0) return
  // Initialize once (and seed defaults if needed).
  booksSingleton.value = getBooks()
}

function ensureSyncAttached() {
  if (syncAttached) return

  // Refresh singleton when another tab updates localStorage.
  window.addEventListener('storage', (e) => {
    if (e && e.key && e.key !== STORAGE_KEY) return
    booksSingleton.value = getBooks()
  })

  // Refresh within the same tab.
  window.addEventListener(BOOKS_UPDATED_EVENT, () => {
    booksSingleton.value = getBooks()
  })

  syncAttached = true
}

export function useBooks() {
  ensureBooksSingletonInit()
  ensureSyncAttached()

  const refresh = () => {
    booksSingleton.value = getBooks()
  }

  // Kept for API compatibility. Event listeners are singleton-managed.
  const stop = () => {}

  return { books: booksSingleton, refresh, stop }
}

