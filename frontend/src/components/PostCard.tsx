import type { Post } from '@/types'
import StatusBadge from './StatusBadge'

interface Props {
  post: Post
  showActions?: Array<'edit' | 'validate' | 'delete' | 'publish'>
  onEdit?: (id: string) => void
  onValidate?: (id: string) => void
  onDelete?: (id: string) => void
  onPublish?: (id: string) => void
}

export default function PostCard({ post, showActions = [], onEdit, onValidate, onDelete, onPublish }: Props) {
  return (
    <div className="card">
      <img src={post.imageUrl} alt={post.title} />
      <div className="card-body">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '0.5rem' }}>
          <h3 className="card-title" title={post.title}>{post.title}</h3>
          <StatusBadge status={post.status} />
        </div>
        <p className="card-text">{post.text}</p>
        <div className="card-actions">
          {showActions.includes('edit') && (
            <button className="btn" onClick={() => onEdit?.(post.id)}>
              <span className="icon">✏️</span>
              Edit
            </button>
          )}
          {showActions.includes('validate') && (
            <button className="btn success" onClick={() => onValidate?.(post.id)}>
              <span className="icon">✅</span>
              Validate
            </button>
          )}
          {showActions.includes('delete') && (
            <button className="btn danger" onClick={() => onDelete?.(post.id)}>
              <span className="icon">🗑️</span>
              Delete
            </button>
          )}
          {showActions.includes('publish') && (
            <button className="btn primary" onClick={() => onPublish?.(post.id)}>
              <span className="icon">📤</span>
              Publish
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
