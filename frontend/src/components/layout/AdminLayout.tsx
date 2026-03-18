import React, { useEffect, useState } from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Header } from './Header';

const STORAGE_KEY = 'sidebar_collapsed';

export function AdminLayout() {
  const [collapsed, setCollapsed] = useState(() => {
    return localStorage.getItem(STORAGE_KEY) === 'true';
  });

  useEffect(() => {
    const handleStorage = () => {
      setCollapsed(localStorage.getItem(STORAGE_KEY) === 'true');
    };
    window.addEventListener('storage', handleStorage);
    const interval = setInterval(() => {
      const val = localStorage.getItem(STORAGE_KEY) === 'true';
      if (val !== collapsed) setCollapsed(val);
    }, 200);
    return () => {
      window.removeEventListener('storage', handleStorage);
      clearInterval(interval);
    };
  }, [collapsed]);

  return (
    <div className="min-h-screen bg-content-bg font-montserrat">
      <Sidebar />
      <div
        className={`transition-all duration-300 ${
          collapsed ? 'ml-16' : 'ml-60'
        }`}
      >
        <Header />
        <main className="p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
