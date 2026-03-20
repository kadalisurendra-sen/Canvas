import type {
  InviteUserRequest,
  InviteUserResponse,
  UpdateUserRequest,
  UserListResponse,
} from '../types/user';
import { apiFetch } from './api';

const API_BASE = '/api/v1/users';

export async function fetchUsers(params: {
  search?: string;
  role?: string;
  status?: string;
  page?: number;
  page_size?: number;
}): Promise<UserListResponse> {
  const query = new URLSearchParams();
  if (params.search) query.set('search', params.search);
  if (params.role) query.set('role', params.role);
  if (params.status) query.set('status', params.status);
  if (params.page) query.set('page', String(params.page));
  if (params.page_size) query.set('page_size', String(params.page_size));

  const response = await apiFetch(`${API_BASE}?${query.toString()}`);
  if (!response.ok) {
    throw new Error('Failed to fetch users');
  }
  return response.json() as Promise<UserListResponse>;
}

export async function inviteUser(
  data: InviteUserRequest
): Promise<InviteUserResponse> {
  const response = await apiFetch(`${API_BASE}/invite`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (response.status === 409) {
    throw new Error('User with this email already exists');
  }
  if (!response.ok) {
    throw new Error('Failed to invite user');
  }
  return response.json() as Promise<InviteUserResponse>;
}

export async function updateUser(
  userId: string,
  data: UpdateUserRequest
): Promise<void> {
  const response = await apiFetch(`${API_BASE}/${userId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!response.ok) {
    throw new Error('Failed to update user');
  }
}

export async function deactivateUser(userId: string): Promise<void> {
  const response = await apiFetch(`${API_BASE}/${userId}`, {
    method: 'DELETE',
  });
  if (response.status === 400) {
    throw new Error('Cannot deactivate yourself');
  }
  if (!response.ok) {
    throw new Error('Failed to deactivate user');
  }
}

export async function deleteUser(userId: string): Promise<void> {
  const response = await apiFetch(`${API_BASE}/${userId}/permanent`, {
    method: 'DELETE',
  });
  if (!response.ok) {
    throw new Error('Failed to delete user');
  }
}
