import axios from 'axios'

export function getOtHealth() {
  return axios.get('/api/health')
}

export function getOtCatalog(groupId = 'default') {
  return axios.get('/api/books/catalog', {
    params: {
      group_id: groupId
    }
  })
}

export function getEncryptedPackage(groupId = 'default') {
  return axios.get('/api/books/encrypted-package/' + groupId)
}

export function createOtSession(groupId = 'default') {
  return axios.post('/api/ot/session', {
    group_id: groupId
  })
}

export function sendOtStep(payload) {
  return axios.post('/api/ot/step', {
    session_id: payload.sessionId,
    level: payload.level,
    h0: payload.h0,
    h1: payload.h1
  })
}

export function clearOtSession(sessionId) {
  return axios.post('/api/ot/session/clear', {
    session_id: sessionId
  })
}