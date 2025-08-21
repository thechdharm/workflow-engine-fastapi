import axios from 'axios'

const API_URL = (import.meta as any).env?.VITE_API_URL || 'http://localhost:8000'

export type Workflow = {
  id: string
  name: string
  description?: string | null
  version: number
  is_active: boolean
  trigger: Record<string, any>
  graph: { nodes: any[]; edges: any[] }
}

export type WorkflowCreate = {
  name: string
  description?: string | null
  definition: { nodes: any[]; edges: any[] }
  trigger: Record<string, any>
  graph?: { nodes: any[]; edges: any[] }
  is_active: boolean
}

export async function listWorkflows(): Promise<Workflow[]> {
  const { data } = await axios.get(`${API_URL}/workflows`)
  return data
}

export async function getWorkflow(id: string): Promise<Workflow> {
  const { data } = await axios.get(`${API_URL}/workflows/${id}`)
  return data
}

export async function createWorkflow(payload: WorkflowCreate): Promise<Workflow> {
  const { data } = await axios.post(`${API_URL}/workflows`, payload)
  return data
}

export async function updateWorkflow(id: string, payload: WorkflowCreate): Promise<Workflow> {
  const { data } = await axios.put(`${API_URL}/workflows/${id}`, payload)
  return data
}

export type Execution = {
  id: string
  workflow_id: string
  status: string
  context?: Record<string, any>
}

export async function listExecutions(workflowId?: string): Promise<Execution[]> {
  const { data } = await axios.get(`${API_URL}/executions`, { params: { workflow_id: workflowId } })
  return data
}

export async function startExecution(workflow_id: string, payload: Record<string, any>) {
  const { data } = await axios.post(`${API_URL}/executions`, { workflow_id, payload })
  return data as Execution
}


