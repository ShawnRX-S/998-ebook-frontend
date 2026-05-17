import { P, G, modPow, randomBigInt, xorBytes, bigintToBytes } from './otUtils'

// SHA-256 helper, same as Python hashlib.sha256(str(k).encode()).digest()
async function sha256OfBigIntDecimal(value) {
  const input = bigintToBytes(value)
  const hashBuffer = await crypto.subtle.digest('SHA-256', input)
  return new Uint8Array(hashBuffer)
}

// Client-side step 1
// Python: receiver_step1(bit)
export function receiverStep1(bit) {
  if (bit !== 0 && bit !== 1) {
    throw new Error('bit must be 0 or 1')
  }

  let x = randomBigInt() % (P - 3n)
  x = x + 2n

  const h = modPow(G, x, P)

  let fake = randomBigInt() % (P - 3n)
  fake = fake + 2n

  if (bit === 0) {
    return {
      h0: h.toString(),
      h1: fake.toString(),
      x
    }
  }

  return {
    h0: fake.toString(),
    h1: h.toString(),
    x
  }
}

// Client-side step 3
// Python: receiver_step3(c0, c1, gy, x, bit)
export async function receiverStep3(c0Bytes, c1Bytes, gyValue, x, bit) {
  if (bit !== 0 && bit !== 1) {
    throw new Error('bit must be 0 or 1')
  }

const gy = BigInt(gyValue)
const k = modPow(gy, x, P)
const kBytes = await sha256OfBigIntDecimal(k)

console.log('Frontend receiverStep3 bit:', bit)
console.log('Frontend shared k prefix:', k.toString().slice(0, 32))
console.log(
  'Frontend shared hash prefix:',
  Array.from(kBytes)
    .map((b) => b.toString(16).padStart(2, '0'))
    .join('')
    .slice(0, 32)
)

  if (bit === 0) {
    return xorBytes(c0Bytes, kBytes.slice(0, c0Bytes.length))
  }

  return xorBytes(c1Bytes, kBytes.slice(0, c1Bytes.length))
}