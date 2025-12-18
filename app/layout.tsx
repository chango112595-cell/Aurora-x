/**
 * Aurora Root Layout - Next.js App Router
 * Replaces index.html with pure TSX
 */
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import { AuroraErrorMonitor } from '../client/src/components/AuroraErrorMonitor'
import '../client/src/index.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Aurora - Quantum Neural Intelligence',
  description: 'Aurora AI - 188 Total Power: 79 Knowledge + 66 Execution + 43 Systems',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <head>
        <meta charSet="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
      </head>
      <body className={inter.className}>
        <AuroraErrorMonitor />
        {children}
      </body>
    </html>
  )
}
