function base64ToBytes(base64) {
  const binary = window.atob(base64)
  const bytes = new Uint8Array(binary.length)

  for (let i = 0; i < binary.length; i++) {
    bytes[i] = binary.charCodeAt(i)
  }

  return bytes
}

function concatBytes(a, b) {
  const result = new Uint8Array(a.length + b.length)
  result.set(a, 0)
  result.set(b, a.length)
  return result
}

function normaliseKeyBytes(key) {
  if (key instanceof Uint8Array) {
    return key
  }

  if (key instanceof ArrayBuffer) {
    return new Uint8Array(key)
  }

  if (Array.isArray(key)) {
    return new Uint8Array(key)
  }

  throw new Error('Invalid AES key format')
}

export async function aesGcmDecrypt(encryptedBook, aesKey) {
  const keyBytes = normaliseKeyBytes(aesKey)

  const nonce = base64ToBytes(encryptedBook.nonce)
  const ciphertext = base64ToBytes(encryptedBook.ciphertext)
  const tag = base64ToBytes(encryptedBook.tag)

  // Web Crypto AES-GCM expects ciphertext and authentication tag together.
  const encryptedData = concatBytes(ciphertext, tag)

  const cryptoKey = await window.crypto.subtle.importKey(
    'raw',
    keyBytes,
    {
      name: 'AES-GCM'
    },
    false,
    ['decrypt']
  )

  const plaintextBuffer = await window.crypto.subtle.decrypt(
    {
      name: 'AES-GCM',
      iv: nonce,
      tagLength: 128
    },
    cryptoKey,
    encryptedData
  )

  const decoder = new TextDecoder('utf-8')
  return decoder.decode(plaintextBuffer)
}