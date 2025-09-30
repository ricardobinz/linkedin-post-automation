import { NavLink, useLocation, useNavigate } from 'react-router-dom'
import { PostsStore } from '@/store/posts'
import { generateDraft } from '@/services/generator'

export default function Header() {
  const navigate = useNavigate()
  const { pathname } = useLocation()

  const handleGenerate = () => {
    const draft = generateDraft()
    PostsStore.addDraft(draft)
    navigate(`/editor/${draft.id}`)
  }

  return (
    <header className="header">
      <div className="header-inner">
        <div className="brand">
          <i className="icon">✦</i>
          <span>LinkedIn Post Generator</span>
        </div>
        <nav className="nav">
          <NavLink to="/" className={({ isActive }) => isActive ? 'active' : ''}>Dashboard</NavLink>
          <NavLink to="/validated" className={({ isActive }) => isActive ? 'active' : ''}>Validated</NavLink>
          <NavLink to="/history" className={({ isActive }) => isActive ? 'active' : ''}>History</NavLink>
          {pathname !== '/editor' && (
            <button className="btn primary" onClick={handleGenerate} title="Generate a new post">
              <span className="icon">➕</span>
              Generate Post
            </button>
          )}
        </nav>
      </div>
    </header>
  )
}
