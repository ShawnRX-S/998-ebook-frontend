import { intToBitList, xorBytes } from './otUtils'
import { prf } from './otPrf'
import { receiverStep1, receiverStep3 } from './otChannel'

function toBytes(value) {
  if (value instanceof Uint8Array) {
    return value
  }

  if (value instanceof ArrayBuffer) {
    return new Uint8Array(value)
  }

  if (Array.isArray(value)) {
    return new Uint8Array(value)
  }

  throw new Error('OTReceiver expects byte arrays. Please base64-decode before calling it.')
}

export class OTReceiver {
  constructor(choiceIndex, levelCount) {
    if (choiceIndex < 0) {
      throw new Error('choiceIndex must be non-negative')
    }

    this.choiceIndex = Number(choiceIndex)
    this.levelCount = Number(levelCount)
    this.bits = intToBitList(this.choiceIndex, this.levelCount)
    this.selectedKeys = []
    this.pendingXByLevel = {}
  }

  startLevel(level) {
    const bit = this.bits[level]
    const result = receiverStep1(bit)

    this.pendingXByLevel[level] = result.x

    return {
      h0: result.h0,
      h1: result.h1
    }
  }

  async finishLevel(level, c0Bytes, c1Bytes, gy) {
    if (!(level in this.pendingXByLevel)) {
      throw new Error('startLevel must be called before finishLevel')
    }

    const bit = this.bits[level]
    const x = this.pendingXByLevel[level]

    delete this.pendingXByLevel[level]

    const selectedKey = await receiverStep3(
      toBytes(c0Bytes),
      toBytes(c1Bytes),
      gy,
      x,
      bit
    )

    this.selectedKeys.push(selectedKey)

    return selectedKey
  }

  async recoverKey(maskedKeys) {
    if (this.choiceIndex >= maskedKeys.length) {
      throw new Error('choiceIndex is outside maskedKeys')
    }

    if (this.selectedKeys.length !== this.bits.length) {
      throw new Error('not all OT levels have been completed')
    }

    const y = toBytes(maskedKeys[this.choiceIndex])

    let mask = new Uint8Array(y.length)

    for (const key of this.selectedKeys) {
      const prfBytes = await prf(key, this.choiceIndex, y.length)
      mask = xorBytes(mask, prfBytes)
    }

    return xorBytes(y, mask)
  }
}