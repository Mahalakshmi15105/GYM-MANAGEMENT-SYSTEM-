import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';

export default function MembershipPlansPage() {
    const { user } = useAuth();
    const [plans, setPlans] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [searchQuery, setSearchQuery] = useState('');
    const [statusFilter, setStatusFilter] = useState('All');
    const [deleteModal, setDeleteModal] = useState({ isOpen: false, plan: null });

    useEffect(() => {
        fetchPlans();
    }, []);

    const fetchPlans = async () => {
        try {
            const response = await api.get('/api/membership-plans');
            setPlans(response.data.membership_plans || []);
        } catch (err) {
            console.error(err);
            setError(err.response?.data?.error || 'Failed to fetch membership plans');
        } finally {
            setLoading(false);
        }
    };

    const handleSearch = async (query) => {
        if (!query.trim()) {
            fetchPlans();
            return;
        }

        try {
            const response = await api.get(`/api/membership-plans/search?q=${encodeURIComponent(query)}`);
            setPlans(response.data.membership_plans || []);
        } catch (err) {
            console.error(err);
            setError('Search failed');
        }
    };

    const handleDelete = async (planId) => {
        try {
            await api.delete(`/api/membership-plans/${planId}`);
            setPlans(plans.filter(p => p.id !== planId));
            setDeleteModal({ isOpen: false, plan: null });
        } catch (err) {
            console.error(err);
            setError(err.response?.data?.error || 'Failed to delete membership plan');
        }
    };

    const filteredPlans = plans.filter(plan => {
        if (statusFilter !== 'All' && plan.status !== statusFilter) return false;
        return true;
    });

    const formatPrice = (price) => {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD'
        }).format(price);
    };

    const formatDuration = (days) => {
        if (days === 30) return '1 Month';
        if (days === 90) return '3 Months';
        if (days === 180) return '6 Months';
        if (days === 365) return '1 Year';
        if (days < 30) return `${days} Days`;
        if (days % 30 === 0) return `${days / 30} Months`;
        return `${days} Days`;
    };

    const getStatusColor = (status) => {
        switch (status) {
            case 'Active':
                return 'bg-green-50 text-green-700 border-green-200';
            case 'Inactive':
                return 'bg-gray-50 text-gray-600 border-gray-200';
            default:
                return 'bg-gray-50 text-gray-600 border-gray-200';
        }
    };

    return (
        <div className="space-y-8">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900 mb-1">Membership Plans</h1>
                    <p className="text-sm text-gray-600">
                        Manage your gym's membership plans - Gym ID: {user?.gym_id}
                    </p>
                </div>
                <Link
                    to="/membership-plans/add"
                    className="bg-orange-600 hover:bg-orange-700 text-white font-bold px-6 py-3 rounded-xl transition-all duration-200 self-start md:self-auto text-center shadow-sm"
                >
                    + Add Plan
                </Link>
            </div>

            <div className="bg-white border border-gray-200 p-6 rounded-2xl shadow-sm">
                <div className="flex flex-col md:flex-row gap-4">
                    <div className="flex-1">
                        <input
                            type="text"
                            placeholder="Search by plan name or description..."
                            value={searchQuery}
                            onChange={(e) => {
                                setSearchQuery(e.target.value);
                                handleSearch(e.target.value);
                            }}
                            className="w-full bg-gray-50 border border-gray-200 focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 rounded-xl px-4 py-3 text-sm text-gray-900 placeholder-gray-500 focus:outline-none transition-all duration-200"
                        />
                    </div>
                    <div>
                        <select
                            value={statusFilter}
                            onChange={(e) => setStatusFilter(e.target.value)}
                            className="bg-gray-50 border border-gray-200 focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 rounded-xl px-4 py-3 text-sm text-gray-900 focus:outline-none transition-all duration-200"
                        >
                            <option value="All">All Status</option>
                            <option value="Active">Active</option>
                            <option value="Inactive">Inactive</option>
                        </select>
                    </div>
                </div>
            </div>

            {error && (
                <div className="bg-red-50 border border-red-200 text-red-700 text-sm p-4 rounded-xl">
                    {error}
                </div>
            )}

            <div className="bg-white border border-gray-200 rounded-2xl overflow-hidden shadow-sm">
                {loading ? (
                    <div className="p-8 text-center text-gray-500">
                        Loading membership plans...
                    </div>
                ) : filteredPlans.length === 0 ? (
                    <div className="p-8 text-center text-gray-500">
                        {searchQuery ? 'No plans found matching your search.' : 'No membership plans created yet.'}
                    </div>
                ) : (
                    <div className="overflow-x-auto">
                        <table className="w-full">
                            <thead>
                                <tr className="border-b border-gray-200 bg-gray-50">
                                    <th className="text-left px-6 py-4 text-xs font-semibold uppercase tracking-wider text-gray-600">
                                        Plan Name
                                    </th>
                                    <th className="text-left px-6 py-4 text-xs font-semibold uppercase tracking-wider text-gray-600">
                                        Duration
                                    </th>
                                    <th className="text-left px-6 py-4 text-xs font-semibold uppercase tracking-wider text-gray-600">
                                        Price
                                    </th>
                                    <th className="text-left px-6 py-4 text-xs font-semibold uppercase tracking-wider text-gray-600">
                                        Description
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
                                {filteredPlans.map((plan) => (
                                    <tr key={plan.id} className="border-b border-gray-100 hover:bg-gray-50">
                                        <td className="px-6 py-4 text-sm text-gray-900 font-medium">
                                            {plan.plan_name}
                                        </td>
                                        <td className="px-6 py-4 text-sm text-gray-700">
                                            {formatDuration(plan.duration)}
                                        </td>
                                        <td className="px-6 py-4 text-sm text-gray-900 font-semibold">
                                            {formatPrice(plan.price)}
                                        </td>
                                        <td className="px-6 py-4 text-sm text-gray-700 max-w-xs truncate">
                                            {plan.description || '-'}
                                        </td>
                                        <td className="px-6 py-4">
                                            <span className={`inline-flex px-2 py-1 rounded-full text-xs font-semibold border ${getStatusColor(plan.status)}`}>
                                                {plan.status}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4">
                                            <div className="flex items-center gap-2">
                                                <Link
                                                    to={`/membership-plans/${plan.id}`}
                                                    className="bg-gray-100 hover:bg-gray-200 text-gray-700 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors"
                                                >
                                                    View
                                                </Link>
                                                <Link
                                                    to={`/membership-plans/${plan.id}/edit`}
                                                    className="bg-orange-600 hover:bg-orange-700 text-white px-3 py-1.5 rounded-lg text-xs font-medium transition-colors"
                                                >
                                                    Edit
                                                </Link>
                                                <button
                                                    onClick={() => setDeleteModal({ isOpen: true, plan })}
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
                        <h3 className="text-lg font-bold text-gray-900 mb-2">Delete Plan</h3>
                        <p className="text-sm text-gray-600 mb-6">
                            Are you sure you want to delete <strong className="text-gray-900">{deleteModal.plan?.plan_name}</strong>? This action cannot be undone.
                        </p>
                        <div className="flex gap-3">
                            <button
                                onClick={() => handleDelete(deleteModal.plan.id)}
                                className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-xl text-sm font-medium transition-colors"
                            >
                                Delete
                            </button>
                            <button
                                onClick={() => setDeleteModal({ isOpen: false, plan: null })}
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