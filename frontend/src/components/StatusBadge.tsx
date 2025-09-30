import type { PostStatus } from '@/types'

export default function StatusBadge({ status }: { status: PostStatus }) {
  return (
    <span className={`badge ${status}`}>
      <span className="dot" />
      {status}
    </span>
  )
}
