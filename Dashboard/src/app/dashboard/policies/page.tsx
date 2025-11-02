'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { motion, AnimatePresence } from 'framer-motion'
import { Shield, Plus, Trash2, Code } from 'lucide-react'
import { fetchPolicies, createPolicy, deletePolicy } from '@/lib/api'
import { Policy } from '@/types'
import { SkeletonTable } from '@/components/ui/Skeleton'
import { Modal } from '@/components/ui/Modal'
import toast from 'react-hot-toast'
import dynamic from 'next/dynamic'

const MonacoEditor = dynamic(() => import('@monaco-editor/react'), { ssr: false })

export default function PoliciesPage() {
  const [isAddModalOpen, setIsAddModalOpen] = useState(false)
  const [viewingPolicy, setViewingPolicy] = useState<Policy | null>(null)
  const queryClient = useQueryClient()

  const { data: policies, isLoading } = useQuery<Policy[]>({
    queryKey: ['policies'],
    queryFn: fetchPolicies,
    refetchInterval: 10000,
  })

  const deleteMutation = useMutation({
    mutationFn: deletePolicy,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['policies'] })
      toast.success('Policy deleted successfully')
    },
    onError: () => {
      toast.error('Failed to delete policy')
    },
  })

  const handleDelete = (id: number) => {
    if (confirm('Are you sure you want to delete this policy?')) {
      deleteMutation.mutate(id)
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 dark:text-white">
            Policies
          </h1>
          <p className="text-slate-600 dark:text-slate-400 mt-1">
            Manage security policies and rules
          </p>
        </div>
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={() => setIsAddModalOpen(true)}
          className="flex items-center gap-2 px-4 py-2 bg-primary text-white rounded-lg hover:bg-blue-600 transition-colors shadow-lg"
        >
          <Plus className="w-5 h-5" />
          Create Policy
        </motion.button>
      </div>

      {/* Policies Grid */}
      {isLoading ? (
        <SkeletonTable rows={6} />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <AnimatePresence>
            {policies?.map((policy, idx) => (
              <motion.div
                key={policy.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.9 }}
                transition={{ delay: idx * 0.05 }}
                className="bg-white dark:bg-slate-800 rounded-lg p-6 shadow-sm border border-slate-200 dark:border-slate-700 hover:shadow-md transition-shadow"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-primary/10 rounded-lg">
                      <Shield className="w-5 h-5 text-primary" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-slate-900 dark:text-white">
                        {policy.name}
                      </h3>
                      <p className="text-xs text-slate-500 dark:text-slate-400 capitalize">
                        {policy.type}
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={() => handleDelete(policy.id)}
                    className="p-2 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors"
                  >
                    <Trash2 className="w-4 h-4 text-red-600 dark:text-red-400" />
                  </button>
                </div>

                <div className="space-y-2">
                  <div className="text-sm text-slate-600 dark:text-slate-400">
                    <span className="font-medium">{policy.assigned_nodes.length}</span> nodes assigned
                  </div>
                  <button
                    onClick={() => setViewingPolicy(policy)}
                    className="flex items-center gap-2 text-sm text-primary hover:text-blue-600 transition-colors"
                  >
                    <Code className="w-4 h-4" />
                    View Rules
                  </button>
                </div>

                {policy.assigned_nodes.length > 0 && (
                  <div className="mt-4 pt-4 border-t border-slate-200 dark:border-slate-700">
                    <p className="text-xs text-slate-500 dark:text-slate-400 mb-2">Assigned to:</p>
                    <div className="flex flex-wrap gap-1">
                      {policy.assigned_nodes.slice(0, 3).map((node) => (
                        <span
                          key={node.id}
                          className="px-2 py-1 bg-slate-100 dark:bg-slate-700 text-xs rounded text-slate-700 dark:text-slate-300"
                        >
                          {node.hostname}
                        </span>
                      ))}
                      {policy.assigned_nodes.length > 3 && (
                        <span className="px-2 py-1 text-xs text-slate-500 dark:text-slate-400">
                          +{policy.assigned_nodes.length - 3} more
                        </span>
                      )}
                    </div>
                  </div>
                )}
              </motion.div>
            ))}
          </AnimatePresence>

          {policies?.length === 0 && (
            <div className="col-span-full text-center py-12 text-slate-500 dark:text-slate-400">
              No policies created yet
            </div>
          )}
        </div>
      )}

      {/* Create Policy Modal */}
      <PolicyModal
        isOpen={isAddModalOpen}
        onClose={() => setIsAddModalOpen(false)}
      />

      {/* View Policy Rules Modal */}
      {viewingPolicy && (
        <Modal
          isOpen={true}
          onClose={() => setViewingPolicy(null)}
          title={`${viewingPolicy.name} - Rules`}
        >
          <div className="rounded-lg overflow-hidden border border-slate-200 dark:border-slate-700">
            <MonacoEditor
              height="400px"
              language="json"
              theme="vs-dark"
              value={JSON.stringify(viewingPolicy.rules_json, null, 2)}
              options={{
                readOnly: true,
                minimap: { enabled: false },
                fontSize: 14,
              }}
            />
          </div>
        </Modal>
      )}
    </div>
  )
}

function PolicyModal({ isOpen, onClose }: { isOpen: boolean; onClose: () => void }) {
  const [name, setName] = useState('')
  const [type, setType] = useState('firewall')
  const [rulesJson, setRulesJson] = useState('{\n  "rules": []\n}')
  const queryClient = useQueryClient()

  const mutation = useMutation({
    mutationFn: createPolicy,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['policies'] })
      toast.success('Policy created successfully')
      onClose()
      setName('')
      setType('firewall')
      setRulesJson('{\n  "rules": []\n}')
    },
    onError: () => {
      toast.error('Failed to create policy')
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const parsedRules = JSON.parse(rulesJson)
      mutation.mutate({ name, type, rules_json: parsedRules })
    } catch (err) {
      toast.error('Invalid JSON in rules')
    }
  }

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Create Policy">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
            Policy Name
          </label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full px-4 py-2 bg-slate-50 dark:bg-slate-700 border border-slate-300 dark:border-slate-600 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent transition-all outline-none text-slate-900 dark:text-white"
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
            Type
          </label>
          <select
            value={type}
            onChange={(e) => setType(e.target.value)}
            className="w-full px-4 py-2 bg-slate-50 dark:bg-slate-700 border border-slate-300 dark:border-slate-600 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent transition-all outline-none text-slate-900 dark:text-white"
          >
            <option value="firewall">Firewall</option>
            <option value="ids">IDS</option>
            <option value="file_integrity">File Integrity</option>
            <option value="compliance">Compliance</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
            Rules (JSON)
          </label>
          <div className="rounded-lg overflow-hidden border border-slate-300 dark:border-slate-600">
            <MonacoEditor
              height="300px"
              language="json"
              theme="vs-dark"
              value={rulesJson}
              onChange={(value) => setRulesJson(value || '')}
              options={{
                minimap: { enabled: false },
                fontSize: 14,
              }}
            />
          </div>
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
            {mutation.isPending ? 'Creating...' : 'Create Policy'}
          </button>
        </div>
      </form>
    </Modal>
  )
}
