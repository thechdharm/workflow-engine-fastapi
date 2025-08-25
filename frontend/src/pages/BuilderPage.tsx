import { useEffect, useState, useCallback } from 'react'
import { useParams } from 'react-router-dom'
import ReactFlow, { 
  Background, 
  Controls, 
  MiniMap, 
  Connection, 
  Edge, 
  Node,
  ReactFlowProvider,
  useReactFlow,
  NodeTypes,
  NodeChange,
  EdgeChange,
  applyNodeChanges,
  applyEdgeChanges,
  Handle,
  Position
} from 'reactflow'
import 'reactflow/dist/style.css'
import { getWorkflow, updateWorkflow, Workflow } from '../lib/api'

// Custom node types
const nodeTypes: NodeTypes = {
  start: ({ data }: any) => (
    <div className="node start-node">
      <div className="node-header">🚀 Start</div>
      <div className="node-content">{data.label}</div>
      <Handle type="source" position={Position.Right} className="handle" />
    </div>
  ),
  send_notification: ({ data }: any) => (
    <div className="node notification-node">
      <Handle type="target" position={Position.Left} className="handle" />
      <div className="node-header">📢 Notification</div>
      <div className="node-content">{data.label}</div>
      <Handle type="source" position={Position.Right} className="handle" />
    </div>
  ),
  delay: ({ data }: any) => (
    <div className="node delay-node">
      <Handle type="target" position={Position.Left} className="handle" />
      <div className="node-header">⏱️ Delay</div>
      <div className="node-content">{data.label}</div>
      <Handle type="source" position={Position.Right} className="handle" />
    </div>
  ),
  http_call: ({ data }: any) => (
    <div className="node http-node">
      <Handle type="target" position={Position.Left} className="handle" />
      <div className="node-header">🌐 HTTP Call</div>
      <div className="node-content">{data.label}</div>
      <Handle type="source" position={Position.Right} className="handle" />
    </div>
  ),
  branch: ({ data }: any) => (
    <div className="node branch-node">
      <Handle type="target" position={Position.Left} className="handle" />
      <div className="node-header">🔀 Branch</div>
      <div className="node-content">{data.label}</div>
      <Handle type="source" position={Position.Right} className="handle" />
    </div>
  ),
}

// Node palette component
function NodePalette() {
  const onDragStart = (event: React.DragEvent, nodeType: string) => {
    event.dataTransfer.setData('application/reactflow', nodeType)
    event.dataTransfer.effectAllowed = 'move'
  }

  const nodeTypes = [
    { type: 'start', label: 'Start', icon: '🚀' },
    { type: 'send_notification', label: 'Notification', icon: '📢' },
    { type: 'delay', label: 'Delay', icon: '⏱️' },
    { type: 'http_call', label: 'HTTP Call', icon: '🌐' },
    { type: 'branch', label: 'Branch', icon: '🔀' },
  ]

  return (
    <div className="node-palette">
      <h3>Node Types</h3>
      <div className="node-list">
        {nodeTypes.map((node) => (
          <div
            key={node.type}
            className="palette-node"
            draggable
            onDragStart={(e) => onDragStart(e, node.type)}
          >
            <span className="node-icon">{node.icon}</span>
            <span className="node-label">{node.label}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

// Main builder component
function BuilderContent() {
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
      try {
        const data = await getWorkflow(id)
        setWf(data)
        setName(data.name)
        setTrigger(JSON.stringify(data.trigger || {}, null, 2))
        
        const ns: Node[] = (data.graph?.nodes || []).map((n: any) => ({ 
          id: n.id, 
          type: n.type || 'default',
          data: { label: n.type || 'unknown' }, 
          position: n.position || { x: 0, y: 0 } 
        }))
        const es: Edge[] = (data.graph?.edges || []).map((e: any) => ({ 
          id: e.id, 
          source: e.source, 
          target: e.target 
        }))
        setNodes(ns)
        setEdges(es)
      } catch (error) {
        console.error('Error loading workflow:', error)
      }
    })()
  }, [id])

  const onConnect = useCallback((conn: Connection) => {
    if (!conn.source || !conn.target) return
    const newEdge: Edge = { 
      id: `${conn.source}-${conn.target}-${Date.now()}`, 
      source: conn.source, 
      target: conn.target 
    }
    setEdges(es => [...es, newEdge])
    setDirty(true)
  }, [])

  const onNodesChange = useCallback((changes: NodeChange[]) => {
    setNodes(ns => applyNodeChanges(changes, ns))
    setDirty(true)
  }, [])

  const onEdgesChange = useCallback((changes: EdgeChange[]) => {
    setEdges(es => applyEdgeChanges(changes, es))
    setDirty(true)
  }, [])

  const onDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault()
    event.dataTransfer.dropEffect = 'move'
  }, [])

  const onDrop = useCallback((event: React.DragEvent) => {
    event.preventDefault()

    const reactFlowBounds = document.querySelector('.react-flow')?.getBoundingClientRect()
    if (!reactFlowBounds) return

    const type = event.dataTransfer.getData('application/reactflow')
    if (!type) return

    const position = {
      x: event.clientX - reactFlowBounds.left,
      y: event.clientY - reactFlowBounds.top,
    }

    const newNode: Node = {
      id: `${type}-${Math.random().toString(36).slice(2, 7)}`,
      type,
      position,
      data: { label: type },
    }

    setNodes(ns => [...ns, newNode])
    setDirty(true)
  }, [])

  async function save() {
    if (!wf) return
    try {
      const graph = {
        nodes: nodes.map(n => ({ 
          id: n.id, 
          type: String(n.data?.label || 'unknown'), 
          data: {}, 
          position: n.position 
        })),
        edges: edges.map(e => ({ 
          id: e.id, 
          source: e.source, 
          target: e.target 
        }))
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
    } catch (error) {
      console.error('Error saving workflow:', error)
    }
  }

  if (!wf) return <div>Loading...</div>

  return (
    <div className="grid">
      <div className="panel">
        <div className="toolbar">
          <input 
            value={name} 
            onChange={e => { setName(e.target.value); setDirty(true) }} 
            placeholder="Workflow name" 
            className="workflow-name"
          />
          <button className="primary" disabled={!dirty} onClick={save}>
            {dirty ? 'Save Changes' : 'Saved'}
          </button>
          {dirty ? <span className="tag unsaved">unsaved</span> : <span className="tag saved">saved</span>}
        </div>
        
        <div className="flow">
          <ReactFlow 
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            onDragOver={onDragOver}
            onDrop={onDrop}
            nodeTypes={nodeTypes}
            fitView
            deleteKeyCode="Delete"
            multiSelectionKeyCode="Shift"

          >
            <MiniMap />
            <Controls />
            <Background />
          </ReactFlow>
        </div>
      </div>
      
      <div className="panel">
        <NodePalette />
        
        <div className="trigger-section">
          <h3>Trigger (JSONLogic)</h3>
          <textarea 
            rows={14} 
            value={trigger} 
            onChange={e => { setTrigger(e.target.value); setDirty(true) }}
            placeholder="Enter JSONLogic condition..."
            className="trigger-input"
          />
          <p className="example-text">
            Example: {`{ "and": [ {"==": [{"var":"lead.source"}, "LinkedIn"]}, {">": [{"var":"lead.score"}, 75]} ] }`}
          </p>
        </div>
        
        <div className="tips-section">
          <h3>Tips</h3>
          <ul>
            <li>Drag nodes from the palette onto the canvas</li>
            <li>Connect nodes by dragging from source handle (right) to target handle (left)</li>
            <li>Ensure a node with id "start" exists and connects to your first step</li>
            <li>Delete nodes/edges with Delete key</li>
            <li>Multi-select with Shift + click</li>
          </ul>
        </div>
      </div>
    </div>
  )
}

// Wrapper component with ReactFlowProvider
export default function BuilderPage() {
  return (
    <ReactFlowProvider>
      <BuilderContent />
    </ReactFlowProvider>
  )
}


