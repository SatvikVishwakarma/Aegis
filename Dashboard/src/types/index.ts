export interface Node {
  id: number
  hostname: string
  ip_address: string
  group?: string | null
  status: string
  last_seen: string
}

export interface Event {
  id: number
  node_id: number
  timestamp: string
  event_type: string
  severity: string
  details: Record<string, any>
}

export interface Policy {
  id: number
  name: string
  type: string
  rules_json: Record<string, any>
  assigned_nodes: Node[]
}

export interface DashboardStats {
  totalNodes: number
  onlineNodes: number
  totalEvents: number
  criticalEvents: number
}
