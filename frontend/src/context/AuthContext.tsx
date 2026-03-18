import React, { createContext, useCallback, useContext, useEffect, useState } from 'react';
import type { AuthState, UserProfile } from '../types/auth';
import { fetchCurrentUser, logout as logoutService } from '../services/authService';

interface AuthContextValue extends AuthState {
  login: () => void;
  logout: () => Promise<void>;
  setUser: (user: UserProfile) => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<AuthState>({
    isAuthenticated: false,
    user: null,
    isLoading: true,
  });

  useEffect(() => {
    // Dev mode: auto-authenticate with mock user
    const devMode = import.meta.env.VITE_AUTH_MODE === 'dev';
    if (devMode) {
      setState({
        isAuthenticated: true,
        user: {
          id: 'a0000000-0000-0000-0000-000000000001',
          email: 'admin@helio.local',
          name: 'Alex Rivera',
          roles: ['admin'],
        },
        isLoading: false,
      });
      return;
    }

    fetchCurrentUser()
      .then((user) => {
        setState({ isAuthenticated: true, user, isLoading: false });
      })
      .catch(() => {
        setState({ isAuthenticated: false, user: null, isLoading: false });
      });
  }, []);

  const login = useCallback(() => {
    window.location.href = '/login';
  }, []);

  const logout = useCallback(async () => {
    await logoutService();
    setState({ isAuthenticated: false, user: null, isLoading: false });
  }, []);

  const setUser = useCallback((user: UserProfile) => {
    setState({ isAuthenticated: true, user, isLoading: false });
  }, []);

  return (
    <AuthContext.Provider value={{ ...state, login, logout, setUser }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
