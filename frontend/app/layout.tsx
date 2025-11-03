import type { Metadata } from 'next'
import './globals.css'
import Navbar from '@/components/Navbar'

export const metadata: Metadata = {
  title: 'Rick & Morty AI Challenge',
  description: 'AI-powered Rick & Morty exploration',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="dark">
      <body className="antialiased">
        <div className="min-h-screen bg-black text-neutral-100">
          <Navbar />
          {children}
        </div>
      </body>
    </html>
  )
}

