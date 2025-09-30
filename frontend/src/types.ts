export type PostStatus = 'draft' | 'validated' | 'posted' | 'deleted'

export interface Post {
  id: string
  title: string
  text: string
  imageUrl: string
  status: PostStatus
  createdAt: string
  updatedAt: string
  validatedAt?: string
  postedAt?: string
  deletedAt?: string
}
