import type { Post, PostStatus } from '@/types'

const STORAGE_KEY = 'lpg_posts_v1'

const nowISO = () => new Date().toISOString()

function read(): Post[] {
  const raw = localStorage.getItem(STORAGE_KEY)
  if (!raw) return []
  try {
    const parsed = JSON.parse(raw) as Post[]
    return Array.isArray(parsed) ? parsed : []
  } catch {
    return []
  }
}

function write(posts: Post[]) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(posts))
}

function upsert(post: Post) {
  const posts = read()
  const idx = posts.findIndex(p => p.id === post.id)
  if (idx >= 0) posts[idx] = post
  else posts.unshift(post)
  write(posts)
}

export const PostsStore = {
  getAll(): Post[] { return read() },

  get(id: string): Post | undefined { return read().find(p => p.id === id) },

  getByStatus(status: PostStatus): Post[] { return read().filter(p => p.status === status) },

  addDraft(post: Post) {
    if (post.status !== 'draft') post.status = 'draft'
    post.createdAt ||= nowISO()
    post.updatedAt = nowISO()
    upsert(post)
  },

  update(post: Post) {
    post.updatedAt = nowISO()
    upsert(post)
  },

  validate(id: string) {
    const posts = read()
    const p = posts.find(x => x.id === id)
    if (!p) return
    p.status = 'validated'
    p.validatedAt = nowISO()
    p.updatedAt = p.validatedAt
    write(posts)
  },

  publish(id: string) {
    const posts = read()
    const p = posts.find(x => x.id === id)
    if (!p) return
    p.status = 'posted'
    p.postedAt = nowISO()
    p.updatedAt = p.postedAt
    write(posts)
  },

  remove(id: string) {
    const posts = read()
    const p = posts.find(x => x.id === id)
    if (!p) return
    p.status = 'deleted'
    p.deletedAt = nowISO()
    p.updatedAt = p.deletedAt
    write(posts)
  },
}
