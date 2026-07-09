import React, { useState, useEffect } from 'react';
import { AdminDataTable, AdminMetricCard, AdminActionModal } from '../components/admin';
import api from '../services/api';
import {
  BuildingOfficeIcon,
  ArrowPathIcon,
  CheckCircleIcon,
  ClockIcon,
  NoSymbolIcon,
  ExclamationTriangleIcon,
  XMarkIcon
} from '@heroicons/react/24/outline';

/**
 * Super Admin Gym Management interface
 * Handles gym approval, suspension, reactivation, and deletion workflows
 */
const GymManagement = () => {
  const [gyms, setGyms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedGym, setSelectedGym] = useState(null);
  const [actionModal, setActionModal] = useState({ isOpen: false, type: null, gym: null });
  const [actionLoading, setActionLoading] = useState(false);
  
  // Filters and pagination
  const [filters, setFilters] = useState({
    status: '',
    search: '',
    page: 1,
    per_page: 20
  });
  const [pagination, setPagination] = useState(null);
  const [metrics, setMetrics] = useState(null);

  // Fetch gyms data
  useEffect(() => {
    fetchGyms();
  }, [filters]);

  // Fetch platform metrics for summary cards
  useEffect(() => {
    fetchMetrics();
  }, []);

  const fetchGyms = async () => {
    try {
      setLoading(true);
      setError(null);

      const params = new URLSearchParams();
      if (filters.status) params.append('status', filters.status);
      if (filters.search) params.append('q', filters.search);
      params.append('page', filters.page);
      params.append('per_page', filters.per_page);

      const response = await api.get(`/api/admin/gyms?${params}`);
      
      setGyms(response.data.gyms);
      setPagination(response.data.pagination);
    } catch (err) {
      console.error('Failed to fetch gyms:', err);
      setError(err.response?.data?.error || 'Failed to load gyms');
    } finally {
      setLoading(false);
    }
  };

  const fetchMetrics = async () => {
    try {
      const response = await api.get('/api/admin/dashboard/analytics');
      setMetrics(response.data.platform_metrics);
    } catch (err) {
      console.error('Failed to fetch metrics:', err);
    }
  };

  const handleSearch = (searchTerm) => {
    setFilters(prev => ({ ...prev, search: searchTerm, page: 1 }));
  };

  const handleStatusFilter = (status) => {
    setFilters(prev => ({ ...prev, status, page: 1 }));
  };

  const openActionModal = (type, gym) => {
    setActionModal({ isOpen: true, type, gym });
  };

  const closeActionModal = () => {
    setActionModal({ isOpen: false, type: null, gym: null });
    setActionLoading(false);
  };

  const handleGymAction = async (action, gymId, additionalData = {}) => {
    try {
      setActionLoading(true);
      
      let endpoint = `/api/admin/gyms/${gymId}`;
      let method = 'PUT';
      
      switch (action) {
        case 'approve':
          endpoint += '/approve';
          break;
        case 'suspend':
          endpoint += '/suspend';
          break;
        case 'reactivate':
          endpoint += '/reactivate';
          break;
        case 'delete':
          method = 'DELETE';
          break;
        default:
          throw new Error('Invalid action');
      }

      const response = await api[method.toLowerCase()](endpoint, additionalData);
      
      // Update the gym in the local state
      setGyms(prev => prev.map(gym => 
        gym.id === gymId ? { ...gym, ...response.data.gym } : gym
      ));
      
      // Refresh metrics
      fetchMetrics();
      
      closeActionModal();
      
      // Show success message (you could add a toast notification here)
      console.log(`Gym ${action} successful:`, response.data.message);
      
    } catch (err) {
      console.error(`Failed to ${action} gym:`, err);
      setError(err.response?.data?.error || `Failed to ${action} gym`);
      setActionLoading(false);
    }
  };

  const getActionModalConfig = () => {
    const { type, gym } = actionModal;
    
    switch (type) {
      case 'approve':
        return {
          title: 'Approve Gym Registration',
          message: `Are you sure you want to approve "${gym?.name}"? This will activate their account and allow them to access the platform.`,
          confirmText: 'Approve Gym',
          cancelText: 'Cancel',
          type: 'info',
          onConfirm: () => handleGymAction('approve', gym.id)
        };
        
      case 'suspend':
        return {
          title: 'Suspend Gym Account',
          message: `Are you sure you want to suspend "${gym?.name}"? This will prevent all users from this gym from accessing the platform.`,
          confirmText: 'Suspend Gym',
          cancelText: 'Keep Active',
          type: 'warning',
          onConfirm: () => handleGymAction('suspend', gym.id, { reason: 'Suspended by Super Admin' })
        };
        
      case 'reactivate':
        return {
          title: 'Reactivate Gym Account',
          message: `Are you sure you want to reactivate "${gym?.name}"? This will restore full platform access for this gym.`,
          confirmText: 'Reactivate Gym',
          cancelText: 'Keep Suspended',
          type: 'info',
          onConfirm: () => handleGymAction('reactivate', gym.id)
        };
        
      case 'delete':
        return {
          title: 'Delete Gym Account',
          message: `Are you sure you want to delete "${gym?.name}"? This action cannot be undone and will remove all gym data.`,
          confirmText: 'Delete Gym',
          cancelText: 'Cancel',
          type: 'danger',
          onConfirm: () => handleGymAction('delete', gym.id)
        };
        
      default:
        return {};
    }
  };

  // Table columns configuration
  const gymColumns = [
    { 
      key: 'name', 
      label: 'Gym Name',
      render: (value, row) => (
        <div>
          <div className="font-medium text-gray-900">{value}</div>
          <div className="text-sm text-gray-500">{row.address}</div>
        </div>
      )
    },
    { 
      key: 'owner_name', 
      label: 'Owner',
      render: (value, row) => (
        <div>
          <div className="font-medium text-gray-900">{value}</div>
          <div className="text-sm text-gray-500">{row.owner_email}</div>
        </div>
      )
    },
    { 
      key: 'status', 
      label: 'Status',
      render: (value) => {
        const statusColors = {
          'Active': 'bg-green-100 text-green-800',
          'Pending': 'bg-yellow-100 text-yellow-800',
          'Suspended': 'bg-red-100 text-red-800',
          'Deleted': 'bg-gray-100 text-gray-800'
        };
        
        return (
          <span className={`px-2 py-1 rounded-full text-xs font-medium ${statusColors[value] || 'bg-gray-100 text-gray-800'}`}>
            {value}
          </span>
        );
      }
    },
    { 
      key: 'created_at', 
      label: 'Registered',
      render: (value) => new Date(value).toLocaleDateString()
    },
    { 
      key: 'id', 
      label: 'Actions',
      sortable: false,
      render: (value, row) => (
        <div className="flex gap-2">
          {row.status === 'Pending' && (
            <button
              onClick={() => openActionModal('approve', row)}
              className="px-3 py-1 text-xs font-medium text-green-700 bg-green-50 border border-green-200 rounded-lg hover:bg-green-100 transition-colors"
            >
              Approve
            </button>
          )}
          
          {row.status === 'Active' && (
            <button
              onClick={() => openActionModal('suspend', row)}
              className="px-3 py-1 text-xs font-medium text-yellow-700 bg-yellow-50 border border-yellow-200 rounded-lg hover:bg-yellow-100 transition-colors"
            >
              Suspend
            </button>
          )}
          
          {row.status === 'Suspended' && (
            <button
              onClick={() => openActionModal('reactivate', row)}
              className="px-3 py-1 text-xs font-medium text-blue-700 bg-blue-50 border border-blue-200 rounded-lg hover:bg-blue-100 transition-colors"
            >
              Reactivate
            </button>
          )}
          
          {['Suspended', 'Pending'].includes(row.status) && (
            <button
              onClick={() => openActionModal('delete', row)}
              className="px-3 py-1 text-xs font-medium text-red-700 bg-red-50 border border-red-200 rounded-lg hover:bg-red-100 transition-colors"
            >
              Delete
            </button>
          )}
        </div>
      )
    }
  ];

  // Status filter options
  const statusFilters = [
    { key: 'status', label: 'Status', options: [
      { value: 'Active', label: 'Active' },
      { value: 'Pending', label: 'Pending' },
      { value: 'Suspended', label: 'Suspended' },
      { value: 'Deleted', label: 'Deleted' }
    ]}
  ];

  const modalConfig = getActionModalConfig();

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="bg-white rounded-2xl border border-gray-200 p-6 shadow-sm">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2 flex items-center gap-2">
                <BuildingOfficeIcon className="w-8 h-8" />
                Gym Management
              </h1>
              <p className="text-gray-600">
                Manage gym registrations, approvals, and account status across the platform
              </p>
            </div>
            <button
              onClick={fetchGyms}
              disabled={loading}
              className="px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 disabled:opacity-50 transition-colors flex items-center gap-2"
            >
              <ArrowPathIcon className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </button>
          </div>
        </div>

        {/* Metrics Overview */}
        {metrics && (
          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Platform Overview</h2>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <AdminMetricCard
                title="Total Gyms"
                value={metrics.total_gyms}
                subtitle="All registered"
                icon={<BuildingOfficeIcon className="w-6 h-6" />}
                color="blue"
              />
              
              <AdminMetricCard
                title="Active Gyms"
                value={metrics.active_gyms}
                subtitle="Currently operational"
                icon={<CheckCircleIcon className="w-6 h-6" />}
                color="green"
              />
              
              <AdminMetricCard
                title="Pending Approval"
                value={metrics.pending_gyms}
                subtitle="Awaiting review"
                icon={<ClockIcon className="w-6 h-6" />}
                trend={metrics.pending_gyms > 5 ? 'High Priority' : 'Normal'}
                trendDirection={metrics.pending_gyms > 5 ? 'down' : 'neutral'}
                color="yellow"
              />
              
              <AdminMetricCard
                title="Suspended"
                value={metrics.suspended_gyms}
                subtitle="Temporarily disabled"
                icon={<NoSymbolIcon className="w-6 h-6" />}
                color="red"
              />
            </div>
          </section>
        )}

        {/* Error Display */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-2xl p-4">
            <div className="flex items-center gap-3">
              <ExclamationTriangleIcon className="w-6 h-6 text-red-500" />
              <div>
                <h3 className="font-medium text-red-900">Error</h3>
                <p className="text-red-700 text-sm">{error}</p>
              </div>
              <button
                onClick={() => setError(null)}
                className="ml-auto text-red-400 hover:text-red-600"
              >
                <XMarkIcon className="w-5 h-5" />
              </button>
            </div>
          </div>
        )}

        {/* Gym Management Table */}
        <section>
          <h2 className="text-xl font-semibold text-gray-900 mb-4">All Gyms</h2>
          <AdminDataTable
            data={gyms}
            columns={gymColumns}
            searchable={true}
            sortable={true}
            filterable={true}
            filters={statusFilters}
            loading={loading}
            emptyMessage="No gyms found"
            onRowClick={(gym) => setSelectedGym(gym)}
            className="cursor-pointer"
          />
        </section>

        {/* Pagination */}
        {pagination && (
          <div className="bg-white rounded-2xl border border-gray-200 p-4">
            <div className="flex items-center justify-between">
              <div className="text-sm text-gray-600">
                Showing {((pagination.page - 1) * pagination.per_page) + 1} to {Math.min(pagination.page * pagination.per_page, pagination.total)} of {pagination.total} gyms
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setFilters(prev => ({ ...prev, page: prev.page - 1 }))}
                  disabled={!pagination.has_prev}
                  className="px-3 py-1 text-sm border border-gray-200 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
                >
                  Previous
                </button>
                <span className="px-3 py-1 text-sm font-medium">
                  {pagination.page} of {pagination.pages}
                </span>
                <button
                  onClick={() => setFilters(prev => ({ ...prev, page: prev.page + 1 }))}
                  disabled={!pagination.has_next}
                  className="px-3 py-1 text-sm border border-gray-200 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
                >
                  Next
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Action Confirmation Modal */}
      <AdminActionModal
        isOpen={actionModal.isOpen}
        onClose={closeActionModal}
        onConfirm={modalConfig.onConfirm}
        title={modalConfig.title}
        message={modalConfig.message}
        confirmText={modalConfig.confirmText}
        cancelText={modalConfig.cancelText}
        type={modalConfig.type}
        loading={actionLoading}
      >
        {actionModal.type === 'delete' && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-3 mt-3">
            <p className="text-sm text-red-800">
              <strong>Warning:</strong> This action will permanently delete all gym data including members, payments, and attendance records. This cannot be undone.
            </p>
          </div>
        )}
        
        {actionModal.type === 'suspend' && (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 mt-3">
            <p className="text-sm text-yellow-800">
              <strong>Note:</strong> Suspending this gym will immediately prevent all users from accessing their accounts. You can reactivate the gym later to restore access.
            </p>
          </div>
        )}
      </AdminActionModal>
    </div>
  );
};

export default GymManagement;