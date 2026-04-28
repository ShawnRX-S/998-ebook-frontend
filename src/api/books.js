import axios from 'axios'

export async function getBooks(params = {}) {
  const res = await axios.get('/api/books', { params })

  const rawBooks = res.data.books || []

  const list = rawBooks.map((b) => ({
    id: b.id,
    title: b.title,
    author: b.author,
    price: Number(b.price),
    rating: b.rating,
    summary: b.summary,
    description: b.description,
    coverText: b.coverText || b.cover_text || shortCode(b.title),
    isPrivacyProtected: b.isPrivacyProtected === 1 || b.isPrivacyProtected === true,
    categoryId: b.category_id,
    category: mapCategoryName(b.category_id),
    coverPath: b.cover_path,
    filePath: b.file_path,
    createdAt: b.created_at
  }))

  return {
    list,
    total: list.length,
    page: Number(params.page || 1),
    pageSize: Number(params.pageSize || 9)
  }
}

export async function getBookDetail(id) {
  const res = await getBooks()
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

function mapCategoryName(categoryId) {
  const map = {
    1: 'Privacy',
    2: 'Cryptography',
    3: 'Security',
    4: 'E-commerce',
    5: 'Blockchain',
    6: 'Systems'
  }

  return map[categoryId] || 'Book'
}