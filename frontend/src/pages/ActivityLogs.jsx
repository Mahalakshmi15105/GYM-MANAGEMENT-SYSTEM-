import React, { useState, useEffect } from 'react';
import { AdminDataTable, AdminMetricCard } from '../components/admin';
import api from '../services/api';
import { ChartBarIcon, ArrowTrendingUpIcon, ExclamationTriangleIcon, UserIcon } from '@heroicons/react/24/outline';

const ActivityLogs = () => {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    startDate: '',
    endDate: '',
    action: '',
    userId: ''
  });

  useEffect(() => {
    fetchActivityLogs();
  }, [filters]);

  const fetchActivityLogs = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      Object.entries(filters).forEach(([key, value]) => {
        if (value) params.append(key, value);
      });
      
      const response = await api.get(`/api/admin/activity-logs?${params}`);
      setLogs(response.data.logs || []);
    } catch (error) {
      console.error('Failed to fetch activity logs:', error);
    } finally {
      setLoading(false);
    }
  };

  const columns = [
    { key: 'timestamp', label: 'Time' },
    { key: 'action', label: 'Action' },
    { key: 'user_id', label: 'User' },
    { key: 'gym_id', label: 'Gym' },
    { key: 'details', label: 'Details' }
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Activity Logs</h1>
        <p className="mt-2 text-sm text-gray-600">
          Monitor all platform activities and administrative actions
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <AdminMetricCard
          title="Total Actions"
          value={logs.length}
          trend={5.2}
          icon={<ChartBarIcon className="w-6 h-6" />}
        />
        <AdminMetricCard
          title="Today's Activity"
          value={logs.filter(log => 
            log?.timestamp && new Date(log.timestamp).toDateString() === new Date().toDateString()
          ).length}
          trend={12.1}
          icon={<ArrowTrendingUpIcon className="w-6 h-6" />}
        />
        <AdminMetricCard
          title="Critical Events"
          value={logs.filter(log => 
            (log?.action || "").includes('delete') || (log?.action || "").includes('suspend')
          ).length}
          trend={-2.4}
          icon={<ExclamationTriangleIcon className="w-6 h-6" />}
        />
        <AdminMetricCard
          title="User Actions"
          value={logs.filter(log => log.user_id).length}
          trend={8.7}
          icon={<UserIcon className="w-6 h-6" />}
        />
      </div>

      <AdminDataTable
        data={logs}
        columns={columns}
        loading={loading}
        searchable
        filterable
      />
    </div>
  );
};

export default ActivityLogs;