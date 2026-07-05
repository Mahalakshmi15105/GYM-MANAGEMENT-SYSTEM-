import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';

export default function CheckInPage() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [members, setMembers] = useState([]);
  const [selectedMember, setSelectedMember] = useState(null);
  const [formData, setFormData] = useState({
    member_id: '',
    check_in_time: new Date().toISOString().slice(0, 16),
    notes: ''
  });

  useEffect(() => {
    fetchMembers();
  }, []);

  const fetchMembers = async () => {
    try {
      const response = await api.get('/api/attendance/members');
      setMembers(response.data.members || []);
    } catch (err) {
      console.error('Failed to fetch members:', err);
    }
  };

  const handleMemberChange = (memberId) => {
    const member = members.find(m => m.id.toString() === memberId);
    setSelectedMember(member);
    setFormData(prev => ({ ...prev, member_id: memberId }));
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validation
    if (!formData.member_id || !formData.check_in_time) {
      setError('Please select a member and check-in time.');
      return;
    }

    setLoading(true);
    setError('');

    try {
      await api.post('/api/attendance', formData);
      navigate('/attendance');
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.error || 'Failed to record check-in. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 mb-1">Member Check In</h1>
          <p className="text-sm text-gray-600">Record a member check-in</p>
        </div>
        <button
          onClick={() => navigate('/attendance')}
          className="bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-2 rounded-xl text-sm font-medium transition-colors self-start md:self-auto"
        >
          ← Back to Attendance
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
          {/* Member Selection */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Member Selection</h3>
            <div className="grid grid-cols-1 gap-4">
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-gray-600 mb-2">
                  Select Member *
                </label>
                <select
                  name="member_id"
                  required
                  value={formData.member_id}
                  onChange={(e) => handleMemberChange(e.target.value)}
                  className="w-full bg-gray-50 border border-gray-200 focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 rounded-xl px-4 py-3 text-sm text-gray-900 focus:outline-none transition-all duration-200"
                >
                  <option value="">Select a member</option>
                  {members.map((member) => (
                    <option key={member.id} value={member.id}>
                      {member.name} - {member.phone}
                    </option>
                  ))}
                </select>
                {selectedMember && (
                  <div className="mt-2 p-3 bg-orange-50 border border-orange-200 rounded-lg">
                    <p className="text-sm text-orange-800">
                      <strong>{selectedMember.name}</strong> - {selectedMember.phone}
                    </p>
                    <p className="text-xs text-orange-600">
                      Plan: {selectedMember.membership_plan_name || 'No plan assigned'}
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Check-in Details */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Check-in Details</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-gray-600 mb-2">
                  Check-in Date & Time *
                </label>
                <input
                  type="datetime-local"
                  name="check_in_time"
                  required
                  value={formData.check_in_time}
                  onChange={handleInputChange}
                  className="w-full bg-gray-50 border border-gray-200 focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 rounded-xl px-4 py-3 text-sm text-gray-900 focus:outline-none transition-all duration-200"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-gray-600 mb-2">
                  Quick Actions
                </label>
                <div className="flex gap-2">
                  <button
                    type="button"
                    onClick={() => setFormData(prev => ({ 
                      ...prev, 
                      check_in_time: new Date().toISOString().slice(0, 16) 
                    }))}
                    className="bg-orange-100 hover:bg-orange-200 text-orange-700 px-3 py-2 rounded-lg text-xs font-medium transition-colors border border-orange-200"
                  >
                    Use Current Time
                  </button>
                </div>
              </div>
            </div>
            <div className="mt-4">
              <label className="block text-xs font-semibold uppercase tracking-wider text-gray-600 mb-2">
                Notes (Optional)
              </label>
              <textarea
                name="notes"
                value={formData.notes}
                onChange={handleInputChange}
                rows="3"
                placeholder="Any additional notes about this check-in..."
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
              {loading ? 'Recording Check-in...' : 'Record Check-in'}
            </button>
            <button
              type="button"
              onClick={() => navigate('/attendance')}
              className="bg-gray-100 hover:bg-gray-200 text-gray-700 font-medium py-3 px-6 rounded-xl transition-colors"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>

      {/* Quick Member Search */}
      <div className="bg-white border border-gray-200 p-6 rounded-2xl shadow-sm">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Member Search</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {members.slice(0, 6).map((member) => (
            <button
              key={member.id}
              onClick={() => handleMemberChange(member.id.toString())}
              className={`p-4 text-left rounded-xl border-2 transition-all duration-200 ${
                formData.member_id === member.id.toString()
                  ? 'border-orange-500 bg-orange-50'
                  : 'border-gray-200 hover:border-orange-300 bg-gray-50 hover:bg-orange-50'
              }`}
            >
              <p className="font-medium text-gray-900">{member.name}</p>
              <p className="text-xs text-gray-500 font-mono">{member.phone}</p>
              <p className="text-xs text-gray-600 mt-1">
                {member.membership_plan_name || 'No plan'}
              </p>
            </button>
          ))}
        </div>
        {members.length > 6 && (
          <p className="text-xs text-gray-500 text-center mt-4">
            Use the dropdown above to see all {members.length} active members
          </p>
        )}
      </div>
    </div>
  );
}