'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { motion } from 'framer-motion';
import { Waves, Home, Database, ChevronDown, TrendingUp } from 'lucide-react';
import { useState } from 'react';

const navItems = [
  {
    href: '/',
    label: 'Overview',
    icon: Home,
    description: 'Project overview and station map'
  },
  {
    href: '/data',
    label: 'Data',
    icon: Database,
    description: 'Data overview, stations, and statistics',
    hasDropdown: true,
    subItems: [
      {
        href: '/data',
        label: 'Overview',
        description: 'Dataset overview and station information'
      },
      {
        href: '/data/acoustic-analysis',
        label: 'Acoustic Analysis',
        description: 'Acoustic indices heatmap and analysis'
      },
      {
        href: '/data/environmental',
        label: 'Environmental Data',
        description: 'Temperature and depth measurements'
      }
    ]
  },
  {
    href: '/analysis',
    label: 'Analysis',
    icon: TrendingUp,
    description: 'Data analysis and pattern discovery',
    hasDropdown: true,
    subItems: [
      {
        href: '/analysis',
        label: 'Overview',
        description: 'Analysis methodology and approach'
      },
      {
        href: '/analysis/reducing-complexity',
        label: 'Reducing Complexity',
        description: 'Dimensionality reduction and feature selection'
      },
      {
        href: '/analysis/models',
        label: 'Predictive Models',
        description: 'Temporal stratification and machine learning models'
      }
    ]
  },
];

export default function Navigation() {
  const pathname = usePathname();
  const [openDropdown, setOpenDropdown] = useState<string | null>(null);

  return (
    <nav className="bg-background/60 backdrop-blur-md backdrop-saturate-150 border-b border-border/50 sticky top-0 z-50 shadow-sm">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-3 group">
            <motion.div
              animate={{ 
                rotateY: [0, 15, 0, -15, 0],
              }}
              transition={{
                duration: 6,
                repeat: Infinity,
                ease: "easeInOut"
              }}
            >
              <Waves className="h-6 w-6 text-primary" />
            </motion.div>
            <div className="hidden sm:block">
              <h1 className="font-medium text-lg">MBON Dashboard</h1>
              <p className="text-xs text-muted-foreground -mt-1">Marine Biodiversity Observatory Network</p>
            </div>
          </Link>

          {/* Navigation Links */}
          <div className="flex items-center space-x-1">
            {navItems.map((item) => {
              const isActive = pathname === item.href || (item.subItems && item.subItems.some(sub => pathname === sub.href));
              const Icon = item.icon;
              
              if (item.hasDropdown && item.subItems) {
                return (
                  <div 
                    key={item.href}
                    className="relative group"
                    onMouseEnter={() => setOpenDropdown(item.href)}
                    onMouseLeave={() => setOpenDropdown(null)}
                  >
                    <Link
                      href={item.href}
                      className="relative group"
                    >
                      <motion.div
                        className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
                          isActive 
                            ? 'bg-primary/10 text-primary' 
                            : 'text-muted-foreground hover:text-foreground hover:bg-accent/50'
                        }`}
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                      >
                        <Icon className="h-4 w-4" />
                        <span className="font-medium text-sm hidden md:block">{item.label}</span>
                        <ChevronDown className="h-3 w-3 ml-1 transition-transform duration-200" />
                      </motion.div>

                      {/* Active indicator */}
                      {isActive && (
                        <motion.div
                          className="absolute bottom-0 left-1/2 w-8 h-0.5 bg-primary rounded-full"
                          layoutId="activeTab"
                          initial={{ opacity: 0 }}
                          animate={{ opacity: 1 }}
                          style={{ translateX: '-50%' }}
                        />
                      )}
                    </Link>

                    {/* Dropdown Menu */}
                    {openDropdown === item.href && (
                      <motion.div
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: 10 }}
                        className="absolute top-full left-0 pt-2 w-64 z-50"
                      >
                        {/* Invisible bridge to prevent dropdown from closing */}
                        <div className="absolute top-0 left-0 right-0 h-2 bg-transparent" />
                        <div className="bg-popover border border-border rounded-lg shadow-lg overflow-hidden"
                        >
                          {item.subItems.map((subItem) => (
                            <Link
                              key={subItem.href}
                              href={subItem.href}
                              className={`block px-4 py-3 hover:bg-accent transition-colors ${
                                pathname === subItem.href ? 'bg-primary/5 text-primary' : 'text-popover-foreground'
                              }`}
                            >
                              <div className="font-medium text-sm">{subItem.label}</div>
                              <div className="text-xs text-muted-foreground mt-1">{subItem.description}</div>
                            </Link>
                          ))}
                        </div>
                      </motion.div>
                    )}
                  </div>
                );
              }

              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className="relative group"
                >
                  <motion.div
                    className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
                      isActive 
                        ? 'bg-primary/10 text-primary' 
                        : 'text-muted-foreground hover:text-foreground hover:bg-accent/50'
                    }`}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <Icon className="h-4 w-4" />
                    <span className="font-medium text-sm hidden md:block">{item.label}</span>
                  </motion.div>

                  {/* Active indicator */}
                  {isActive && (
                    <motion.div
                      className="absolute bottom-0 left-1/2 w-8 h-0.5 bg-primary rounded-full"
                      layoutId="activeTab"
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      style={{ translateX: '-50%' }}
                    />
                  )}

                  {/* Tooltip for mobile */}
                  <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none md:hidden">
                    <div className="bg-popover text-popover-foreground text-xs px-2 py-1 rounded border shadow-lg whitespace-nowrap">
                      {item.label}
                    </div>
                  </div>
                </Link>
              );
            })}
          </div>
        </div>
      </div>
    </nav>
  );
}