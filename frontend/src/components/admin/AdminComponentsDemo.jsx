import React, { useState } from 'react';
import { 
  AdminDataTable, 
  AdminMetricCard, 
  AdminActionModal, 
  AdminChart 
} from './index';
import {
  BuildingOffice,
  Users,
  CurrencyDollar,
  Ticket,
  Clock
} from '@heroicons/react/24/outline';

/**
 * Demo page showcasing all Super Admin UI components
 * Useful for development and testing
 */
const AdminComponentsDemo = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [modalLoading, setModalLoading] = useState(false);

  // Sample data for demonstrations
  const sampleData = [
    { id: 1, name: 'FitZone Gym', owner: 'John Smith', members: 150, status: 'Active', revenue: '$12,500' },
    { id: 2, name: 'PowerHouse Fitness', owner: 'Sarah Johnson', members: 89, status: 'Suspended', revenue: '$8,200' },
    { id: 3, name: 'Elite Training Center', owner: 'Mike Brown', members: 200, status: 'Active', revenue: '$18,900' },
    { id: 4, name: 'Wellness Hub', owner: 'Lisa Davis', members: 75, status: 'Pending', revenue: '$5,800' }
  ];

  const tableColumns = [
    { key: 'name', label: 'Gym Name' },
    { key: 'owner', label: 'Owner' },
    { key: 'members', label: 'Members' },
    { key: 'status', label: 'Status', render: (value) => (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
        value === 'Active' ? 'bg-green-100 text-green-800' :
        value === 'Suspended' ? 'bg-red-100 text-red-800' :
        'bg-yellow-100 text-yellow-800'
      }`}>
        {value}
      </span>
    )},
    { key: 'revenue', label: 'Monthly Revenue' }
  ];

  const chartData = [
    { label: 'Jan', value: 45 },
    { label: 'Feb', value: 52 },
    { label: 'Mar', value: 48 },
    { label: 'Apr', value: 61 },
    { label: 'May', value: 55 },
    { label: 'Jun', value: 67 }
  ];

  const pieData = [
    { label: 'Active Gyms', value: 75 },
    { label: 'Suspended', value: 15 },
    { label: 'Pending', value: 10 }
  ];

  const filters = [
    {
      key: 'status',
      label: 'Status',
      options: [
        { value: 'Active', label: 'Active' },
        { value: 'Suspended', label: 'Suspended' },
        { value: 'Pending', label: 'Pending' }
      ]
    }
  ];

  const handleModalConfirm = () => {
    setModalLoading(true);
    setTimeout(() => {
      setModalLoading(false);
      setIsModalOpen(false);
      alert('Action confirmed!');
    }, 2000);
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Page Header */}
        <div className="bg-white rounded-2xl border border-gray-200 p-6 shadow-sm">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Admin Components Demo</h1>
          <p className="text-gray-600">
            Showcase of reusable Super Admin UI components for the SmartGoNext Gym platform
          </p>
        </div>

        {/* Metric Cards Section */}
        <section>
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">Metric Cards</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <AdminMetricCard
              title="Total Gyms"
              value={247}
              subtitle="Registered facilities"
              icon={<BuildingOffice className="w-6 h-6" />}
              trend="+12%"
              trendDirection="up"
              color="blue"
            />
            <AdminMetricCard
              title="Active Members"
              value={15420}
              subtitle="Across all gyms"
              icon={<Users className="w-6 h-6" />}
              trend="+8.5%"
              trendDirection="up"
              color="green"
            />
            <AdminMetricCard
              title="Monthly Revenue"
              value="$89,240"
              subtitle="Platform earnings"
              icon={<CurrencyDollar className="w-6 h-6" />}
              trend="-2.1%"
              trendDirection="down"
              color="orange"
            />
            <AdminMetricCard
              title="Support Tickets"
              value={23}
              subtitle="Open issues"
              icon={<Ticket className="w-6 h-6" />}
              trend="0%"
              trendDirection="neutral"
              color="red"
            />
          </div>
        </section>

        {/* Charts Section */}
        <section>
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">Charts & Analytics</h2>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <AdminChart
              type="bar"
              data={chartData}
              title="Monthly Gym Registrations"
              subtitle="New gyms joining the platform"
              height="300px"
              color="blue"
            />
            <AdminChart
              type="line"
              data={chartData}
              title="Revenue Trend"
              subtitle="Platform revenue over time"
              height="300px"
              color="green"
            />
            <AdminChart
              type="pie"
              data={pieData}
              title="Gym Status Distribution"
              subtitle="Current status breakdown"
              height="300px"
              color="orange"
            />
            <div className="bg-white border border-gray-200 rounded-2xl p-6">
              <h3 className="text-lg font-semibold mb-4">Chart Loading State</h3>
              <AdminChart
                type="bar"
                data={chartData}
                title="Loading Example"
                loading={true}
                height="200px"
              />
            </div>
          </div>
        </section>

        {/* Data Table Section */}
        <section>
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">Data Tables</h2>
          <AdminDataTable
            data={sampleData}
            columns={tableColumns}
            searchable={true}
            sortable={true}
            filterable={true}
            filters={filters}
            onRowClick={(row) => alert(`Clicked on ${row.name}`)}
            emptyMessage="No gyms found"
          />
        </section>

        {/* Modal Section */}
        <section>
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">Action Modals</h2>
          <div className="bg-white border border-gray-200 rounded-2xl p-6 space-y-4">
            <p className="text-gray-600 mb-4">
              Click the buttons below to see different types of confirmation modals:
            </p>
            <div className="flex flex-wrap gap-4">
              <button
                onClick={() => setIsModalOpen(true)}
                className="px-4 py-2 bg-yellow-500 text-white rounded-lg hover:bg-yellow-600"
              >
                Warning Modal
              </button>
              <button
                onClick={() => setIsModalOpen(true)}
                className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600"
              >
                Danger Modal
              </button>
              <button
                onClick={() => setIsModalOpen(true)}
                className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
              >
                Info Modal
              </button>
            </div>
          </div>
        </section>

        {/* Loading States Section */}
        <section>
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">Loading States</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <AdminMetricCard
              title="Loading Metric"
              value={1234}
              loading={true}
              icon={<Clock className="w-6 h-6" />}
            />
            <div>
              <AdminDataTable
                data={[]}
                columns={tableColumns}
                loading={true}
                emptyMessage="No data found"
              />
            </div>
          </div>
        </section>
      </div>

      {/* Demo Modal */}
      <AdminActionModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onConfirm={handleModalConfirm}
        title="Confirm Gym Suspension"
        message="Are you sure you want to suspend this gym? This action will prevent all users from this gym from accessing the platform."
        confirmText="Suspend Gym"
        cancelText="Keep Active"
        type="warning"
        loading={modalLoading}
      >
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 mt-3">
          <p className="text-sm text-yellow-800">
            <strong>Note:</strong> You can reactivate the gym later from the gym management panel.
          </p>
        </div>
      </AdminActionModal>
    </div>
  );
};

export default AdminComponentsDemo;