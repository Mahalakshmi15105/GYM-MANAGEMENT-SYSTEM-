import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { BoltIcon, ArrowLeftIcon } from '@heroicons/react/24/outline';
import api from '../services/api';

export default function SuperAdminAddGym() {
  const [gymName, setGymName] = useState('');
  const [gymAddress, setGymAddress] = useState('');
  const [gymPhone, setGymPhone] = useState('');
  const [ownerName, setOwnerName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!gymName || !gymAddress || !gymPhone || !ownerName || !email || !password) {
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
      const response = await api.post('/api/admin/gyms/create', {
        gym_name: gymName,
        gym_address: gymAddress,
        gym_phone: gymPhone,
        name: ownerName,
        email,
        password
      });
      
      // Success - navigate back to gym management
      navigate('/admin/gyms', { 
        state: { success: true, message: 'Gym created successfully' }
      });
    } catch (err) {
      console.error('Gym creation error:', err);
      const errorMessage = err.response?.data?.error || err.response?.data?.message || 'Failed to create gym. Please try again.';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <button
            onClick={() => navigate('/admin/gyms')}
            className="flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-4"
          >
            <ArrowLeftIcon className="w-5 h-5" />
            Back to Gym Management
          </button>
          <div className="flex items-center gap-3 mb-2">
            <BoltIcon className="w-8 h-8 text-orange-500" />
            <h1 className="text-2xl font-bold text-gray-900">Add New Gym</h1>
          </div>
          <p className="text-gray-600">Create a new gym tenant workspace and owner account</p>
        </div>

        {/* Form Card */}
        <div className="bg-white border border-gray-200 rounded-2xl shadow-sm p-8">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-600 text-sm p-4 rounded-xl mb-6">
              <span className="font-bold">Error:</span> {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Gym Information */}
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4 pb-2 border-b border-gray-200">
                Gym Information
              </h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Gym Name
                  </label>
                  <input
                    type="text"
                    required
                    disabled={loading}
                    value={gymName}
                    onChange={(e) => setGymName(e.target.value)}
                    placeholder="Elite Fitness Academy"
                    className="w-full bg-gray-50 border border-gray-200 focus:border-orange-400 focus:bg-white rounded-lg px-4 py-3 text-sm text-gray-900 placeholder-gray-500 focus:outline-none transition-all duration-200"
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Gym Address
                  </label>
                  <textarea
                    required
                    disabled={loading}
                    value={gymAddress}
                    onChange={(e) => setGymAddress(e.target.value)}
                    placeholder="123 Fitness Street, Health District, City, State, ZIP"
                    rows="3"
                    className="w-full bg-gray-50 border border-gray-200 focus:border-orange-400 focus:bg-white rounded-lg px-4 py-3 text-sm text-gray-900 placeholder-gray-500 focus:outline-none transition-all duration-200 resize-none"
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Gym Phone Number
                  </label>
                  <input
                    type="tel"
                    required
                    disabled={loading}
                    value={gymPhone}
                    onChange={(e) => setGymPhone(e.target.value)}
                    placeholder="+1 (555) 123-4567"
                    className="w-full bg-gray-50 border border-gray-200 focus:border-orange-400 focus:bg-white rounded-lg px-4 py-3 text-sm text-gray-900 placeholder-gray-500 focus:outline-none transition-all duration-200"
                  />
                </div>
              </div>
            </div>

            {/* Owner Information */}
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4 pb-2 border-b border-gray-200">
                Owner Information
              </h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Owner's Name
                  </label>
                  <input
                    type="text"
                    required
                    disabled={loading}
                    value={ownerName}
                    onChange={(e) => setOwnerName(e.target.value)}
                    placeholder="Alex Mercer"
                    className="w-full bg-gray-50 border border-gray-200 focus:border-orange-400 focus:bg-white rounded-lg px-4 py-3 text-sm text-gray-900 placeholder-gray-500 focus:outline-none transition-all duration-200"
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Email Address
                  </label>
                  <input
                    type="email"
                    required
                    disabled={loading}
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="owner@yourgym.com"
                    className="w-full bg-gray-50 border border-gray-200 focus:border-orange-400 focus:bg-white rounded-lg px-4 py-3 text-sm text-gray-900 placeholder-gray-500 focus:outline-none transition-all duration-200"
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Password
                  </label>
                  <input
                    type="password"
                    required
                    disabled={loading}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••"
                    className="w-full bg-gray-50 border border-gray-200 focus:border-orange-400 focus:bg-white rounded-lg px-4 py-3 text-sm text-gray-900 placeholder-gray-500 focus:outline-none transition-all duration-200"
                  />
                </div>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-orange-500 hover:bg-orange-600 text-white font-bold py-3.5 px-4 rounded-xl transition-all duration-200 shadow-md disabled:opacity-50 disabled:cursor-not-allowed text-sm"
            >
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <svg className="animate-spin h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  Creating Gym...
                </span>
              ) : (
                'Create Gym & Owner Account'
              )}
            </button>
          </form>
        </div>

        {/* Info Note */}
        <div className="mt-6 bg-blue-50 border border-blue-200 rounded-xl p-4">
          <p className="text-sm text-blue-800">
            <strong>Note:</strong> The gym will be created with "Active" status. The owner will be able to log in immediately after creation.
          </p>
        </div>
      </div>
    </div>
  );
}
