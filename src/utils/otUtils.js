// OT helper utilities

// Public DH parameters from backend config.py
export const P = BigInt(
  '208351617316091241234326746312124448251235562226470491514186331217050270460481'
)

export const G = 2n

// XOR two Uint8Arrays
export function xorBytes(a, b) {
  const len = Math.min(a.length, b.length)
  const out = new Uint8Array(len)

  for (let i = 0; i < len; i++) {
    out[i] = a[i] ^ b[i]
  }

  return out
}

// Convert integer to fixed-length bit list
export function intToBitList(n, length) {
  const bits = Number(n)
    .toString(2)
    .padStart(length, '0')

  return bits.split('').map((x) => Number(x))
}

// Next power of two
export function nextPowerOfTwo(n) {
  if (n <= 1) return 1
  return 2 ** Math.ceil(Math.log2(n))
}

// Fast modular exponentiation for BigInt
export function modPow(base, exponent, modulus) {
  if (modulus === 1n) return 0n

  let result = 1n
  let b = base % modulus
  let e = exponent

  while (e > 0n) {
    if (e % 2n === 1n) {
      result = (result * b) % modulus
    }

    e = e / 2n
    b = (b * b) % modulus
  }

  return result
}

// Generate random bigint
export function randomBigInt() {
  const array = crypto.getRandomValues(new Uint32Array(8))

  let hex = ''

  for (const n of array) {
    hex += n.toString(16).padStart(8, '0')
  }

  return BigInt('0x' + hex)
}

// Convert Uint8Array to base64
export function bytesToBase64(bytes) {
  let binary = ''

  for (let i = 0; i < bytes.length; i++) {
    binary += String.fromCharCode(bytes[i])
  }

  return btoa(binary)
}

// Convert base64 to Uint8Array
export function base64ToBytes(base64) {
  const binary = atob(base64)
  const bytes = new Uint8Array(binary.length)

  for (let i = 0; i < binary.length; i++) {
    bytes[i] = binary.charCodeAt(i)
  }

  return bytes
}

// Convert bigint to SHA-256 input string
export function bigintToBytes(value) {
  return new TextEncoder().encode(value.toString())
}