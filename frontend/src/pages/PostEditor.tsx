import { useEffect, useMemo, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { PostsStore } from '@/store/posts'
import { generateImage } from '@/services/generator'
import type { Post } from '@/types'

export default function PostEditor() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [post, setPost] = useState<Post | null>(null)

  useEffect(() => {
    if (!id) return
    const p = PostsStore.get(id)
    setPost(p ?? null)
  }, [id])

  const canValidate = useMemo(() => !!post && post.title.trim() && post.text.trim() && post.imageUrl.trim(), [post])

  if (!post) {
    return (
      <section>
        <h2 className="section-title">Post not found</h2>
        <p className="muted">The draft you are looking for does not exist. It may have been deleted.</p>
      </section>
    )
  }

  const update = (patch: Partial<Post>) => setPost(p => p ? { ...p, ...patch } : p)

  const saveDraft = () => {
    if (!post) return
    PostsStore.update(post)
    navigate('/')
  }

  const validate = () => {
    if (!post) return
    PostsStore.update(post)
    PostsStore.validate(post.id)
    navigate('/validated')
  }

  const regenImage = () => {
    const url = generateImage(post.title)
    update({ imageUrl: url })
  }

  return (
    <section>
      <div className="section-header">
        <h2 className="section-title">Edit Post</h2>
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <button className="btn" onClick={saveDraft}>
            <span className="icon">💾</span>
            Save draft
          </button>
          <button className="btn success" onClick={validate} disabled={!canValidate}>
            <span className="icon">✅</span>
            Validate
          </button>
        </div>
      </div>

      <div className="spacer" />
      <div className="form">
        <div className="field">
          <label className="label" htmlFor="title">Title</label>
          <input id="title" className="input" value={post.title} onChange={e => update({ title: e.target.value })} placeholder="Enter a short, descriptive title" />
        </div>

        <div className="field">
          <label className="label" htmlFor="text">Post text</label>
          <textarea id="text" className="textarea" value={post.text} onChange={e => update({ text: e.target.value })} placeholder="Write your LinkedIn post here" />
        </div>

        <div className="field">
          <label className="label">Image</label>
          <img src={post.imageUrl} alt="Post" style={{ width: '100%', borderRadius: 12, border: '1px solid var(--border)' }} />
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <button className="btn" onClick={regenImage}>
              <span className="icon">🎲</span>
              Regenerate image
            </button>
            <input className="input" value={post.imageUrl} onChange={e => update({ imageUrl: e.target.value })} placeholder="Paste image URL" />
          </div>
        </div>
      </div>
    </section>
  )
}
