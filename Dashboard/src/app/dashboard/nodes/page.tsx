'use client'

import { useState, useMemo } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useRouter } from 'next/navigation'
import { motion, AnimatePresence } from 'framer-motion'
import { Server, Search, Plus, Trash2, Edit2, Circle, Tag, Filter, ExternalLink } from 'lucide-react'
import Fuse from 'fuse.js'
import { fetchNodes, registerNode, deleteNode, updateNode } from '@/lib/api'
import { Node } from '@/types'
import { getRelativeTime, getStatusColor } from '@/lib/utils'
import { SkeletonTable } from '@/components/ui/Skeleton'
import { Modal } from '@/components/ui/Modal'
import toast from 'react-hot-toast'

export default function NodesPage() {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedGroup, setSelectedGroup] = useState<string>('all')
  const [isAddModalOpen, setIsAddModalOpen] = useState(false)
  const [editingNode, setEditingNode] = useState<Node | null>(null)
  const queryClient = useQueryClient()
  const router = useRouter()

  const { data: nodes, isLoading } = useQuery<Node[]>({
    queryKey: ['nodes'],
    queryFn: fetchNodes,
    refetchInterval: 5000,
  })

  // Get unique groups from nodes
  const groups = useMemo(() => {
    if (!nodes) return []
    const uniqueGroups = new Set(
      nodes
        .map(n => n.group)
        .filter((g): g is string => g !== null && g !== undefined && g !== '')
    )
    return Array.from(uniqueGroups).sort()
  }, [nodes])

  // Fuzzy search with Fuse.js
  const fuse = useMemo(() => {
    if (!nodes) return null
    return new Fuse(nodes, {
      keys: ['hostname', 'ip_address', 'status', 'group'],
      threshold: 0.3,
    })
  }, [nodes])

  const filteredNodes = useMemo(() => {
    if (!nodes) return []
    
    // Filter by group first
    let filtered = nodes
    if (selectedGroup !== 'all') {
      filtered = nodes.filter(node => node.group === selectedGroup)
    }
    
    // Then apply search
    if (!searchQuery) return filtered
    if (!fuse) return filtered
    
    const searchResults = fuse.search(searchQuery).map((result) => result.item)
    return filtered.filter(node => searchResults.some(r => r.id === node.id))
  }, [nodes, searchQuery, selectedGroup, fuse])

  const deleteMutation = useMutation({
    mutationFn: ({ id, password }: { id: number; password: string }) => 
      deleteNode(id, password),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['nodes'] })
      toast.success('Node deleted successfully')
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || 'Failed to delete node'
      toast.error(message)
    },
  })

  const handleDelete = (id: number) => {
    const password = prompt('Enter admin password to confirm deletion:')
    if (!password) {
      toast.error('Deletion cancelled')
      return
    }
    deleteMutation.mutate({ id, password })
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 dark:text-white">
            Nodes
          </h1>
          <p className="text-slate-600 dark:text-slate-400 mt-1">
            Manage and monitor your security nodes
          </p>
        </div>
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={() => setIsAddModalOpen(true)}
          className="flex items-center gap-2 px-4 py-2 bg-primary text-white rounded-lg hover:bg-blue-600 transition-colors shadow-lg"
        >
          <Plus className="w-5 h-5" />
          Add Node
        </motion.button>
      </div>

      {/* Search and Filter Bar */}
      <div className="flex gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search nodes by hostname, IP, group, or status..."
            className="w-full pl-12 pr-4 py-3 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent transition-all outline-none text-slate-900 dark:text-white"
          />
        </div>
        
        {/* Group Filter */}
        <div className="relative min-w-[200px]">
          <Filter className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
          <select
            value={selectedGroup}
            onChange={(e) => setSelectedGroup(e.target.value)}
            className="w-full pl-12 pr-4 py-3 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent transition-all outline-none text-slate-900 dark:text-white appearance-none cursor-pointer"
          >
            <option value="all">All Groups</option>
            {groups.map(group => (
              <option key={group} value={group}>{group}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Nodes Table */}
      {isLoading ? (
        <SkeletonTable rows={8} />
      ) : (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="bg-white dark:bg-slate-800 rounded-lg shadow-sm border border-slate-200 dark:border-slate-700 overflow-hidden"
        >
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-slate-50 dark:bg-slate-700/50 border-b border-slate-200 dark:border-slate-700">
                <tr>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-slate-600 dark:text-slate-400 uppercase tracking-wider">
                    ID
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-slate-600 dark:text-slate-400 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-slate-600 dark:text-slate-400 uppercase tracking-wider">
                    Hostname
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-slate-600 dark:text-slate-400 uppercase tracking-wider">
                    IP Address
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-slate-600 dark:text-slate-400 uppercase tracking-wider">
                    Group
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-slate-600 dark:text-slate-400 uppercase tracking-wider">
                    Last Seen
                  </th>
                  <th className="px-6 py-4 text-right text-xs font-semibold text-slate-600 dark:text-slate-400 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200 dark:divide-slate-700">
                <AnimatePresence>
                  {filteredNodes.map((node, idx) => (
                    <motion.tr
                      key={node.id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: 20 }}
                      transition={{ delay: idx * 0.03 }}
                      className="hover:bg-slate-50 dark:hover:bg-slate-700/30 transition-colors"
                    >
                      <td className="px-6 py-4">
                        <span className="text-sm font-mono text-slate-600 dark:text-slate-400">
                          #{node.id}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-2">
                          <div className="relative">
                            <Circle
                              className={`w-3 h-3 ${
                                node.status === 'online'
                                  ? 'fill-emerald-500 text-emerald-500'
                                  : 'fill-slate-400 text-slate-400'
                              }`}
                            />
                            {node.status === 'online' && (
                              <Circle className="absolute inset-0 w-3 h-3 text-emerald-500 pulse-ring" />
                            )}
                          </div>
                          <span
                            className={`px-2 py-1 text-xs font-medium rounded capitalize ${getStatusColor(
                              node.status
                            )}`}
                          >
                            {node.status}
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <button
                          onClick={() => router.push(`/dashboard/nodes/${node.id}`)}
                          className="flex items-center gap-2 group hover:bg-slate-100 dark:hover:bg-slate-700 px-2 py-1 rounded transition-colors"
                        >
                          <Server className="w-4 h-4 text-slate-400" />
                          <span className="font-medium text-slate-900 dark:text-white group-hover:text-primary transition-colors">
                            {node.hostname}
                          </span>
                          <ExternalLink className="w-3 h-3 text-slate-400 opacity-0 group-hover:opacity-100 transition-opacity" />
                        </button>
                      </td>
                      <td className="px-6 py-4">
                        <code className="text-sm text-slate-600 dark:text-slate-400">
                          {node.ip_address}
                        </code>
                      </td>
                      <td className="px-6 py-4">
                        {node.group ? (
                          <div className="flex items-center gap-2">
                            <Tag className="w-4 h-4 text-slate-400" />
                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300">
                              {node.group}
                            </span>
                          </div>
                        ) : (
                          <span className="text-sm text-slate-400 dark:text-slate-500">—</span>
                        )}
                      </td>
                      <td className="px-6 py-4">
                        <span className="text-sm text-slate-600 dark:text-slate-400">
                          {getRelativeTime(node.last_seen)}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center justify-end gap-2">
                          <button
                            onClick={() => setEditingNode(node)}
                            className="p-2 hover:bg-slate-100 dark:hover:bg-slate-600 rounded-lg transition-colors"
                          >
                            <Edit2 className="w-4 h-4 text-slate-600 dark:text-slate-400" />
                          </button>
                          <button
                            onClick={() => handleDelete(node.id)}
                            className="p-2 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors"
                          >
                            <Trash2 className="w-4 h-4 text-red-600 dark:text-red-400" />
                          </button>
                        </div>
                      </td>
                    </motion.tr>
                  ))}
                </AnimatePresence>
              </tbody>
            </table>
            {filteredNodes.length === 0 && (
              <div className="text-center py-12 text-slate-500 dark:text-slate-400">
                {searchQuery ? 'No nodes found matching your search' : 'No nodes registered yet'}
              </div>
            )}
          </div>
        </motion.div>
      )}

      {/* Add/Edit Modal */}
      <NodeModal
        isOpen={isAddModalOpen || editingNode !== null}
        onClose={() => {
          setIsAddModalOpen(false)
          setEditingNode(null)
        }}
        node={editingNode}
      />
    </div>
  )
}

function NodeModal({
  isOpen,
  onClose,
  node,
}: {
  isOpen: boolean
  onClose: () => void
  node: Node | null
}) {
  const [hostname, setHostname] = useState(node?.hostname || '')
  const [ipAddress, setIpAddress] = useState(node?.ip_address || '')
  const [group, setGroup] = useState(node?.group || '')
  const queryClient = useQueryClient()

  const mutation = useMutation({
    mutationFn: node
      ? (data: any) => updateNode(node.id, data)
      : registerNode,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['nodes'] })
      toast.success(node ? 'Node updated successfully' : 'Node registered successfully')
      onClose()
    },
    onError: () => {
      toast.error('Failed to save node')
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    mutation.mutate({ 
      hostname, 
      ip_address: ipAddress,
      group: group || null
    })
  }

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={node ? 'Edit Node' : 'Register Node'}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
            Hostname
          </label>
          <input
            type="text"
            value={hostname}
            onChange={(e) => setHostname(e.target.value)}
            className="w-full px-4 py-2 bg-slate-50 dark:bg-slate-700 border border-slate-300 dark:border-slate-600 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent transition-all outline-none text-slate-900 dark:text-white"
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
            IP Address
          </label>
          <input
            type="text"
            value={ipAddress}
            onChange={(e) => setIpAddress(e.target.value)}
            className="w-full px-4 py-2 bg-slate-50 dark:bg-slate-700 border border-slate-300 dark:border-slate-600 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent transition-all outline-none text-slate-900 dark:text-white"
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
            Group (Optional)
          </label>
          <input
            type="text"
            value={group}
            onChange={(e) => setGroup(e.target.value)}
            placeholder="e.g., IT, HR, Linux, Windows"
            className="w-full px-4 py-2 bg-slate-50 dark:bg-slate-700 border border-slate-300 dark:border-slate-600 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent transition-all outline-none text-slate-900 dark:text-white"
          />
          <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
            Group nodes by department, OS type, or any category
          </p>
        </div>
        <div className="flex gap-3 pt-4">
          <button
            type="button"
            onClick={onClose}
            className="flex-1 px-4 py-2 bg-slate-100 dark:bg-slate-700 text-slate-900 dark:text-white rounded-lg hover:bg-slate-200 dark:hover:bg-slate-600 transition-colors"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={mutation.isPending}
            className="flex-1 px-4 py-2 bg-primary text-white rounded-lg hover:bg-blue-600 transition-colors disabled:opacity-50"
          >
            {mutation.isPending ? 'Saving...' : node ? 'Update' : 'Register'}
          </button>
        </div>
      </form>
    </Modal>
  )
}
