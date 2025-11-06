import axios from 'axios'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
const API_URL = `${API_BASE_URL}/api/v1`
const DASHBOARD_API_KEY = process.env.NEXT_PUBLIC_DASHBOARD_API_KEY || ''

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
    ...(DASHBOARD_API_KEY && { 'X-Dashboard-Key': DASHBOARD_API_KEY }),
  },
})

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('aegis_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('aegis_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// Auth
export const login = async (username: string, password: string) => {
  const formData = new FormData()
  formData.append('username', username)
  formData.append('password', password)
  
  const response = await axios.post(`${API_URL}/auth/login`, formData)
  return response.data
}

// Nodes
export const fetchNodes = async () => {
  const response = await api.get('/nodes')
  return response.data
}

export const registerNode = async (data: { hostname: string; ip_address: string; group?: string | null }) => {
  const response = await api.post('/nodes/register', data)
  return response.data
}

export const updateNode = async (nodeId: number, data: { hostname?: string; ip_address?: string; group?: string | null }) => {
  const response = await api.put(`/nodes/${nodeId}`, data)
  return response.data
}

export const deleteNode = async (nodeId: number, password: string) => {
  const response = await api.delete(`/nodes/${nodeId}`, {
    data: { password }
  })
  return response.data
}

// Events/Logs
export const fetchEvents = async (params?: {
  node_id?: number
  severity?: string
  event_type?: string
  limit?: number
}) => {
  const response = await api.get('/logs', { params })
  return response.data
}

// Policies
export const fetchPolicies = async () => {
  const response = await api.get('/policies')
  return response.data
}

export const createPolicy = async (data: {
  name: string
  type: string
  rules_json: Record<string, any>
}) => {
  const response = await api.post('/policies', data)
  return response.data
}

export const deletePolicy = async (policyId: number, password: string) => {
  const response = await api.delete(`/policies/${policyId}`, {
    data: { password }
  })
  return response.data
}

export const assignPolicy = async (nodeId: number, policyId: number) => {
  const response = await api.post('/policies/assign', { node_id: nodeId, policy_id: policyId })
  return response.data
}
