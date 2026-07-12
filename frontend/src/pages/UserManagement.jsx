import React, { useState, useEffect } from 'react';
import { AdminDataTable, AdminMetricCard } from '../components/admin';
import api from '../services/api';
import {
  UsersIcon,
  CheckCircleIcon,
  XCircleIcon,
  ShieldCheckIcon
} from '@heroicons/react/24/outline';

const UserManagement = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    role: '',
    status: '',
    gym_id: '',
    search: ''
  });
  const [metrics, setMetrics] = useState({ total: 0, active: 0, inactive: 0, super_admins: 0 });

  useEffect(() => {
    fetchUsers();
  }, [filters]);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      Object.entries(filters).forEach(([key, value]) => {
        if (value) params.append(key, value);
      });

      // Fetch users from real API endpoint
      const [usersRes, analyticsRes] = await Promise.all([
        api.get(`/api/admin/users?${params.toString()}`),
        api.get('/api/admin/users/analytics')
      ]);

      setUsers(usersRes.data.users || []);
      
      // Set metrics from analytics endpoint
      const analytics = analyticsRes.data.activity_metrics;
      setMetrics({
        total: analytics.total_users,
        active: analytics.active_users_last_week,
        inactive: analytics.total_users - analytics.active_users_last_week,
        super_admins: analytics.super_admins
      });
    } catch (err) {
      console.error('Failed to load users:', err);
      setError(err.response?.data?.error || 'Failed to load users');
    } finally {
      setLoading(false);
    }
  };

  const columns = [
    { key: 'name', label: 'Name' },
    { key: 'email', label: 'Email' },
    { 
      key: 'role', 
      label: 'Role',
      render: (value) => (
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
          value === 'super_admin' ? 'bg-red-100 text-red-800' :
          value === 'gym_owner' ? 'bg-blue-100 text-blue-800' :
          'bg-gray-100 text-gray-800'
        }`}>
          {value.replace('_', ' ').toUpperCase()}
        </span>
      )
    },
    { key: 'gym_name', label: 'Gym' },
    { 
      key: 'status', 
      label: 'Status',
      render: (value) => {
        const statusColors = {
          'Active': 'bg-green-100 text-green-800',
          'Inactive': 'bg-gray-100 text-gray-800',
          'Suspended': 'bg-red-100 text-red-800'
        };
        
        return (
          <span className={`px-2 py-1 rounded-full text-xs font-medium ${statusColors[value] || 'bg-gray-100 text-gray-800'}`}>
            {value || 'Unknown'}
          </span>
        );
      }
    },
    {
      key: 'last_login_at',
      label: 'Last Login',
      render: (value) => value ? new Date(value).toLocaleString() : 'Never'
    }
  ];

  const filterOptions = [
    {
      key: 'role',
      label: 'Role',
      options: [
        { value: 'super_admin', label: 'Super Admin' },
        { value: 'gym_owner', label: 'Gym Owner' },
        { value: 'member', label: 'Member' }
      ]
    },
    {
      key: 'status',
      label: 'Status',
      options: [
        { value: 'all', label: 'All Status' },
        { value: 'Active', label: 'Active' },
        { value: 'Inactive', label: 'Inactive' },
        { value: 'Suspended', label: 'Suspended' }
      ]
    }
  ];

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-7xl mx-auto">
          <div className="bg-red-50 border border-red-200 rounded-2xl p-8 text-center">
            <h2 className="text-xl font-semibold text-red-900 mb-2">Error Loading Users</h2>
            <p className="text-red-700 mb-4">{error}</p>
            <button onClick={fetchUsers} className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600">
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
        <div className="bg-white rounded-2xl border border-gray-200 p-6 shadow-sm">
          <h1 className="text-3xl font-bold text-gray-900 mb-2 flex items-center gap-2">
            <UsersIcon className="w-8 h-8" />
            User Management
          </h1>
          <p className="text-gray-600">Manage user accounts across all gyms on the platform</p>
        </div>

        <section>
          <h2 className="text-xl font-semibold text-gray-900 mb-4">User Overview</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <AdminMetricCard title="Total Users" value={metrics.total} icon={<UsersIcon className="w-6 h-6" />} color="blue" />
            <AdminMetricCard title="Active Users" value={metrics.active} icon={<CheckCircleIcon className="w-6 h-6" />} color="green" />
            <AdminMetricCard title="Inactive Users" value={metrics.inactive} icon={<XCircleIcon className="w-6 h-6" />} color="red" />
            <AdminMetricCard title="Super Admins" value={metrics.super_admins} icon={<ShieldCheckIcon className="w-6 h-6" />} color="orange" />
          </div>
        </section>

        <section>
          <h2 className="text-xl font-semibold text-gray-900 mb-4">All Users</h2>
          <AdminDataTable
            data={users}
            columns={columns}
            searchable={true}
            sortable={true}
            filterable={true}
            filters={filterOptions}
            loading={loading}
            emptyMessage="No users found"
          />
        </section>
      </div>
    </div>
  );
};

export default UserManagement;