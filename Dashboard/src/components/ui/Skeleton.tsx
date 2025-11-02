'use client'

import { motion } from 'framer-motion'

export function SkeletonCard() {
  return (
    <div className="bg-white dark:bg-slate-800 rounded-lg p-6 shadow-sm border border-slate-200 dark:border-slate-700">
      <div className="animate-pulse space-y-4">
        <div className="h-4 bg-slate-200 dark:bg-slate-700 rounded w-1/3"></div>
        <div className="h-8 bg-slate-200 dark:bg-slate-700 rounded w-1/2"></div>
      </div>
    </div>
  )
}

export function SkeletonTable({ rows = 5 }: { rows?: number }) {
  return (
    <div className="bg-white dark:bg-slate-800 rounded-lg shadow-sm border border-slate-200 dark:border-slate-700 overflow-hidden">
      <div className="p-6">
        <div className="h-6 bg-slate-200 dark:bg-slate-700 rounded w-1/4 mb-4 animate-pulse"></div>
        <div className="space-y-3">
          {Array.from({ length: rows }).map((_, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: i * 0.05 }}
              className="h-12 bg-slate-100 dark:bg-slate-700/50 rounded animate-pulse"
            />
          ))}
        </div>
      </div>
    </div>
  )
}
