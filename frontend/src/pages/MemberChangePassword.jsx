import React, { useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';
import { KeyIcon, CheckCircleIcon } from '@heroicons/react/24/outline';

export default function MemberChangePassword() {
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [markingAttendance, setMarkingAttendance] = useState(false);
  
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const gymParam = searchParams.get('gym');

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
    
    // For first-time setup, only require new password
    if (!newPassword || !confirmPassword) {
      setError('Please fill in all required fields.');
      return;
    }

    if (newPassword.length < 6) {
      setError('New password must be at least 6 characters long.');
      return;
    }

    if (newPassword !== confirmPassword) {
      setError('New passwords do not match.');
      return;
    }

    setLoading(true);
    setError('');

    try {
      // Update member password directly (member is already authenticated)
      await api.put(`/api/members/${user.member_id}`, {
        password: newPassword
      });

      // After password change, mark attendance if gym param exists
      if (gymParam) {
        const attendanceResult = await markAttendance(gymParam);
        
        if (attendanceResult.success) {
          navigate('/member/dashboard', { 
            state: { 
              attendanceSuccess: true,
              attendanceData: attendanceResult.data.attendance 
            } 
          });
        } else {
          navigate('/member/dashboard', { 
            state: { 
              attendanceError: attendanceResult.error 
            } 
          });
        }
      } else {
        navigate('/member/dashboard');
      }
    } catch (err) {
      console.error(err);
      if (err.response?.status === 401) {
        setError('Current password is incorrect.');
      } else {
        setError(err.response?.data?.error || 'Failed to change password. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center py-12 px-4">
      <div className="max-w-md w-full">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="mx-auto w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center mb-4">
            <KeyIcon className="w-6 h-6 text-orange-600" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Create Your Password</h1>
          <p className="text-gray-600 text-sm">
            Welcome to your member account! Please create a secure password to continue.
          </p>
        </div>

        {/* Form Card */}
        <div className="bg-white border border-gray-200 p-6 rounded-2xl shadow-sm">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 text-sm p-4 rounded-xl mb-6">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-gray-600 mb-2">
                New Password *
              </label>
              <input
                type="password"
                required
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                placeholder="Enter new password (minimum 6 characters)"
                className="w-full bg-gray-50 border border-gray-200 focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 rounded-xl px-4 py-3 text-sm text-gray-900 focus:outline-none transition-all duration-200"
                disabled={loading}
              />
            </div>

            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-gray-600 mb-2">
                Confirm New Password *
              </label>
              <input
                type="password"
                required
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="Confirm your new password"
                className="w-full bg-gray-50 border border-gray-200 focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 rounded-xl px-4 py-3 text-sm text-gray-900 focus:outline-none transition-all duration-200"
                disabled={loading}
              />
            </div>

            <div className="space-y-3 pt-4">
              <button
                type="submit"
                disabled={loading}
                className="w-full bg-orange-600 hover:bg-orange-700 text-white font-bold py-3 px-6 rounded-xl transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {loading ? (
                  <span className="flex items-center gap-2">
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    Changing Password...
                  </span>
                ) : (
                  <>
                    <CheckCircleIcon className="w-4 h-4" />
                    Change Password
                  </>
                )}
              </button>

            </div>
          </form>

          <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-xl">
            <h3 className="text-sm font-semibold text-blue-900 mb-2">Security Tips</h3>
            <ul className="text-xs text-blue-800 space-y-1">
              <li>• Use at least 6 characters</li>
              <li>• Include letters and numbers</li>
              <li>• Don't use common words or personal information</li>
              <li>• Keep your password secure and private</li>
            </ul>
          </div>
        </div>

        {/* Member Info */}
        <div className="mt-6 text-center text-xs text-gray-500">
          Logged in as: {user?.email} at {user?.gym_name}
        </div>
      </div>
    </div>
  );
}