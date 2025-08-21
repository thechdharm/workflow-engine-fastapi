import { Route, Routes, Link, Navigate } from 'react-router-dom'
import WorkflowsPage from './pages/WorkflowsPage'
import BuilderPage from './pages/BuilderPage'
import ExecutionsPage from './pages/ExecutionsPage'

export default function App() {
  return (
    <div className="app-shell">
      <header>
        <nav>
          <Link to="/workflows">Workflows</Link>
          <Link to="/executions">Executions</Link>
          <a href="https://reactflow.dev" target="_blank" rel="noreferrer">React Flow</a>
        </nav>
      </header>
      <main>
        <Routes>
          <Route path="/" element={<Navigate to="/workflows" replace />} />
          <Route path="/workflows" element={<WorkflowsPage />} />
          <Route path="/workflows/:id" element={<BuilderPage />} />
          <Route path="/executions" element={<ExecutionsPage />} />
        </Routes>
      </main>
    </div>
  )
}


