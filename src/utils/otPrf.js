// SHA-256 based PRF for OT key recovery

// Convert number to 8-byte big-endian Uint8Array
function intTo8Bytes(n) {
  let value = BigInt(n)
  const out = new Uint8Array(8)

  for (let i = 7; i >= 0; i--) {
    out[i] = Number(value & 0xffn)
    value = value >> 8n
  }

  return out
}

// Concatenate two Uint8Arrays
function concatBytes(a, b) {
  const out = new Uint8Array(a.length + b.length)
  out.set(a, 0)
  out.set(b, a.length)
  return out
}

// PRF(key, x) = SHA256(key || x_8bytes), truncated to length
export async function prf(keyBytes, x, length) {
  const xBytes = intTo8Bytes(x)
  const input = concatBytes(keyBytes, xBytes)

  const hashBuffer = await crypto.subtle.digest('SHA-256', input)
  const hashBytes = new Uint8Array(hashBuffer)

  return hashBytes.slice(0, length)
}