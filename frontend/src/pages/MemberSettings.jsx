import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';
import { Cog6ToothIcon, BellIcon, BellSlashIcon, ArrowLeftIcon } from '@heroicons/react/24/outline';

export default function MemberSettings() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [showGymStatus, setShowGymStatus] = useState(true);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);

  useEffect(() => {
    fetchPreference();
  }, []);

  const fetchPreference = async () => {
    try {
      const response = await api.get('/api/members/gym-status');
      setShowGymStatus(response.data.show_gym_status);
    } catch (err) {
      console.error('Failed to fetch preference:', err);
    }
  };

  const handleToggle = async () => {
    setLoading(true);
    setMessage(null);

    try {
      const newValue = !showGymStatus;
      const response = await api.put('/api/members/gym-status/preference', {
        show_gym_status: newValue
      });
      console.log('Preference update response:', response.data);
      setShowGymStatus(newValue);
      setMessage({
        type: 'success',
        text: `Gym Status ${newValue ? 'enabled' : 'disabled'}`
      });
    } catch (err) {
      console.error('Failed to update preference:', err);
      console.error('Error response:', err.response?.data);
      setMessage({
        type: 'error',
        text: `Failed to update preference: ${err.response?.data?.error || err.message}`
      });
    } finally {
      setLoading(false);
    }
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
            Manage your account preferences and display settings
          </p>
        </div>

        {/* Gym Status Setting */}
        <div className="bg-white rounded-2xl border border-gray-200 p-6 shadow-sm">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-orange-100 rounded-xl flex items-center justify-center">
                {showGymStatus ? (
                  <BellIcon className="w-6 h-6 text-orange-600" />
                ) : (
                  <BellSlashIcon className="w-6 h-6 text-gray-400" />
                )}
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900">Gym Status</h3>
                <p className="text-sm text-gray-600">
                  Show Gym Status card on your dashboard
                </p>
              </div>
            </div>
            <button
              onClick={handleToggle}
              disabled={loading}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors duration-200 ${
                showGymStatus ? 'bg-orange-500' : 'bg-gray-300'
              } ${loading ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform duration-200 ${
                  showGymStatus ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
          </div>

          {message && (
            <div className={`mt-4 p-3 rounded-lg text-sm ${
              message.type === 'success' 
                ? 'bg-green-50 text-green-800' 
                : 'bg-red-50 text-red-800'
            }`}>
              {message.text}
            </div>
          )}
        </div>

        {/* Info Card */}
        <div className="bg-blue-50 border border-blue-200 rounded-2xl p-6 mt-6">
          <h3 className="text-sm font-semibold text-blue-900 mb-2">About Gym Status</h3>
          <p className="text-sm text-blue-800">
            When enabled, you'll see your gym's operational status (Open/Closed) at the top of your dashboard.
            This status updates automatically when your gym owner logs in or out. Disabling this only hides
            the status card for you - it doesn't change the actual gym status.
          </p>
        </div>
      </div>
    </div>
  );
}
