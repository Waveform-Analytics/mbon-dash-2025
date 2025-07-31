import type { Metadata } from 'next'
import './globals.css'

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
      <body>
        <header className="bg-ocean-800 text-white shadow-lg">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between h-16">
              <div className="flex items-center">
                <h1 className="text-xl font-bold">MBON Dashboard</h1>
                <span className="ml-3 text-ocean-200 text-sm">Marine Biodiversity Observatory Network</span>
              </div>
              <nav className="hidden md:block">
                <div className="ml-10 flex items-baseline space-x-4">
                  <a href="/" className="text-ocean-100 hover:text-white px-3 py-2 rounded-md text-sm font-medium">
                    Overview
                  </a>
                  <a href="/species" className="text-ocean-200 hover:text-white px-3 py-2 rounded-md text-sm font-medium">
                    Species
                  </a>
                  <a href="/stations" className="text-ocean-200 hover:text-white px-3 py-2 rounded-md text-sm font-medium">
                    Stations
                  </a>
                  <a href="/temporal" className="text-ocean-200 hover:text-white px-3 py-2 rounded-md text-sm font-medium">
                    Temporal
                  </a>
                  <a href="/explorer" className="text-ocean-200 hover:text-white px-3 py-2 rounded-md text-sm font-medium">
                    Explorer
                  </a>
                </div>
              </nav>
            </div>
          </div>
        </header>
        <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          {children}
        </main>
      </body>
    </html>
  )
}