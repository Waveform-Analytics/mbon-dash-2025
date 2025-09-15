'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

interface NavLink {
  href: string;
  label: string;
}

interface PageNavigationProps {
  links: NavLink[];
}

export default function PageNavigation({ links }: PageNavigationProps) {
  const pathname = usePathname();

  return (
    <nav className="flex items-center space-x-4">
      {links.map((link) => {
        const isActive = pathname === link.href;
        return (
          <Link
            key={link.href}
            href={link.href}
            className={`px-4 py-2 text-sm font-medium transition-colors ${
              isActive
                ? 'text-primary border-b-2 border-primary'
                : 'text-gray-700 hover:text-primary'
            }`}
          >
            {link.label}
          </Link>
        );
      })}
    </nav>
  );
}