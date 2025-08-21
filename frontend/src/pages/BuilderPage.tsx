import { useEffect, useMemo, useState } from 'react'
import { useParams } from 'react-router-dom'
import ReactFlow, { Background, Controls, MiniMap, addEdge, Connection, Edge, Node } from 'reactflow'
import 'reactflow/dist/style.css'
import { getWorkflow, updateWorkflow, Workflow } from '../lib/api'

export default function BuilderPage() {
  const { id } = useParams<{ id: string }>()
  const [wf, setWf] = useState<Workflow | null>(null)
  const [nodes, setNodes] = useState<Node[]>([])
  const [edges, setEdges] = useState<Edge[]>([])
  const [name, setName] = useState('')
  const [trigger, setTrigger] = useState('{}')
  const [dirty, setDirty] = useState(false)

  useEffect(() => {
    (async () => {
      if (!id) return
      const data = await getWorkflow(id)
      setWf(data)
      setName(data.name)
      setTrigger(JSON.stringify(data.trigger || {}, null, 2))
      const ns: Node[] = (data.graph?.nodes || []).map((n: any) => ({ id: n.id, data: { label: n.type }, position: n.position || { x: 0, y: 0 } }))
      const es: Edge[] = (data.graph?.edges || []).map((e: any) => ({ id: e.id, source: e.source, target: e.target }))
      setNodes(ns)
      setEdges(es)
    })()
  }, [id])

  const rfNodes = useMemo(() => nodes, [nodes])
  const rfEdges = useMemo(() => edges, [edges])

  function onConnect(conn: Connection) {
    if (!conn.source || !conn.target) return
    const newEdge: Edge = { id: `${conn.source}-${conn.target}-${Date.now()}`, source: conn.source, target: conn.target }
    setEdges(es => [...es, newEdge])
    setDirty(true)
  }

  function addNode(type: string) {
    const id = `${type}-${Math.random().toString(36).slice(2, 7)}`
    const node: Node = { id, data: { label: type }, position: { x: 100 + Math.random() * 400, y: 60 + Math.random() * 300 } }
    setNodes(ns => [...ns, node])
    setDirty(true)
  }

  async function save() {
    if (!wf) return
    const graph = {
      nodes: nodes.map(n => ({ id: n.id, type: String(n.data?.label || 'unknown'), data: {}, position: n.position })),
      edges: edges.map(e => ({ id: e.id, source: e.source, target: e.target }))
    }
    const payload = {
      name,
      description: wf.description || null,
      definition: graph,
      trigger: JSON.parse(trigger || '{}'),
      graph,
      is_active: wf.is_active
    }
    const res = await updateWorkflow(wf.id, payload)
    setWf(res)
    setDirty(false)
  }

  if (!wf) return <div>Loading...</div>

  return (
    <div className="grid">
      <div className="panel">
        <div className="toolbar">
          <input value={name} onChange={e => { setName(e.target.value); setDirty(true) }} placeholder="Workflow name" />
          <button className="primary" disabled={!dirty} onClick={save}>Save</button>
          {dirty ? <span className="tag">unsaved</span> : <span className="tag">saved</span>}
        </div>
        <div className="toolbar">
          <button onClick={() => addNode('start')}>Add Start</button>
          <button onClick={() => addNode('send_notification')}>Add Notification</button>
          <button onClick={() => addNode('delay')}>Add Delay</button>
          <button onClick={() => addNode('http_call')}>Add HTTP Call</button>
          <button onClick={() => addNode('branch')}>Add Branch</button>
        </div>
        <div className="flow">
          <ReactFlow nodes={rfNodes} edges={rfEdges} onConnect={onConnect} fitView>
            <MiniMap />
            <Controls />
            <Background />
          </ReactFlow>
        </div>
      </div>
      <div className="panel">
        <h3>Trigger (JSONLogic)</h3>
        <textarea rows={14} value={trigger} onChange={e => { setTrigger(e.target.value); setDirty(true) }} />
        <p style={{ fontSize: 12, opacity: 0.8 }}>Example: {`{ "and": [ {"==": [{"var":"lead.source"}, "LinkedIn"]}, {">": [{"var":"lead.score"}, 75]} ] }`}</p>
        <h3 style={{ marginTop: 16 }}>Tips</h3>
        <ul>
          <li>Ensure a node with id "start" exists and connects to your first step.</li>
          <li>Node types supported: start, send_notification, delay, http_call, branch.</li>
        </ul>
      </div>
    </div>
  )
}


