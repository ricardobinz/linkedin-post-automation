import { Routes, Route, Navigate } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import PostEditor from './pages/PostEditor'
import Validated from './pages/Validated'
import History from './pages/History'
import Header from './components/Header'

function App() {
  return (
    <div className="app">
      <Header />
      <main className="container">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/editor/:id" element={<PostEditor />} />
          <Route path="/validated" element={<Validated />} />
          <Route path="/history" element={<History />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </div>
  )
}

export default App
