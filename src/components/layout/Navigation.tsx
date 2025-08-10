'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useState } from 'react'
import { 
  HomeIcon, 
  ChartBarIcon, 
  BookOpenIcon, 
  MagnifyingGlassIcon,
  ChevronDownIcon,
  Bars3Icon,
  XMarkIcon
} from '@heroicons/react/24/outline'
import type { NavItem, NavChild } from '@/types/data'

const navigation: NavItem[] = [
  { name: 'Overview', href: '/', icon: HomeIcon },
  {
    name: 'Analysis',
    icon: ChartBarIcon,
    children: [
      { name: 'Acoustic Indices', href: '/acoustic-biodiversity', description: 'Which indices predict biodiversity?' },
      { name: 'Environmental Factors', href: '/environmental-factors', description: 'Temperature, depth & seasonal effects' },
    ]
  },
  {
    name: 'Resources',
    icon: BookOpenIcon,
    children: [
      { name: 'Index Guide', href: '/acoustic-glossary', description: 'Understanding acoustic indices' },
      { name: 'Station Profiles', href: '/stations', description: 'Study sites & spatial context' },
    ]
  },
  { name: 'Explorer', href: '/explorer', icon: MagnifyingGlassIcon },
]

export default function Navigation() {
  const pathname = usePathname()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [activeDropdown, setActiveDropdown] = useState<string | null>(null)

  // Helper function to check if a dropdown should be active
  const isDropdownActive = (children: NavChild[]) => {
    return children.some((child: NavChild) => pathname === child.href)
  }

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

          {/* Desktop Navigation */}
          <nav className="hidden md:flex space-x-2">
            {navigation.map((item) => {
              // Single page items
              if (item.href) {
                const isActive = pathname === item.href
                return (
                  <Link
                    key={item.name}
                    href={item.href}
                    className={`inline-flex items-center space-x-2 px-3 py-2 text-sm font-medium rounded-lg transition-colors ${
                      isActive
                        ? 'bg-ocean-50 text-ocean-700 border border-ocean-200'
                        : 'text-slate-600 hover:text-ocean-700 hover:bg-slate-50'
                    }`}
                  >
                    {item.icon ? <item.icon className="w-5 h-5" /> : null}
                    <span>{item.name}</span>
                  </Link>
                )
              }

              // Dropdown items
              if (item.children) {
                const isActive = isDropdownActive(item.children)
                return (
                  <div
                    key={item.name}
                    className="relative"
                    onMouseEnter={() => setActiveDropdown(item.name)}
                    onMouseLeave={() => setActiveDropdown(null)}
                  >
                    <button
                      className={`inline-flex items-center space-x-2 px-3 py-2 text-sm font-medium transition-colors ${
                        activeDropdown === item.name
                          ? 'bg-ocean-50 text-ocean-700 border border-ocean-200 rounded-t-lg rounded-b-none'
                          : isActive
                          ? 'bg-ocean-50 text-ocean-700 border border-ocean-200 rounded-lg'
                          : 'text-slate-600 hover:text-ocean-700 hover:bg-slate-50 rounded-lg'
                      }`}
                    >
                      {item.icon ? <item.icon className="w-5 h-5" /> : null}
                      <span>{item.name}</span>
                      <ChevronDownIcon className="w-4 h-4 ml-1" />
                    </button>

                    {/* Dropdown Menu */}
                    {activeDropdown === item.name && (
                      <div className="absolute top-full left-0 w-72 bg-white border border-slate-200 border-t-0 rounded-b-lg rounded-tr-lg shadow-lg py-2 z-50">
                        {item.children.map((child) => {
                          const childIsActive = pathname === child.href
                          return (
                            <Link
                              key={child.name}
                              href={child.href}
                              className={`flex items-start space-x-3 px-4 py-3 hover:bg-slate-50 transition-colors ${
                                childIsActive ? 'bg-ocean-50 border-r-2 border-ocean-500' : ''
                              }`}
                            >
                              <div>
                                <div className={`font-medium ${childIsActive ? 'text-ocean-700' : 'text-slate-900'}`}>
                                  {child.name}
                                </div>
                                <div className="text-sm text-slate-500 mt-0.5">
                                  {child.description}
                                </div>
                              </div>
                            </Link>
                          )
                        })}
                      </div>
                    )}
                  </div>
                )
              }

              return null
            })}
          </nav>

          {/* Mobile menu button */}
          <div className="md:hidden">
            <button
              type="button"
              className="text-slate-600 hover:text-ocean-700 focus:outline-none focus:ring-2 focus:ring-ocean-500 focus:ring-offset-2 p-2 rounded-lg"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            >
              <span className="sr-only">Open main menu</span>
              {mobileMenuOpen ? (
                <XMarkIcon className="w-6 h-6" />
              ) : (
                <Bars3Icon className="w-6 h-6" />
              )}
            </button>
          </div>
        </div>

        {/* Mobile Navigation Menu */}
        {mobileMenuOpen && (
          <div className="md:hidden border-t border-slate-200 py-4">
            <nav className="space-y-1">
              {navigation.map((item) => {
                // Single page items
                if (item.href) {
                  const isActive = pathname === item.href
                  return (
                    <Link
                      key={item.name}
                      href={item.href}
                      className={`flex items-center space-x-3 px-3 py-2 text-base font-medium rounded-lg transition-colors ${
                        isActive
                          ? 'bg-ocean-50 text-ocean-700 border border-ocean-200'
                          : 'text-slate-600 hover:text-ocean-700 hover:bg-slate-50'
                      }`}
                      onClick={() => setMobileMenuOpen(false)}
                    >
                      {item.icon ? <item.icon className="w-5 h-5" /> : null}
                      <span>{item.name}</span>
                    </Link>
                  )
                }

                // Dropdown items - show as expanded sections
                if (item.children) {
                  return (
                    <div key={item.name} className="space-y-1">
                      <div className="px-3 py-2 text-base font-semibold text-slate-700 flex items-center space-x-3">
                        {item.icon ? <item.icon className="w-5 h-5" /> : null}
                        <span>{item.name}</span>
                      </div>
                      <div className="ml-6 space-y-1">
                        {item.children.map((child) => {
                          const childIsActive = pathname === child.href
                          return (
                            <Link
                              key={child.name}
                              href={child.href}
                              className={`flex items-center space-x-3 px-3 py-2 text-sm rounded-lg transition-colors ${
                                childIsActive
                                  ? 'bg-ocean-50 text-ocean-700 border border-ocean-200'
                                  : 'text-slate-600 hover:text-ocean-700 hover:bg-slate-50'
                              }`}
                              onClick={() => setMobileMenuOpen(false)}
                            >
                              <span>{child.name}</span>
                            </Link>
                          )
                        })}
                      </div>
                    </div>
                  )
                }

                return null
              })}
            </nav>
          </div>
        )}
      </div>
    </header>
  )
}