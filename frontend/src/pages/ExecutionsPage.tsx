import { useEffect, useState } from 'react'
import { listWorkflows, listExecutions, startExecution, Workflow, Execution } from '../lib/api'

export default function ExecutionsPage() {
  const [workflows, setWorkflows] = useState<Workflow[]>([])
  const [selected, setSelected] = useState<string>('')
  const [payload, setPayload] = useState<string>('{}')
  const [items, setItems] = useState<Execution[]>([])

  async function refresh() {
    const ex = await listExecutions(selected || undefined)
    setItems(ex)
  }

  useEffect(() => { (async () => { const w = await listWorkflows(); setWorkflows(w) })() }, [])
  useEffect(() => { refresh() }, [selected])

  async function run() {
    if (!selected) return
    await startExecution(selected, JSON.parse(payload || '{}'))
    await refresh()
  }

  return (
    <div>
      <div className="toolbar">
        <select value={selected} onChange={e => setSelected(e.target.value)}>
          <option value="">All Workflows</option>
          {workflows.map(w => <option key={w.id} value={w.id}>{w.name}</option>)}
        </select>
        <input style={{ width: 360 }} value={payload} onChange={e => setPayload(e.target.value)} placeholder='{"lead": {"title":"CEO"}}' />
        <button onClick={run} className="primary" disabled={!selected}>Start Execution</button>
        <button onClick={refresh}>Refresh</button>
      </div>
      <div className="panel">
        <table>
          <thead>
            <tr><th>ID</th><th>Workflow</th><th>Status</th></tr>
          </thead>
          <tbody>
            {items.map(ex => (
              <tr key={ex.id}>
                <td>{ex.id}</td>
                <td>{ex.workflow_id}</td>
                <td><span className="tag">{ex.status}</span></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}


