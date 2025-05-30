'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { 
  LayoutDashboard, 
  MousePointer, 
  Activity, 
  BarChart, 
  Users, 
  Settings, 
  LogOut 
} from 'lucide-react';

interface DashboardLayoutProps {
  children: React.ReactNode;
}

export default function DashboardLayout({ children }: DashboardLayoutProps) {
  const pathname = usePathname();
  
  const navItems = [
    { href: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { href: '/dashboard/sessions', label: 'Sessions', icon: Users },
    { href: '/dashboard/tracking', label: 'Tracking', icon: MousePointer },
    { href: '/dashboard/analytics', label: 'Analytics', icon: Activity },
    { href: '/dashboard/reports', label: 'Reports', icon: BarChart },
    { href: '/dashboard/settings', label: 'Settings', icon: Settings },
  ];
  
  return (
    <div className="flex h-screen bg-background">
      {/* Sidebar */}
      <div className="w-64 bg-card border-r border-border flex flex-col">
        <div className="p-4 border-b border-border">
          <Link href="/" className="flex items-center gap-2 font-bold text-xl">
            <MousePointer size={24} />
            <span>Mouse Tracker</span>
          </Link>
        </div>
        
        <nav className="flex-1 overflow-y-auto p-2">
          <ul className="space-y-1">
            {navItems.map((item) => {
              const isActive = pathname === item.href;
              const Icon = item.icon;
              
              return (
                <li key={item.href}>
                  <Link
                    href={item.href}
                    className={`flex items-center gap-3 px-3 py-2 rounded-md ${
                      isActive 
                        ? 'bg-primary text-primary-foreground' 
                        : 'hover:bg-secondary'
                    }`}
                  >
                    <Icon size={18} />
                    <span>{item.label}</span>
                  </Link>
                </li>
              );
            })}
          </ul>
        </nav>
        
        <div className="p-4 border-t border-border">
          <Link
            href="/auth/logout"
            className="flex items-center gap-3 px-3 py-2 rounded-md hover:bg-secondary w-full"
          >
            <LogOut size={18} />
            <span>Logout</span>
          </Link>
        </div>
      </div>
      
      {/* Main content */}
      <div className="flex-1 overflow-y-auto">
        {children}
      </div>
    </div>
  );
} 