import Link from 'next/link'

export default function NavigationFixed() {
  return (
    <header className="bg-white border-b border-slate-200 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <div className="flex items-center">
            <Link href="/" className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-gradient-to-br from-ocean-500 to-coral-500 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">M</span>
              </div>
              <div>
                <h1 className="font-display font-bold text-ocean-900 text-lg">
                  MBON Biosound : May River, SC
                </h1>
                <p className="text-xs text-slate-500 -mt-1">Acoustic indices and marine biodiversity</p>
              </div>
            </Link>
          </div>

          {/* Simple Navigation */}
          <nav className="hidden md:flex space-x-4">
            <Link href="/" className="px-3 py-2 text-sm font-medium text-slate-600 hover:text-ocean-700">
              Overview
            </Link>
            <Link href="/acoustic-biodiversity" className="px-3 py-2 text-sm font-medium text-slate-600 hover:text-ocean-700">
              Analysis
            </Link>
            <Link href="/stations" className="px-3 py-2 text-sm font-medium text-slate-600 hover:text-ocean-700">
              Stations
            </Link>
            <Link href="/explore/indices" className="px-3 py-2 text-sm font-medium text-slate-600 hover:text-ocean-700">
              Explore
            </Link>
          </nav>
        </div>
      </div>
    </header>
  )
}