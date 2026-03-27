import CryptoJS from 'crypto-js'

// Simple AES helper for simulating encrypted ebook payloads.
// Uses CryptoJS' built-in passphrase-based AES encryption scheme.

/**
 * Encrypt a string with AES.
 * @param {string} plainText
 * @param {string} secret Passphrase used as encryption key.
 * @returns {string} Ciphertext (string form, suitable for storage)
 */
export function aesEncryptString(plainText, secret) {
  if (plainText === undefined || plainText === null) return ''
  if (!secret) throw new Error('aesEncryptString: secret is required')
  return CryptoJS.AES.encrypt(String(plainText), secret).toString()
}

/**
 * Decrypt AES ciphertext back to a UTF-8 string.
 * @param {string} cipherText
 * @param {string} secret Passphrase used as encryption key.
 * @returns {string|null}
 */
export function aesDecryptString(cipherText, secret) {
  if (cipherText === undefined || cipherText === null || cipherText === '') return null
  if (!secret) throw new Error('aesDecryptString: secret is required')

  try {
    const bytes = CryptoJS.AES.decrypt(String(cipherText), secret)
    const out = bytes.toString(CryptoJS.enc.Utf8)
    return out || null
  } catch (e) {
    return null
  }
}

/**
 * Encrypt any JSON-serializable value.
 * @param {any} value
 * @param {string} secret
 * @returns {string}
 */
export function aesEncryptJson(value, secret) {
  return aesEncryptString(JSON.stringify(value), secret)
}

/**
 * Decrypt ciphertext into JSON.
 * @param {string} cipherText
 * @param {string} secret
 * @returns {any|null}
 */
export function aesDecryptJson(cipherText, secret) {
  const str = aesDecryptString(cipherText, secret)
  if (!str) return null
  try {
    return JSON.parse(str)
  } catch (e) {
    return null
  }
}

