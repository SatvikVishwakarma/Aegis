'use client'

import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { Server, Activity, AlertTriangle, Shield } from 'lucide-react'
import { fetchNodes, fetchEvents } from '@/lib/api'
import { StatCard } from '@/components/ui/StatCard'
import { SkeletonCard } from '@/components/ui/Skeleton'
import { Node, Event } from '@/types'
import { getRelativeTime, getSeverityColor } from '@/lib/utils'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

export default function DashboardPage() {
  const { data: nodes, isLoading: nodesLoading } = useQuery<Node[]>({
    queryKey: ['nodes'],
    queryFn: fetchNodes,
    refetchInterval: 5000, // Refresh every 5 seconds
  })

  const { data: events, isLoading: eventsLoading } = useQuery<Event[]>({
    queryKey: ['events'],
    queryFn: () => fetchEvents({ limit: 100 }),
    refetchInterval: 5000,
  })

  const stats = {
    totalNodes: nodes?.length || 0,
    onlineNodes: nodes?.filter((n) => n.status === 'online').length || 0,
    totalEvents: events?.length || 0,
    criticalEvents: events?.filter((e) => e.severity === 'critical').length || 0,
  }

  // Prepare chart data (events over time)
  const chartData = events?.slice(0, 24).reverse().map((event, idx) => ({
    name: `${idx}`,
    events: 1,
    time: new Date(event.timestamp).toLocaleTimeString(),
  })) || []

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold text-slate-900 dark:text-white">
          Dashboard
        </h1>
        <p className="text-slate-600 dark:text-slate-400 mt-1">
          Real-time security monitoring overview
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {nodesLoading ? (
          <>
            <SkeletonCard />
            <SkeletonCard />
            <SkeletonCard />
            <SkeletonCard />
          </>
        ) : (
          <>
            <StatCard
              title="Total Nodes"
              value={stats.totalNodes}
              icon={<Server className="w-6 h-6" />}
              delay={0}
            />
            <StatCard
              title="Online Nodes"
              value={stats.onlineNodes}
              icon={<Activity className="w-6 h-6" />}
              delay={0.1}
            />
            <StatCard
              title="Total Events"
              value={stats.totalEvents}
              icon={<Shield className="w-6 h-6" />}
              delay={0.2}
            />
            <StatCard
              title="Critical Alerts"
              value={stats.criticalEvents}
              icon={<AlertTriangle className="w-6 h-6" />}
              delay={0.3}
            />
          </>
        )}
      </div>

      {/* Charts & Live Feed */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Event Chart */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="bg-white dark:bg-slate-800 rounded-lg p-6 shadow-sm border border-slate-200 dark:border-slate-700"
        >
          <h2 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">
            Events Over Time
          </h2>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.2} />
              <XAxis dataKey="name" stroke="#94a3b8" />
              <YAxis stroke="#94a3b8" />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#1e293b',
                  border: 'none',
                  borderRadius: '8px',
                  color: '#fff',
                }}
              />
              <Line
                type="monotone"
                dataKey="events"
                stroke="#3B82F6"
                strokeWidth={2}
                dot={{ fill: '#3B82F6', r: 4 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </motion.div>

        {/* Recent Events */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="bg-white dark:bg-slate-800 rounded-lg p-6 shadow-sm border border-slate-200 dark:border-slate-700"
        >
          <h2 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">
            Recent Events
          </h2>
          <div className="space-y-3 max-h-[250px] overflow-y-auto">
            {eventsLoading ? (
              <div className="text-slate-500 dark:text-slate-400 text-sm">
                Loading events...
              </div>
            ) : events && events.length > 0 ? (
              events.slice(0, 5).map((event, idx) => (
                <motion.div
                  key={event.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: idx * 0.05 }}
                  className="flex items-start justify-between p-3 bg-slate-50 dark:bg-slate-700/50 rounded-lg"
                >
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium text-slate-900 dark:text-white">
                        {event.event_type}
                      </span>
                      <span
                        className={`px-2 py-0.5 text-xs font-medium rounded ${getSeverityColor(
                          event.severity
                        )}`}
                      >
                        {event.severity}
                      </span>
                    </div>
                    <p className="text-xs text-slate-600 dark:text-slate-400 mt-1">
                      Node ID: {event.node_id}
                    </p>
                  </div>
                  <span className="text-xs text-slate-500 dark:text-slate-400">
                    {getRelativeTime(event.timestamp)}
                  </span>
                </motion.div>
              ))
            ) : (
              <div className="text-slate-500 dark:text-slate-400 text-sm">
                No events yet
              </div>
            )}
          </div>
        </motion.div>
      </div>
    </div>
  )
}
