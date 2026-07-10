import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import Footer from '../components/Footer';
import api from '../services/api';
import { BoltIcon, EyeIcon, EyeSlashIcon } from '@heroicons/react/24/outline';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [markingAttendance, setMarkingAttendance] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  
  const { login } = useAuth();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const gymParam = searchParams.get('gym');

  // Ensure fields are always empty when component mounts
  useEffect(() => {
    setEmail('');
    setPassword('');
    setError('');
  }, []);

  const markAttendance = async (qrCode) => {
    setMarkingAttendance(true);
    try {
      // Send the full URL since QR now encodes a URL
      const frontendUrl = window.location.origin;
      const fullQrUrl = `${frontendUrl}/login?gym=${qrCode}`;
      const response = await api.post('/api/attendance/qr-checkin', { qr_code: fullQrUrl });
      return { success: true, data: response.data };
    } catch (err) {
      console.error('Attendance marking failed:', err);
      return { 
        success: false, 
        error: err.response?.data?.error || 'Failed to mark attendance' 
      };
    } finally {
      setMarkingAttendance(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email || !password) {
      setError('Please fill in all fields.');
      return;
    }

    setError('');
    setLoading(true);

    try {
      const response = await api.post('/api/auth/login', { email, password });
      const { token, user } = response.data;
      
      // Store authentication data
      login(token, user);
      
      // Role-based redirection
      if (user.role === 'super_admin') {
        navigate('/admin/dashboard');
      } else if (user.role === 'gym_owner') {
        navigate('/dashboard');
      } else if (user.role === 'member') {
        // Mark attendance automatically if gym param exists
        if (gymParam) {
          const attendanceResult = await markAttendance(gymParam);
          
          if (attendanceResult.success) {
            // Navigate to dashboard with success message
            navigate('/member/dashboard', { 
              state: { 
                attendanceSuccess: true,
                attendanceData: attendanceResult.data.attendance 
              } 
            });
          } else {
            // Navigate to dashboard with error message
            navigate('/member/dashboard', { 
              state: { 
                attendanceError: attendanceResult.error 
              } 
            });
          }
        } else {
          navigate('/member/dashboard');
        }
      } else {
        // Fallback for unknown roles
        navigate('/dashboard');
      }
    } catch (err) {
      console.error(err);
      // Improved error handling to differentiate between error types
      if (err.response) {
        // Server responded with error status
        const status = err.response.status;
        const serverError = err.response.data?.error;
        
        if (status === 401) {
          setError('Invalid email or password');
        } else if (status === 403) {
          setError(serverError || 'Account is disabled or suspended. Please contact support.');
        } else if (status === 404) {
          setError('Account not found');
        } else if (status === 500) {
          setError('Server error. Please try again later.');
        } else {
          setError(serverError || 'Login failed. Please try again.');
        }
      } else if (err.request) {
        // Request was made but no response received (network error)
        setError('Failed to connect. Please ensure your backend server and MySQL database are running.');
      } else {
        // Something else happened
        setError('An unexpected error occurred. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white min-h-screen flex items-center justify-center relative overflow-hidden px-4">
      {/* Background gradients */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[400px] h-[400px] bg-orange-100/30 rounded-full blur-[100px] pointer-events-none"></div>

      <div className="w-full max-w-md relative z-10">
        {/* Brand */}
        <div className="text-center mb-8">
          <Link to="/" className="inline-flex items-center gap-2 text-3xl font-extrabold text-gray-900">
            <BoltIcon className="w-10 h-10 text-orange-500" />
            <span className="text-orange-500">
              FlexiGym
            </span>
          </Link>
          <p className="text-gray-600 mt-2 text-sm">Log in to manage your gym tenant workspace</p>
        </div>

        {/* Card */}
        <div className="bg-white border border-gray-200 p-8 rounded-2xl shadow-xl">
          <h2 className="text-xl font-bold mb-6 text-gray-900 text-center">Welcome Back</h2>
          
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-600 text-xs p-4 rounded-xl mb-6">
              <span className="font-bold">Error:</span> {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5" autoComplete="off">
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-gray-600 mb-2">
                Email Address
              </label>
              <input
                type="email"
                required
                disabled={loading}
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Enter your email"
                autoComplete="off"
                autoCorrect="off"
                autoCapitalize="off"
                spellCheck="false"
                className="w-full bg-gray-50 border border-gray-200 focus:border-orange-400 focus:bg-white rounded-xl px-4 py-3 text-sm text-gray-900 placeholder-gray-500 focus:outline-none transition-all duration-200"
              />
            </div>

            <div>
              <div className="flex justify-between items-center mb-2">
                <label className="block text-xs font-semibold uppercase tracking-wider text-gray-600">
                  Password
                </label>
              </div>
              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  required
                  disabled={loading}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Enter your password"
                  autoComplete="off"
                  className="w-full bg-gray-50 border border-gray-200 focus:border-orange-400 focus:bg-white rounded-xl px-4 py-3 pr-12 text-sm text-gray-900 placeholder-gray-500 focus:outline-none transition-all duration-200"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  disabled={loading}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 focus:outline-none disabled:opacity-50 disabled:cursor-not-allowed z-10"
                  tabIndex={-1}
                >
                  {showPassword ? (
                    <EyeSlashIcon className="w-5 h-5" />
                  ) : (
                    <EyeIcon className="w-5 h-5" />
                  )}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-orange-500 hover:bg-orange-600 text-white font-bold py-3.5 px-4 rounded-xl transition-all duration-200 shadow-md disabled:opacity-50 disabled:cursor-not-allowed text-sm mt-2"
            >
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <svg className="animate-spin h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  Authenticating...
                </span>
              ) : (
                'Sign In'
              )}
            </button>
          </form>

          <div className="mt-8 text-center text-xs text-gray-500">
            Need a new tenant account?{' '}
            <Link to="/register" className="text-orange-500 hover:underline font-semibold">
              Register Gym & Owner
            </Link>
          </div>
        </div>
      </div>
      
      <Footer />
    </div>
  );
}
