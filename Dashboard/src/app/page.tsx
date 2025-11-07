'use client'

import { useEffect, useState } from 'react'
import { useAuthStore } from '@/store'
import LoginPage from './login/page'
import { useRouter } from 'next/navigation'

export default function Home() {
  const router = useRouter()
  const [mounted, setMounted] = useState(false)
  const token = useAuthStore((state) => state.token)
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated)

  useEffect(() => {
    setMounted(true)
  }, [])

  useEffect(() => {
    // Only redirect to dashboard if authenticated, never to login
    if (mounted && isAuthenticated && token) {
      router.replace('/dashboard')
    }
  }, [mounted, isAuthenticated, token, router])

  // Show loading on server-side render
  if (!mounted) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50 dark:bg-slate-900">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
          <p className="mt-4 text-slate-600 dark:text-slate-400">Loading...</p>
        </div>
      </div>
    )
  }

  // If not authenticated, show login page directly (no redirect)
  if (!isAuthenticated || !token) {
    return <LoginPage />
  }

  // Show loading while redirecting to dashboard
  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 dark:bg-slate-900">
      <div className="text-center">
        <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
        <p className="mt-4 text-slate-600 dark:text-slate-400">Loading...</p>
      </div>
    </div>
  )
}
