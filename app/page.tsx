/**
 * Aurora Home Page - Next.js Entry Point
 */
'use client'

import { QueryClientProvider } from "@tanstack/react-query"
import { queryClient } from "../client/src/lib/queryClient"
import AuroraFuturisticLayout from "../client/src/components/AuroraFuturisticLayout"
import App from "../client/src/App"
import { Toaster } from "@/components/ui/toaster"

export default function Home() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuroraFuturisticLayout>
        <App />
      </AuroraFuturisticLayout>
      <Toaster />
    </QueryClientProvider>
  )
}
