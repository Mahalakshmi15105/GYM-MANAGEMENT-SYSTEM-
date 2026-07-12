import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';
import { ChartBarIcon, PlusIcon, QrCodeIcon, DocumentArrowDownIcon, PrinterIcon, ExclamationTriangleIcon } from '@heroicons/react/24/outline';

export default function AttendancePage() {
    const { user } = useAuth();
    const [attendance, setAttendance] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [searchQuery, setSearchQuery] = useState('');
    const [statusFilter, setStatusFilter] = useState('All');
    const [dateRange, setDateRange] = useState({ start: '', end: '' });
    const [selectedView, setSelectedView] = useState('today');
    const [deleteModal, setDeleteModal] = useState({ isOpen: false, record: null });
    
    // QR Code state
    const [qrData, setQrData] = useState(null);
    const [qrImageUrl, setQrImageUrl] = useState('');
    const [qrLoading, setQrLoading] = useState(true);
    const [qrError, setQrError] = useState('');
    const [showQrSection, setShowQrSection] = useState(false);

    useEffect(() => {
        fetchAttendance();
        fetchQRData();
    }, [selectedView]);

    const fetchAttendance = async () => {
        try {
            const params = new URLSearchParams();
            
            // Set date range based on selected view
            const today = new Date();
            if (selectedView === 'today') {
                const todayStr = today.toISOString().split('T')[0];
                params.append('start_date', todayStr);
                params.append('end_date', todayStr);
            } else if (selectedView === 'week') {
                const weekStart = new Date(today);
                weekStart.setDate(today.getDate() - today.getDay());
                const weekEnd = new Date(weekStart);
                weekEnd.setDate(weekStart.getDate() + 6);
                params.append('start_date', weekStart.toISOString().split('T')[0]);
                params.append('end_date', weekEnd.toISOString().split('T')[0]);
            }
            
            if (statusFilter !== 'All') params.append('status', statusFilter);
            if (dateRange.start) params.append('start_date', dateRange.start);
            if (dateRange.end) params.append('end_date', dateRange.end);
            if (searchQuery.trim()) params.append('q', searchQuery.trim());

            const response = await api.get(`/api/attendance?${params.toString()}`);
            setAttendance(response.data.attendance || []);
        } catch (err) {
            console.error(err);
            setError(err.response?.data?.error || 'Failed to fetch attendance records');
        } finally {
            setLoading(false);
        }
    };

    const handleSearch = async (query) => {
        setSearchQuery(query);
        if (!query.trim()) {
            fetchAttendance();
            return;
        }

        try {
            const response = await api.get(`/api/attendance/search?q=${encodeURIComponent(query)}`);
            setAttendance(response.data.attendance || []);
        } catch (err) {
            console.error(err);
            setError('Search failed');
        }
    };

    const handleFilterChange = () => {
        fetchAttendance();
    };

    const handleCheckout = async (attendanceId) => {
        try {
            await api.put(`/api/attendance/${attendanceId}/checkout`);
            fetchAttendance(); // Refresh the list
        } catch (err) {
            console.error(err);
            setError(err.response?.data?.error || 'Failed to record checkout');
        }
    };

    const handleDelete = async (attendanceId) => {
        try {
            await api.delete(`/api/attendance/${attendanceId}`);
            setAttendance(attendance.filter(a => a.id !== attendanceId));
            setDeleteModal({ isOpen: false, record: null });
        } catch (err) {
            console.error(err);
            setError(err.response?.data?.error || 'Failed to delete attendance record');
        }
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

    const formatDate = (dateString) => {
        if (!dateString) return '-';
        return new Date(dateString).toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric'
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

    const getStatusColor = (status) => {
        switch (status) {
            case 'Checked In':
                return 'bg-orange-50 text-orange-700 border-orange-200';
            case 'Checked Out':
                return 'bg-green-50 text-green-700 border-green-200';
            default:
                return 'bg-gray-50 text-gray-600 border-gray-200';
        }
    };

    const fetchQRData = async () => {
        try {
            const response = await api.get('/api/gym/qr/info');
            setQrData(response.data);
            
            if (response.data.has_qr) {
                const imageResponse = await api.get('/api/gym/qr/image', {
                    responseType: 'blob'
                });
                const imageUrl = URL.createObjectURL(imageResponse.data);
                setQrImageUrl(imageUrl);
            }
        } catch (err) {
            console.error('Failed to fetch QR data:', err);
            setQrError(err.response?.data?.error || 'Failed to load QR data');
        } finally {
            setQrLoading(false);
        }
    };

    const handleDownloadQR = async () => {
        try {
            const response = await api.get('/api/gym/qr/image', {
                responseType: 'blob'
            });
            
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const a = document.createElement('a');
            a.href = url;
            a.download = `gym-qr-code-${qrData.gym?.name || 'gym'}.png`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        } catch (err) {
            console.error('Failed to download QR:', err);
            setQrError('Failed to download QR code');
        }
    };

    const handlePrintQR = async () => {
        try {
            const response = await api.get('/api/gym/qr/printable', {
                responseType: 'blob'
            });
            
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const printWindow = window.open(url, '_blank');
            if (printWindow) {
                printWindow.onload = () => {
                    printWindow.print();
                };
            }
        } catch (err) {
            console.error('Failed to print QR:', err);
            setQrError('Failed to generate printable QR');
        }
    };

    return (
        <div className="space-y-8">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900 mb-1">Attendance</h1>
                    <p className="text-sm text-gray-600">
                        Track member check-ins and check-outs - Gym ID: {user?.gym_id}
                    </p>
                </div>
                <div className="flex gap-3">
                    <Link
                        to="/attendance/reports"
                        className="bg-green-600 hover:bg-green-700 text-white font-medium px-4 py-2 rounded-xl transition-all duration-200 text-sm shadow-sm flex items-center gap-2"
                    >
                        <ChartBarIcon className="w-4 h-4 mr-2" /> Reports
                    </Link>
                    <button
                        onClick={() => setShowQrSection(!showQrSection)}
                        className="bg-blue-600 hover:bg-blue-700 text-white font-medium px-4 py-2 rounded-xl transition-all duration-200 text-sm shadow-sm flex items-center gap-2"
                    >
                        <QrCodeIcon className="w-4 h-4 mr-2" /> Attendance QR
                    </button>
                    <Link
                        to="/attendance/checkin"
                        className="bg-orange-600 hover:bg-orange-700 text-white font-bold px-6 py-3 rounded-xl transition-all duration-200 self-start md:self-auto text-center shadow-sm flex items-center gap-2"
                    >
                        <PlusIcon className="w-4 h-4 mr-2" /> Check In
                    </Link>
                </div>
            </div>

            {/* View Selector */}
            <div className="bg-white border border-gray-200 p-4 rounded-2xl shadow-sm">
                <div className="flex flex-wrap gap-2">
                    {[
                        { key: 'today', label: 'Today' },
                        { key: 'week', label: 'This Week' },
                        { key: 'all', label: 'All Records' }
                    ].map((view) => (
                        <button
                            key={view.key}
                            onClick={() => {
                                setSelectedView(view.key);
                                setDateRange({ start: '', end: '' });
                            }}
                            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                                selectedView === view.key
                                    ? 'bg-orange-600 text-white'
                                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                            }`}
                        >
                            {view.label}
                        </button>
                    ))}
                </div>
            </div>

            {/* Filters */}
            <div className="bg-white border border-gray-200 p-6 rounded-2xl shadow-sm">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    <div>
                        <input
                            type="text"
                            placeholder="Search by member name or phone..."
                            value={searchQuery}
                            onChange={(e) => handleSearch(e.target.value)}
                            className="w-full bg-gray-50 border border-gray-200 focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 rounded-xl px-4 py-3 text-sm text-gray-900 placeholder-gray-500 focus:outline-none transition-all duration-200"
                        />
                    </div>
                    <div>
                        <select
                            value={statusFilter}
                            onChange={(e) => {
                                setStatusFilter(e.target.value);
                                handleFilterChange();
                            }}
                            className="w-full bg-gray-50 border border-gray-200 focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 rounded-xl px-4 py-3 text-sm text-gray-900 focus:outline-none transition-all duration-200"
                        >
                            <option value="All">All Status</option>
                            <option value="Checked In">Checked In</option>
                            <option value="Checked Out">Checked Out</option>
                        </select>
                    </div>
                    <div>
                        <input
                            type="date"
                            value={dateRange.start}
                            onChange={(e) => {
                                setDateRange(prev => ({ ...prev, start: e.target.value }));
                                setSelectedView('custom');
                                handleFilterChange();
                            }}
                            className="w-full bg-gray-50 border border-gray-200 focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 rounded-xl px-4 py-3 text-sm text-gray-900 focus:outline-none transition-all duration-200"
                            placeholder="Start Date"
                        />
                    </div>
                    <div>
                        <input
                            type="date"
                            value={dateRange.end}
                            onChange={(e) => {
                                setDateRange(prev => ({ ...prev, end: e.target.value }));
                                setSelectedView('custom');
                                handleFilterChange();
                            }}
                            className="w-full bg-gray-50 border border-gray-200 focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 rounded-xl px-4 py-3 text-sm text-gray-900 focus:outline-none transition-all duration-200"
                            placeholder="End Date"
                        />
                    </div>
                </div>
            </div>

            {error && (
                <div className="bg-red-50 border border-red-200 text-red-700 text-sm p-4 rounded-xl">
                    {error}
                </div>
            )}

            {/* Attendance QR Code Section */}
            {showQrSection && (
                <div className="bg-white border border-gray-200 rounded-2xl p-6 shadow-sm">
                    <div className="flex items-center justify-between mb-4">
                        <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                            <QrCodeIcon className="w-5 h-5 text-orange-500" />
                            Attendance QR Code
                        </h3>
                        <button
                            onClick={() => setShowQrSection(false)}
                            className="text-gray-400 hover:text-gray-600"
                        >
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                            </svg>
                        </button>
                    </div>

                    {qrError && (
                        <div className="bg-red-50 border border-red-200 text-red-700 text-sm p-4 rounded-xl mb-4 flex items-start gap-3">
                            <ExclamationTriangleIcon className="w-5 h-5 flex-shrink-0 mt-0.5" />
                            <p className="text-sm">{qrError}</p>
                        </div>
                    )}

                    {qrLoading ? (
                        <div className="text-center py-8">
                            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-orange-600 mx-auto"></div>
                            <p className="mt-2 text-sm text-gray-600">Loading QR code...</p>
                        </div>
                    ) : qrData?.has_qr ? (
                        <div className="flex flex-col md:flex-row gap-6 items-start">
                            <div className="bg-gray-50 border-2 border-dashed border-gray-300 rounded-xl p-6 flex flex-col items-center">
                                <p className="text-xs text-gray-600 uppercase tracking-wider mb-4">QR Code</p>
                                {qrImageUrl && (
                                    <img 
                                        src={qrImageUrl} 
                                        alt="Gym Attendance QR Code" 
                                        className="w-48 h-48 object-contain mb-4"
                                        onError={() => setQrError('Failed to load QR image')}
                                    />
                                )}
                                <p className="text-xs text-gray-500 mt-2 text-center">
                                    Scan this QR code to check in at {qrData.gym?.name || 'your gym'}
                                </p>
                            </div>

                            <div className="flex-1 space-y-4">
                                <div className="flex flex-col sm:flex-row gap-3">
                                    <button
                                        onClick={handleDownloadQR}
                                        className="flex items-center justify-center gap-2 bg-gray-100 hover:bg-gray-200 text-gray-700 font-medium py-3 px-6 rounded-xl transition-colors"
                                    >
                                        <DocumentArrowDownIcon className="w-5 h-5" />
                                        Download QR Code
                                    </button>
                                    <button
                                        onClick={handlePrintQR}
                                        className="flex items-center justify-center gap-2 bg-gray-100 hover:bg-gray-200 text-gray-700 font-medium py-3 px-6 rounded-xl transition-colors"
                                    >
                                        <PrinterIcon className="w-5 h-5" />
                                        Print QR Code
                                    </button>
                                </div>

                                <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
                                    <h4 className="font-semibold text-blue-900 mb-2 text-sm">How to Use</h4>
                                    <ol className="text-sm text-blue-800 space-y-1 list-decimal list-inside">
                                        <li>Print the QR code and display it at your gym entrance</li>
                                        <li>Members will scan this QR code to check in</li>
                                        <li>Each member can only check in once per day</li>
                                    </ol>
                                </div>
                            </div>
                        </div>
                    ) : (
                        <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-6">
                            <p className="text-yellow-800 text-sm">
                                No QR code generated yet. Please contact support to generate your gym's attendance QR code.
                            </p>
                        </div>
                    )}
                </div>
            )}

            <div className="bg-white border border-gray-200 rounded-2xl overflow-hidden shadow-sm">
                {loading ? (
                    <div className="p-8 text-center text-gray-500">
                        Loading attendance records...
                    </div>
                ) : attendance.length === 0 ? (
                    <div className="p-8 text-center text-gray-500">
                        {searchQuery ? 'No attendance records found matching your search.' : 'No attendance records found.'}
                    </div>
                ) : (
                    <div className="overflow-x-auto">
                        <table className="w-full">
                            <thead>
                                <tr className="border-b border-gray-200 bg-gray-50">
                                    <th className="text-left px-6 py-4 text-xs font-semibold uppercase tracking-wider text-gray-600">
                                        Member
                                    </th>
                                    <th className="text-left px-6 py-4 text-xs font-semibold uppercase tracking-wider text-gray-600">
                                        Date
                                    </th>
                                    <th className="text-left px-6 py-4 text-xs font-semibold uppercase tracking-wider text-gray-600">
                                        Check In
                                    </th>
                                    <th className="text-left px-6 py-4 text-xs font-semibold uppercase tracking-wider text-gray-600">
                                        Check Out
                                    </th>
                                    <th className="text-left px-6 py-4 text-xs font-semibold uppercase tracking-wider text-gray-600">
                                        Duration
                                    </th>
                                    <th className="text-left px-6 py-4 text-xs font-semibold uppercase tracking-wider text-gray-600">
                                        Status
                                    </th>
                                    <th className="text-left px-6 py-4 text-xs font-semibold uppercase tracking-wider text-gray-600">
                                        Actions
                                    </th>
                                </tr>
                            </thead>
                            <tbody>
                                {attendance.map((record) => (
                                    <tr key={record.id} className="border-b border-gray-100 hover:bg-gray-50">
                                        <td className="px-6 py-4">
                                            <div>
                                                <p className="text-sm text-gray-900 font-medium">
                                                    {record.member_name}
                                                </p>
                                                <p className="text-xs text-gray-500 font-mono">
                                                    {record.member_phone}
                                                </p>
                                            </div>
                                        </td>
                                        <td className="px-6 py-4 text-sm text-gray-700">
                                            {formatDate(record.attendance_date)}
                                        </td>
                                        <td className="px-6 py-4 text-sm text-gray-700">
                                            {formatDateTime(record.check_in_time)}
                                        </td>
                                        <td className="px-6 py-4 text-sm text-gray-700">
                                            {formatDateTime(record.check_out_time)}
                                        </td>
                                        <td className="px-6 py-4 text-sm text-gray-700 font-medium">
                                            {formatDuration(record.duration_minutes)}
                                        </td>
                                        <td className="px-6 py-4">
                                            <span className={`inline-flex px-2 py-1 rounded-full text-xs font-semibold border ${getStatusColor(record.status)}`}>
                                                {record.status}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4">
                                            <div className="flex items-center gap-2">
                                                {record.status === 'Checked In' && (
                                                    <button
                                                        onClick={() => handleCheckout(record.id)}
                                                        className="bg-green-600 hover:bg-green-700 text-white px-3 py-1.5 rounded-lg text-xs font-medium transition-colors"
                                                    >
                                                        Check Out
                                                    </button>
                                                )}
                                                <Link
                                                    to={`/attendance/${record.id}`}
                                                    className="bg-gray-100 hover:bg-gray-200 text-gray-700 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors"
                                                >
                                                    View
                                                </Link>
                                                <Link
                                                    to={`/attendance/${record.id}/edit`}
                                                    className="bg-orange-600 hover:bg-orange-700 text-white px-3 py-1.5 rounded-lg text-xs font-medium transition-colors"
                                                >
                                                    Edit
                                                </Link>
                                                <button
                                                    onClick={() => setDeleteModal({ isOpen: true, record })}
                                                    className="bg-red-600 hover:bg-red-700 text-white px-3 py-1.5 rounded-lg text-xs font-medium transition-colors"
                                                >
                                                    Delete
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>

            {deleteModal.isOpen && (
                <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
                    <div className="bg-white border border-gray-200 rounded-2xl p-6 max-w-md w-full shadow-lg">
                        <h3 className="text-lg font-bold text-gray-900 mb-2">Delete Attendance Record</h3>
                        <p className="text-sm text-gray-600 mb-6">
                            Are you sure you want to delete the attendance record for <strong className="text-gray-900">{deleteModal.record?.member_name}</strong>? This action cannot be undone.
                        </p>
                        <div className="flex gap-3">
                            <button
                                onClick={() => handleDelete(deleteModal.record.id)}
                                className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-xl text-sm font-medium transition-colors"
                            >
                                Delete
                            </button>
                            <button
                                onClick={() => setDeleteModal({ isOpen: false, record: null })}
                                className="bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-2 rounded-xl text-sm font-medium transition-colors"
                            >
                                Cancel
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}