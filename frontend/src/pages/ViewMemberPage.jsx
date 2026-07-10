import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../services/api';
import {
  ArrowLeftIcon,
  UserIcon,
  ExclamationTriangleIcon,
  HeartIcon,
  ChartBarIcon,
  CreditCardIcon,
  CameraIcon,
  KeyIcon
} from '@heroicons/react/24/outline';

export default function ViewMemberPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [member, setMember] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [actionLoading, setActionLoading] = useState(false);

  useEffect(() => {
    fetchMember();
  }, [id]);

  const fetchMember = async () => {
    try {
      const response = await api.get(`/api/members/${id}`);
      setMember(response.data.member);
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.error || 'Failed to fetch member details');
    } finally {
      setLoading(false);
    }
  };

  const handleDeactivate = async () => {
    if (!window.confirm('Are you sure you want to deactivate this member? They will not be able to log in, but all historical data will be preserved.')) {
      return;
    }

    setActionLoading(true);
    setError('');

    try {
      await api.post(`/api/members/${id}/deactivate`);
      // Refresh member data
      await fetchMember();
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.error || 'Failed to deactivate member');
    } finally {
      setActionLoading(false);
    }
  };

  const handleReactivate = async () => {
    if (!window.confirm('Are you sure you want to reactivate this member? They will be able to log in again.')) {
      return;
    }

    setActionLoading(true);
    setError('');

    try {
      await api.post(`/api/members/${id}/reactivate`);
      // Refresh member data
      await fetchMember();
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.error || 'Failed to reactivate member');
    } finally {
      setActionLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!window.confirm('Are you sure you want to permanently delete this member? This action cannot be undone.')) {
      return;
    }

    setActionLoading(true);
    setError('');

    try {
      await api.delete(`/api/members/${id}`);
      navigate('/members');
    } catch (err) {
      console.error(err);
      const errorMsg = err.response?.data?.message || err.response?.data?.error || 'Failed to delete member';
      setError(errorMsg);
    } finally {
      setActionLoading(false);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Not provided';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'Active':
        return 'bg-green-50 text-green-700 border-green-200';
      case 'Expired':
        return 'bg-red-50 text-red-700 border-red-200';
      case 'Inactive':
        return 'bg-gray-50 text-gray-600 border-gray-200';
      default:
        return 'bg-gray-50 text-gray-600 border-gray-200';
    }
  };

  if (loading) {
    return (
      <div className="space-y-8">
        <div className="flex items-center justify-center py-12">
          <div className="text-gray-600">Loading member details...</div>
        </div>
      </div>
    );
  }

  if (error || !member) {
    return (
      <div className="space-y-8">
        <div className="bg-red-50 border border-red-200 text-red-700 text-sm p-4 rounded-xl">
          {error || 'Member not found'}
        </div>
        <button
          onClick={() => navigate('/members')}
          className="bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-2 rounded-xl text-sm font-medium transition-colors flex items-center gap-2"
        >
          <ArrowLeftIcon className="w-4 h-4" /> Back to Members
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
            {member.first_name} {member.last_name}
          </h1>
          <p className="text-sm text-gray-600">Member ID: {member.member_id}</p>
        </div>
        <div className="flex flex-wrap gap-3">
          <button
            onClick={() => navigate(`/members/${id}/edit`)}
            className="bg-orange-600 hover:bg-orange-700 text-white px-4 py-2 rounded-xl text-sm font-medium transition-colors"
          >
            Edit Member
          </button>
          {member.status === 'Active' ? (
            <button
              onClick={handleDeactivate}
              disabled={actionLoading}
              className="bg-yellow-600 hover:bg-yellow-700 text-white px-4 py-2 rounded-xl text-sm font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {actionLoading ? 'Deactivating...' : 'Deactivate Member'}
            </button>
          ) : (
            <button
              onClick={handleReactivate}
              disabled={actionLoading}
              className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-xl text-sm font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {actionLoading ? 'Reactivating...' : 'Reactivate Member'}
            </button>
          )}
          <button
            onClick={handleDelete}
            disabled={actionLoading}
            className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-xl text-sm font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {actionLoading ? 'Deleting...' : 'Delete Member'}
          </button>
          <button
            onClick={() => navigate('/members')}
            className="bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-2 rounded-xl text-sm font-medium transition-colors flex items-center gap-2"
          >
            <ArrowLeftIcon className="w-4 h-4" /> Back to Members
          </button>
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-8">
        {/* Main Information */}
        <div className="lg:col-span-2 space-y-6">
          {/* Personal Details */}
          <div className="bg-white border border-gray-200 p-6 rounded-2xl shadow-sm">
            <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
              <UserIcon className="w-5 h-5 text-orange-500" /> Personal Information
            </h2>
            <div className="grid md:grid-cols-2 gap-4">
              <div className="space-y-3">
                <div>
                  <label className="text-xs uppercase font-semibold tracking-wider text-gray-600">First Name</label>
                  <p className="text-gray-900 font-medium">{member.first_name || 'Not provided'}</p>
                </div>
                <div>
                  <label className="text-xs uppercase font-semibold tracking-wider text-gray-600">Gender</label>
                  <p className="text-gray-900 font-medium">{member.gender || 'Not specified'}</p>
                </div>
                <div>
                  <label className="text-xs uppercase font-semibold tracking-wider text-gray-600">Phone</label>
                  <p className="text-gray-900 font-medium font-mono">{member.phone || 'Not provided'}</p>
                </div>
              </div>
              <div className="space-y-3">
                <div>
                  <label className="text-xs uppercase font-semibold tracking-wider text-gray-600">Last Name</label>
                  <p className="text-gray-900 font-medium">{member.last_name || 'Not provided'}</p>
                </div>
                <div>
                  <label className="text-xs uppercase font-semibold tracking-wider text-gray-600">Date of Birth</label>
                  <p className="text-gray-900 font-medium">{formatDate(member.date_of_birth)}</p>
                </div>
                <div>
                  <label className="text-xs uppercase font-semibold tracking-wider text-gray-600">Email</label>
                  <p className="text-gray-900 font-medium font-mono">{member.email || 'Not provided'}</p>
                </div>
              </div>
            </div>
            {member.address && (
              <div className="mt-4 pt-4 border-t border-gray-200">
                <label className="text-xs uppercase font-semibold tracking-wider text-gray-600">Address</label>
                <p className="text-gray-900 font-medium mt-1">{member.address}</p>
              </div>
            )}
          </div>

          {/* Emergency Contact */}
          <div className="bg-white border border-gray-200 p-6 rounded-2xl shadow-sm">
            <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
              <ExclamationTriangleIcon className="w-5 h-5 text-orange-500" /> Emergency Contact
            </h2>
            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <label className="text-xs uppercase font-semibold tracking-wider text-gray-600">Contact Name</label>
                <p className="text-gray-900 font-medium">{member.emergency_contact_name || 'Not provided'}</p>
              </div>
              <div>
                <label className="text-xs uppercase font-semibold tracking-wider text-gray-600">Contact Phone</label>
                <p className="text-gray-900 font-medium font-mono">{member.emergency_contact_phone || 'Not provided'}</p>
              </div>
            </div>
          </div>

          {/* Medical Notes */}
          {member.medical_notes && (
            <div className="bg-white border border-gray-200 p-6 rounded-2xl shadow-sm">
              <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                <HeartIcon className="w-5 h-5 text-orange-500" /> Medical Notes
              </h2>
              <p className="text-gray-700 leading-relaxed">{member.medical_notes}</p>
            </div>
          )}
        </div>

        {/* Sidebar Information */}
        <div className="space-y-6">
          {/* Status */}
          <div className="bg-white border border-gray-200 p-6 rounded-2xl shadow-sm">
            <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
              <ChartBarIcon className="w-5 h-5 text-orange-500" /> Status
            </h2>
            <div className="space-y-3">
              <div>
                <label className="text-xs uppercase font-semibold tracking-wider text-gray-600">Current Status</label>
                <div className="mt-1">
                  <span className={`inline-flex px-3 py-1 rounded-full text-xs font-semibold border ${getStatusColor(member.status)}`}>
                    {member.status}
                  </span>
                </div>
              </div>
              <div>
                <label className="text-xs uppercase font-semibold tracking-wider text-gray-600">Account Access</label>
                <div className="mt-1">
                  {member.has_account ? (
                    <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold border bg-green-50 text-green-700 border-green-200">
                      <KeyIcon className="w-3 h-3" /> Has Login Account
                    </span>
                  ) : (
                    <span className="inline-flex px-3 py-1 rounded-full text-xs font-semibold border bg-gray-50 text-gray-600 border-gray-200">
                      No Account
                    </span>
                  )}
                </div>
              </div>
              <div>
                <label className="text-xs uppercase font-semibold tracking-wider text-gray-600">Member Since</label>
                <p className="text-gray-900 font-medium">{formatDate(member.created_at)}</p>
              </div>
            </div>
          </div>

          {/* Membership Details */}
          <div className="bg-white border border-gray-200 p-6 rounded-2xl shadow-sm">
            <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
              <CreditCardIcon className="w-5 h-5 text-orange-500" /> Membership
            </h2>
            <div className="space-y-3">
              <div>
                <label className="text-xs uppercase font-semibold tracking-wider text-gray-600">Plan</label>
                <p className="text-gray-900 font-medium">{member.membership_plan_name || 'No plan assigned'}</p>
              </div>
              <div>
                <label className="text-xs uppercase font-semibold tracking-wider text-gray-600">Start Date</label>
                <p className="text-gray-900 font-medium">{formatDate(member.membership_start_date)}</p>
              </div>
              <div>
                <label className="text-xs uppercase font-semibold tracking-wider text-gray-600">End Date</label>
                <p className="text-gray-900 font-medium">{formatDate(member.membership_end_date)}</p>
              </div>
            </div>
          </div>

          {/* Profile Photo Placeholder */}
          <div className="bg-white border border-gray-200 p-6 rounded-2xl shadow-sm">
            <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
              <CameraIcon className="w-5 h-5 text-orange-500" /> Profile Photo
            </h2>
            <div className="w-32 h-32 bg-orange-100 border-2 border-orange-200 rounded-xl flex items-center justify-center mx-auto">
              <span className="text-3xl font-bold text-orange-600">
                {member.first_name?.charAt(0)?.toUpperCase() || '?'}
              </span>
            </div>
            <p className="text-xs text-gray-500 text-center mt-2">Photo upload coming soon</p>
          </div>
        </div>
      </div>
    </div>
  );
}