const USERS_KEY = 'users'
const AUTH_KEY = 'auth'
const ROLE_USER = 'user'
const ROLE_ADMIN = 'admin'
const DEFAULT_ADMIN_USERNAME = 'admin'
const DEFAULT_ADMIN_PASSWORD = 'admin123'

const DEFAULT_USERS = {
  [DEFAULT_ADMIN_USERNAME]: {
    password: DEFAULT_ADMIN_PASSWORD,
    role: ROLE_ADMIN
  }
}

function safeParseJson(raw) {
  try {
    return raw ? JSON.parse(raw) : null
  } catch {
    return null
  }
}

function normalizeUsers(parsed) {
  // Backward compatible migration:
  // old shape -> { username: "password" }
  // new shape -> { username: { password, role } }
  const normalized = {}
  for (const [username, value] of Object.entries(parsed || {})) {
    if (value && typeof value === 'object') {
      normalized[username] = {
        password: String(value.password || ''),
        role: value.role === ROLE_ADMIN ? ROLE_ADMIN : ROLE_USER
      }
      continue
    }
    normalized[username] = {
      password: String(value || ''),
      role: ROLE_USER
    }
  }

  // Ensure built-in super admin always exists in initial logic.
  if (!normalized[DEFAULT_ADMIN_USERNAME]) {
    normalized[DEFAULT_ADMIN_USERNAME] = { ...DEFAULT_USERS[DEFAULT_ADMIN_USERNAME] }
  }

  return normalized
}

function writeUsers(users) {
  localStorage.setItem(USERS_KEY, JSON.stringify(users))
  window.dispatchEvent(new CustomEvent('users-changed'))
}

function readUsers() {
  const parsed = safeParseJson(localStorage.getItem(USERS_KEY))
  const normalized = normalizeUsers(parsed && typeof parsed === 'object' ? parsed : {})
  const raw = localStorage.getItem(USERS_KEY)
  if (!raw || safeParseJson(raw)?.[DEFAULT_ADMIN_USERNAME] == null) {
    writeUsers(normalized)
  }
  return normalized
}

function notifyAuthChanged() {
  window.dispatchEvent(new CustomEvent('auth-changed'))
}

export function getAuth() {
  const parsed = safeParseJson(localStorage.getItem(AUTH_KEY))
  if (!parsed || typeof parsed !== 'object') return null

  const role = parsed.role === ROLE_ADMIN ? ROLE_ADMIN : ROLE_USER
  return {
    loggedIn: !!parsed.loggedIn,
    username: String(parsed.username || ''),
    role,
    isAdmin: role === ROLE_ADMIN
  }
}

export function isLoggedIn() {
  const auth = getAuth()
  return !!(auth && auth.loggedIn)
}

export function getCurrentUsername() {
  const auth = getAuth()
  return auth?.username || ''
}

export function hasRole(role) {
  const auth = getAuth()
  if (!auth || !auth.loggedIn) return false
  return auth.role === role
}

export function isAdmin() {
  return hasRole(ROLE_ADMIN)
}

export function register(username, password) {
  const u = String(username || '').trim()
  const p = String(password || '')

  if (!u) throw new Error('Username is required')
  if (!p) throw new Error('Password is required')

  const users = readUsers()
  if (users[u]) throw new Error('Username already exists')

  // Demo-only: store plaintext password.
  users[u] = {
    password: p,
    role: ROLE_USER
  }
  writeUsers(users)
}

export function login(username, password) {
  const u = String(username || '').trim()
  const p = String(password || '')
  const users = readUsers()
  const account = users[u]

  if (!u || !p) throw new Error('Invalid credentials')
  if (!account || account.password !== p) throw new Error('Invalid credentials')

  const role = account.role === ROLE_ADMIN ? ROLE_ADMIN : ROLE_USER
  const auth = {
    loggedIn: true,
    username: u,
    role,
    isAdmin: role === ROLE_ADMIN
  }
  localStorage.setItem(AUTH_KEY, JSON.stringify(auth))
  notifyAuthChanged()
  return auth
}

export function logout() {
  localStorage.removeItem(AUTH_KEY)
  notifyAuthChanged()
}

