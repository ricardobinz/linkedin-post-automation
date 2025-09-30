import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { PostsStore } from '@/store/posts'
import { generateDraft } from '@/services/generator'
import type { Post } from '@/types'
import PostCard from '@/components/PostCard'

export default function Dashboard() {
  const [drafts, setDrafts] = useState<Post[]>([])
  const navigate = useNavigate()

  const refresh = () => setDrafts(PostsStore.getByStatus('draft'))

  useEffect(() => { refresh() }, [])

  const handleGenerate = () => {
    const draft = generateDraft()
    PostsStore.addDraft(draft)
    refresh()
    navigate(`/editor/${draft.id}`)
  }

  const handleEdit = (id: string) => navigate(`/editor/${id}`)
  const handleValidate = (id: string) => { PostsStore.validate(id); refresh() }
  const handleDelete = (id: string) => { PostsStore.remove(id); refresh() }

  return (
    <section>
      <div className="section-header">
        <h2 className="section-title">Dashboard</h2>
        <button className="btn primary" onClick={handleGenerate}>
          <span className="icon">➕</span>
          Generate Post
        </button>
      </div>
      <p className="muted">Draft posts ready for review. Edit, validate, or delete.</p>
      <div className="spacer" />
      {drafts.length === 0 ? (
        <p className="muted">No drafts yet. Click "Generate Post" to create one.</p>
      ) : (
        <div className="grid">
          {drafts.map(p => (
            <PostCard key={p.id} post={p}
              showActions={['edit','validate','delete']}
              onEdit={handleEdit}
              onValidate={handleValidate}
              onDelete={handleDelete}
            />
          ))}
        </div>
      )}
    </section>
  )
}
