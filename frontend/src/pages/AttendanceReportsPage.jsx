import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';
import { ArrowLeftIcon } from '@heroicons/react/24/outline';

export default function AttendanceReportsPage() {
    const { user } = useAuth();
    const navigate = useNavigate();
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [selectedReport, setSelectedReport] = useState('daily');
    const [reportData, setReportData] = useState(null);
    const [reportDate, setReportDate] = useState(new Date().toISOString().split('T')[0]);

    useEffect(() => {
        fetchReport();
    }, [selectedReport, reportDate]);

    const fetchReport = async () => {
        setLoading(true);
        setError('');
        
        try {
            let endpoint = '';
            const params = new URLSearchParams();
            
            switch (selectedReport) {
                case 'daily':
                    endpoint = '/api/attendance/reports/daily';
                    params.append('date', reportDate);
                    break;
                case 'weekly':
                    endpoint = '/api/attendance/reports/weekly';
                    const weekStart = new Date(reportDate);
                    weekStart.setDate(weekStart.getDate() - weekStart.getDay());
                    params.append('week_start', weekStart.toISOString().split('T')[0]);
                    break;
                case 'monthly':
                    endpoint = '/api/attendance/reports/monthly';
                    const [year, month] = reportDate.split('-');
                    params.append('month', `${year}-${month}`);
                    break;
                default:
                    return;
            }

            const response = await api.get(`${endpoint}?${params.toString()}`);
            setReportData(response.data);
        } catch (err) {
            console.error(err);
            setError(err.response?.data?.error || 'Failed to fetch report');
        } finally {
            setLoading(false);
        }
    };

    const formatDate = (dateString) => {
        return new Date(dateString).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    };

    const formatDuration = (minutes) => {
        if (!minutes) return '-';
        const hours = Math.floor(minutes / 60);
        const mins = minutes % 60;
        if (hours > 0) {
            return `${hours}h ${mins}m`;
        }
        return `${mins}m`;
    };

    return (
        <div className="space-y-8">
            {/* Header */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900 mb-1">Attendance Reports</h1>
                    <p className="text-sm text-gray-600">
                        View detailed attendance analytics - Gym ID: {user?.gym_id}
                    </p>
                </div>
                <button
                    onClick={() => navigate('/attendance')}
                    className="bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-2 rounded-xl text-sm font-medium transition-colors self-start md:self-auto flex items-center gap-2"
                >
                    <ArrowLeftIcon className="w-4 h-4" /> Back to Attendance
                </button>
            </div>

            {/* Report Controls */}
            <div className="bg-white border border-gray-200 p-6 rounded-2xl shadow-sm">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                        <label className="block text-xs font-semibold uppercase tracking-wider text-gray-600 mb-2">
                            Report Type
                        </label>
                        <select
                            value={selectedReport}
                            onChange={(e) => setSelectedReport(e.target.value)}
                            className="w-full bg-gray-50 border border-gray-200 focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 rounded-xl px-4 py-3 text-sm text-gray-900 focus:outline-none transition-all duration-200"
                        >
                            <option value="daily">Daily Report</option>
                            <option value="weekly">Weekly Report</option>
                            <option value="monthly">Monthly Report</option>
                        </select>
                    </div>
                    <div>
                        <label className="block text-xs font-semibold uppercase tracking-wider text-gray-600 mb-2">
                            {selectedReport === 'monthly' ? 'Month' : 'Date'}
                        </label>
                        <input
                            type={selectedReport === 'monthly' ? 'month' : 'date'}
                            value={selectedReport === 'monthly' ? reportDate.slice(0, 7) : reportDate}
                            onChange={(e) => setReportDate(selectedReport === 'monthly' ? e.target.value + '-01' : e.target.value)}
                            className="w-full bg-gray-50 border border-gray-200 focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 rounded-xl px-4 py-3 text-sm text-gray-900 focus:outline-none transition-all duration-200"
                        />
                    </div>
                    <div className="flex items-end">
                        <button
                            onClick={fetchReport}
                            disabled={loading}
                            className="w-full bg-orange-600 hover:bg-orange-700 text-white font-medium py-3 px-6 rounded-xl transition-all duration-200 disabled:opacity-50"
                        >
                            {loading ? 'Loading...' : 'Generate Report'}
                        </button>
                    </div>
                </div>
            </div>

            {error && (
                <div className="bg-red-50 border border-red-200 text-red-700 text-sm p-4 rounded-xl">
                    {error}
                </div>
            )}

            {/* Report Content */}
            {reportData && (
                <div className="space-y-6">
                    {/* Statistics */}
                    <div className="bg-white border border-gray-200 p-6 rounded-2xl shadow-sm">
                        <h2 className="text-lg font-bold text-gray-900 mb-4">
                            {selectedReport === 'daily' && `Daily Report - ${formatDate(reportData.date)}`}
                            {selectedReport === 'weekly' && `Weekly Report - ${formatDate(reportData.week_start)} to ${formatDate(reportData.week_end)}`}
                            {selectedReport === 'monthly' && `Monthly Report - ${reportData.month}`}
                        </h2>
                        
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                            <div className="text-center">
                                <p className="text-3xl font-bold text-orange-600">
                                    {reportData.statistics.total_checkins}
                                </p>
                                <p className="text-sm text-gray-600 mt-1">Total Check-ins</p>
                            </div>
                            
                            {selectedReport !== 'daily' && (
                                <div className="text-center">
                                    <p className="text-3xl font-bold text-green-600">
                                        {reportData.statistics.unique_members}
                                    </p>
                                    <p className="text-sm text-gray-600 mt-1">Unique Members</p>
                                </div>
                            )}
                            
                            {selectedReport === 'daily' && (
                                <>
                                    <div className="text-center">
                                        <p className="text-3xl font-bold text-green-600">
                                            {reportData.statistics.checked_out}
                                        </p>
                                        <p className="text-sm text-gray-600 mt-1">Checked Out</p>
                                    </div>
                                    <div className="text-center">
                                        <p className="text-3xl font-bold text-blue-600">
                                            {reportData.statistics.still_inside}
                                        </p>
                                        <p className="text-sm text-gray-600 mt-1">Still Inside</p>
                                    </div>
                                    <div className="text-center">
                                        <p className="text-3xl font-bold text-purple-600">
                                            {formatDuration(reportData.statistics.average_duration_minutes)}
                                        </p>
                                        <p className="text-sm text-gray-600 mt-1">Avg Duration</p>
                                    </div>
                                </>
                            )}
                            
                            {selectedReport !== 'daily' && (
                                <div className="text-center">
                                    <p className="text-3xl font-bold text-blue-600">
                                        {reportData.statistics.daily_average}
                                    </p>
                                    <p className="text-sm text-gray-600 mt-1">Daily Average</p>
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Breakdown */}
                    {(selectedReport === 'weekly' || selectedReport === 'monthly') && (
                        <div className="bg-white border border-gray-200 p-6 rounded-2xl shadow-sm">
                            <h3 className="text-lg font-bold text-gray-900 mb-4">
                                {selectedReport === 'weekly' ? 'Daily Breakdown' : 'Weekly Breakdown'}
                            </h3>
                            
                            <div className="overflow-x-auto">
                                <table className="w-full">
                                    <thead>
                                        <tr className="border-b border-gray-200 bg-gray-50">
                                            <th className="text-left px-4 py-3 text-xs font-semibold uppercase tracking-wider text-gray-600">
                                                {selectedReport === 'weekly' ? 'Day' : 'Week'}
                                            </th>
                                            <th className="text-left px-4 py-3 text-xs font-semibold uppercase tracking-wider text-gray-600">
                                                Check-ins
                                            </th>
                                            <th className="text-left px-4 py-3 text-xs font-semibold uppercase tracking-wider text-gray-600">
                                                {selectedReport === 'weekly' ? 'Checked Out' : 'Unique Members'}
                                            </th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {(selectedReport === 'weekly' ? reportData.daily_breakdown : reportData.weekly_breakdown).map((item, index) => (
                                            <tr key={index} className="border-b border-gray-100">
                                                <td className="px-4 py-3 text-sm text-gray-900">
                                                    {selectedReport === 'weekly' 
                                                        ? `${item.day_name} - ${formatDate(item.date)}`
                                                        : `${formatDate(item.week_start)} to ${formatDate(item.week_end)}`
                                                    }
                                                </td>
                                                <td className="px-4 py-3 text-sm text-gray-700 font-medium">
                                                    {item.total_checkins}
                                                </td>
                                                <td className="px-4 py-3 text-sm text-gray-700">
                                                    {selectedReport === 'weekly' ? item.checked_out : item.unique_members}
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    )}

                    {/* Daily Attendance List (for daily reports) */}
                    {selectedReport === 'daily' && reportData.attendance && reportData.attendance.length > 0 && (
                        <div className="bg-white border border-gray-200 p-6 rounded-2xl shadow-sm">
                            <h3 className="text-lg font-bold text-gray-900 mb-4">Attendance Details</h3>
                            
                            <div className="overflow-x-auto">
                                <table className="w-full">
                                    <thead>
                                        <tr className="border-b border-gray-200 bg-gray-50">
                                            <th className="text-left px-4 py-3 text-xs font-semibold uppercase tracking-wider text-gray-600">
                                                Member
                                            </th>
                                            <th className="text-left px-4 py-3 text-xs font-semibold uppercase tracking-wider text-gray-600">
                                                Check In
                                            </th>
                                            <th className="text-left px-4 py-3 text-xs font-semibold uppercase tracking-wider text-gray-600">
                                                Check Out
                                            </th>
                                            <th className="text-left px-4 py-3 text-xs font-semibold uppercase tracking-wider text-gray-600">
                                                Duration
                                            </th>
                                            <th className="text-left px-4 py-3 text-xs font-semibold uppercase tracking-wider text-gray-600">
                                                Status
                                            </th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {reportData.attendance.map((record) => (
                                            <tr key={record.id} className="border-b border-gray-100">
                                                <td className="px-4 py-3 text-sm text-gray-900 font-medium">
                                                    {record.member_name}
                                                </td>
                                                <td className="px-4 py-3 text-sm text-gray-700">
                                                    {new Date(record.check_in_time).toLocaleTimeString('en-US', {
                                                        hour: '2-digit',
                                                        minute: '2-digit'
                                                    })}
                                                </td>
                                                <td className="px-4 py-3 text-sm text-gray-700">
                                                    {record.check_out_time 
                                                        ? new Date(record.check_out_time).toLocaleTimeString('en-US', {
                                                            hour: '2-digit',
                                                            minute: '2-digit'
                                                        })
                                                        : '-'
                                                    }
                                                </td>
                                                <td className="px-4 py-3 text-sm text-gray-700 font-medium">
                                                    {formatDuration(record.duration_minutes)}
                                                </td>
                                                <td className="px-4 py-3">
                                                    <span className={`inline-flex px-2 py-1 rounded-full text-xs font-semibold ${
                                                        record.status === 'Checked Out' 
                                                            ? 'bg-green-50 text-green-700 border border-green-200'
                                                            : 'bg-orange-50 text-orange-700 border border-orange-200'
                                                    }`}>
                                                        {record.status}
                                                    </span>
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}