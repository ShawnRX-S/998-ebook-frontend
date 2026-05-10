function base64ToBytes(base64) {
  const binary = atob(base64)

  const bytes = new Uint8Array(binary.length)

  for (let i = 0; i < binary.length; i++) {
    bytes[i] = binary.charCodeAt(i)
  }

  return bytes
}

export async function aesGcmDecrypt(payload, keyBytes) {
  const nonce = base64ToBytes(payload.nonce)
  const ciphertext = base64ToBytes(payload.ciphertext)
  const tag = base64ToBytes(payload.tag)

  const encrypted = new Uint8Array(ciphertext.length + tag.length)

  encrypted.set(ciphertext)
  encrypted.set(tag, ciphertext.length)

  const cryptoKey = await window.crypto.subtle.importKey(
    'raw',
    keyBytes,
    {
      name: 'AES-GCM'
    },
    false,
    ['decrypt']
  )

  const decrypted = await window.crypto.subtle.decrypt(
    {
      name: 'AES-GCM',
      iv: nonce
    },
    cryptoKey,
    encrypted
  )

  return new TextDecoder().decode(decrypted)
}