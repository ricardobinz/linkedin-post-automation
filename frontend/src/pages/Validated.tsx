import { useEffect, useState } from 'react'
import { PostsStore } from '@/store/posts'
import type { Post } from '@/types'
import PostCard from '@/components/PostCard'

export default function Validated() {
  const [items, setItems] = useState<Post[]>([])
  const refresh = () => setItems(PostsStore.getByStatus('validated'))
  useEffect(() => { refresh() }, [])

  const handlePublish = (id: string) => { PostsStore.publish(id); refresh() }

  return (
    <section>
      <div className="section-header">
        <h2 className="section-title">Validated Posts</h2>
      </div>
      <p className="muted">These posts are ready to publish. Click publish when you're ready.</p>
      <div className="spacer" />
      {items.length === 0 ? (
        <p className="muted">No validated posts yet. Validate a draft to see it here.</p>
      ) : (
        <div className="grid">
          {items.map(p => (
            <PostCard key={p.id} post={p}
              showActions={['publish']}
              onPublish={handlePublish}
            />
          ))}
        </div>
      )}
    </section>
  )
}
