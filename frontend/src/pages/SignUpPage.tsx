import React, { useState, useEffect } from 'react';
import { useNavigate, Link, useSearchParams } from 'react-router-dom';
import { registerUser } from '../services/authService';
import { setTenantId, getTenantId } from '../services/api';

export function SignUpPage() {
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const tenantSlug = searchParams.get('tenant') || getTenantId();

  useEffect(() => {
    if (tenantSlug) {
      setTenantId(tenantSlug);
    }
  }, [tenantSlug]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (!email.trim() || !username.trim() || !password.trim()) {
      setError('Email, username, and password are required');
      return;
    }

    setIsSubmitting(true);
    try {
      const result = await registerUser({
        email, username, password, first_name: firstName, last_name: lastName,
      });
      setSuccess(result.message);
      setTimeout(() => navigate(tenantSlug ? `/login?tenant=${tenantSlug}` : '/login'), 2000);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Registration failed');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="flex min-h-screen font-montserrat">
      <div className="w-full lg:w-[45%] xl:w-[40%] flex flex-col relative">
        <div className="p-8">
          <Link to={tenantSlug ? `/login?tenant=${tenantSlug}` : '/login'} className="flex items-center gap-1 text-gray-800 font-semibold text-sm hover:opacity-70">
            <span className="material-symbols-outlined text-lg">chevron_left</span>
            Back
          </Link>
        </div>
        <div className="flex-1 flex items-center justify-center px-6 md:px-12 pb-12">
          <div className="w-full max-w-[500px] bg-white rounded-3xl p-8 md:p-14 shadow-sm border border-gray-100">
            <div className="text-center mb-10">
              <h1 className="text-3xl font-bold tracking-tight mb-4">SIGN UP</h1>
              <p className="text-gray-500 text-base max-w-xs mx-auto">
                Please enter your information to create your account
              </p>
            </div>

            {error && (
              <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-600 text-sm">
                {error}
              </div>
            )}
            {success && (
              <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded-lg text-green-600 text-sm">
                {success}
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-5">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-800 mb-2">First Name</label>
                  <input
                    type="text"
                    value={firstName}
                    onChange={(e) => setFirstName(e.target.value)}
                    placeholder="First name"
                    className="w-full h-12 px-4 border border-gray-200 rounded-md text-sm focus:outline-none focus:border-purple-600 focus:ring-1 focus:ring-purple-600"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-800 mb-2">Last Name</label>
                  <input
                    type="text"
                    value={lastName}
                    onChange={(e) => setLastName(e.target.value)}
                    placeholder="Last name"
                    className="w-full h-12 px-4 border border-gray-200 rounded-md text-sm focus:outline-none focus:border-purple-600 focus:ring-1 focus:ring-purple-600"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-800 mb-2">Username</label>
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="Choose a username"
                  className="w-full h-12 px-4 border border-gray-200 rounded-md text-sm focus:outline-none focus:border-purple-600 focus:ring-1 focus:ring-purple-600"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-800 mb-2">Email Address</label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="Enter your email"
                  className="w-full h-12 px-4 border border-gray-200 rounded-md text-sm focus:outline-none focus:border-purple-600 focus:ring-1 focus:ring-purple-600"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-800 mb-2">Password</label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Create a password"
                  className="w-full h-12 px-4 border border-gray-200 rounded-md text-sm focus:outline-none focus:border-purple-600 focus:ring-1 focus:ring-purple-600"
                  required
                />
              </div>
              <button
                type="submit"
                disabled={isSubmitting}
                className="w-full bg-[#00ffaa] hover:brightness-95 transition-all py-4 rounded-full text-gray-900 font-bold text-lg mt-2 shadow-sm disabled:opacity-50"
              >
                {isSubmitting ? 'Creating account...' : 'Sign Up'}
              </button>
            </form>

            <div className="text-center mt-10 text-sm">
              <span className="text-gray-500">Already have an account?</span>
              <Link to={tenantSlug ? `/login?tenant=${tenantSlug}` : '/login'} className="text-purple-700 font-bold ml-1 hover:underline">
                Login
              </Link>
            </div>
          </div>
        </div>
      </div>

      <div className="hidden lg:flex lg:w-[55%] xl:w-[60%] items-center justify-center p-12 text-white relative overflow-hidden" style={{ background: 'linear-gradient(180deg, #4029E7 0%, #2914BF 100%)' }}>
        <div className="absolute inset-0" style={{ background: 'linear-gradient(135deg, rgba(255,255,255,0.1) 0%, transparent 70%)', clipPath: 'ellipse(120% 60% at 100% 0%)' }} />
        <div className="absolute inset-0" style={{ background: 'linear-gradient(315deg, rgba(255,255,255,0.05) 0%, transparent 50%)', clipPath: 'ellipse(100% 50% at 0% 100%)' }} />
        <div className="relative z-10 w-full max-w-xl text-center">
          <div className="flex flex-col items-center mb-10">
            <span className="text-xl font-bold tracking-wide">virtusa</span>
            <span className="text-7xl font-bold tracking-tight">helio</span>
          </div>
          <p className="text-lg leading-relaxed font-medium px-8 opacity-95">
            The Virtusa Helio platform and solutions consist of a suite of agnostic agents and toolkits that are customizable to a client-approved ecosystem
          </p>
        </div>
      </div>
    </div>
  );
}
