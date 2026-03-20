export type UserRole = 'system_admin' | 'admin' | 'contributor' | 'viewer';
export type UserStatusType = 'active' | 'invited' | 'deactivated';

export interface User {
  id: string;
  name: string;
  email: string;
  role: UserRole;
  status: UserStatusType;
  last_login: string | null;
}

export interface UserListResponse {
  users: User[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
  active_count: number;
  deactivated_count: number;
}

export interface InviteUserRequest {
  email: string;
  role: UserRole;
  username: string;
  password: string;
  first_name: string;
  last_name: string;
}

export interface InviteUserResponse {
  id: string;
  email: string;
  role: UserRole;
  status: UserStatusType;
  message: string;
}

export interface UpdateUserRequest {
  role?: UserRole;
  status?: UserStatusType;
}
