import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  getKeycloakPasswordResetUrl,
  loginWithCredentials,
  fetchCurrentUser,
} from '../services/authService';
import { getTenantId, setTenantId } from '../services/api';

interface FormErrors {
  username?: string;
  password?: string;
}

export function LoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);
  const [errors, setErrors] = useState<FormErrors>({});
  const [authError, setAuthError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [tenantName, setTenantName] = useState('');
  const [tenantSlug, setTenantSlug] = useState('');
  const [orgCode, setOrgCode] = useState('');
  const [orgError, setOrgError] = useState('');
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { isAuthenticated, setUser } = useAuth();

  useEffect(() => {
    const tenantParam = searchParams.get('tenant');
    const existingTenant = getTenantId();
    const slug = tenantParam || existingTenant;

    if (slug) {
      setTenantSlug(slug);
      setTenantId(slug);
      // Resolve tenant name for display
      fetch(`/api/v1/tenants/resolve?slug=${slug}`)
        .then((r) => { if (r.ok) return r.json(); throw new Error(); })
        .then((data) => setTenantName(data.name))
        .catch(() => setTenantName(''));
    }
  }, [searchParams]);

  if (isAuthenticated) {
    navigate('/templates', { replace: true });
    return null;
  }

  const validate = (): boolean => {
    const newErrors: FormErrors = {};
    if (!username.trim()) newErrors.username = 'Username is required';
    if (!password.trim()) newErrors.password = 'Password is required';
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleOrgSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!orgCode.trim()) {
      setOrgError('Organization code is required');
      return;
    }
    setOrgError('');
    // Resolve and redirect with tenant param
    fetch(`/api/v1/tenants/resolve?slug=${orgCode.trim().toLowerCase()}`)
      .then((r) => {
        if (!r.ok) throw new Error('Organization not found');
        return r.json();
      })
      .then((data) => {
        setTenantId(data.slug);
        setTenantSlug(data.slug);
        setTenantName(data.name);
      })
      .catch(() => {
        setOrgError('Organization not found. Please check your code.');
      });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setAuthError('');
    if (!validate()) return;

    setIsSubmitting(true);
    try {
      await loginWithCredentials(username, password);
      const user = await fetchCurrentUser();
      setUser(user);
      navigate('/templates', { replace: true });
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Login failed';
      setAuthError(msg);
    } finally {
      setIsSubmitting(false);
    }
  };

  // No tenant resolved yet — show org code input
  if (!tenantSlug) {
    return (
      <div className="min-h-screen flex font-montserrat">
        <LeftPanel />
        <div className="w-full lg:w-1/2 flex flex-col items-center justify-center bg-content-bg px-6">
          <div className="w-full max-w-md">
            <div className="bg-white rounded-xl shadow-sm p-8">
              <div className="text-center mb-8">
                <div className="w-12 h-12 rounded-xl bg-primary flex items-center justify-center mx-auto mb-4">
                  <span className="text-white font-bold text-lg">HC</span>
                </div>
                <h2 className="text-2xl font-bold text-gray-800">Welcome</h2>
                <p className="text-gray-500 text-sm mt-1">Enter your organization code to continue</p>
              </div>

              {orgError && (
                <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-600 text-sm">
                  {orgError}
                </div>
              )}

              <form onSubmit={handleOrgSubmit} noValidate>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-1">Organization Code</label>
                  <div className="relative">
                    <span className="absolute left-3 top-1/2 -translate-y-1/2 material-symbols-outlined text-gray-400 text-lg">
                      business
                    </span>
                    <input
                      type="text"
                      value={orgCode}
                      onChange={(e) => setOrgCode(e.target.value)}
                      placeholder="e.g. acme"
                      className="w-full h-10 pl-10 pr-3 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
                    />
                  </div>
                </div>
                <button
                  type="submit"
                  className="w-full h-10 bg-primary hover:bg-primary-600 text-white font-semibold rounded-lg transition-colors"
                >
                  Continue
                </button>
              </form>
            </div>
            <Footer />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex font-montserrat">
      <LeftPanel />
      <RightPanel
        username={username}
        password={password}
        showPassword={showPassword}
        rememberMe={rememberMe}
        errors={errors}
        authError={authError}
        isSubmitting={isSubmitting}
        tenantName={tenantName}
        tenantSlug={tenantSlug}
        onUsernameChange={setUsername}
        onPasswordChange={setPassword}
        onShowPasswordToggle={() => setShowPassword(!showPassword)}
        onRememberMeChange={setRememberMe}
        onSubmit={handleSubmit}
      />
    </div>
  );
}

function LeftPanel() {
  return (
    <div className="hidden lg:flex lg:w-1/2 relative overflow-hidden bg-gradient-to-br from-blue-900 via-purple-800 to-indigo-900">
      <svg
        className="absolute inset-0 w-full h-full"
        viewBox="0 0 800 900"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        preserveAspectRatio="none"
      >
        <path
          d="M0 0 Q400 200 800 100 L800 900 Q400 700 0 800 Z"
          fill="rgba(255,255,255,0.03)"
        />
        <path
          d="M0 200 Q400 400 800 300 L800 600 Q400 500 0 600 Z"
          fill="rgba(255,255,255,0.02)"
        />
        <circle cx="200" cy="300" r="150" fill="rgba(95,44,255,0.15)" />
        <circle cx="600" cy="600" r="200" fill="rgba(2,245,118,0.08)" />
      </svg>
      <div className="relative z-10 flex flex-col items-center justify-center w-full px-12">
        <div className="w-16 h-16 rounded-2xl bg-primary flex items-center justify-center mb-6">
          <span className="text-white font-bold text-2xl">HC</span>
        </div>
        <h1 className="text-white text-3xl font-bold mb-3">Helio Canvas 2.0</h1>
        <p className="text-white/60 text-center text-sm max-w-sm">
          Multi-tenant evaluation template management platform
        </p>
      </div>
    </div>
  );
}

interface RightPanelProps {
  username: string;
  password: string;
  showPassword: boolean;
  rememberMe: boolean;
  errors: FormErrors;
  authError: string;
  isSubmitting: boolean;
  tenantName: string;
  tenantSlug: string;
  onUsernameChange: (v: string) => void;
  onPasswordChange: (v: string) => void;
  onShowPasswordToggle: () => void;
  onRememberMeChange: (v: boolean) => void;
  onSubmit: (e: React.FormEvent) => void;
}

function RightPanel(props: RightPanelProps) {
  return (
    <div className="w-full lg:w-1/2 flex flex-col items-center justify-center bg-content-bg px-6">
      <div className="w-full max-w-md">
        <LoginForm {...props} />
        <Footer />
      </div>
    </div>
  );
}

function LoginForm(props: RightPanelProps) {
  return (
    <div className="bg-white rounded-xl shadow-sm p-8">
      <div className="text-center mb-8">
        <div className="w-12 h-12 rounded-xl bg-primary flex items-center justify-center mx-auto mb-4 lg:hidden">
          <span className="text-white font-bold text-lg">HC</span>
        </div>
        <h2 className="text-2xl font-bold text-gray-800">Sign In</h2>
        <p className="text-gray-500 text-sm mt-1">
          {props.tenantName
            ? `Welcome to ${props.tenantName}`
            : 'Welcome back to Helio Canvas'}
        </p>
      </div>

      {props.authError && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-600 text-sm">
          {props.authError}
        </div>
      )}

      <form onSubmit={props.onSubmit} noValidate>
        <InputField
          label="Username"
          type="text"
          value={props.username}
          onChange={props.onUsernameChange}
          error={props.errors.username}
          placeholder="Enter your username"
          icon="person"
        />
        <PasswordField
          value={props.password}
          onChange={props.onPasswordChange}
          showPassword={props.showPassword}
          onToggle={props.onShowPasswordToggle}
          error={props.errors.password}
        />

        <div className="flex items-center justify-between mb-6">
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={props.rememberMe}
              onChange={(e) => props.onRememberMeChange(e.target.checked)}
              className="w-4 h-4 rounded border-gray-300 text-primary focus:ring-primary"
            />
            <span className="text-sm text-gray-600">Remember me</span>
          </label>
          <a
            href={getKeycloakPasswordResetUrl()}
            className="text-sm text-primary hover:text-primary-600 font-medium"
          >
            Forgot Password?
          </a>
        </div>

        <button
          type="submit"
          disabled={props.isSubmitting}
          className="w-full h-10 bg-primary hover:bg-primary-600 text-white font-semibold rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {props.isSubmitting ? 'Signing in...' : 'Sign In'}
        </button>
      </form>

      <p className="text-center text-sm text-gray-500 mt-6">
        Don&apos;t have an account?{' '}
        <a
          href={`/signup?tenant=${props.tenantSlug}`}
          className="text-primary hover:text-primary-600 font-medium"
        >
          Register
        </a>
      </p>
    </div>
  );
}

interface InputFieldProps {
  label: string;
  type: string;
  value: string;
  onChange: (v: string) => void;
  error?: string;
  placeholder: string;
  icon: string;
}

function InputField({ label, type, value, onChange, error, placeholder, icon }: InputFieldProps) {
  return (
    <div className="mb-4">
      <label className="block text-sm font-medium text-gray-700 mb-1">{label}</label>
      <div className="relative">
        <span className="absolute left-3 top-1/2 -translate-y-1/2 material-symbols-outlined text-gray-400 text-lg">
          {icon}
        </span>
        <input
          type={type}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          className={`w-full h-10 pl-10 pr-3 border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 ${
            error ? 'border-red-300' : 'border-gray-300'
          }`}
        />
      </div>
      {error && <p className="text-red-500 text-xs mt-1">{error}</p>}
    </div>
  );
}

interface PasswordFieldProps {
  value: string;
  onChange: (v: string) => void;
  showPassword: boolean;
  onToggle: () => void;
  error?: string;
}

function PasswordField({ value, onChange, showPassword, onToggle, error }: PasswordFieldProps) {
  return (
    <div className="mb-4">
      <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
      <div className="relative">
        <span className="absolute left-3 top-1/2 -translate-y-1/2 material-symbols-outlined text-gray-400 text-lg">
          lock
        </span>
        <input
          type={showPassword ? 'text' : 'password'}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder="Enter your password"
          className={`w-full h-10 pl-10 pr-10 border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 ${
            error ? 'border-red-300' : 'border-gray-300'
          }`}
        />
        <button
          type="button"
          onClick={onToggle}
          className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
          aria-label={showPassword ? 'Hide password' : 'Show password'}
        >
          <span className="material-symbols-outlined text-lg">
            {showPassword ? 'visibility_off' : 'visibility'}
          </span>
        </button>
      </div>
      {error && <p className="text-red-500 text-xs mt-1">{error}</p>}
    </div>
  );
}

function Footer() {
  return (
    <div className="flex items-center justify-between mt-8 text-xs text-gray-400">
      <span>virtusa</span>
      <span>helio</span>
    </div>
  );
}
