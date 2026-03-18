import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { handleCallback, fetchCurrentUser } from '../services/authService';

export function CallbackPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { setUser } = useAuth();
  const [error, setError] = useState('');

  useEffect(() => {
    const code = searchParams.get('code');
    const state = searchParams.get('state');

    if (!code || !state) {
      setError('Missing authentication parameters');
      return;
    }

    handleCallback(code, state)
      .then(() => fetchCurrentUser())
      .then((user) => {
        setUser(user);
        navigate('/templates', { replace: true });
      })
      .catch(() => {
        setError('Authentication failed. Please try again.');
      });
  }, [searchParams, navigate, setUser]);

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-content-bg font-montserrat">
        <div className="bg-white rounded-xl shadow-sm p-8 text-center">
          <span className="material-symbols-outlined text-4xl text-red-500 mb-4">error</span>
          <p className="text-red-600 mb-4">{error}</p>
          <a href="/login" className="text-primary hover:text-primary-600 font-medium">
            Return to Login
          </a>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-content-bg font-montserrat">
      <div className="text-center">
        <div className="animate-spin w-8 h-8 border-3 border-primary border-t-transparent rounded-full mx-auto mb-4" />
        <p className="text-gray-500 text-sm">Completing authentication...</p>
      </div>
    </div>
  );
}
