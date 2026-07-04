import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';

export default function RegisterPage() {
  const [gymName, setGymName] = useState('');
  const [gymAddress, setGymAddress] = useState('');
  const [gymPhone, setGymPhone] = useState('');
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!gymName || !gymAddress || !gymPhone || !name || !email || !password) {
      setError('Please fill in all fields.');
      return;
    }

    // Phone number validation
    const phoneRegex = /^[\+]?[\d\s\-\(\)]{10,}$/;
    if (!phoneRegex.test(gymPhone)) {
      setError('Please enter a valid phone number (minimum 10 digits).');
      return;
    }

    setError('');
    setLoading(true);

    try {
      const response = await api.post('/api/auth/register', {
        gym_name: gymName,
        gym_address: gymAddress,
        gym_phone: gymPhone,
        name,
        email,
        password
      });
      const { token, user } = response.data;
      
      login(token, user);
      navigate('/dashboard');
    } catch (err) {
      console.error(err);
      setError(
        err.response?.data?.error || 
        'Registration failed. Please verify MySQL database connectivity and try again.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-slate-950 min-h-screen flex items-center justify-center relative overflow-hidden px-4 py-12">
      {/* Background gradients */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[400px] h-[400px] bg-emerald-500/10 rounded-full blur-[100px] pointer-events-none"></div>

      <div className="w-full max-w-md relative z-10">
        {/* Brand */}
        <div className="text-center mb-8">
          <Link to="/" className="inline-flex items-center gap-2 text-3xl font-extrabold text-white">
            <span>🏋️‍♂️</span>
            <span className="bg-gradient-to-r from-emerald-400 to-teal-400 bg-clip-text text-transparent">
              FlexiGym
            </span>
          </Link>
          <p className="text-slate-400 mt-2 text-sm">Register a new gym tenant workspace</p>
        </div>

        {/* Card */}
        <div className="bg-slate-900/50 backdrop-blur-md border border-slate-850 p-8 rounded-2xl shadow-xl">
          <h2 className="text-xl font-bold mb-6 text-white text-center">Get Started</h2>
          
          {error && (
            <div className="bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs p-4 rounded-xl mb-6">
              <span className="font-bold">Error:</span> {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">
                Gym Name
              </label>
              <input
                type="text"
                required
                disabled={loading}
                value={gymName}
                onChange={(e) => setGymName(e.target.value)}
                placeholder="Elite Fitness Academy"
                className="w-full bg-slate-950 border border-slate-850 focus:border-emerald-500/40 rounded-xl px-4 py-3 text-sm text-slate-100 placeholder-slate-600 focus:outline-none transition-all duration-200"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">
                Gym Address
              </label>
              <textarea
                required
                disabled={loading}
                value={gymAddress}
                onChange={(e) => setGymAddress(e.target.value)}
                placeholder="123 Fitness Street, Health District, City, State, ZIP"
                rows="3"
                className="w-full bg-slate-950 border border-slate-850 focus:border-emerald-500/40 rounded-xl px-4 py-3 text-sm text-slate-100 placeholder-slate-600 focus:outline-none transition-all duration-200 resize-none"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">
                Gym Phone Number
              </label>
              <input
                type="tel"
                required
                disabled={loading}
                value={gymPhone}
                onChange={(e) => setGymPhone(e.target.value)}
                placeholder="+1 (555) 123-4567"
                className="w-full bg-slate-950 border border-slate-850 focus:border-emerald-500/40 rounded-xl px-4 py-3 text-sm text-slate-100 placeholder-slate-600 focus:outline-none transition-all duration-200"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">
                Owner's Name
              </label>
              <input
                type="text"
                required
                disabled={loading}
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Alex Mercer"
                className="w-full bg-slate-950 border border-slate-850 focus:border-emerald-500/40 rounded-xl px-4 py-3 text-sm text-slate-100 placeholder-slate-600 focus:outline-none transition-all duration-200"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">
                Email Address
              </label>
              <input
                type="email"
                required
                disabled={loading}
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="owner@yourgym.com"
                className="w-full bg-slate-950 border border-slate-850 focus:border-emerald-500/40 rounded-xl px-4 py-3 text-sm text-slate-100 placeholder-slate-600 focus:outline-none transition-all duration-200"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">
                Password
              </label>
              <input
                type="password"
                required
                disabled={loading}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full bg-slate-950 border border-slate-850 focus:border-emerald-500/40 rounded-xl px-4 py-3 text-sm text-slate-100 placeholder-slate-600 focus:outline-none transition-all duration-200"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-gradient-to-r from-emerald-400 to-teal-500 hover:from-emerald-500 hover:to-teal-600 text-slate-950 font-bold py-3.5 px-4 rounded-xl transition-all duration-200 shadow-md shadow-emerald-500/10 disabled:opacity-50 disabled:cursor-not-allowed text-sm mt-2"
            >
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <svg className="animate-spin h-4 w-4 text-slate-950" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  Registering Workspace...
                </span>
              ) : (
                'Register Gym & Owner'
              )}
            </button>
          </form>

          <div className="mt-8 text-center text-xs text-slate-500">
            Already have a tenant workspace?{' '}
            <Link to="/login" className="text-emerald-400 hover:underline font-semibold">
              Sign In
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
