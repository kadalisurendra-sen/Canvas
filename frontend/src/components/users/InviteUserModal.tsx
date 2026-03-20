import React, { useState } from 'react';
import type { UserRole } from '../../types/user';
import { inviteUser } from '../../services/userService';

interface InviteUserModalProps {
  onClose: () => void;
  onSuccess: () => void;
}

export function InviteUserModal({ onClose, onSuccess }: InviteUserModalProps) {
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState<UserRole>('viewer');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const isValidEmail = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  const isValid =
    isValidEmail &&
    username.trim().length >= 3 &&
    firstName.trim().length >= 1 &&
    lastName.trim().length >= 1 &&
    password.trim().length >= 6;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!isValid) {
      if (!isValidEmail) setError('Please enter a valid email address');
      else if (username.trim().length < 3) setError('Username must be at least 3 characters');
      else if (!firstName.trim()) setError('First name is required');
      else if (!lastName.trim()) setError('Last name is required');
      else if (password.trim().length < 6) setError('Password must be at least 6 characters');
      return;
    }
    setLoading(true);
    setError('');
    try {
      await inviteUser({ email, role, username, password, first_name: firstName, last_name: lastName });
      onSuccess();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to send invite');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-md mx-4 p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-bold text-slate-900">Invite User</h3>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600">
            <span className="material-symbols-outlined">close</span>
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                First Name <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                className="w-full px-4 py-2 border border-slate-200 rounded-lg text-sm focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none"
                placeholder="John"
                value={firstName}
                onChange={(e) => setFirstName(e.target.value)}
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Last Name <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                className="w-full px-4 py-2 border border-slate-200 rounded-lg text-sm focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none"
                placeholder="Doe"
                value={lastName}
                onChange={(e) => setLastName(e.target.value)}
                required
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Email Address <span className="text-red-500">*</span>
            </label>
            <input
              type="email"
              className="w-full px-4 py-2 border border-slate-200 rounded-lg text-sm focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none"
              placeholder="user@company.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Username <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              className="w-full px-4 py-2 border border-slate-200 rounded-lg text-sm focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none"
              placeholder="Choose a username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              minLength={3}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Password <span className="text-red-500">*</span>
            </label>
            <input
              type="password"
              className="w-full px-4 py-2 border border-slate-200 rounded-lg text-sm focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none"
              placeholder="Set initial password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={6}
            />
            <p className="text-xs text-slate-400 mt-1">Minimum 6 characters</p>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Role
            </label>
            <select
              className="w-full px-4 py-2 border border-slate-200 rounded-lg text-sm focus:ring-primary focus:border-primary"
              value={role}
              onChange={(e) => setRole(e.target.value as UserRole)}
            >
              <option value="admin">Admin</option>
              <option value="contributor">Contributor</option>
              <option value="viewer">Viewer</option>
            </select>
          </div>

          {error && (
            <p className="text-sm text-red-600 bg-red-50 px-3 py-2 rounded-lg">
              {error}
            </p>
          )}

          <div className="flex justify-end gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-slate-600 hover:text-slate-800 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading || !isValid}
              className="px-5 py-2 bg-primary text-white text-sm font-bold rounded-lg hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center gap-2"
            >
              {loading && (
                <span className="material-symbols-outlined text-sm animate-spin">progress_activity</span>
              )}
              Create User
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
