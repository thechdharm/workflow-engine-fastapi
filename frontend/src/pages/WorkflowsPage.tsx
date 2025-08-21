import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { listWorkflows, createWorkflow, Workflow } from '../lib/api'

const emptyGraph = { nodes: [{ id: 'start', type: 'start', data: {} }], edges: [] }

export default function WorkflowsPage() {
  const [items, setItems] = useState<Workflow[]>([])
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  async function load() {
    setLoading(true)
    const data = await listWorkflows()
    setItems(data)
    setLoading(false)
  }

  useEffect(() => { load() }, [])

  async function handleNew() {
    const wf = await createWorkflow({ name: 'New Workflow', description: null, definition: emptyGraph, trigger: {}, graph: emptyGraph, is_active: true })
    navigate(`/workflows/${wf.id}`)
  }

  return (
    <div>
      <div className="toolbar">
        <button className="primary" onClick={handleNew}>New Workflow</button>
        <button onClick={load}>Refresh</button>
      </div>
      {loading ? <div>Loading...</div> : (
        <div className="panel">
          <table>
            <thead>
              <tr><th>Name</th><th>Version</th><th>Status</th><th>Actions</th></tr>
            </thead>
            <tbody>
              {items.map(wf => (
                <tr key={wf.id}>
                  <td>{wf.name}</td>
                  <td>{wf.version}</td>
                  <td><span className="tag">{wf.is_active ? 'Active' : 'Inactive'}</span></td>
                  <td>
                    <Link to={`/workflows/${wf.id}`}>Edit</Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}


