import React, { useState, useEffect } from 'react';
import { AdminDataTable, AdminActionModal, AdminMetricCard } from '../components/admin';
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
  const [modalState, setModalState] = useState({ isOpen: false, type: null, user: null });
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

      // Mock API call - would use real endpoint
      const mockUsers = [
        { id: 1, name: 'Super Admin', email: 'admin@flexigym.com', role: 'super_admin', status: 'Active', gym_name: 'Platform', last_login: '2023-12-10T10:30:00Z' },
        { id: 2, name: 'John Smith', email: 'john@fitzone.com', role: 'gym_owner', status: 'Active', gym_name: 'FitZone Gym', last_login: '2023-12-09T14:20:00Z' },
        { id: 3, name: 'Jane Doe', email: 'jane@fitzone.com', role: 'member', status: 'Active', gym_name: 'FitZone Gym', last_login: '2023-12-08T18:45:00Z' }
      ];
      
      setUsers(mockUsers);
      setMetrics({
        total: mockUsers.length,
        active: mockUsers.filter(u => u.status === 'Active').length,
        inactive: mockUsers.filter(u => u.status === 'Inactive').length,
        super_admins: mockUsers.filter(u => u.role === 'super_admin').length
      });
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to load users');
    } finally {
      setLoading(false);
    }
  };

  const handleUserAction = async (action, user) => {
    try {
      setModalState(prev => ({ ...prev, loading: true }));
      
      switch (action) {
        case 'disable':
          await api.put(`/api/admin/users/${user.id}/disable`);
          break;
        case 'enable':
          await api.put(`/api/admin/users/${user.id}/enable`);
          break;
      }
      
      await fetchUsers();
      setModalState({ isOpen: false, type: null, user: null });
    } catch (err) {
      setError(err.response?.data?.error || `Failed to ${action} user`);
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
      render: (value) => (
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
          value === 'Active' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
        }`}>
          {value}
        </span>
      )
    },
    {
      key: 'last_login',
      label: 'Last Login',
      render: (value) => value ? new Date(value).toLocaleString() : 'Never'
    },
    {
      key: 'actions',
      label: 'Actions',
      sortable: false,
      render: (_, user) => (
        <div className="flex gap-2">
          {user.status === 'Active' ? (
            <button
              onClick={(e) => {
                e.stopPropagation();
                setModalState({ isOpen: true, type: 'disable', user });
              }}
              className="px-2 py-1 bg-red-500 text-white rounded text-xs hover:bg-red-600"
            >
              Disable
            </button>
          ) : (
            <button
              onClick={(e) => {
                e.stopPropagation();
                setModalState({ isOpen: true, type: 'enable', user });
              }}
              className="px-2 py-1 bg-green-500 text-white rounded text-xs hover:bg-green-600"
            >
              Enable
            </button>
          )}
        </div>
      )
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
        { value: 'Active', label: 'Active' },
        { value: 'Inactive', label: 'Inactive' }
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

      <AdminActionModal
        isOpen={modalState.isOpen}
        onClose={() => setModalState({ isOpen: false, type: null, user: null })}
        onConfirm={() => handleUserAction(modalState.type, modalState.user)}
        title={`${modalState.type === 'disable' ? 'Disable' : 'Enable'} User`}
        message={`Are you sure you want to ${modalState.type} ${modalState.user?.name}?`}
        confirmText={modalState.type === 'disable' ? 'Disable' : 'Enable'}
        type={modalState.type === 'disable' ? 'warning' : 'info'}
      />
    </div>
  );
};

export default UserManagement;