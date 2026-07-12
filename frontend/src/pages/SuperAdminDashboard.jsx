import React, { useState, useEffect } from 'react';
import { AdminMetricCard, AdminChart, AdminDataTable } from '../components/admin';
import MobileNavigation from '../components/admin/MobileNavigation';
import { useResponsive } from '../hooks/useResponsive';
import { useCurrency } from '../utils/currency';
import NotificationBell from '../components/NotificationBell';
import api from '../services/api';
import '../styles/responsive.css';
import {
  GlobeAltIcon,
  ArrowPathIcon,
  BuildingOfficeIcon,
  UsersIcon,
  CurrencyDollarIcon,
  ClipboardDocumentListIcon,
  ClockIcon,
  NoSymbolIcon,
  CheckCircleIcon,
  UserIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';

/**
 * Super Admin Dashboard with platform-wide analytics and metrics
 */
const SuperAdminDashboard = () => {
  // Super Admin uses default currency (no gym_id)
  const { formatCurrency, setCurrencyCode } = useCurrency(null);
  const [platformMetrics, setPlatformMetrics] = useState(null);
  const [growthMetrics, setGrowthMetrics] = useState(null);
  const { isMobile, isTablet } = useResponsive();
  const [recentActivity, setRecentActivity] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);

  // Fetch all dashboard data
  useEffect(() => {
    // Force platform currency to INR for Super Admin
    setCurrencyCode('INR');
    fetchDashboardData();
    
    // Auto-refresh every 5 minutes
    const interval = setInterval(fetchDashboardData, 300000);
    return () => clearInterval(interval);
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch all data in parallel
      const [analyticsRes, growthRes, activityRes] = await Promise.all([
        api.get('/api/admin/dashboard/analytics'),
        api.get('/api/admin/dashboard/growth-metrics?days=30'),
        api.get('/api/admin/activity-logs?per_page=10')
      ]);

      setPlatformMetrics(analyticsRes.data.platform_metrics);
      setGrowthMetrics(growthRes.data);
      setRecentActivity(activityRes.data.logs);
      setLastUpdated(new Date());
    } catch (err) {
      console.error('Failed to fetch dashboard data:', err);
      setError(err.response?.data?.error || 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = () => {
    fetchDashboardData();
  };

  // Transform growth data for charts
  const getChartData = (growthData, key, label) => {
    if (!growthData || !growthData[key]) return [];
    
    return growthData[key].map(item => ({
      label: new Date(item.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
      value: key === 'revenue_growth' ? item.amount : item.count
    }));
  };

  // Activity log table columns
  const activityColumns = [
    { 
      key: 'timestamp', 
      label: 'Time',
      render: (value) => new Date(value).toLocaleString()
    },
    { key: 'action_type', label: 'Action' },
    { key: 'description', label: 'Description' },
    { 
      key: 'severity', 
      label: 'Level',
      render: (value) => (
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
          value === 'critical' ? 'bg-red-100 text-red-800' :
          value === 'warning' ? 'bg-yellow-100 text-yellow-800' :
          'bg-blue-100 text-blue-800'
        }`}>
          {value}
        </span>
      )
    }
  ];

  if (loading && !platformMetrics) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-center h-64">
            <div className="flex items-center gap-3 text-gray-600">
              <div className="animate-spin w-8 h-8 border-3 border-orange-500 border-t-transparent rounded-full"></div>
              <span className="text-lg">Loading platform analytics...</span>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error && !platformMetrics) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-7xl mx-auto">
          <div className="bg-red-50 border border-red-200 rounded-2xl p-8 text-center">
            <ExclamationTriangleIcon className="w-16 h-16 text-red-600 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-red-900 mb-2">Dashboard Error</h2>
            <p className="text-red-700 mb-4">{error}</p>
            <button
              onClick={handleRefresh}
              className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors"
            >
              Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="bg-white rounded-2xl border border-gray-200 p-6 shadow-sm">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2 flex items-center gap-2">
                <GlobeAltIcon className="w-8 h-8" />
                Platform Dashboard
              </h1>
              <p className="text-gray-600">
                Real-time analytics and platform oversight for SmartGoNext Gym SaaS
              </p>
            </div>
            <div className="flex items-center gap-4">
              <NotificationBell />
              {lastUpdated && (
                <div className="text-sm text-gray-500">
                  Last updated: {lastUpdated.toLocaleTimeString()}
                </div>
              )}
              <button
                onClick={handleRefresh}
                disabled={loading}
                className="px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 disabled:opacity-50 transition-colors flex items-center gap-2"
              >
                <ArrowPathIcon className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                Refresh
              </button>
            </div>
          </div>
        </div>

        {/* Platform Metrics Cards */}
        {platformMetrics && (
          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Platform Overview</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <AdminMetricCard
                title="Total Gyms"
                value={platformMetrics.total_gyms}
                subtitle={`${platformMetrics.active_gyms} active`}
                icon={<BuildingOfficeIcon className="w-6 h-6" />}
                trend={platformMetrics.new_gyms_7_days > 0 ? `+${platformMetrics.new_gyms_7_days} this week` : null}
                trendDirection={platformMetrics.new_gyms_7_days > 0 ? 'up' : 'neutral'}
                color="blue"
              />
              
              <AdminMetricCard
                title="Platform Members"
                value={platformMetrics.total_members}
                subtitle={`${platformMetrics.active_members} active`}
                icon={<UsersIcon className="w-6 h-6" />}
                trend={platformMetrics.new_members_7_days > 0 ? `+${platformMetrics.new_members_7_days} this week` : null}
                trendDirection={platformMetrics.new_members_7_days > 0 ? 'up' : 'neutral'}
                color="green"
              />
              
              <AdminMetricCard
                title="Monthly Revenue"
                value={formatCurrency(platformMetrics.revenue_30_days)}
                subtitle="Last 30 days"
                icon={<CurrencyDollarIcon className="w-6 h-6" />}
                color="orange"
              />
              
              <AdminMetricCard
                title="Subscriptions"
                value={platformMetrics.active_subscriptions}
                subtitle={platformMetrics.expiring_subscriptions > 0 ? 
                  `${platformMetrics.expiring_subscriptions} expiring soon` : 
                  'All current'
                }
                icon={<ClipboardDocumentListIcon className="w-6 h-6" />}
                trend={platformMetrics.expiring_subscriptions > 0 ? 
                  `${platformMetrics.expiring_subscriptions} expiring` : null}
                trendDirection={platformMetrics.expiring_subscriptions > 0 ? 'down' : 'neutral'}
                color="red"
              />
            </div>
          </section>
        )}

        {/* Platform Health Status */}
        {platformMetrics && (
          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Platform Health</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <AdminMetricCard
                title="Pending Approvals"
                value={platformMetrics.pending_gyms}
                subtitle="Gyms awaiting approval"
                icon={<ClockIcon className="w-6 h-6" />}
                trend={platformMetrics.pending_gyms > 5 ? 'High' : platformMetrics.pending_gyms > 0 ? 'Normal' : 'Clear'}
                trendDirection={platformMetrics.pending_gyms > 5 ? 'down' : 'neutral'}
                color={platformMetrics.pending_gyms > 5 ? 'red' : 'blue'}
              />
              
              <AdminMetricCard
                title="Suspended Gyms"
                value={platformMetrics.suspended_gyms}
                subtitle="Currently suspended"
                icon={<NoSymbolIcon className="w-6 h-6" />}
                color="red"
              />
              
              <AdminMetricCard
                title="System Status"
                value="Operational"
                subtitle="All services running"
                icon={<CheckCircleIcon className="w-6 h-6" />}
                color="green"
              />
            </div>
          </section>
        )}

        {/* Growth Charts */}
        {growthMetrics && (
          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Growth Analytics (30 Days)</h2>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <AdminChart
                type="line"
                data={getChartData(growthMetrics, 'gym_growth', 'Gyms')}
                title="Gym Registrations"
                subtitle="New gyms joining daily"
                height="300px"
                color="blue"
                loading={loading}
              />
              
              <AdminChart
                type="bar"
                data={getChartData(growthMetrics, 'member_growth', 'Members')}
                title="Member Growth"
                subtitle="New member registrations"
                height="300px"
                color="green"
                loading={loading}
              />
              
              <AdminChart
                type="line"
                data={getChartData(growthMetrics, 'revenue_growth', 'Revenue')}
                title="Revenue Trends"
                subtitle="Daily platform revenue"
                height="300px"
                color="orange"
                loading={loading}
              />
              
              <AdminChart
                type="pie"
                data={platformMetrics ? [
                  { label: 'Active', value: platformMetrics.active_gyms },
                  { label: 'Pending', value: platformMetrics.pending_gyms },
                  { label: 'Suspended', value: platformMetrics.suspended_gyms }
                ] : []}
                title="Gym Status Distribution"
                subtitle="Current platform status"
                height="300px"
                color="blue"
                loading={loading}
              />
            </div>
          </section>
        )}

        {/* Recent Activity */}
        <section>
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Recent Platform Activity</h2>
          <AdminDataTable
            data={recentActivity}
            columns={activityColumns}
            searchable={false}
            sortable={false}
            loading={loading}
            emptyMessage="No recent activity"
            onRowClick={(log) => console.log('Activity log:', log)}
          />
        </section>

        {/* Quick Actions */}
        <section>
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Quick Actions</h2>
          <div className="bg-white rounded-2xl border border-gray-200 p-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <button className="flex items-center gap-3 p-4 border border-gray-200 rounded-xl hover:border-orange-300 hover:bg-orange-50 transition-colors">
                <BuildingOfficeIcon className="w-10 h-10 text-orange-600" />
                <div className="text-left">
                  <div className="font-medium text-gray-900">Manage Gyms</div>
                  <div className="text-sm text-gray-600">Approve, suspend, or review gyms</div>
                </div>
              </button>
              
              <button className="flex items-center gap-3 p-4 border border-gray-200 rounded-xl hover:border-orange-300 hover:bg-orange-50 transition-colors">
                <UserIcon className="w-10 h-10 text-orange-600" />
                <div className="text-left">
                  <div className="font-medium text-gray-900">User Management</div>
                  <div className="text-sm text-gray-600">View and manage all users</div>
                </div>
              </button>
              
              <button className="flex items-center gap-3 p-4 border border-gray-200 rounded-xl hover:border-orange-300 hover:bg-orange-50 transition-colors">
                <ClipboardDocumentListIcon className="w-10 h-10 text-orange-600" />
                <div className="text-left">
                  <div className="font-medium text-gray-900">Activity Logs</div>
                  <div className="text-sm text-gray-600">Review platform activity</div>
                </div>
              </button>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
};

export default SuperAdminDashboard;