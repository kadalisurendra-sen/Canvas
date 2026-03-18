export type UserRole = 'system_admin' | 'admin' | 'contributor' | 'viewer';

export interface UserProfile {
  user_id: string;
  email: string;
  name: string;
  roles: UserRole[];
  tenant_id: string;
}

export interface AuthState {
  isAuthenticated: boolean;
  user: UserProfile | null;
  isLoading: boolean;
}

export interface LoginCredentials {
  username: string;
  password: string;
  rememberMe: boolean;
}
