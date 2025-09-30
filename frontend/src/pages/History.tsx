import { useEffect, useMemo, useState } from 'react'
import { PostsStore } from '@/store/posts'
import type { Post, PostStatus } from '@/types'
import StatusBadge from '@/components/StatusBadge'

const filters: Array<{ key: 'all' | PostStatus, label: string }> = [
  { key: 'all', label: 'All' },
  { key: 'draft', label: 'Draft' },
  { key: 'validated', label: 'Validated' },
  { key: 'posted', label: 'Posted' },
  { key: 'deleted', label: 'Deleted' },
]

export default function History() {
  const [items, setItems] = useState<Post[]>([])
  const [filter, setFilter] = useState<typeof filters[number]['key']>('all')

  const refresh = () => setItems(PostsStore.getAll())
  useEffect(() => { refresh() }, [])

  const visible = useMemo(() => {
    return filter === 'all' ? items : items.filter(p => p.status === filter)
  }, [items, filter])

  const timeFor = (p: Post) => {
    if (p.status === 'posted') return p.postedAt || p.updatedAt
    if (p.status === 'validated') return p.validatedAt || p.updatedAt
    if (p.status === 'deleted') return p.deletedAt || p.updatedAt
    return p.updatedAt
  }

  return (
    <section>
      <div className="section-header">
        <h2 className="section-title">History</h2>
        <div style={{ display: 'flex', gap: '.4rem', flexWrap: 'wrap' }}>
          {filters.map(f => (
            <button key={f.key} className={`btn ${filter === f.key ? 'primary' : ''}`} onClick={() => setFilter(f.key)}>
              {f.label}
            </button>
          ))}
        </div>
      </div>
      <div className="spacer" />
      <div className="grid">
        {visible.map(p => (
          <div key={p.id} className="card">
            <img src={p.imageUrl} alt={p.title} />
            <div className="card-body">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '0.5rem' }}>
                <h3 className="card-title">{p.title}</h3>
                <StatusBadge status={p.status} />
              </div>
              <p className="card-text">{p.text}</p>
              <p className="muted" style={{ fontSize: '.85rem' }}>
                {new Date(timeFor(p)).toLocaleString()}
              </p>
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}
