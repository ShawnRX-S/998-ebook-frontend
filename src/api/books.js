import { getOtCatalog } from './ot'

export async function getBooks(params = {}) {
  const {
    page = 1,
    pageSize = 9,
    category = 'ALL',
    keyword = '',
    sort = 'NONE'
  } = params

  const res = await getOtCatalog('default')
  const rawBooks = res.data.books || []

  let list = rawBooks.map((b) => ({
    id: Number(b.index) + 1,
    choiceIndex: Number(b.index),
    groupId: res.data.group_id || 'default',
    title: b.title,
    author: b.author,
    filename: b.filename,
    price: 9.99,
    rating: 4.5,
    summary: 'Privacy-preserving ebook protected by OT.',
    description: 'This ebook can be purchased through the OT privacy-preserving flow.',
    coverText: shortCode(b.title),
    isPrivacyProtected: true,
    category: 'Privacy'
  }))

  if (category !== 'ALL') {
    list = list.filter((b) => b.category === category)
  }

  const k = keyword.trim().toLowerCase()
  if (k) {
    list = list.filter((b) => {
      const t = (b.title || '').toLowerCase()
      const a = (b.author || '').toLowerCase()
      const s = (b.summary || b.description || '').toLowerCase()
      return t.includes(k) || a.includes(k) || s.includes(k)
    })
  }

  if (sort === 'PRICE_ASC') {
    list.sort((x, y) => Number(x.price) - Number(y.price))
  } else if (sort === 'PRICE_DESC') {
    list.sort((x, y) => Number(y.price) - Number(x.price))
  }

  const total = list.length
  const size = Number(pageSize)
  const start = (Number(page) - 1) * size
  const paged = list.slice(start, start + size)

  return {
    list: paged,
    total,
    page: Number(page),
    pageSize: size
  }
}

export async function getBookDetail(id) {
  const res = await getBooks({
    page: 1,
    pageSize: 999
  })

  return res.list.find((b) => b.id === Number(id)) || null
}

function shortCode(title) {
  return String(title || '')
    .split(' ')
    .slice(0, 3)
    .map((x) => x[0])
    .join('')
    .toUpperCase()
}