import type { UserProfile } from '../types/auth';
import { apiFetch } from './api';

const AUTH_URL = '/api/v1/auth';

export async function loginWithCredentials(
  username: string,
  password: string,
): Promise<{ message: string; redirect?: string }> {
  const response = await apiFetch(`${AUTH_URL}/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  });
  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.detail || 'Invalid username or password');
  }
  return response.json();
}

export async function registerUser(data: {
  email: string;
  username: string;
  password: string;
  first_name: string;
  last_name: string;
}): Promise<{ message: string }> {
  const response = await apiFetch(`${AUTH_URL}/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.detail || 'Registration failed');
  }
  return response.json();
}

export async function initiateLogin(_rememberMe: boolean = false): Promise<string> {
  return '/login';
}

export async function handleCallback(code: string, state: string): Promise<void> {
  const response = await apiFetch(`${AUTH_URL}/callback?code=${code}&state=${state}`, {
    method: 'POST',
  });
  if (!response.ok) throw new Error('Authentication callback failed');
}

export async function fetchCurrentUser(): Promise<UserProfile> {
  const response = await apiFetch(`${AUTH_URL}/me`);
  if (!response.ok) throw new Error('Not authenticated');
  return response.json() as Promise<UserProfile>;
}

export async function logout(): Promise<void> {
  await apiFetch(`${AUTH_URL}/logout`, { method: 'POST' });
}

export function getKeycloakPasswordResetUrl(): string {
  const keycloakUrl = import.meta.env.VITE_KEYCLOAK_URL || 'http://localhost:8080';
  const realm = import.meta.env.VITE_KEYCLOAK_REALM || 'helio';
  return `${keycloakUrl}/realms/${realm}/login-actions/reset-credentials`;
}

export function getKeycloakRegistrationUrl(): string {
  return '/signup';
}
