import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatDate(date: string | Date): string {
  return new Date(date).toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export function getRelativeTime(date: string | Date): string {
  const now = new Date().getTime()
  const then = new Date(date).getTime()
  const diff = now - then
  
  const seconds = Math.floor(diff / 1000)
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)
  const days = Math.floor(hours / 24)
  
  if (days > 0) return `${days}d ago`
  if (hours > 0) return `${hours}h ago`
  if (minutes > 0) return `${minutes}m ago`
  if (seconds > 0) return `${seconds}s ago`
  return 'just now'
}

export function getSeverityColor(severity: string): string {
  const colors: Record<string, string> = {
    low: 'text-blue-600 bg-blue-50 dark:text-blue-400 dark:bg-blue-950',
    medium: 'text-amber-600 bg-amber-50 dark:text-amber-400 dark:bg-amber-950',
    high: 'text-orange-600 bg-orange-50 dark:text-orange-400 dark:bg-orange-950',
    critical: 'text-red-600 bg-red-50 dark:text-red-400 dark:bg-red-950',
  }
  return colors[severity.toLowerCase()] || colors.low
}

export function getStatusColor(status: string): string {
  const colors: Record<string, string> = {
    online: 'text-emerald-600 bg-emerald-50 dark:text-emerald-400 dark:bg-emerald-950',
    offline: 'text-slate-600 bg-slate-50 dark:text-slate-400 dark:bg-slate-950',
  }
  return colors[status.toLowerCase()] || colors.offline
}
