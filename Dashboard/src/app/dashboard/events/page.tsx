'use client'

import { useState, useEffect, useMemo, Fragment } from 'react'
import { useQuery } from '@tanstack/react-query'
import { motion, AnimatePresence } from 'framer-motion'
import { FileText, Filter, ChevronDown, ChevronUp } from 'lucide-react'
import { fetchEvents } from '@/lib/api'
import { Event } from '@/types'
import { formatDate, getSeverityColor } from '@/lib/utils'
import { SkeletonTable } from '@/components/ui/Skeleton'

export default function EventsPage() {
  const [severityFilter, setSeverityFilter] = useState<string>('')
  const [typeFilter, setTypeFilter] = useState<string>('')
  const [expandedRows, setExpandedRows] = useState<Set<number>>(new Set())
  const [debouncedFilters, setDebouncedFilters] = useState({ severity: '', type: '' })

  // Debounce filters
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedFilters({ severity: severityFilter, type: typeFilter })
    }, 300)

    return () => clearTimeout(timer)
  }, [severityFilter, typeFilter])

  const { data: events, isLoading } = useQuery<Event[]>({
    queryKey: ['events', debouncedFilters],
    queryFn: () =>
      fetchEvents({
        severity: debouncedFilters.severity || undefined,
        event_type: debouncedFilters.type || undefined,
        limit: 100,
      }),
    refetchInterval: 5000,
  })

  const toggleRow = (id: number) => {
    const newSet = new Set(expandedRows)
    if (newSet.has(id)) {
      newSet.delete(id)
    } else {
      newSet.add(id)
    }
    setExpandedRows(newSet)
  }

  // Get unique event types for filter
  const eventTypes = useMemo(() => {
    if (!events) return []
    return Array.from(new Set(events.map((e) => e.event_type)))
  }, [events])

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-slate-900 dark:text-white">
          Event Viewer
        </h1>
        <p className="text-slate-600 dark:text-slate-400 mt-1">
          Monitor and analyze security events in real-time
        </p>
      </div>

      {/* Filters */}
      <div className="bg-white dark:bg-slate-800 rounded-lg p-4 shadow-sm border border-slate-200 dark:border-slate-700">
        <div className="flex items-center gap-3 mb-4">
          <Filter className="w-5 h-5 text-slate-600 dark:text-slate-400" />
          <h2 className="font-semibold text-slate-900 dark:text-white">Filters</h2>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
              Severity
            </label>
            <select
              value={severityFilter}
              onChange={(e) => setSeverityFilter(e.target.value)}
              className="w-full px-4 py-2 bg-slate-50 dark:bg-slate-700 border border-slate-300 dark:border-slate-600 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent transition-all outline-none text-slate-900 dark:text-white"
            >
              <option value="">All Severities</option>
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
              <option value="critical">Critical</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
              Event Type
            </label>
            <select
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
              className="w-full px-4 py-2 bg-slate-50 dark:bg-slate-700 border border-slate-300 dark:border-slate-600 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent transition-all outline-none text-slate-900 dark:text-white"
            >
              <option value="">All Types</option>
              {eventTypes.map((type) => (
                <option key={type} value={type}>
                  {type}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Events Table */}
      {isLoading ? (
        <SkeletonTable rows={10} />
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
                  <th className="px-6 py-4 text-left text-xs font-semibold text-slate-600 dark:text-slate-400 uppercase tracking-wider w-12">
                    
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-slate-600 dark:text-slate-400 uppercase tracking-wider">
                    Timestamp
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-slate-600 dark:text-slate-400 uppercase tracking-wider">
                    Event Type
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-slate-600 dark:text-slate-400 uppercase tracking-wider">
                    Severity
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-slate-600 dark:text-slate-400 uppercase tracking-wider">
                    Node ID
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200 dark:divide-slate-700">
                <AnimatePresence>
                  {events?.map((event, idx) => (
                    <Fragment key={event.id}>
                      <motion.tr
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: 20 }}
                        transition={{ delay: idx * 0.02 }}
                        className="hover:bg-slate-50 dark:hover:bg-slate-700/30 transition-colors cursor-pointer"
                        onClick={() => toggleRow(event.id)}
                      >
                        <td className="px-6 py-4">
                          <button className="p-1 hover:bg-slate-200 dark:hover:bg-slate-600 rounded">
                            {expandedRows.has(event.id) ? (
                              <ChevronUp className="w-4 h-4 text-slate-600 dark:text-slate-400" />
                            ) : (
                              <ChevronDown className="w-4 h-4 text-slate-600 dark:text-slate-400" />
                            )}
                          </button>
                        </td>
                        <td className="px-6 py-4">
                          <span className="text-sm text-slate-900 dark:text-white">
                            {formatDate(event.timestamp)}
                          </span>
                        </td>
                        <td className="px-6 py-4">
                          <div className="flex items-center gap-2">
                            <FileText className="w-4 h-4 text-slate-400" />
                            <span className="text-sm font-medium text-slate-900 dark:text-white">
                              {event.event_type}
                            </span>
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <span
                            className={`px-2 py-1 text-xs font-medium rounded capitalize ${getSeverityColor(
                              event.severity
                            )}`}
                          >
                            {event.severity}
                          </span>
                        </td>
                        <td className="px-6 py-4">
                          <code className="text-sm text-slate-600 dark:text-slate-400">
                            {event.node_id}
                          </code>
                        </td>
                      </motion.tr>
                      
                      {/* Expandable Details Row */}
                      <AnimatePresence>
                        {expandedRows.has(event.id) && (
                          <motion.tr
                            key={`details-${event.id}`}
                            initial={{ opacity: 0, height: 0 }}
                            animate={{ opacity: 1, height: 'auto' }}
                            exit={{ opacity: 0, height: 0 }}
                          >
                            <td colSpan={5} className="px-6 py-4 bg-slate-50 dark:bg-slate-700/30">
                              <div className="space-y-2">
                                <h4 className="text-sm font-semibold text-slate-900 dark:text-white mb-2">
                                  Event Details
                                </h4>
                                <pre className="bg-slate-100 dark:bg-slate-800 p-4 rounded-lg text-xs overflow-auto text-slate-900 dark:text-slate-100">
                                  {JSON.stringify(event.details, null, 2)}
                                </pre>
                              </div>
                            </td>
                          </motion.tr>
                        )}
                      </AnimatePresence>
                    </Fragment>
                  ))}
                </AnimatePresence>
              </tbody>
            </table>
            {events?.length === 0 && (
              <div className="text-center py-12 text-slate-500 dark:text-slate-400">
                No events found matching your filters
              </div>
            )}
          </div>
        </motion.div>
      )}

      {events && events.length > 0 && (
        <div className="text-sm text-slate-600 dark:text-slate-400 text-center">
          Showing {events.length} events
        </div>
      )}
    </div>
  )
}
