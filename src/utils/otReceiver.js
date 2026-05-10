import { intToBitList, base64ToBytes, xorBytes } from './otUtils'
import { prf } from './otPrf'
import { receiverStep1, receiverStep3 } from './otChannel'

export class OTReceiver {
  constructor(choiceIndex, levelCount) {
    if (choiceIndex < 0) {
      throw new Error('choiceIndex must be non-negative')
    }

    this.choiceIndex = choiceIndex
    this.levelCount = levelCount
    this.bits = intToBitList(choiceIndex, levelCount)
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

  async finishLevel(level, c0Base64, c1Base64, gy) {
    if (!(level in this.pendingXByLevel)) {
      throw new Error('startLevel must be called before finishLevel')
    }

    const bit = this.bits[level]
    const x = this.pendingXByLevel[level]

    delete this.pendingXByLevel[level]

    const c0Bytes = base64ToBytes(c0Base64)
    const c1Bytes = base64ToBytes(c1Base64)

    const selectedKey = await receiverStep3(c0Bytes, c1Bytes, gy, x, bit)

    this.selectedKeys.push(selectedKey)

    return selectedKey
  }

  async recoverKey(maskedKeysBase64) {
    if (this.choiceIndex >= maskedKeysBase64.length) {
      throw new Error('choiceIndex is outside maskedKeys')
    }

    if (this.selectedKeys.length !== this.bits.length) {
      throw new Error('not all OT levels have been completed')
    }

    const y = base64ToBytes(maskedKeysBase64[this.choiceIndex])

    let mask = new Uint8Array(y.length)

    for (const key of this.selectedKeys) {
      const prfBytes = await prf(key, this.choiceIndex, y.length)
      mask = xorBytes(mask, prfBytes)
    }

    return xorBytes(y, mask)
  }
}