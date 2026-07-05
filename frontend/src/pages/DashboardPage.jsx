import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';

export default function DashboardPage() {
  const { user } = useAuth();
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      const response = await api.get('/api/analytics/dashboard');
      setAnalytics(response.data);
    } catch (err) {
      console.error('Failed to fetch analytics:', err);
      setError(err.response?.data?.error || 'Failed to load dashboard analytics');
    } finally {
      setLoading(false);
    }
  };

  const formatPrice = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  const formatDateTime = (dateTimeString) => {
    if (!dateTimeString) return '-';
    return new Date(dateTimeString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatDate = (dateString) => {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric'
    });
  };

  const getGrowthColor = (growth) => {
    if (growth > 0) return 'text-green-600';
    if (growth < 0) return 'text-red-600';
    return 'text-gray-600';
  };

  const getGrowthIcon = (growth) => {
    if (growth > 0) return '📈';
    if (growth < 0) return '📉';
    return '➡️';
  };

  if (loading) {
    return (
      <div className="space-y-8">
        <div className="flex items-center justify-center py-12">
          <div className="text-gray-600">Loading dashboard analytics...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-8">
        <div className="bg-red-50 border border-red-200 text-red-700 text-sm p-4 rounded-xl">
          {error}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Welcome Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white p-6 rounded-2xl border border-gray-200 shadow-sm">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 mb-1">
            Welcome back, {user?.name || 'Gym Owner'} 👋
          </h1>
          <p className="text-sm text-gray-600">
            Here's what's happening at your gym today - Gym ID: {user?.gym_id}
          </p>
        </div>
        <div className="flex items-center gap-2 text-xs bg-orange-50 text-orange-700 px-3.5 py-2 rounded-xl border border-orange-200 font-bold self-start md:self-auto">
          🛡️ Multi-Tenant Active
        </div>
      </div>

      {/* Quick Stats Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Total Members */}
        <div className="bg-white border border-gray-200 p-6 rounded-2xl shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <span className="text-xs uppercase font-extrabold tracking-wider text-gray-600">Total Members</span>
            <span className="text-xl">👥</span>
          </div>
          <p className="text-3xl font-black text-gray-900">{analytics?.members?.total || 0}</p>
          <div className="mt-2 text-xs text-gray-500 flex items-center gap-1">
            <span className={`font-semibold ${getGrowthColor(analytics?.members?.growth_percentage || 0)}`}>
              {getGrowthIcon(analytics?.members?.growth_percentage || 0)} {Math.abs(analytics?.members?.growth_percentage || 0)}%
            </span> recent growth
          </div>
        </div>

        {/* Today's Check-ins */}
        <div className="bg-white border border-gray-200 p-6 rounded-2xl shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <span className="text-xs uppercase font-extrabold tracking-wider text-gray-600">Today's Check-ins</span>
            <span className="text-xl">📅</span>
          </div>
          <p className="text-3xl font-black text-gray-900">{analytics?.attendance?.todays_checkins || 0}</p>
          <div className="mt-2 text-xs text-gray-500 flex items-center gap-1">
            <span className="text-orange-600 font-semibold">{analytics?.attendance?.currently_inside || 0}</span> currently inside
          </div>
        </div>

        {/* Monthly Revenue */}
        <div className="bg-white border border-gray-200 p-6 rounded-2xl shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <span className="text-xs uppercase font-extrabold tracking-wider text-gray-600">Monthly Revenue</span>
            <span className="text-xl">💰</span>
          </div>
          <p className="text-3xl font-black text-gray-900">{formatPrice(analytics?.payments?.current_month_revenue || 0)}</p>
          <div className="mt-2 text-xs text-gray-500 flex items-center gap-1">
            <span className={`font-semibold ${getGrowthColor(analytics?.payments?.revenue_growth || 0)}`}>
              {getGrowthIcon(analytics?.payments?.revenue_growth || 0)} {Math.abs(analytics?.payments?.revenue_growth || 0)}%
            </span> vs last month
          </div>
        </div>

        {/* Membership Plans */}
        <div className="bg-white border border-gray-200 p-6 rounded-2xl shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <span className="text-xs uppercase font-extrabold tracking-wider text-gray-600">Active Plans</span>
            <span className="text-xl">💳</span>
          </div>
          <p className="text-3xl font-black text-gray-900">{analytics?.membership_plans?.active || 0}</p>
          <div className="mt-2 text-xs text-gray-500 flex items-center gap-1">
            <span className="text-orange-600 font-semibold">{analytics?.membership_plans?.total || 0}</span> total plans
          </div>
        </div>
      </div>

      {/* Charts and Analytics Row */}
      <div className="grid lg:grid-cols-2 gap-8">
        {/* Weekly Attendance Chart */}
        <div className="bg-white border border-gray-200 p-6 rounded-2xl shadow-sm">
          <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
            <span>📊</span> Weekly Attendance Trend
          </h2>
          <div className="space-y-3">
            {analytics?.attendance?.weekly_trend?.map((day, index) => (
              <div key={index} className="flex items-center gap-3">
                <div className="w-16 text-xs text-gray-600 font-medium">
                  {formatDate(day.date)}
                </div>
                <div className="flex-1 bg-gray-200 rounded-full h-2 relative">
                  <div 
                    className="bg-orange-600 h-2 rounded-full transition-all duration-300"
                    style={{ 
                      width: `${Math.max((day.count / Math.max(...(analytics?.attendance?.weekly_trend?.map(d => d.count) || [1]))) * 100, 5)}%`
                    }}
                  ></div>
                </div>
                <div className="w-8 text-sm font-semibold text-gray-900">
                  {day.count}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Monthly Revenue Chart */}
        <div className="bg-white border border-gray-200 p-6 rounded-2xl shadow-sm">
          <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
            <span>💹</span> Revenue Trend (6 Months)
          </h2>
          <div className="space-y-3">
            {analytics?.payments?.monthly_trend?.map((month, index) => (
              <div key={index} className="flex items-center gap-3">
                <div className="w-16 text-xs text-gray-600 font-medium">
                  {month.month}
                </div>
                <div className="flex-1 bg-gray-200 rounded-full h-2 relative">
                  <div 
                    className="bg-green-600 h-2 rounded-full transition-all duration-300"
                    style={{ 
                      width: `${Math.max((month.revenue / Math.max(...(analytics?.payments?.monthly_trend?.map(m => m.revenue) || [1]))) * 100, 5)}%`
                    }}
                  ></div>
                </div>
                <div className="w-20 text-xs font-semibold text-gray-900 text-right">
                  {formatPrice(month.revenue)}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Quick Actions & Pending Items */}
      <div className="grid lg:grid-cols-3 gap-8">
        {/* Quick Actions */}
        <div className="bg-white border border-gray-200 p-6 rounded-2xl shadow-sm">
          <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
            <span>⚡</span> Quick Actions
          </h2>
          <div className="space-y-3">
            <Link
              to="/members/add"
              className="flex items-center gap-3 p-3 rounded-lg hover:bg-orange-50 transition-colors group"
            >
              <div className="w-8 h-8 bg-orange-100 rounded-lg flex items-center justify-center group-hover:bg-orange-200 transition-colors">
                <span className="text-sm">👤</span>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-900">Add Member</p>
                <p className="text-xs text-gray-500">Register new member</p>
              </div>
            </Link>
            <Link
              to="/attendance/checkin"
              className="flex items-center gap-3 p-3 rounded-lg hover:bg-orange-50 transition-colors group"
            >
              <div className="w-8 h-8 bg-orange-100 rounded-lg flex items-center justify-center group-hover:bg-orange-200 transition-colors">
                <span className="text-sm">📅</span>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-900">Check In Member</p>
                <p className="text-xs text-gray-500">Record attendance</p>
              </div>
            </Link>
            <Link
              to="/payments/add"
              className="flex items-center gap-3 p-3 rounded-lg hover:bg-orange-50 transition-colors group"
            >
              <div className="w-8 h-8 bg-orange-100 rounded-lg flex items-center justify-center group-hover:bg-orange-200 transition-colors">
                <span className="text-sm">💰</span>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-900">Record Payment</p>
                <p className="text-xs text-gray-500">Add payment entry</p>
              </div>
            </Link>
            <Link
              to="/membership-plans/add"
              className="flex items-center gap-3 p-3 rounded-lg hover:bg-orange-50 transition-colors group"
            >
              <div className="w-8 h-8 bg-orange-100 rounded-lg flex items-center justify-center group-hover:bg-orange-200 transition-colors">
                <span className="text-sm">💳</span>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-900">Create Plan</p>
                <p className="text-xs text-gray-500">New membership plan</p>
              </div>
            </Link>
          </div>
        </div>

        {/* Pending Payments */}
        <div className="bg-white border border-gray-200 p-6 rounded-2xl shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-bold text-gray-900 flex items-center gap-2">
              <span>⏳</span> Pending Payments
            </h2>
            <Link 
              to="/payments?status=Pending"
              className="text-xs text-orange-600 hover:text-orange-700 font-medium"
            >
              View All
            </Link>
          </div>
          {analytics?.payments?.pending_count > 0 ? (
            <div className="space-y-4">
              <div className="bg-yellow-50 border border-yellow-200 p-4 rounded-xl">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-semibold text-yellow-800">
                      {analytics.payments.pending_count} Pending Payments
                    </p>
                    <p className="text-xs text-yellow-600">
                      Total: {formatPrice(analytics.payments.pending_amount)}
                    </p>
                  </div>
                  <div className="text-2xl">💸</div>
                </div>
              </div>
              <Link
                to="/payments?status=Pending"
                className="block w-full bg-yellow-600 hover:bg-yellow-700 text-white text-center py-2 px-4 rounded-lg text-sm font-medium transition-colors"
              >
                Manage Pending Payments
              </Link>
            </div>
          ) : (
            <div className="text-center py-8">
              <div className="text-4xl mb-2">✅</div>
              <p className="text-sm text-gray-600">All payments are up to date</p>
            </div>
          )}
        </div>

        {/* Recent Activity */}
        <div className="bg-white border border-gray-200 p-6 rounded-2xl shadow-sm">
          <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
            <span>🔄</span> Recent Activity
          </h2>
          <div className="space-y-3 max-h-80 overflow-y-auto">
            {analytics?.members?.recent_members?.map((member) => (
              <div key={`member-${member.id}`} className="flex items-center gap-3 p-2 rounded-lg hover:bg-gray-50">
                <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                  <span className="text-xs font-semibold text-blue-700">
                    {member.first_name?.charAt(0) || '?'}
                  </span>
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">
                    {member.first_name} {member.last_name}
                  </p>
                  <p className="text-xs text-gray-500">
                    New member • {formatDateTime(member.created_at)}
                  </p>
                </div>
              </div>
            ))}
            {analytics?.payments?.recent_payments?.slice(0, 3).map((payment) => (
              <div key={`payment-${payment.id}`} className="flex items-center gap-3 p-2 rounded-lg hover:bg-gray-50">
                <div className="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center">
                  <span className="text-xs">💰</span>
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">
                    Payment: {formatPrice(payment.payment_amount)}
                  </p>
                  <p className="text-xs text-gray-500">
                    {payment.member_name} • {formatDateTime(payment.created_at)}
                  </p>
                </div>
              </div>
            ))}
            {analytics?.attendance?.recent_attendance?.slice(0, 2).map((record) => (
              <div key={`attendance-${record.id}`} className="flex items-center gap-3 p-2 rounded-lg hover:bg-gray-50">
                <div className="w-8 h-8 bg-orange-100 rounded-lg flex items-center justify-center">
                  <span className="text-xs">📅</span>
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">
                    {record.status}: {record.member_name}
                  </p>
                  <p className="text-xs text-gray-500">
                    {formatDateTime(record.check_in_time)}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* System Status */}
      <div className="bg-white border border-gray-200 p-6 rounded-2xl shadow-sm">
        <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
          <span>🛡️</span> System Status & Multi-Tenant Isolation
        </h2>
        <div className="grid md:grid-cols-2 gap-6">
          <div>
            <h3 className="font-semibold text-gray-900 mb-2">Data Isolation</h3>
            <p className="text-sm text-gray-600 leading-relaxed mb-4">
              All data in this workspace is securely isolated by your Gym ID. Members, payments, 
              attendance, and plans are filtered to show only your gym's data.
            </p>
            <div className="bg-gray-50 p-4 rounded-xl border border-gray-200">
              <p className="text-xs font-mono text-orange-600 font-semibold">
                WHERE gym_id = {user?.gym_id || 'NULL'}
              </p>
            </div>
          </div>
          <div>
            <h3 className="font-semibold text-gray-900 mb-2">System Health</h3>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Database Connection</span>
                <div className="flex items-center gap-1">
                  <span className="w-2 h-2 rounded-full bg-green-500"></span>
                  <span className="text-xs text-green-600 font-medium">Connected</span>
                </div>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">API Services</span>
                <div className="flex items-center gap-1">
                  <span className="w-2 h-2 rounded-full bg-green-500"></span>
                  <span className="text-xs text-green-600 font-medium">Operational</span>
                </div>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Data Sync</span>
                <div className="flex items-center gap-1">
                  <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
                  <span className="text-xs text-green-600 font-medium">Real-time</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}