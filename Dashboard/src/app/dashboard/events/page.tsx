'use client'

import { useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import { Layers, Server, ChevronRight, Users, Activity } from 'lucide-react'
import { fetchNodes } from '@/lib/api'
import { Node } from '@/types'
import { getRelativeTime } from '@/lib/utils'
import { SkeletonTable } from '@/components/ui/Skeleton'

export default function EventsPage() {
  const router = useRouter()

  const { data: nodes, isLoading } = useQuery<Node[]>({
    queryKey: ['nodes'],
    queryFn: fetchNodes,
    refetchInterval: 5000,
  })

  // Group nodes by their group field
  const groupedNodes = useMemo(() => {
    if (!nodes) return new Map<string, Node[]>()
    
    const groups = new Map<string, Node[]>()
    
    // Create "Ungrouped" category for nodes without a group
    const ungrouped: Node[] = []
    
    nodes.forEach(node => {
      if (node.group) {
        if (!groups.has(node.group)) {
          groups.set(node.group, [])
        }
        groups.get(node.group)!.push(node)
      } else {
        ungrouped.push(node)
      }
    })
    
    // Add ungrouped nodes if any exist
    if (ungrouped.length > 0) {
      groups.set('Ungrouped', ungrouped)
    }
    
    // Sort groups alphabetically, but keep "Ungrouped" at the end
    return new Map([...groups.entries()].sort((a, b) => {
      if (a[0] === 'Ungrouped') return 1
      if (b[0] === 'Ungrouped') return -1
      return a[0].localeCompare(b[0])
    }))
  }, [nodes])

  const totalNodes = nodes?.length || 0
  const totalGroups = groupedNodes.size

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-slate-900 dark:text-white">
          Event Viewer
        </h1>
        <p className="text-slate-600 dark:text-slate-400 mt-1">
          Browse nodes by group to view their event and network logs
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-white dark:bg-slate-800 rounded-lg p-6 border border-slate-200 dark:border-slate-700">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
              <Layers className="w-6 h-6 text-blue-600 dark:text-blue-400" />
            </div>
            <div>
              <p className="text-sm text-slate-600 dark:text-slate-400">Total Groups</p>
              <p className="text-2xl font-bold text-slate-900 dark:text-white">{totalGroups}</p>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-slate-800 rounded-lg p-6 border border-slate-200 dark:border-slate-700">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-emerald-100 dark:bg-emerald-900/30 rounded-lg">
              <Server className="w-6 h-6 text-emerald-600 dark:text-emerald-400" />
            </div>
            <div>
              <p className="text-sm text-slate-600 dark:text-slate-400">Total Nodes</p>
              <p className="text-2xl font-bold text-slate-900 dark:text-white">{totalNodes}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Groups List */}
      {isLoading ? (
        <SkeletonTable rows={5} />
      ) : (
        <div className="space-y-4">
          {Array.from(groupedNodes.entries()).map(([groupName, groupNodes], idx) => (
            <motion.div
              key={groupName}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.05 }}
              className="bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700 overflow-hidden"
            >
              {/* Group Header */}
              <div className="bg-slate-50 dark:bg-slate-700/50 px-6 py-4 border-b border-slate-200 dark:border-slate-700">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
                      <Users className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold text-slate-900 dark:text-white">
                        {groupName}
                      </h3>
                      <p className="text-sm text-slate-600 dark:text-slate-400">
                        {groupNodes.length} {groupNodes.length === 1 ? 'node' : 'nodes'}
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Nodes List */}
              <div className="divide-y divide-slate-200 dark:divide-slate-700">
                {groupNodes.map((node, nodeIdx) => (
                  <motion.button
                    key={node.id}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: idx * 0.05 + nodeIdx * 0.02 }}
                    onClick={() => router.push(`/dashboard/nodes/${node.id}`)}
                    className="w-full px-6 py-4 flex items-center justify-between hover:bg-slate-50 dark:hover:bg-slate-700/30 transition-colors group"
                  >
                    <div className="flex items-center gap-4 flex-1">
                      <div className="p-2 bg-slate-100 dark:bg-slate-700 rounded-lg group-hover:bg-blue-100 dark:group-hover:bg-blue-900/30 transition-colors">
                        <Server className="w-5 h-5 text-slate-600 dark:text-slate-400 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors" />
                      </div>
                      
                      <div className="flex-1 text-left">
                        <div className="flex items-center gap-3">
                          <h4 className="font-semibold text-slate-900 dark:text-white group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
                            {node.hostname}
                          </h4>
                          <div className="flex items-center gap-2">
                            <div className={`w-2 h-2 rounded-full ${
                              node.status === 'online' 
                                ? 'bg-emerald-500' 
                                : 'bg-slate-400'
                            }`} />
                            <span className="text-sm capitalize text-slate-600 dark:text-slate-400">
                              {node.status}
                            </span>
                          </div>
                        </div>
                        <div className="flex items-center gap-4 mt-1">
                          <code className="text-sm text-slate-500 dark:text-slate-500">
                            {node.ip_address}
                          </code>
                          <span className="text-sm text-slate-500 dark:text-slate-500">
                            Last seen: {getRelativeTime(node.last_seen)}
                          </span>
                        </div>
                      </div>

                      <div className="flex items-center gap-2 px-3 py-1.5 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                        <Activity className="w-4 h-4 text-blue-600 dark:text-blue-400" />
                        <span className="text-sm font-medium text-blue-600 dark:text-blue-400">
                          View Logs
                        </span>
                      </div>
                    </div>

                    <ChevronRight className="w-5 h-5 text-slate-400 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors" />
                  </motion.button>
                ))}
              </div>
            </motion.div>
          ))}

          {groupedNodes.size === 0 && (
            <div className="bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700 p-12 text-center">
              <Server className="w-16 h-16 text-slate-300 dark:text-slate-600 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-2">
                No Nodes Available
              </h3>
              <p className="text-slate-600 dark:text-slate-400">
                Register nodes to start viewing their event and network logs
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
