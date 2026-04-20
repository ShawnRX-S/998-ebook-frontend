import { books } from '../data/books'

export function getBooks(params = {}) {
  const {
    page = 1,
    pageSize = 9,
    category = 'ALL',
    keyword = '',
    sort = 'NONE'
  } = params

  let list = [...books]

  if (category !== 'ALL') {
    list = list.filter((b) => b.category === category)
  }

  const k = keyword.trim().toLowerCase()
  if (k) {
    list = list.filter((b) => {
      const t = (b.title || '').toLowerCase()
      const a = (b.author || '').toLowerCase()
      const s = (b.summary || '').toLowerCase()
      return t.includes(k) || a.includes(k) || s.includes(k)
    })
  }

  if (sort === 'PRICE_ASC') {
    list.sort((x, y) => Number(x.price) - Number(y.price))
  } else if (sort === 'PRICE_DESC') {
    list.sort((x, y) => Number(y.price) - Number(x.price))
  }

  const total = list.length
  const start = (Number(page) - 1) * Number(pageSize)
  const paged = list.slice(start, start + Number(pageSize))

  return Promise.resolve({
    list: paged,
    total,
    page: Number(page),
    pageSize: Number(pageSize)
  })
}

export function getBookDetail(id) {
  const book = books.find((b) => b.id === Number(id))
  return Promise.resolve(book || null)
}