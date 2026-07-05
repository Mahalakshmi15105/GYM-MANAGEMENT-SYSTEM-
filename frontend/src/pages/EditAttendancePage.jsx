import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../services/api';

export default function EditAttendancePage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [members, setMembers] = useState([]);
  const [selectedMember, setSelectedMember] = useState(null);
  const [formData, setFormData] = useState({
    member_id: '',
    check_in_time: '',
    check_out_time: '',
    notes: ''
  });

  useEffect(() => {
    fetchAttendance();
    fetchMembers();
  }, [id]);

  const fetchAttendance = async () => {
    try {
      const response = await api.get(`/api/attendance/${id}`);
      const attendance = response.data;
      
      setFormData({
        member_id: attendance.member_id.toString(),
        check_in_time: attendance.check_in_time ? 
          new Date(attendance.check_in_time).toISOString().slice(0, 16) : '',
        check_out_time: attendance.check_out_time ? 
          new Date(attendance.check_out_time).toISOString().slice(0, 16) : '',
        notes: attendance.notes || ''
      });
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.error || 'Failed to fetch attendance details');
    } finally {
      setLoading(false);
    }
  };

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

    // Validate check-out time is after check-in time
    if (formData.check_out_time && formData.check_out_time <= formData.check_in_time) {
      setError('Check-out time must be after check-in time.');
      return;
    }

    setSaving(true);
    setError('');

    try {
      await api.put(`/api/attendance/${id}`, formData);
      navigate(`/attendance/${id}`);
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.error || 'Failed to update attendance record. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  // Set selected member once data is loaded
  useEffect(() => {
    if (members.length > 0 && formData.member_id) {
      const member = members.find(m => m.id.toString() === formData.member_id);
      setSelectedMember(member);
    }
  }, [members, formData.member_id]);

  if (loading) {
    return (
      <div className="space-y-8">
        <div className="flex items-center justify-center py-12">
          <div className="text-gray-600">Loading attendance details...</div>
        </div>
      </div>
    );
  }

  if (error && !formData.member_id) {
    return (
      <div className="space-y-8">
        <div className="bg-red-50 border border-red-200 text-red-700 text-sm p-4 rounded-xl">
          {error}
        </div>
        <button
          onClick={() => navigate('/attendance')}
          className="bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-2 rounded-xl text-sm font-medium transition-colors"
        >
          ← Back to Attendance
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 mb-1">Edit Attendance Record</h1>
          <p className="text-sm text-gray-600">Update attendance information</p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={() => navigate(`/attendance/${id}`)}
            className="bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-2 rounded-xl text-sm font-medium transition-colors"
          >
            Cancel
          </button>
        </div>
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

          {/* Time Details */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Time Details</h3>
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
                  Check-out Date & Time
                </label>
                <input
                  type="datetime-local"
                  name="check_out_time"
                  value={formData.check_out_time}
                  onChange={handleInputChange}
                  className="w-full bg-gray-50 border border-gray-200 focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 rounded-xl px-4 py-3 text-sm text-gray-900 focus:outline-none transition-all duration-200"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Leave empty if member is still checked in
                </p>
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
            <div className="flex flex-wrap gap-2">
              <button
                type="button"
                onClick={() => setFormData(prev => ({ 
                  ...prev, 
                  check_in_time: new Date().toISOString().slice(0, 16) 
                }))}
                className="bg-orange-100 hover:bg-orange-200 text-orange-700 px-3 py-2 rounded-lg text-xs font-medium transition-colors border border-orange-200"
              >
                Set Check-in to Now
              </button>
              <button
                type="button"
                onClick={() => setFormData(prev => ({ 
                  ...prev, 
                  check_out_time: new Date().toISOString().slice(0, 16) 
                }))}
                className="bg-green-100 hover:bg-green-200 text-green-700 px-3 py-2 rounded-lg text-xs font-medium transition-colors border border-green-200"
              >
                Set Check-out to Now
              </button>
              <button
                type="button"
                onClick={() => setFormData(prev => ({ ...prev, check_out_time: '' }))}
                className="bg-gray-100 hover:bg-gray-200 text-gray-700 px-3 py-2 rounded-lg text-xs font-medium transition-colors border border-gray-200"
              >
                Clear Check-out
              </button>
            </div>
          </div>

          {/* Notes */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Additional Information</h3>
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-gray-600 mb-2">
                Notes
              </label>
              <textarea
                name="notes"
                value={formData.notes}
                onChange={handleInputChange}
                rows="3"
                placeholder="Any additional notes about this attendance record..."
                className="w-full bg-gray-50 border border-gray-200 focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 rounded-xl px-4 py-3 text-sm text-gray-900 placeholder-gray-500 focus:outline-none transition-all duration-200 resize-none"
              />
            </div>
          </div>

          {/* Duration Preview */}
          {formData.check_in_time && formData.check_out_time && (
            <div className="bg-orange-50 border border-orange-200 p-4 rounded-xl">
              <h4 className="font-semibold text-orange-800 mb-2">Duration Preview</h4>
              <p className="text-orange-700">
                Workout Duration: {
                  Math.floor((new Date(formData.check_out_time) - new Date(formData.check_in_time)) / (1000 * 60))
                } minutes
              </p>
            </div>
          )}

          {/* Submit Buttons */}
          <div className="flex flex-col sm:flex-row gap-3 pt-4">
            <button
              type="submit"
              disabled={saving}
              className="bg-orange-600 hover:bg-orange-700 text-white font-bold py-3 px-6 rounded-xl transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {saving ? 'Updating Record...' : 'Update Record'}
            </button>
            <button
              type="button"
              onClick={() => navigate(`/attendance/${id}`)}
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