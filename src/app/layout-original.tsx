import './globals.css'
import type { Metadata } from 'next'
import { Inter, Source_Sans_3 } from 'next/font/google'
import Navigation from '@/components/layout/Navigation'

const inter = Inter({ 
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap',
  fallback: ['system-ui', 'arial'],
})

const sourceSans = Source_Sans_3({ 
  subsets: ['latin'],
  variable: '--font-source-sans',
  display: 'swap',
  fallback: ['system-ui', 'sans-serif'],
})

export const metadata: Metadata = {
  title: 'MBON Marine Biodiversity Dashboard',
  description: 'Interactive dashboard for exploring marine acoustic monitoring data from the OSA MBON project',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body 
        className={`${inter.variable} ${sourceSans.variable} font-sans bg-slate-50`}
        style={{ 
          backgroundColor: '#f8fafc', 
          color: '#0f172a', 
          fontFamily: 'var(--font-source-sans), system-ui, sans-serif',
          margin: 0,
          padding: 0
        }}
      >
        <Navigation />
        <main className="min-h-screen" style={{ minHeight: '100vh' }}>
          {children}
        </main>
      </body>
    </html>
  )
}