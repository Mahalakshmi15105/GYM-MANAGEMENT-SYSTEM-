import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../services/api';
import {
  UserIcon,
  ClockIcon,
  ShieldCheckIcon,
  ArrowLeftIcon,
  CheckIcon,
  CheckCircleIcon,
  BoltIcon,
  DocumentTextIcon,
  ChartBarIcon
} from '@heroicons/react/24/outline';

export default function ViewAttendancePage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [attendance, setAttendance] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchAttendance();
  }, [id]);

  const fetchAttendance = async () => {
    try {
      const response = await api.get(`/api/attendance/${id}`);
      setAttendance(response.data);
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.error || 'Failed to fetch attendance details');
    } finally {
      setLoading(false);
    }
  };

  const handleCheckout = async () => {
    try {
      await api.put(`/api/attendance/${id}/checkout`);
      fetchAttendance(); // Refresh the data
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.error || 'Failed to record checkout');
    }
  };

  const formatDateTime = (dateTimeString) => {
    if (!dateTimeString) return 'Not provided';
    return new Date(dateTimeString).toLocaleString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Not provided';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const formatDuration = (minutes) => {
    if (!minutes) return 'Still checked in';
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    if (hours > 0) {
      return `${hours} hour${hours > 1 ? 's' : ''} ${mins} minute${mins !== 1 ? 's' : ''}`;
    }
    return `${mins} minute${mins !== 1 ? 's' : ''}`;
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'Checked In':
        return 'bg-orange-50 text-orange-700 border-orange-200';
      case 'Checked Out':
        return 'bg-green-50 text-green-700 border-green-200';
      default:
        return 'bg-gray-50 text-gray-600 border-gray-200';
    }
  };

  if (loading) {
    return (
      <div className="space-y-8">
        <div className="flex items-center justify-center py-12">
          <div className="text-gray-600">Loading attendance details...</div>
        </div>
      </div>
    );
  }

  if (error || !attendance) {
    return (
      <div className="space-y-8">
        <div className="bg-red-50 border border-red-200 text-red-700 text-sm p-4 rounded-xl">
          {error || 'Attendance record not found'}
        </div>
        <button
          onClick={() => navigate('/attendance')}
          className="bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-2 rounded-xl text-sm font-medium transition-colors flex items-center gap-2"
        >
          <ArrowLeftIcon className="w-4 h-4" /> Back to Attendance
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 mb-1">
            Attendance Details
          </h1>
          <p className="text-sm text-gray-600">
            {attendance.member_name} - {formatDate(attendance.attendance_date)}
          </p>
        </div>
        <div className="flex flex-wrap gap-3">
          {attendance.status === 'Checked In' && (
            <button
              onClick={handleCheckout}
              className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-xl text-sm font-medium transition-colors flex items-center gap-2"
            >
              <CheckIcon className="w-4 h-4 mr-2" /> Check Out
            </button>
          )}
          <button
            onClick={() => navigate(`/attendance/${id}/edit`)}
            className="bg-orange-600 hover:bg-orange-700 text-white px-4 py-2 rounded-xl text-sm font-medium transition-colors"
          >
            Edit Record
          </button>
          <button
            onClick={() => navigate('/attendance')}
            className="bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-2 rounded-xl text-sm font-medium transition-colors flex items-center gap-2"
          >
            <ArrowLeftIcon className="w-4 h-4" /> Back to Attendance
          </button>
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-8">
        {/* Main Information */}
        <div className="lg:col-span-2 space-y-6">
          {/* Member & Attendance Details */}
          <div className="bg-white border border-gray-200 p-6 rounded-2xl shadow-sm">
            <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
              <UserIcon className="w-5 h-5 text-orange-500" /> Member & Attendance Information
            </h2>
            <div className="grid md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <div>
                  <label className="text-xs uppercase font-semibold tracking-wider text-gray-600">Member Name</label>
                  <p className="text-gray-900 font-medium text-lg">{attendance.member_name}</p>
                </div>
                <div>
                  <label className="text-xs uppercase font-semibold tracking-wider text-gray-600">Phone Number</label>
                  <p className="text-gray-900 font-mono">{attendance.member_phone}</p>
                </div>
                <div>
                  <label className="text-xs uppercase font-semibold tracking-wider text-gray-600">Attendance Date</label>
                  <p className="text-gray-900 font-medium">{formatDate(attendance.attendance_date)}</p>
                </div>
              </div>
              <div className="space-y-4">
                <div>
                  <label className="text-xs uppercase font-semibold tracking-wider text-gray-600">Status</label>
                  <div className="mt-1">
                    <span className={`inline-flex px-3 py-1 rounded-full text-sm font-semibold border ${getStatusColor(attendance.status)}`}>
                      {attendance.status}
                    </span>
                  </div>
                </div>
                <div>
                  <label className="text-xs uppercase font-semibold tracking-wider text-gray-600">Workout Duration</label>
                  <p className="text-gray-900 font-medium">{formatDuration(attendance.duration_minutes)}</p>
                </div>
              </div>
            </div>
          </div>

          {/* Time Details */}
          <div className="bg-white border border-gray-200 p-6 rounded-2xl shadow-sm">
            <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
              <ClockIcon className="w-5 h-5 text-orange-500" /> Time Details
            </h2>
            <div className="grid md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <div>
                  <label className="text-xs uppercase font-semibold tracking-wider text-gray-600">Check-in Time</label>
                  <p className="text-gray-900 font-medium">{formatDateTime(attendance.check_in_time)}</p>
                </div>
              </div>
              <div className="space-y-4">
                <div>
                  <label className="text-xs uppercase font-semibold tracking-wider text-gray-600">Check-out Time</label>
                  <p className="text-gray-900 font-medium">{formatDateTime(attendance.check_out_time)}</p>
                </div>
              </div>
            </div>
          </div>

          {/* Notes */}
          {attendance.notes && (
            <div className="bg-white border border-gray-200 p-6 rounded-2xl shadow-sm">
              <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                <DocumentTextIcon className="w-5 h-5 text-orange-500" /> Notes
              </h2>
              <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">{attendance.notes}</p>
            </div>
          )}
        </div>

        {/* Sidebar Information */}
        <div className="space-y-6">
          {/* Quick Stats */}
          <div className="bg-white border border-gray-200 p-6 rounded-2xl shadow-sm">
            <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
              <ChartBarIcon className="w-5 h-5 text-orange-500" /> Quick Stats
            </h2>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-gray-600 text-sm">Duration</span>
                <span className="text-gray-900 font-medium">
                  {attendance.duration_minutes ? `${attendance.duration_minutes} min` : 'Ongoing'}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600 text-sm">Day of Week</span>
                <span className="text-gray-900 font-medium">
                  {new Date(attendance.attendance_date).toLocaleDateString('en-US', { weekday: 'long' })}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600 text-sm">Check-in Hour</span>
                <span className="text-gray-900 font-medium">
                  {new Date(attendance.check_in_time).toLocaleTimeString('en-US', { 
                    hour: 'numeric', 
                    hour12: true 
                  })}
                </span>
              </div>
            </div>
          </div>

          {/* Timestamps */}
          <div className="bg-white border border-gray-200 p-6 rounded-2xl shadow-sm">
            <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
              <ClockIcon className="w-5 h-5 text-orange-500" /> Record Timestamps
            </h2>
            <div className="space-y-3">
              <div>
                <label className="text-xs uppercase font-semibold tracking-wider text-gray-600">Created At</label>
                <p className="text-gray-900 text-sm">{formatDateTime(attendance.created_at)}</p>
              </div>
              <div>
                <label className="text-xs uppercase font-semibold tracking-wider text-gray-600">Last Updated</label>
                <p className="text-gray-900 text-sm">{formatDateTime(attendance.updated_at)}</p>
              </div>
            </div>
          </div>

          {/* Status Icon */}
          <div className="bg-white border border-gray-200 p-6 rounded-2xl shadow-sm">
            <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
              <ShieldCheckIcon className="w-5 h-5 text-orange-500" /> Status Icon
            </h2>
            <div className="w-32 h-32 bg-orange-100 border-2 border-orange-200 rounded-xl flex items-center justify-center mx-auto">
              {attendance.status === 'Checked In' ? (
                <BoltIcon className="w-16 h-16 text-orange-600" />
              ) : (
                <CheckCircleIcon className="w-16 h-16 text-green-600" />
              )}
            </div>
            <p className="text-xs text-gray-500 text-center mt-2">
              {attendance.status === 'Checked In' ? 'Currently Working Out' : 'Workout Complete'}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}