import { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useCurrency } from '../utils/currency';
import NotificationBell from '../components/NotificationBell';
import Footer from '../components/Footer';
import api from '../services/api';
import GymLogo from '../components/GymLogo';
import {
  UserIcon,
  CalendarIcon,
  CurrencyDollarIcon,
  ClockIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  ArrowPathIcon,
  BellIcon,
  IdentificationIcon,
  CreditCardIcon,
  XMarkIcon,
  ChatBubbleLeftIcon,
  Cog6ToothIcon
} from '@heroicons/react/24/outline';

export default function MemberDashboard() {
  const { user, logout } = useAuth();
  const { formatCurrency } = useCurrency(user?.gym_id);
  const navigate = useNavigate();
  const location = useLocation();
  
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('overview');
  const [attendanceMessage, setAttendanceMessage] = useState(null);
  const [gymStatus, setGymStatus] = useState(null);
  const [showGymStatus, setShowGymStatus] = useState(true);

  useEffect(() => {
    fetchDashboardData();
    fetchGymStatus();
    
    // Check for attendance success/error from navigation state
    if (location.state) {
      if (location.state.attendanceSuccess) {
        setAttendanceMessage({
          type: 'success',
          text: 'Attendance marked successfully!',
          data: location.state.attendanceData
        });
      } else if (location.state.attendanceError) {
        setAttendanceMessage({
          type: 'error',
          text: location.state.attendanceError
        });
      }
      // Clear the state after displaying
      window.history.replaceState({}, document.title);
    }
  }, [location.state]);

  const fetchGymStatus = async () => {
    try {
      const response = await api.get('/api/members/gym-status');
      console.log('Gym status response:', response.data);
      setGymStatus(response.data);
      setShowGymStatus(response.data.show_gym_status);
    } catch (err) {
      console.error('Failed to fetch gym status:', err);
      console.error('Error response:', err.response?.data);
    }
  };

  const fetchDashboardData = async () => {
    try {
      const response = await api.get('/api/members/me');
      setDashboardData(response.data);
    } catch (err) {
      console.error('Failed to fetch dashboard data:', err);
      setError(err.response?.data?.error || 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  const formatDateTime = (dateTimeString) => {
    if (!dateTimeString) return '-';
    return new Date(dateTimeString).toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading your dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
        <div className="bg-red-50 border border-red-200 text-red-700 p-6 rounded-xl max-w-md">
          <p className="font-semibold">Error</p>
          <p className="mt-2">{error}</p>
          <button
            onClick={fetchDashboardData}
            className="mt-4 bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  const { member, gym, attendance, payments, membership } = dashboardData;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Attendance Message */}
      {attendanceMessage && (
        <div className={`${
          attendanceMessage.type === 'success' 
            ? 'bg-green-50 border-green-200 text-green-800' 
            : 'bg-red-50 border-red-200 text-red-800'
        } border p-4 mx-4 mt-4 rounded-xl`}>
          <div className="flex items-start gap-3">
            {attendanceMessage.type === 'success' ? (
              <CheckCircleIcon className="w-5 h-5 flex-shrink-0 mt-0.5" />
            ) : (
              <ExclamationTriangleIcon className="w-5 h-5 flex-shrink-0 mt-0.5" />
            )}
            <div className="flex-1">
              <p className="font-semibold">{attendanceMessage.text}</p>
              {attendanceMessage.data && (
                <p className="text-sm mt-1">
                  Check-in time: {new Date(attendanceMessage.data.check_in_time).toLocaleTimeString()}
                </p>
              )}
            </div>
            <button
              onClick={() => setAttendanceMessage(null)}
              className="flex-shrink-0 hover:opacity-70"
            >
              <XMarkIcon className="w-5 h-5" />
            </button>
          </div>
        </div>
      )}

      {/* Gym Status Card */}
      {showGymStatus && gymStatus && (
        <div className={`${
          gymStatus.operational_status === 'Open' 
            ? 'bg-green-50 border-green-200' 
            : 'bg-red-50 border-red-200'
        } border mx-4 mt-4 rounded-xl p-4`}>
          <div className="flex items-center gap-3">
            <div className={`w-3 h-3 rounded-full ${
              gymStatus.operational_status === 'Open' ? 'bg-green-500' : 'bg-red-500'
            }`}></div>
            <div>
              <p className="font-semibold text-gray-900">Gym Status</p>
              <p className={`text-sm ${
                gymStatus.operational_status === 'Open' ? 'text-green-700' : 'text-red-700'
              }`}>
                {gymStatus.operational_status === 'Open' ? '🟢 OPEN' : '🔴 CLOSED'}
              </p>
              <p className="text-xs text-gray-600">
                {gymStatus.operational_status === 'Open' 
                  ? 'Your gym is currently open.' 
                  : 'Your gym is currently closed.'}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center gap-4">
              <GymLogo 
                className="w-12 h-12" 
                showGymName={true}
                gymNameClassName="text-sm font-medium text-gray-900"
              />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Welcome, {member.first_name}!</h1>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <NotificationBell />
              <button
                onClick={() => navigate('/member/settings')}
                className="bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-2 rounded-lg text-sm font-medium flex items-center gap-2"
              >
                <Cog6ToothIcon className="w-4 h-4" />
                Settings
              </button>
              <button
                onClick={handleLogout}
                className="bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-2 rounded-lg text-sm font-medium"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Tabs */}
        <div className="flex space-x-4 mb-8 border-b border-gray-200">
          <button
            onClick={() => setActiveTab('overview')}
            className={`pb-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'overview'
                ? 'border-orange-500 text-orange-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            Overview
          </button>
          <button
            onClick={() => setActiveTab('attendance')}
            className={`pb-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'attendance'
                ? 'border-orange-500 text-orange-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            Attendance
          </button>
          <button
            onClick={() => setActiveTab('payments')}
            className={`pb-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'payments'
                ? 'border-orange-500 text-orange-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            Payments
          </button>
          <button
            onClick={() => setActiveTab('profile')}
            className={`pb-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'profile'
                ? 'border-orange-500 text-orange-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            Profile
          </button>
          <button
            onClick={() => navigate('/member/messages')}
            className={`pb-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'messages'
                ? 'border-orange-500 text-orange-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            Messages
          </button>
        </div>

        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="space-y-6">
            {/* Membership Card */}
            <div className="bg-gradient-to-r from-orange-500 to-orange-600 rounded-2xl p-6 text-white shadow-lg">
              <div className="flex justify-between items-start">
                <div>
                  <h2 className="text-lg font-semibold mb-1">Membership Card</h2>
                  <p className="text-orange-100 text-sm">{member.membership_plan_name || 'Standard Plan'}</p>
                </div>
                <IdentificationIcon className="w-8 h-8 text-orange-200" />
              </div>
              <div className="mt-6 grid grid-cols-2 gap-4">
                <div>
                  <p className="text-orange-100 text-xs uppercase tracking-wider">Member ID</p>
                  <p className="font-mono text-lg">{member.member_id}</p>
                </div>
                <div>
                  <p className="text-orange-100 text-xs uppercase tracking-wider">Status</p>
                  <p className="font-semibold">{member.status}</p>
                </div>
                <div>
                  <p className="text-orange-100 text-xs uppercase tracking-wider">Start Date</p>
                  <p className="font-semibold">{formatDate(member.membership_start_date)}</p>
                </div>
                <div>
                  <p className="text-orange-100 text-xs uppercase tracking-wider">End Date</p>
                  <p className="font-semibold">{formatDate(member.membership_end_date)}</p>
                </div>
              </div>
              {membership.is_expiring_soon && (
                <div className="mt-4 bg-orange-700/50 rounded-lg p-3 flex items-center gap-2">
                  <ExclamationTriangleIcon className="w-5 h-5" />
                  <p className="text-sm">
                    Your membership expires in {membership.remaining_days} days. Please renew soon.
                  </p>
                </div>
              )}
            </div>

            {/* Quick Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-white border border-gray-200 rounded-xl p-6">
                <div className="flex items-center gap-3">
                  <div className="bg-blue-100 p-3 rounded-lg">
                    <CalendarIcon className="w-6 h-6 text-blue-600" />
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Total Visits</p>
                    <p className="text-2xl font-bold text-gray-900">{attendance.total_visits}</p>
                  </div>
                </div>
              </div>
              <div className="bg-white border border-gray-200 rounded-xl p-6">
                <div className="flex items-center gap-3">
                  <div className="bg-green-100 p-3 rounded-lg">
                    <CurrencyDollarIcon className="w-6 h-6 text-green-600" />
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Total Paid</p>
                    <p className="text-2xl font-bold text-gray-900">{formatCurrency(payments.total_paid)}</p>
                  </div>
                </div>
              </div>
              <div className="bg-white border border-gray-200 rounded-xl p-6">
                <div className="flex items-center gap-3">
                  <div className="bg-purple-100 p-3 rounded-lg">
                    <ClockIcon className="w-6 h-6 text-purple-600" />
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Monthly Visits</p>
                    <p className="text-2xl font-bold text-gray-900">{attendance.monthly_visits}</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Today's Status */}
            <div className="bg-white border border-gray-200 rounded-xl p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Today's Status</h3>
              <div className="flex items-center gap-4">
                <div className={`p-4 rounded-lg ${
                  attendance.today_status === 'Checked In' 
                    ? 'bg-green-100' 
                    : 'bg-gray-100'
                }`}>
                  {attendance.today_status === 'Checked In' ? (
                    <CheckCircleIcon className="w-8 h-8 text-green-600" />
                  ) : (
                    <ClockIcon className="w-8 h-8 text-gray-600" />
                  )}
                </div>
                <div className="flex-1">
                  <p className="text-sm text-gray-600">Attendance Status</p>
                  <p className="text-xl font-bold text-gray-900">{attendance.today_status}</p>
                  {attendance.last_check_in && (
                    <p className="text-sm text-gray-500">
                      Last check-in: {formatDateTime(attendance.last_check_in)}
                    </p>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Attendance Tab */}
        {activeTab === 'attendance' && (
          <div className="space-y-6">
            <div className="bg-white border border-gray-200 rounded-xl p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Attendance History</h3>
              {attendance.history.length === 0 ? (
                <p className="text-gray-500 text-center py-8">No attendance records found</p>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-gray-200">
                        <th className="text-left py-3 px-4 text-sm font-semibold text-gray-600">Date</th>
                        <th className="text-left py-3 px-4 text-sm font-semibold text-gray-600">Check In</th>
                        <th className="text-left py-3 px-4 text-sm font-semibold text-gray-600">Check Out</th>
                        <th className="text-left py-3 px-4 text-sm font-semibold text-gray-600">Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {attendance.history.map((record) => (
                        <tr key={record.id} className="border-b border-gray-100">
                          <td className="py-3 px-4 text-sm text-gray-900">{formatDate(record.attendance_date)}</td>
                          <td className="py-3 px-4 text-sm text-gray-900">{formatDateTime(record.check_in_time)}</td>
                          <td className="py-3 px-4 text-sm text-gray-900">
                            {record.check_out_time ? formatDateTime(record.check_out_time) : '-'}
                          </td>
                          <td className="py-3 px-4">
                            <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                              record.status === 'Checked In' 
                                ? 'bg-green-100 text-green-800' 
                                : 'bg-gray-100 text-gray-800'
                            }`}>
                              {record.status}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Payments Tab */}
        {activeTab === 'payments' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-white border border-gray-200 rounded-xl p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Total Paid</h3>
                <p className="text-3xl font-bold text-green-600">{formatCurrency(payments.total_paid)}</p>
              </div>
              <div className="bg-white border border-gray-200 rounded-xl p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Pending Amount</h3>
                <p className="text-3xl font-bold text-orange-600">{formatCurrency(payments.pending_amount)}</p>
              </div>
            </div>

            <div className="bg-white border border-gray-200 rounded-xl p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Payment History</h3>
              {payments.history.length === 0 ? (
                <p className="text-gray-500 text-center py-8">No payment records found</p>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-gray-200">
                        <th className="text-left py-3 px-4 text-sm font-semibold text-gray-600">Date</th>
                        <th className="text-left py-3 px-4 text-sm font-semibold text-gray-600">Amount</th>
                        <th className="text-left py-3 px-4 text-sm font-semibold text-gray-600">Method</th>
                        <th className="text-left py-3 px-4 text-sm font-semibold text-gray-600">Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {payments.history.map((payment) => (
                        <tr key={payment.id} className="border-b border-gray-100">
                          <td className="py-3 px-4 text-sm text-gray-900">{formatDate(payment.payment_date)}</td>
                          <td className="py-3 px-4 text-sm font-semibold text-gray-900">
                            {formatCurrency(payment.payment_amount)}
                          </td>
                          <td className="py-3 px-4 text-sm text-gray-900">{payment.payment_method}</td>
                          <td className="py-3 px-4">
                            <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                              payment.payment_status === 'Paid' 
                                ? 'bg-green-100 text-green-800' 
                                : 'bg-orange-100 text-orange-800'
                            }`}>
                              {payment.payment_status}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Profile Tab */}
        {activeTab === 'profile' && (
          <div className="space-y-6">
            <div className="bg-white border border-gray-200 rounded-xl p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Profile Information</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-600 mb-1">Full Name</label>
                  <p className="text-gray-900">{member.first_name} {member.last_name}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-600 mb-1">Email</label>
                  <p className="text-gray-900">{member.email}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-600 mb-1">Phone</label>
                  <p className="text-gray-900">{member.phone}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-600 mb-1">Member ID</label>
                  <p className="text-gray-900 font-mono">{member.member_id}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-600 mb-1">Date of Birth</label>
                  <p className="text-gray-900">{formatDate(member.date_of_birth)}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-600 mb-1">Gender</label>
                  <p className="text-gray-900">{member.gender || '-'}</p>
                </div>
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-600 mb-1">Address</label>
                  <p className="text-gray-900">{member.address || '-'}</p>
                </div>
              </div>
            </div>

            <div className="bg-white border border-gray-200 rounded-xl p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Account Settings</h3>
              <div className="space-y-4">
                <button
                  onClick={() => navigate('/member/messages')}
                  className="w-full flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <ChatBubbleLeftIcon className="w-5 h-5 text-gray-600" />
                    <span className="font-medium text-gray-900">View Messages</span>
                  </div>
                  <span className="text-gray-400">→</span>
                </button>
                <button className="w-full flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors opacity-50 cursor-not-allowed">
                  <div className="flex items-center gap-3">
                    <BellIcon className="w-5 h-5 text-gray-600" />
                    <span className="font-medium text-gray-900">Notifications</span>
                  </div>
                  <span className="text-gray-400">Coming Soon</span>
                </button>
              </div>
            </div>

            <div className="bg-white border border-gray-200 rounded-xl p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Emergency Contact</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-600 mb-1">Contact Name</label>
                  <p className="text-gray-900">{member.emergency_contact_name || '-'}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-600 mb-1">Contact Phone</label>
                  <p className="text-gray-900">{member.emergency_contact_phone || '-'}</p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
      
      <Footer />
    </div>
  );
}
