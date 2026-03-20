import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import type { UserRole } from '../../types/auth';

interface RoleGuardProps {
  children: React.ReactNode;
  roles: UserRole[];
  fallback?: string;
}

export function RoleGuard({ children, roles, fallback = '/templates' }: RoleGuardProps) {
  const { user } = useAuth();

  const hasAccess = user?.roles.some((r) => roles.includes(r));

  if (!hasAccess) {
    return <Navigate to={fallback} replace />;
  }

  return <>{children}</>;
}
