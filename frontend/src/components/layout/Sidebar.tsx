import React, { useEffect, useState } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import type { UserRole } from '../../types/auth';

interface NavItem {
  path: string;
  label: string;
  icon: string;
  roles: UserRole[]; // which roles can see this item
}

const NAV_ITEMS: NavItem[] = [
  {
    path: '/templates',
    label: 'Template Management',
    icon: 'layers',
    roles: ['system_admin', 'admin', 'contributor', 'viewer'],
  },
  {
    path: '/users',
    label: 'User Management',
    icon: 'group',
    roles: ['system_admin', 'admin'],
  },
  {
    path: '/settings',
    label: 'Tenant Settings',
    icon: 'settings',
    roles: ['system_admin', 'admin'],
  },
  {
    path: '/analytics',
    label: 'Analytics & Audit Logs',
    icon: 'analytics',
    roles: ['system_admin', 'admin'],
  },
  {
    path: '/master-data',
    label: 'Master Data Management',
    icon: 'database',
    roles: ['system_admin', 'admin'],
  },
];

const STORAGE_KEY = 'sidebar_collapsed';

function getRoleBadgeColor(role: string): string {
  switch (role) {
    case 'system_admin': return 'bg-primary-500';
    case 'admin': return 'bg-accent-500 text-gray-900';
    case 'contributor': return 'bg-blue-500';
    case 'viewer': return 'bg-gray-500';
    default: return 'bg-gray-500';
  }
}

function getRoleLabel(role: string): string {
  switch (role) {
    case 'system_admin': return 'System Admin';
    case 'admin': return 'Admin';
    case 'contributor': return 'Contributor';
    case 'viewer': return 'Viewer';
    default: return role;
  }
}

export function Sidebar() {
  const [collapsed, setCollapsed] = useState(() => {
    return localStorage.getItem(STORAGE_KEY) === 'true';
  });
  const { user } = useAuth();
  const location = useLocation();

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, String(collapsed));
  }, [collapsed]);

  const primaryRole = user?.roles[0] || 'viewer';
  const userRoles = user?.roles || [];

  // Filter nav items by user's roles
  const visibleItems = NAV_ITEMS.filter((item) =>
    item.roles.some((r) => userRoles.includes(r))
  );

  return (
    <aside
      className={`fixed left-0 top-0 h-screen bg-sidebar flex flex-col transition-all duration-300 z-50 ${
        collapsed ? 'w-16' : 'w-60'
      }`}
    >
      {/* Logo */}
      <div className="flex items-center gap-3 px-4 py-5 border-b border-white/10">
        <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center flex-shrink-0">
          <span className="text-white font-bold text-sm">HC</span>
        </div>
        {!collapsed && (
          <span className="text-white font-semibold text-sm whitespace-nowrap">
            Helio Canvas 2.0
          </span>
        )}
      </div>

      {/* Toggle */}
      <button
        onClick={() => setCollapsed(!collapsed)}
        className="flex items-center justify-center py-2 text-sidebar-text hover:text-white transition-colors"
        aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
      >
        <span className="material-symbols-outlined text-xl">
          {collapsed ? 'chevron_right' : 'chevron_left'}
        </span>
      </button>

      {/* Navigation */}
      <nav className="flex-1 py-2 overflow-y-auto">
        {visibleItems.map((item) => {
          const isActive = location.pathname.startsWith(item.path);
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={`flex items-center gap-3 px-4 py-3 mx-2 rounded-lg transition-colors ${
                isActive
                  ? 'text-white bg-white/10 border-l-3 border-accent'
                  : 'text-sidebar-text hover:text-white hover:bg-white/5'
              }`}
              title={collapsed ? item.label : undefined}
            >
              <span className="material-symbols-outlined text-xl flex-shrink-0">
                {item.icon}
              </span>
              {!collapsed && (
                <span className="text-sm font-medium truncate">{item.label}</span>
              )}
            </NavLink>
          );
        })}
      </nav>

      {/* User Profile */}
      <div className="border-t border-white/10 px-4 py-4">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-primary-400 flex items-center justify-center flex-shrink-0">
            <span className="text-white text-xs font-semibold">
              {user?.name ? user.name.charAt(0).toUpperCase() : 'U'}
            </span>
          </div>
          {!collapsed && (
            <div className="min-w-0">
              <p className="text-white text-sm font-medium truncate">
                {user?.name || 'User'}
              </p>
              <span
                className={`inline-block px-2 py-0.5 rounded-full text-xs text-white ${getRoleBadgeColor(primaryRole)}`}
              >
                {getRoleLabel(primaryRole)}
              </span>
            </div>
          )}
        </div>
      </div>
    </aside>
  );
}
