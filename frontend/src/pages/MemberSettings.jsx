import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';
import { Cog6ToothIcon, ArrowLeftIcon } from '@heroicons/react/24/outline';

export default function MemberSettings() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);

  const handleLogout = () => {
    // Navigate to login page
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-3xl mx-auto">
        {/* Back Button */}
        <button
          onClick={() => navigate('/member/dashboard')}
          className="mb-4 flex items-center gap-2 text-gray-600 hover:text-gray-900 transition-colors"
        >
          <ArrowLeftIcon className="w-5 h-5" />
          <span className="text-sm font-medium">Back to Dashboard</span>
        </button>

        {/* Header */}
        <div className="bg-white rounded-2xl border border-gray-200 p-6 shadow-sm mb-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-2 flex items-center gap-2">
            <Cog6ToothIcon className="w-8 h-8" />
            Settings
          </h1>
          <p className="text-gray-600">
            Manage your account preferences
          </p>
        </div>

        {/* Info Card */}
        <div className="bg-blue-50 border border-blue-200 rounded-2xl p-6">
          <h3 className="text-sm font-semibold text-blue-900 mb-2">About Settings</h3>
          <p className="text-sm text-blue-800">
            Additional settings will be available soon. For now, you can view your profile information and messages from the Dashboard.
          </p>
        </div>
      </div>
    </div>
  );
}
