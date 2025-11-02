'use client'

import { motion } from 'framer-motion'
import { cn } from '@/lib/utils'

interface StatCardProps {
  title: string
  value: string | number
  icon: React.ReactNode
  trend?: {
    value: number
    isPositive: boolean
  }
  delay?: number
}

export function StatCard({ title, value, icon, trend, delay = 0 }: StatCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay }}
      className="bg-white dark:bg-slate-800 rounded-lg p-6 shadow-sm border border-slate-200 dark:border-slate-700 hover:shadow-md transition-shadow"
    >
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-slate-600 dark:text-slate-400">
            {title}
          </p>
          <p className="text-3xl font-bold text-slate-900 dark:text-white mt-2">
            {value}
          </p>
          {trend && (
            <div className="flex items-center mt-2">
              <span
                className={cn(
                  'text-xs font-medium',
                  trend.isPositive
                    ? 'text-emerald-600 dark:text-emerald-400'
                    : 'text-red-600 dark:text-red-400'
                )}
              >
                {trend.isPositive ? '+' : '-'}
                {Math.abs(trend.value)}%
              </span>
              <span className="text-xs text-slate-500 dark:text-slate-400 ml-2">
                vs last hour
              </span>
            </div>
          )}
        </div>
        <div className="ml-4 p-3 bg-primary/10 rounded-lg text-primary">
          {icon}
        </div>
      </div>
    </motion.div>
  )
}
