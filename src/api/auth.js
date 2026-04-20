export function login(data) {
  const { username, password } = data

  if (!username || !password) {
    return Promise.resolve({
      success: false,
      message: 'Username or password is required'
    })
  }

  if (username === 'admin') {
    return Promise.resolve({
      success: true,
      token: 'mock-admin-token',
      role: 'admin',
      username: 'admin'
    })
  }

  return Promise.resolve({
    success: true,
    token: 'mock-user-token',
    role: 'user',
    username
  })
}