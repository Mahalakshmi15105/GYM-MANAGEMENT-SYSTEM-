import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import { ArrowLeftIcon } from '@heroicons/react/24/outline';

export default function AddMembershipPlanPage() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [formData, setFormData] = useState({
    plan_name: '',
    duration: '',
    price: '',
    description: '',
    status: 'Active'
  });

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validation
    if (!formData.plan_name || !formData.duration || !formData.price) {
      setError('Please fill in all required fields.');
      return;
    }

    // Duration validation
    if (parseInt(formData.duration) <= 0) {
      setError('Duration must be a positive number.');
      return;
    }

    // Price validation
    if (parseFloat(formData.price) < 0) {
      setError('Price cannot be negative.');
      return;
    }

    setLoading(true);
    setError('');

    try {
      await api.post('/api/membership-plans', formData);
      navigate('/membership-plans');
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.error || 'Failed to create membership plan. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const commonDurations = [
    { value: 7, label: '1 Week' },
    { value: 30, label: '1 Month' },
    { value: 90, label: '3 Months' },
    { value: 180, label: '6 Months' },
    { value: 365, label: '1 Year' }
  ];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 mb-1">Add New Membership Plan</h1>
          <p className="text-sm text-gray-600">Create a new membership plan for your gym</p>
        </div>
        <button
          onClick={() => navigate('/membership-plans')}
          className="bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-2 rounded-xl text-sm font-medium transition-colors self-start md:self-auto flex items-center gap-2"
        >
          <ArrowLeftIcon className="w-4 h-4" /> Back to Plans
        </button>
      </div>

      {/* Form */}
      <div className="bg-white border border-gray-200 p-6 rounded-2xl shadow-sm">
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 text-sm p-4 rounded-xl mb-6">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Plan Information */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Plan Information</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-gray-600 mb-2">
                  Plan Name *
                </label>
                <input
                  type="text"
                  name="plan_name"
                  required
                  value={formData.plan_name}
                  onChange={handleInputChange}
                  placeholder="e.g., Premium Monthly, Basic Annual"
                  className="w-full bg-gray-50 border border-gray-200 focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 rounded-xl px-4 py-3 text-sm text-gray-900 placeholder-gray-500 focus:outline-none transition-all duration-200"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-gray-600 mb-2">
                  Status
                </label>
                <select
                  name="status"
                  value={formData.status}
                  onChange={handleInputChange}
                  className="w-full bg-gray-50 border border-gray-200 focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 rounded-xl px-4 py-3 text-sm text-gray-900 focus:outline-none transition-all duration-200"
                >
                  <option value="Active">Active</option>
                  <option value="Inactive">Inactive</option>
                </select>
              </div>
            </div>
          </div>

          {/* Duration & Price */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Duration & Pricing</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-gray-600 mb-2">
                  Duration (days) *
                </label>
                <div className="space-y-2">
                  <input
                    type="number"
                    name="duration"
                    required
                    min="1"
                    value={formData.duration}
                    onChange={handleInputChange}
                    placeholder="e.g., 30"
                    className="w-full bg-gray-50 border border-gray-200 focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 rounded-xl px-4 py-3 text-sm text-gray-900 placeholder-gray-500 focus:outline-none transition-all duration-200"
                  />
                  <div className="flex flex-wrap gap-2">
                    {commonDurations.map((duration) => (
                      <button
                        key={duration.value}
                        type="button"
                        onClick={() => setFormData(prev => ({ ...prev, duration: duration.value.toString() }))}
                        className="bg-orange-50 hover:bg-orange-100 text-orange-700 px-3 py-1 rounded-lg text-xs font-medium transition-colors border border-orange-200"
                      >
                        {duration.label}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-gray-600 mb-2">
                  Price *
                </label>
                <input
                  type="number"
                  name="price"
                  required
                  min="0"
                  step="0.01"
                  value={formData.price}
                  onChange={handleInputChange}
                  placeholder="e.g., 49.99"
                  className="w-full bg-gray-50 border border-gray-200 focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 rounded-xl px-4 py-3 text-sm text-gray-900 placeholder-gray-500 focus:outline-none transition-all duration-200"
                />
              </div>
            </div>
          </div>

          {/* Description */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Description</h3>
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-gray-600 mb-2">
                Plan Description
              </label>
              <textarea
                name="description"
                value={formData.description}
                onChange={handleInputChange}
                rows="4"
                placeholder="Describe what this membership plan includes..."
                className="w-full bg-gray-50 border border-gray-200 focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 rounded-xl px-4 py-3 text-sm text-gray-900 placeholder-gray-500 focus:outline-none transition-all duration-200 resize-none"
              />
            </div>
          </div>

          {/* Submit Buttons */}
          <div className="flex flex-col sm:flex-row gap-3 pt-4">
            <button
              type="submit"
              disabled={loading}
              className="bg-orange-600 hover:bg-orange-700 text-white font-bold py-3 px-6 rounded-xl transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Creating Plan...' : 'Create Plan'}
            </button>
            <button
              type="button"
              onClick={() => navigate('/membership-plans')}
              className="bg-gray-100 hover:bg-gray-200 text-gray-700 font-medium py-3 px-6 rounded-xl transition-colors"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}