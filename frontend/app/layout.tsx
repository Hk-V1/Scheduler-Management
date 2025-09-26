import './globals.css'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Scheduler Dashboard',
  description: 'Manage your scheduled jobs and view execution logs',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
