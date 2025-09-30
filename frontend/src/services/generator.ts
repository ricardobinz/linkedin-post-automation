import type { Post } from '@/types'

const topics = [
  'AI productivity', 'Remote work', 'Leadership', 'Career growth', 'Developer tools', 'Open source',
  'Design systems', 'Product strategy', 'Team culture', 'Testing', 'Performance', 'Security',
]

const templates = [
  (topic: string) => `Quick tip on ${topic}: start small, measure impact, iterate fast. Consistency beats intensity. #${topic.replace(/\s+/g, '')}`,
  (topic: string) => `Lessons learned shipping a feature around ${topic}:\n- Define success clearly\n- Align early with stakeholders\n- Ship in slices\nWhat would you add?`,
  (topic: string) => `Why ${topic} matters in 2025: it helps teams focus on outcomes, not output. The best teams are ruthlessly simple.`,
]

function randomOf<T>(arr: T[]): T { return arr[Math.floor(Math.random() * arr.length)] }

function safeKeyword(s: string) { return s.toLowerCase().replace(/[^a-z0-9]+/g, '-').slice(0, 24) || 'post' }

export function generateTitle(): string {
  const topic = randomOf(topics)
  const variations = [
    `Thoughts on ${topic}`,
    `${topic} in practice`,
    `Making the most of ${topic}`,
    `${topic}: what works for us`,
  ]
  return randomOf(variations)
}

export function generateText(title?: string): string {
  const topic = title?.replace(/:.*/,'').replace(/\s+in.*/, '') || randomOf(topics)
  return randomOf(templates)(topic)
}

export function generateImage(seed?: string): string {
  const k = safeKeyword(seed || randomOf(topics))
  // Stable placeholder image based on seed using picsum
  return `https://picsum.photos/seed/${encodeURIComponent(k)}-lg/800/450`
}

export function generateDraft(): Post {
  const id = crypto?.randomUUID ? crypto.randomUUID() : Math.random().toString(36).slice(2)
  const title = generateTitle()
  const text = generateText(title)
  const imageUrl = generateImage(title)
  const now = new Date().toISOString()
  return {
    id,
    title,
    text,
    imageUrl,
    status: 'draft',
    createdAt: now,
    updatedAt: now,
  }
}
