'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { motion } from 'framer-motion';
import { Waves, Home, BarChart3, FlaskConical, Compass, BookOpen } from 'lucide-react';

const navItems = [
  {
    href: '/',
    label: 'Home',
    icon: Home,
    description: 'Project overview and marine monitoring innovation'
  },
  {
    href: '/challenge',
    label: 'The Challenge',
    icon: BookOpen,
    description: 'Marine monitoring challenges and ESONS foundation'
  },
  {
    href: '/approach',
    label: 'Our Approach',
    icon: BarChart3,
    description: 'Acoustic indices methodology and study design'
  },
  {
    href: '/findings',
    label: 'Key Findings',
    icon: Compass,
    description: 'Results and community-level screening validation'
  },
  {
    href: '/analysis',
    label: 'Deep Dive',
    icon: FlaskConical,
    description: 'Technical methods, notebooks, and future directions'
  },
];

export default function Navigation() {
  const pathname = usePathname();

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
            <div className="hidden lg:block">
              <h1 className="font-medium text-lg">Marine Acoustic Indices Dashboard</h1>
            </div>
          </Link>

          {/* Navigation Links */}
          <div className="flex items-center space-x-0.5">
            {navItems.map((item) => {
              // Check if current path matches this section (exact match or starts with the section path)
              const isActive = pathname === item.href || (item.href !== '/' && pathname.startsWith(item.href + '/'));
              const Icon = item.icon;
              
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className="relative group"
                >
                  <motion.div
                    className={`flex items-center gap-2 px-2 md:px-4 py-2 rounded-lg transition-colors ${
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
                  <div className="absolute top-full left-1/2 transform -translate-x-1/2 mt-2 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none md:hidden z-50">
                    <div className="bg-popover text-popover-foreground text-xs px-2 py-1 rounded border shadow-lg whitespace-nowrap">
                      {item.label}
                      <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-4 border-r-4 border-b-4 border-l-transparent border-r-transparent border-b-popover"></div>
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