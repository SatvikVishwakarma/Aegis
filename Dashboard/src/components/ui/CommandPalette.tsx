'use client'

import { Command } from 'cmdk'
import { useEffect, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Search, Home, Server, Shield, FileText, Settings } from 'lucide-react'
import { useRouter } from 'next/navigation'

export function CommandPalette() {
  const [open, setOpen] = useState(false)
  const router = useRouter()

  useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (e.key === 'k' && (e.metaKey || e.ctrlKey)) {
        e.preventDefault()
        setOpen((open) => !open)
      }
    }

    document.addEventListener('keydown', down)
    return () => document.removeEventListener('keydown', down)
  }, [])

  const navigate = (path: string) => {
    router.push(path)
    setOpen(false)
  }

  return (
    <AnimatePresence>
      {open && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50"
            onClick={() => setOpen(false)}
          />
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: -20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: -20 }}
            className="fixed top-[20%] left-1/2 -translate-x-1/2 w-full max-w-2xl z-50"
          >
            <Command className="rounded-lg border border-slate-200 dark:border-slate-700 shadow-2xl bg-white dark:bg-slate-800">
              <div className="flex items-center border-b border-slate-200 dark:border-slate-700 px-4">
                <Search className="w-5 h-5 text-slate-400 mr-2" />
                <Command.Input
                  placeholder="Type a command or search..."
                  className="flex-1 py-4 bg-transparent outline-none text-slate-900 dark:text-white placeholder:text-slate-400"
                />
              </div>
              <Command.List className="max-h-96 overflow-auto p-2">
                <Command.Empty className="py-6 text-center text-sm text-slate-500">
                  No results found.
                </Command.Empty>

                <Command.Group heading="Navigation" className="text-slate-500 dark:text-slate-400 text-xs font-semibold px-2 py-1">
                  <Command.Item
                    onSelect={() => navigate('/dashboard')}
                    className="flex items-center gap-3 px-4 py-3 rounded-lg cursor-pointer hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-900 dark:text-white"
                  >
                    <Home className="w-5 h-5" />
                    <span>Dashboard</span>
                  </Command.Item>
                  <Command.Item
                    onSelect={() => navigate('/dashboard/nodes')}
                    className="flex items-center gap-3 px-4 py-3 rounded-lg cursor-pointer hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-900 dark:text-white"
                  >
                    <Server className="w-5 h-5" />
                    <span>Nodes</span>
                  </Command.Item>
                  <Command.Item
                    onSelect={() => navigate('/dashboard/policies')}
                    className="flex items-center gap-3 px-4 py-3 rounded-lg cursor-pointer hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-900 dark:text-white"
                  >
                    <Shield className="w-5 h-5" />
                    <span>Policies</span>
                  </Command.Item>
                  <Command.Item
                    onSelect={() => navigate('/dashboard/events')}
                    className="flex items-center gap-3 px-4 py-3 rounded-lg cursor-pointer hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-900 dark:text-white"
                  >
                    <FileText className="w-5 h-5" />
                    <span>Event Viewer</span>
                  </Command.Item>
                </Command.Group>
              </Command.List>
            </Command>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}
