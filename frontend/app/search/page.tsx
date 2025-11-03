'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'

export default function SearchPage() {
  const router = useRouter()

  // Redirect to dashboard - search is now handled by navbar
  useEffect(() => {
    router.push('/dashboard')
  }, [router])

  // Show loading state while redirecting
  return (
    <main className="container mx-auto px-4 py-12">
      <div className="max-w-4xl mx-auto text-center">
        <div className="animate-spin text-4xl mb-4">⚡</div>
        <p className="text-neutral-400">Redirecting to dashboard...</p>
      </div>
    </main>
  )
}

