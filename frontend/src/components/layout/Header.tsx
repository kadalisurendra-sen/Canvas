import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

const ROUTE_TITLES: Record<string, string> = {
  '/templates': 'Template Management',
  '/users': 'User Management',
  '/settings': 'Tenant Settings',
  '/analytics': 'Analytics & Audit Logs',
  '/master-data': 'Master Data Management',
};

function getBreadcrumb(pathname: string): string {
  for (const [route, title] of Object.entries(ROUTE_TITLES)) {
    if (pathname.startsWith(route)) {
      return title;
    }
  }
  return 'Dashboard';
}

export function Header() {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [dropdownOpen, setDropdownOpen] = useState(false);

  const pageTitle = getBreadcrumb(location.pathname);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <header className="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-6">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2">
        <span className="text-gray-400 text-sm">Home</span>
        <span className="text-gray-300">/</span>
        <span className="text-gray-800 text-sm font-semibold">{pageTitle}</span>
      </div>

      {/* Right section */}
      <div className="flex items-center gap-4">
        {/* Notification bell */}
        <button
          className="relative p-2 text-gray-500 hover:text-gray-700 transition-colors"
          aria-label="Notifications"
        >
          <span className="material-symbols-outlined text-xl">notifications</span>
        </button>

        {/* User dropdown */}
        <div className="relative">
          <button
            onClick={() => setDropdownOpen(!dropdownOpen)}
            className="flex items-center gap-2 p-1 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center">
              <span className="text-white text-xs font-semibold">
                {user?.name ? user.name.charAt(0).toUpperCase() : 'U'}
              </span>
            </div>
            <span className="material-symbols-outlined text-gray-500 text-sm">
              expand_more
            </span>
          </button>

          {dropdownOpen && (
            <div className="absolute right-0 top-12 w-48 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-50">
              <div className="px-4 py-2 border-b border-gray-100">
                <p className="text-sm font-medium text-gray-800">{user?.name || 'User'}</p>
                <p className="text-xs text-gray-500">{user?.email || ''}</p>
              </div>
              <button
                onClick={() => { setDropdownOpen(false); }}
                className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
              >
                Profile
              </button>
              <button
                onClick={handleLogout}
                className="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50"
              >
                Logout
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
