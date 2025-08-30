import React from 'react';
import { motion } from 'motion/react';
import { Map, FileText, TrendingUp, Waves } from 'lucide-react';
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarHeader,
} from './ui/sidebar';

interface AppSidebarProps {
  currentPage: string;
  setCurrentPage: (page: string) => void;
}

const menuItems = [
  {
    id: 'landing',
    title: 'Overview',
    icon: Map,
    description: 'Instruments & Deployment Schedule'
  },
  {
    id: 'data-types',
    title: 'Data Types',
    icon: FileText,
    description: 'Acoustic Indices & Methods'
  },
  {
    id: 'analysis',
    title: 'Analysis',
    icon: TrendingUp,
    description: 'Narrative Discovery'
  }
];

export function AppSidebar({ currentPage, setCurrentPage }: AppSidebarProps) {
  return (
    <Sidebar>
      <SidebarHeader className="p-4">
        <motion.div 
          className="flex items-center gap-2"
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5 }}
        >
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
          <div>
            <h2 className="font-semibold">May River Acoustics</h2>
            <p className="text-xs text-muted-foreground">Scientific Dashboard</p>
          </div>
        </motion.div>
      </SidebarHeader>
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel>Navigation</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {menuItems.map((item, index) => (
                <motion.div
                  key={item.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.3, delay: index * 0.1 }}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <SidebarMenuItem>
                    <SidebarMenuButton 
                      onClick={() => setCurrentPage(item.id)}
                      isActive={currentPage === item.id}
                      className="flex items-start gap-3 p-3 relative overflow-hidden group"
                    >
                      {/* Ripple effect background */}
                      <motion.div
                        className="absolute inset-0 bg-gradient-to-r from-teal-500/10 to-cyan-500/10 rounded-md"
                        initial={{ scale: 0, opacity: 0 }}
                        whileHover={{ scale: 1, opacity: 1 }}
                        transition={{ duration: 0.3 }}
                      />
                      
                      <motion.div
                        whileHover={{ rotate: 5, scale: 1.1 }}
                        transition={{ type: "spring", stiffness: 400, damping: 10 }}
                      >
                        <item.icon className="h-4 w-4 mt-0.5 flex-shrink-0 relative z-10" />
                      </motion.div>
                      <div className="flex flex-col relative z-10">
                        <span className="font-medium">{item.title}</span>
                        <span className="text-xs text-muted-foreground group-hover:text-teal-600 transition-colors">
                          {item.description}
                        </span>
                      </div>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                </motion.div>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
    </Sidebar>
  );
}