import React, { useState, useEffect } from 'react';
import { AdminDataTable, AdminActionModal, AdminMetricCard, AdminChart } from '../components/admin';
import api from '../services/api';
import { CreditCardIcon, CheckCircleIcon, ExclamationTriangleIcon, XCircleIcon, ArrowPathIcon } from '@heroicons/react/24/outline';

/**
 * Subscription Management interface for Super Admin
 * Provides subscription oversight, billing management, and analytics
 */
const SubscriptionManagement = () => {
  const [subscriptions, setSubscriptions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [pagination, setPagination] = useState({});
  const [filters, setFilters] = useState({
    status: '',
    plan_name: '',
    expiring_soon: false,
    page: 1,
    per_page: 20
  });

  // Platform plans state
  const [plans, setPlans] = useState([]);
  const [plansLoading, setPlansLoading] = useState(false);

  // Modal states
  const [modalState, setModalState] = useState({
    isOpen: false,
    type: null,
    subscription: null,
    plan: null,
    loading: false
  });

  // Subscription metrics
  const [metrics, setMetrics] = useState({
    total: 0,
    active: 0,
    expired: 0,
    expiring_soon: 0
  });

  useEffect(() => {
    fetchSubscriptions();
    fetchPlans();
  }, [filters]);

  // Fetch platform plans
  const fetchPlans = async () => {
    try {
      setPlansLoading(true);
      const response = await api.get('/api/admin/subscription-plans');
      setPlans(response.data.plans);
    } catch (err) {
      console.error('Failed to fetch plans:', err);
    } finally {
      setPlansLoading(false);
    }
  };

  // Handle plan actions
  const openPlanModal = (type, plan = null) => {
    setModalState({
      isOpen: true,
      type,
      plan,
      subscription: null,
      loading: false
    });
  };

  const handlePlanAction = async (action, plan, formData = {}) => {
    try {
      setModalState(prev => ({ ...prev, loading: true }));

      let response;
      switch (action) {
        case 'create':
          response = await api.post('/api/admin/subscription-plans', formData);
          break;
        case 'update':
          response = await api.put(`/api/admin/subscription-plans/${plan.id}`, formData);
          break;
        case 'delete':
          response = await api.delete(`/api/admin/subscription-plans/${plan.id}`);
          break;
        default:
          throw new Error(`Unknown action: ${action}`);
      }

      await fetchPlans();
      closeModal();

      console.log(`${action} successful:`, response.data.message);

    } catch (err) {
      console.error(`Failed to ${action} plan:`, err);
      setError(err.response?.data?.error || `Failed to ${action} plan`);
      setModalState(prev => ({ ...prev, loading: false }));
    }
  };

  const fetchSubscriptions = async () => {
    try {
      setLoading(true);
      setError(null);

      const params = new URLSearchParams();
      if (filters.status) params.append('status', filters.status);
      if (filters.plan_name) params.append('plan_name', filters.plan_name);
      if (filters.expiring_soon) params.append('expiring_soon', 'true');
      params.append('page', filters.page);
      params.append('per_page', filters.per_page);

      const response = await api.get(`/api/admin/subscriptions?${params.toString()}`);
      
      setSubscriptions(response.data.subscriptions);
      setPagination(response.data.pagination);
      
      // Calculate metrics
      const counts = response.data.subscriptions.reduce(
        (acc, sub) => {
          acc.total++;
          if (sub.status === 'Active') acc.active++;
          if (sub.status === 'Expired') acc.expired++;
          if (sub.days_until_expiry <= 7 && sub.status === 'Active') acc.expiring_soon++;
          return acc;
        },
        { total: 0, active: 0, expired: 0, expiring_soon: 0 }
      );
      setMetrics(counts);
      
    } catch (err) {
      console.error('Failed to fetch subscriptions:', err);
      setError(err.response?.data?.error || 'Failed to load subscriptions');
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({
      ...prev,
      [key]: value,
      page: key !== 'page' ? 1 : value
    }));
  };

  const openModal = (type, subscription) => {
    setModalState({
      isOpen: true,
      type,
      subscription,
      loading: false
    });
  };

  const closeModal = () => {
    setModalState({
      isOpen: false,
      type: null,
      subscription: null,
      loading: false
    });
  };

  const handleSubscriptionAction = async (action, subscription, formData = {}) => {
    try {
      setModalState(prev => ({ ...prev, loading: true }));

      let response;
      
      switch (action) {
        case 'update':
          response = await api.put(`/api/admin/subscriptions/${subscription.id}`, formData);
          break;
        case 'renew':
          response = await api.put(`/api/admin/subscriptions/${subscription.id}`, {
            billing_cycle_end: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
          });
          break;
        case 'suspend':
          response = await api.put(`/api/admin/subscriptions/${subscription.id}`, {
            status: 'Suspended'
          });
          break;
        default:
          throw new Error(`Unknown action: ${action}`);
      }

      await fetchSubscriptions();
      closeModal();
      
      console.log(`${action} successful:`, response.data.message);
      
    } catch (err) {
      console.error(`Failed to ${action} subscription:`, err);
      setError(err.response?.data?.error || `Failed to ${action} subscription`);
      setModalState(prev => ({ ...prev, loading: false }));
    }
  };

  // Table columns
  const columns = [
    { key: 'gym_name', label: 'Gym Name' },
    { key: 'plan_name', label: 'Plan' },
    { 
      key: 'monthly_price', 
      label: 'Monthly Price',
      render: (value) => `$${value.toLocaleString()}`
    },
    { key: 'max_members', label: 'Member Limit' },
    { 
      key: 'current_members', 
      label: 'Current Usage',
      render: (value, row) => `${value || 0}/${row.max_members}`
    },
    { 
      key: 'status', 
      label: 'Status',
      render: (value) => (
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
          value === 'Active' ? 'bg-green-100 text-green-800' :
          value === 'Expired' ? 'bg-red-100 text-red-800' :
          value === 'Suspended' ? 'bg-yellow-100 text-yellow-800' :
          'bg-gray-100 text-gray-800'
        }`}>
          {value}
        </span>
      )
    },
    {
      key: 'next_billing_date',
      label: 'Next Billing',
      render: (value) => new Date(value).toLocaleDateString()
    },
    {
      key: 'days_until_expiry',
      label: 'Days Left',
      render: (value) => (
        <span className={`font-medium ${
          value <= 7 ? 'text-red-600' : 
          value <= 30 ? 'text-yellow-600' : 
          'text-green-600'
        }`}>
          {value} days
        </span>
      )
    },
    {
      key: 'actions',
      label: 'Actions',
      sortable: false,
      render: (_, subscription) => (
        <div className="flex gap-2">
          <button
            onClick={(e) => {
              e.stopPropagation();
              openModal('edit', subscription);
            }}
            className="px-2 py-1 bg-blue-500 text-white rounded text-xs hover:bg-blue-600"
          >
            Edit
          </button>
          
          {subscription.status === 'Active' && subscription.days_until_expiry <= 7 && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                openModal('renew', subscription);
              }}
              className="px-2 py-1 bg-green-500 text-white rounded text-xs hover:bg-green-600"
            >
              Renew
            </button>
          )}
          
          {subscription.status === 'Active' && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                openModal('suspend', subscription);
              }}
              className="px-2 py-1 bg-yellow-500 text-white rounded text-xs hover:bg-yellow-600"
            >
              Suspend
            </button>
          )}
        </div>
      )
    }
  ];

  // Filter options
  const statusFilters = [
    {
      key: 'status',
      label: 'Status',
      options: [
        { value: 'Active', label: 'Active' },
        { value: 'Expired', label: 'Expired' },
        { value: 'Suspended', label: 'Suspended' }
      ]
    }
  ];

  const renderModal = () => {
    const { type, subscription, plan } = modalState;
    
    if (!type) return null;

    if (type === 'createPlan' || type === 'editPlan' || type === 'deletePlan') {
      const modalProps = {
        isOpen: modalState.isOpen,
        onClose: closeModal,
        loading: modalState.loading
      };

      if (type === 'deletePlan') {
        return (
          <AdminActionModal
            {...modalProps}
            title="Delete Plan"
            message={`Are you sure you want to delete the plan "${plan.plan_name}"?`}
            confirmText="Delete"
            type="warning"
            onConfirm={() => handlePlanAction('delete', plan)}
          />
        );
      }

      const isCreate = type === 'createPlan';
      const defaultPlan = plan || {
        plan_name: '',
        price: '',
        currency: 'INR',
        billing_cycle: 'monthly',
        description: '',
        features: [],
        recommended: false,
        is_active: true
      };

      return (
        <AdminActionModal
          {...modalProps}
          title={isCreate ? "Create Plan" : "Edit Plan"}
          message={isCreate ? "Add a new platform subscription plan" : "Edit the subscription plan details"}
          confirmText={isCreate ? "Create Plan" : "Update Plan"}
          type="info"
          onConfirm={(formData) => {
            const processedData = {
              ...formData,
              price: parseFloat(formData.price),
              features: formData.features.split(',').map(s => s.trim()).filter(Boolean),
              recommended: formData.recommended === 'on',
              is_active: formData.is_active === 'on'
            };
            handlePlanAction(isCreate ? 'create' : 'update', plan, processedData);
          }}
        >
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Plan Name
              </label>
              <input
                type="text"
                name="plan_name"
                defaultValue={defaultPlan.plan_name}
                className="w-full p-2 border border-gray-300 rounded-md"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Price (₹)
              </label>
              <input
                type="number"
                name="price"
                defaultValue={defaultPlan.price}
                className="w-full p-2 border border-gray-300 rounded-md"
                step="0.01"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Billing Cycle
              </label>
              <select
                name="billing_cycle"
                defaultValue={defaultPlan.billing_cycle}
                className="w-full p-2 border border-gray-300 rounded-md"
              >
                <option value="monthly">Monthly</option>
                <option value="yearly">Yearly</option>
                <option value="quarterly">Quarterly</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Description
              </label>
              <textarea
                name="description"
                defaultValue={defaultPlan.description}
                className="w-full p-2 border border-gray-300 rounded-md"
                rows="3"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Features (comma separated)
              </label>
              <input
                type="text"
                name="features"
                defaultValue={defaultPlan.features?.join(', ') || ''}
                className="w-full p-2 border border-gray-300 rounded-md"
              />
            </div>
            <div className="flex items-center gap-4">
              <div className="flex items-center">
                <input
                  type="checkbox"
                  name="recommended"
                  defaultChecked={defaultPlan.recommended}
                  className="mr-2"
                />
                <label className="text-sm text-gray-700">Recommended</label>
              </div>
              <div className="flex items-center">
                <input
                  type="checkbox"
                  name="is_active"
                  defaultChecked={defaultPlan.is_active}
                  className="mr-2"
                />
                <label className="text-sm text-gray-700">Active</label>
              </div>
            </div>
          </div>
        </AdminActionModal>
      );
    }
    
    if (!subscription) return null;

    const modalProps = {
      isOpen: modalState.isOpen,
      onClose: closeModal,
      loading: modalState.loading
    };

    switch (type) {
      case 'edit':
        return (
          <AdminActionModal
            {...modalProps}
            title="Edit Subscription"
            message={`Edit subscription details for ${subscription.gym_name}`}
            confirmText="Update Subscription"
            type="info"
            onConfirm={() => {
              // In a real implementation, you'd collect form data
              const formData = {
                monthly_price: subscription.monthly_price,
                max_members: subscription.max_members,
                auto_renew: subscription.auto_renew
              };
              handleSubscriptionAction('update', subscription, formData);
            }}
          >
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Monthly Price ($)
                </label>
                <input
                  type="number"
                  defaultValue={subscription.monthly_price}
                  className="w-full p-2 border border-gray-300 rounded-md"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Member Limit
                </label>
                <input
                  type="number"
                  defaultValue={subscription.max_members}
                  className="w-full p-2 border border-gray-300 rounded-md"
                />
              </div>
              <div className="flex items-center">
                <input
                  type="checkbox"
                  defaultChecked={subscription.auto_renew}
                  className="mr-2"
                />
                <label className="text-sm text-gray-700">Auto-renew enabled</label>
              </div>
            </div>
          </AdminActionModal>
        );

      case 'renew':
        return (
          <AdminActionModal
            {...modalProps}
            title="Renew Subscription"
            message={`Renew subscription for ${subscription.gym_name} for another 30 days?`}
            confirmText="Renew Now"
            type="info"
            onConfirm={() => handleSubscriptionAction('renew', subscription)}
          >
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 mt-3">
              <p className="text-sm text-blue-800">
                This will extend the billing cycle by 30 days from the current end date.
              </p>
            </div>
          </AdminActionModal>
        );

      case 'suspend':
        return (
          <AdminActionModal
            {...modalProps}
            title="Suspend Subscription"
            message={`Suspend subscription for ${subscription.gym_name}? This will prevent billing and limit gym functionality.`}
            confirmText="Suspend"
            type="warning"
            onConfirm={() => handleSubscriptionAction('suspend', subscription)}
          >
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 mt-3">
              <p className="text-sm text-yellow-800">
                <strong>Warning:</strong> Suspending will stop billing but may limit gym access to platform features.
              </p>
            </div>
          </AdminActionModal>
        );

      default:
        return null;
    }
  };

  // Revenue chart data (mock - would come from analytics endpoint)
  const revenueData = [
    { label: 'Jan', value: 25400 },
    { label: 'Feb', value: 28200 },
    { label: 'Mar', value: 31100 },
    { label: 'Apr', value: 29800 },
    { label: 'May', value: 33500 },
    { label: 'Jun', value: 36200 }
  ];

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-7xl mx-auto">
          <div className="bg-red-50 border border-red-200 rounded-2xl p-8 text-center">
            <ExclamationTriangleIcon className="w-16 h-16 text-red-600 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-red-900 mb-2">Error Loading Subscriptions</h2>
            <p className="text-red-700 mb-4">{error}</p>
            <button
              onClick={fetchSubscriptions}
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
                <CreditCardIcon className="w-8 h-8" />
                Subscription Management
              </h1>
              <p className="text-gray-600">
                Manage gym subscriptions, billing cycles, and revenue analytics
              </p>
            </div>
            <div className="flex items-center gap-4">
              <button
                onClick={() => handleFilterChange('expiring_soon', !filters.expiring_soon)}
                className={`px-4 py-2 rounded-lg transition-colors ${
                  filters.expiring_soon 
                    ? 'bg-red-500 text-white' 
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {filters.expiring_soon ? 'Show All' : 'Show Expiring Soon'}
              </button>
              <button
                onClick={fetchSubscriptions}
                disabled={loading}
                className="px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 disabled:opacity-50 transition-colors flex items-center gap-2"
              >
                <ArrowPathIcon className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                Refresh
              </button>
            </div>
          </div>
        </div>

        {/* Subscription Metrics */}
        <section>
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Subscription Overview</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <AdminMetricCard
              title="Total Subscriptions"
              value={metrics.total}
              subtitle="All gym subscriptions"
              icon={<CreditCardIcon className="w-6 h-6" />}
              color="blue"
            />
            <AdminMetricCard
              title="Active Subscriptions"
              value={metrics.active}
              subtitle="Currently active"
              icon={<CheckCircleIcon className="w-6 h-6" />}
              color="green"
            />
            <AdminMetricCard
              title="Expiring Soon"
              value={metrics.expiring_soon}
              subtitle="Within 7 days"
              icon={<ExclamationTriangleIcon className="w-6 h-6" />}
              color="orange"
              trend={metrics.expiring_soon > 0 ? `${metrics.expiring_soon} need attention` : null}
              trendDirection={metrics.expiring_soon > 0 ? 'down' : 'neutral'}
            />
            <AdminMetricCard
              title="Expired"
              value={metrics.expired}
              subtitle="Require renewal"
              icon={<XCircleIcon className="w-6 h-6" />}
              color="red"
            />
          </div>
        </section>

        {/* Revenue Analytics */}
        <section>
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Revenue Analytics</h2>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <AdminChart
              type="line"
              data={revenueData}
              title="Monthly Recurring Revenue"
              subtitle="Subscription revenue over time"
              height="300px"
              color="green"
              loading={loading}
            />
            <AdminChart
              type="pie"
              data={[
                { label: 'Active', value: metrics.active },
                { label: 'Expiring Soon', value: metrics.expiring_soon },
                { label: 'Expired', value: metrics.expired }
              ]}
              title="Subscription Status Distribution"
              subtitle="Current subscription breakdown"
              height="300px"
              color="blue"
              loading={loading}
            />
          </div>
        </section>

        {/* Subscription Table */}
        <section>
          <h2 className="text-xl font-semibold text-gray-900 mb-4">All Subscriptions</h2>
          <AdminDataTable
            data={subscriptions}
            columns={columns}
            searchable={true}
            sortable={true}
            filterable={true}
            filters={statusFilters}
            loading={loading}
            emptyMessage="No subscriptions found"
            onRowClick={(subscription) => console.log('View subscription details:', subscription)}
          />
          
          {/* Pagination */}
          {pagination.pages > 1 && (
            <div className="flex items-center justify-between mt-4 px-4 py-3 bg-white border border-gray-200 rounded-lg">
              <div className="text-sm text-gray-600">
                Showing {((pagination.page - 1) * pagination.per_page) + 1} to {Math.min(pagination.page * pagination.per_page, pagination.total)} of {pagination.total} subscriptions
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => handleFilterChange('page', pagination.page - 1)}
                  disabled={!pagination.has_prev}
                  className="px-3 py-1 bg-gray-100 text-gray-600 rounded disabled:opacity-50 hover:bg-gray-200"
                >
                  Previous
                </button>
                <span className="px-3 py-1 bg-orange-100 text-orange-800 rounded">
                  {pagination.page} of {pagination.pages}
                </span>
                <button
                  onClick={() => handleFilterChange('page', pagination.page + 1)}
                  disabled={!pagination.has_next}
                  className="px-3 py-1 bg-gray-100 text-gray-600 rounded disabled:opacity-50 hover:bg-gray-200"
                >
                  Next
                </button>
              </div>
            </div>
          )}
        </section>

        {/* Platform Subscription Plans */}
        <section>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-gray-900">Platform Subscription Plans</h2>
            <button
              onClick={() => openPlanModal('createPlan')}
              className="px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 transition-colors"
            >
              Add Plan
            </button>
          </div>
          <div className="bg-white border border-gray-200 rounded-2xl p-4 shadow-sm">
            {plansLoading ? (
              <div className="flex items-center justify-center py-12">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-orange-500"></div>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-gray-200">
                      <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Plan Name</th>
                      <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Price</th>
                      <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Billing Cycle</th>
                      <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Recommended</th>
                      <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Active</th>
                      <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {plans.map((plan) => (
                      <tr key={plan.id} className="border-b border-gray-100">
                        <td className="py-3 px-4 text-sm text-gray-900">{plan.plan_name}</td>
                        <td className="py-3 px-4 text-sm text-gray-900">₹{plan.price}</td>
                        <td className="py-3 px-4 text-sm text-gray-900">{plan.billing_cycle}</td>
                        <td className="py-3 px-4">
                          {plan.recommended ? (
                            <span className="px-2 py-1 rounded-full text-xs font-medium bg-orange-100 text-orange-800">Yes</span>
                          ) : (
                            <span className="px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800">No</span>
                          )}
                        </td>
                        <td className="py-3 px-4">
                          {plan.is_active ? (
                            <span className="px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">Yes</span>
                          ) : (
                            <span className="px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800">No</span>
                          )}
                        </td>
                        <td className="py-3 px-4">
                          <div className="flex gap-2">
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                openPlanModal('editPlan', plan);
                              }}
                              className="px-2 py-1 bg-blue-500 text-white rounded text-xs hover:bg-blue-600"
                            >
                              Edit
                            </button>
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                openPlanModal('deletePlan', plan);
                              }}
                              className="px-2 py-1 bg-red-500 text-white rounded text-xs hover:bg-red-600"
                            >
                              Delete
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                {plans.length === 0 && (
                  <div className="text-center py-12 text-gray-500">
                    No plans found. Add your first plan!
                  </div>
                )}
              </div>
            )}
          </div>
        </section>
      </div>

      {/* Action Modals */}
      {renderModal()}
    </div>
  );
};

export default SubscriptionManagement;