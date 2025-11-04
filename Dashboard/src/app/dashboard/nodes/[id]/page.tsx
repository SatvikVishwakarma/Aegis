'use client'

import { useParams, useRouter } from 'next/navigation'
import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { 
  ArrowLeft, 
  Server, 
  Activity, 
  Network,
  AlertCircle,
  Info,
  AlertTriangle,
  XCircle,
  Clock,
  Tag,
  Wifi
} from 'lucide-react'
import { fetchNodes, fetchEvents } from '@/lib/api'
import { Node, Event } from '@/types'
import { getRelativeTime } from '@/lib/utils'
import { SkeletonTable } from '@/components/ui/Skeleton'
import { useState, useMemo } from 'react'

export default function NodeDetailPage() {
  const params = useParams()
  const router = useRouter()
  const nodeId = parseInt(params.id as string)
  const [activeTab, setActiveTab] = useState<'events' | 'network'>('events')

  const { data: nodes } = useQuery<Node[]>({
    queryKey: ['nodes'],
    queryFn: fetchNodes,
  })

  const { data: events, isLoading: eventsLoading } = useQuery<Event[]>({
    queryKey: ['node-events', nodeId],
    queryFn: () => fetchEvents({ node_id: nodeId, limit: 1000 }),
    refetchInterval: 5000,
  })

  const node = useMemo(() => {
    return nodes?.find(n => n.id === nodeId)
  }, [nodes, nodeId])

  const eventLogs = useMemo(() => {
    if (!events) return []
    return events.filter(e => {
      const type = e.event_type.toLowerCase()
      return !type.includes('network') && !type.includes('connection')
    })
  }, [events])

  const networkLogs = useMemo(() => {
    if (!events) return []
    return events.filter(e => {
      const type = e.event_type.toLowerCase()
      return type.includes('network') || type.includes('connection')
    })
  }, [events])

  const getSeverityIcon = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'critical':
        return <XCircle className="w-5 h-5 text-red-500" />
      case 'high':
        return <AlertCircle className="w-5 h-5 text-orange-500" />
      case 'medium':
        return <AlertTriangle className="w-5 h-5 text-yellow-500" />
      case 'low':
        return <Info className="w-5 h-5 text-blue-500" />
      default:
        return <Info className="w-5 h-5 text-slate-500" />
    }
  }

  const getSeverityColor = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'critical':
        return 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300'
      case 'high':
        return 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-300'
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300'
      case 'low':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300'
      default:
        return 'bg-slate-100 text-slate-800 dark:bg-slate-700 dark:text-slate-300'
    }
  }

  if (!node) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <Server className="w-16 h-16 text-slate-400 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-slate-900 dark:text-white">Node not found</h2>
          <p className="text-slate-600 dark:text-slate-400 mt-2">The requested node does not exist</p>
          <button
            onClick={() => router.push('/dashboard/nodes')}
            className="mt-4 px-4 py-2 bg-primary text-white rounded-lg hover:bg-blue-600 transition-colors"
          >
            Back to Nodes
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="flex items-start gap-4">
          <button
            onClick={() => router.push('/dashboard/nodes')}
            className="p-2 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-colors"
          >
            <ArrowLeft className="w-5 h-5 text-slate-600 dark:text-slate-400" />
          </button>
          <div>
            <div className="flex items-center gap-3">
              <Server className="w-8 h-8 text-primary" />
              <h1 className="text-3xl font-bold text-slate-900 dark:text-white">
                {node.hostname}
              </h1>
            </div>
            <p className="text-slate-600 dark:text-slate-400 mt-1">
              Node details and activity logs
            </p>
          </div>
        </div>
      </div>

      {/* Node Info Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white dark:bg-slate-800 rounded-lg p-4 border border-slate-200 dark:border-slate-700">
          <div className="flex items-center gap-2 text-slate-600 dark:text-slate-400 text-sm mb-1">
            <Server className="w-4 h-4" />
            Node ID
          </div>
          <div className="text-2xl font-bold text-slate-900 dark:text-white">#{node.id}</div>
        </div>

        <div className="bg-white dark:bg-slate-800 rounded-lg p-4 border border-slate-200 dark:border-slate-700">
          <div className="flex items-center gap-2 text-slate-600 dark:text-slate-400 text-sm mb-1">
            <Network className="w-4 h-4" />
            IP Address
          </div>
          <div className="text-xl font-mono font-semibold text-slate-900 dark:text-white">
            {node.ip_address}
          </div>
        </div>

        <div className="bg-white dark:bg-slate-800 rounded-lg p-4 border border-slate-200 dark:border-slate-700">
          <div className="flex items-center gap-2 text-slate-600 dark:text-slate-400 text-sm mb-1">
            <Activity className="w-4 h-4" />
            Status
          </div>
          <div className="flex items-center gap-2">
            <div className={`w-3 h-3 rounded-full ${node.status === 'online' ? 'bg-emerald-500' : 'bg-slate-400'}`} />
            <span className="text-xl font-semibold text-slate-900 dark:text-white capitalize">
              {node.status}
            </span>
          </div>
        </div>

        <div className="bg-white dark:bg-slate-800 rounded-lg p-4 border border-slate-200 dark:border-slate-700">
          <div className="flex items-center gap-2 text-slate-600 dark:text-slate-400 text-sm mb-1">
            <Clock className="w-4 h-4" />
            Last Seen
          </div>
          <div className="text-xl font-semibold text-slate-900 dark:text-white">
            {getRelativeTime(node.last_seen)}
          </div>
        </div>
      </div>

      {node.group && (
        <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4 border border-blue-200 dark:border-blue-800">
          <div className="flex items-center gap-2">
            <Tag className="w-5 h-5 text-blue-600 dark:text-blue-400" />
            <span className="text-sm font-medium text-blue-600 dark:text-blue-400">Group:</span>
            <span className="text-sm font-semibold text-blue-700 dark:text-blue-300">{node.group}</span>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700">
        <div className="flex border-b border-slate-200 dark:border-slate-700">
          <button
            onClick={() => setActiveTab('events')}
            className={`flex items-center gap-2 px-6 py-4 font-medium transition-colors relative ${
              activeTab === 'events'
                ? 'text-primary border-b-2 border-primary'
                : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
            }`}
          >
            <Activity className="w-5 h-5" />
            Event Logs
            <span className="ml-2 px-2 py-0.5 text-xs rounded-full bg-slate-100 dark:bg-slate-700">
              {eventLogs.length}
            </span>
          </button>
          <button
            onClick={() => setActiveTab('network')}
            className={`flex items-center gap-2 px-6 py-4 font-medium transition-colors relative ${
              activeTab === 'network'
                ? 'text-primary border-b-2 border-primary'
                : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
            }`}
          >
            <Wifi className="w-5 h-5" />
            Network Logs
            <span className="ml-2 px-2 py-0.5 text-xs rounded-full bg-slate-100 dark:bg-slate-700">
              {networkLogs.length}
            </span>
          </button>
        </div>

        {/* Logs Content */}
        <div className="p-6">
          {eventsLoading ? (
            <SkeletonTable rows={5} />
          ) : (
            <div className="space-y-3">
              {activeTab === 'events' && (
                <>
                  {eventLogs.length === 0 ? (
                    <div className="text-center py-12 text-slate-500 dark:text-slate-400">
                      No event logs found for this node
                    </div>
                  ) : (
                    eventLogs.map((event) => (
                      <motion.div
                        key={event.id}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="bg-slate-50 dark:bg-slate-700/50 rounded-lg p-4 border border-slate-200 dark:border-slate-600"
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex items-start gap-3 flex-1">
                            {getSeverityIcon(event.severity)}
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center gap-2 mb-1">
                                <h3 className="font-semibold text-slate-900 dark:text-white">
                                  {event.event_type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                                </h3>
                                <span className={`px-2 py-0.5 text-xs font-medium rounded capitalize ${getSeverityColor(event.severity)}`}>
                                  {event.severity}
                                </span>
                              </div>
                              <p className="text-sm text-slate-600 dark:text-slate-400 mb-2">
                                {new Date(event.timestamp).toLocaleString()}
                              </p>
                              {event.details && Object.keys(event.details).length > 0 && (
                                <div className="bg-white dark:bg-slate-800 rounded p-3 mt-2">
                                  <pre className="text-xs text-slate-700 dark:text-slate-300 overflow-x-auto">
                                    {JSON.stringify(event.details, null, 2)}
                                  </pre>
                                </div>
                              )}
                            </div>
                          </div>
                        </div>
                      </motion.div>
                    ))
                  )}
                </>
              )}

              {activeTab === 'network' && (
                <>
                  {networkLogs.length === 0 ? (
                    <div className="text-center py-12 text-slate-500 dark:text-slate-400">
                      No network logs found for this node
                    </div>
                  ) : (
                    networkLogs.map((event) => (
                      <motion.div
                        key={event.id}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="bg-slate-50 dark:bg-slate-700/50 rounded-lg p-4 border border-slate-200 dark:border-slate-600"
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex items-start gap-3 flex-1">
                            <Wifi className="w-5 h-5 text-primary mt-0.5" />
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center gap-2 mb-1">
                                <h3 className="font-semibold text-slate-900 dark:text-white">
                                  {event.event_type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                                </h3>
                                <span className={`px-2 py-0.5 text-xs font-medium rounded capitalize ${getSeverityColor(event.severity)}`}>
                                  {event.severity}
                                </span>
                              </div>
                              <p className="text-sm text-slate-600 dark:text-slate-400 mb-2">
                                {new Date(event.timestamp).toLocaleString()}
                              </p>
                              {event.details && Object.keys(event.details).length > 0 && (
                                <div className="bg-white dark:bg-slate-800 rounded p-3 mt-2">
                                  <pre className="text-xs text-slate-700 dark:text-slate-300 overflow-x-auto">
                                    {JSON.stringify(event.details, null, 2)}
                                  </pre>
                                </div>
                              )}
                            </div>
                          </div>
                        </div>
                      </motion.div>
                    ))
                  )}
                </>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
