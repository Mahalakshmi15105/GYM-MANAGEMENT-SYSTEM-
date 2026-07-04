import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';

export default function MembersPage() {
    const { user } = useAuth();
    const [members, setMembers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [searchQuery, setSearchQuery] = useState('');
    const [statusFilter, setStatusFilter] = useState('All');
    const [deleteModal, setDeleteModal] = useState({ isOpen: false, member: null });

    useEffect(() => {
        fetchMembers();
    }, []);

    const fetchMembers = async () => {
        try {
            const response = await api.get('/api/members');
            setMembers(response.data.members || []);
        } catch (err) {
            console.error(err);
            setError(err.response?.data?.error || 'Failed to fetch members');
        } finally {
            setLoading(false);
        }
    };

    const handleSearch = async (query) => {
        if (!query.trim()) {
            fetchMembers();
            return;
        }

        try {
            const response = await api.get(`/api/members/search?q=${encodeURIComponent(query)}`);
            setMembers(response.data.members || []);
        } catch (err) {
            console.error(err);
            setError('Search failed');
        }
    };

    const handleDelete = async (memberId) => {
        try {
            await api.delete(`/api/members/${memberId}`);
            setMembers(members.filter(m => m.id !== memberId));
            setDeleteModal({ isOpen: false, member: null });
        } catch (err) {
            console.error(err);
            setError(err.response?.data?.error || 'Failed to delete member');
        }
    };

    const filteredMembers = members.filter(member => {
        if (statusFilter !== 'All' && member.status !== statusFilter) return false;
        return true;
    });

    const formatDate = (dateString) => {
        if (!dateString) return '-';
        return new Date(dateString).toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric'
        });
    };

    const getStatusColor = (status) => {
        switch (status) {
            case 'Active':
                return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20';
            case 'Expired':
                return 'bg-rose-500/10 text-rose-400 border-rose-500/20';
            case 'Inactive':
                return 'bg-slate-500/10 text-slate-400 border-slate-500/20';
            default:
                return 'bg-slate-500/10 text-slate-400 border-slate-500/20';
        }
    };

    return (
        <div className="space-y-8">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-bold text-white mb-1">Members Management</h1>
                    <p className="text-sm text-slate-400">
                        Manage your gym members - Gym ID: {user?.gym_id}
                    </p>
                </div>
                <Link
                    to="/members/add"
                    className="bg-gradient-to-r from-emerald-400 to-teal-500 hover:from-emerald-500 hover:to-teal-600 text-slate-950 font-bold px-6 py-3 rounded-xl transition-all duration-200 self-start md:self-auto text-center"
                >
                    + Add Member
                </Link>
            </div>

            <div className="bg-slate-900/50 border border-slate-850 p-6 rounded-2xl">
                <div className="flex flex-col md:flex-row gap-4">
                    <div className="flex-1">
                        <input
                            type="text"
                            placeholder="Search by name, phone, email, or member ID..."
                            value={searchQuery}
                            onChange={(e) => {
                                setSearchQuery(e.target.value);
                                handleSearch(e.target.value);
                            }}
                            className="w-full bg-slate-950 border border-slate-850 focus:border-emerald-500/40 rounded-xl px-4 py-3 text-sm text-slate-100 placeholder-slate-600 focus:outline-none transition-all duration-200"
                        />
                    </div>
                    <div>
                        <select
                            value={statusFilter}
                            onChange={(e) => setStatusFilter(e.target.value)}
                            className="bg-slate-950 border border-slate-850 focus:border-emerald-500/40 rounded-xl px-4 py-3 text-sm text-slate-100 focus:outline-none transition-all duration-200"
                        >
                            <option value="All">All Status</option>
                            <option value="Active">Active</option>
                            <option value="Expired">Expired</option>
                            <option value="Inactive">Inactive</option>
                        </select>
                    </div>
                </div>
            </div>

            {error && (
                <div className="bg-rose-500/10 border border-rose-500/20 text-rose-400 text-sm p-4 rounded-xl">
                    {error}
                </div>
            )}

            <div className="bg-slate-900/50 border border-slate-850 rounded-2xl overflow-hidden">
                {loading ? (
                    <div className="p-8 text-center text-slate-400">
                        Loading members...
                    </div>
                ) : filteredMembers.length === 0 ? (
                    <div className="p-8 text-center text-slate-400">
                        {searchQuery ? 'No members found matching your search.' : 'No members registered yet.'}
                    </div>
                ) : (
                    <div className="overflow-x-auto">
                        <table className="w-full">
                            <thead>
                                <tr className="border-b border-slate-800">
                                    <th className="text-left px-6 py-4 text-xs font-semibold uppercase tracking-wider text-slate-400">
                                        Photo
                                    </th>
                                    <th className="text-left px-6 py-4 text-xs font-semibold uppercase tracking-wider text-slate-400">
                                        Member ID
                                    </th>
                                    <th className="text-left px-6 py-4 text-xs font-semibold uppercase tracking-wider text-slate-400">
                                        Full Name
                                    </th>
                                    <th className="text-left px-6 py-4 text-xs font-semibold uppercase tracking-wider text-slate-400">
                                        Phone
                                    </th>
                                    <th className="text-left px-6 py-4 text-xs font-semibold uppercase tracking-wider text-slate-400">
                                        Plan
                                    </th>
                                    <th className="text-left px-6 py-4 text-xs font-semibold uppercase tracking-wider text-slate-400">
                                        Start Date
                                    </th>
                                    <th className="text-left px-6 py-4 text-xs font-semibold uppercase tracking-wider text-slate-400">
                                        End Date
                                    </th>
                                    <th className="text-left px-6 py-4 text-xs font-semibold uppercase tracking-wider text-slate-400">
                                        Status
                                    </th>
                                    <th className="text-left px-6 py-4 text-xs font-semibold uppercase tracking-wider text-slate-400">
                                        Actions
                                    </th>
                                </tr>
                            </thead>
                            <tbody>
                                {filteredMembers.map((member) => (
                                    <tr key={member.id} className="border-b border-slate-850 hover:bg-slate-800/30">
                                        <td className="px-6 py-4">
                                            <div className="w-10 h-10 bg-slate-700 border border-slate-600 rounded-lg flex items-center justify-center">
                                                <span className="text-sm font-semibold text-slate-300">
                                                    {member.first_name?.charAt(0)?.toUpperCase() || '?'}
                                                </span>
                                            </div>
                                        </td>
                                        <td className="px-6 py-4 text-sm font-mono text-slate-300">
                                            {member.member_id}
                                        </td>
                                        <td className="px-6 py-4 text-sm text-slate-100 font-medium">
                                            {member.first_name} {member.last_name}
                                        </td>
                                        <td className="px-6 py-4 text-sm font-mono text-slate-300">
                                            {member.phone || '-'}
                                        </td>
                                        <td className="px-6 py-4 text-sm text-slate-300">
                                            {member.membership_plan_name || '-'}
                                        </td>
                                        <td className="px-6 py-4 text-sm text-slate-300">
                                            {formatDate(member.membership_start_date)}
                                        </td>
                                        <td className="px-6 py-4 text-sm text-slate-300">
                                            {formatDate(member.membership_end_date)}
                                        </td>
                                        <td className="px-6 py-4">
                                            <span className={`inline-flex px-2 py-1 rounded-full text-xs font-semibold border ${getStatusColor(member.status)}`}>
                                                {member.status}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4">
                                            <div className="flex items-center gap-2">
                                                <Link
                                                    to={`/members/${member.id}`}
                                                    className="bg-slate-700 hover:bg-slate-600 text-slate-200 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors"
                                                >
                                                    View
                                                </Link>
                                                <Link
                                                    to={`/members/${member.id}/edit`}
                                                    className="bg-emerald-600 hover:bg-emerald-700 text-white px-3 py-1.5 rounded-lg text-xs font-medium transition-colors"
                                                >
                                                    Edit
                                                </Link>
                                                <button
                                                    onClick={() => setDeleteModal({ isOpen: true, member })}
                                                    className="bg-rose-600 hover:bg-rose-700 text-white px-3 py-1.5 rounded-lg text-xs font-medium transition-colors"
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
                <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
                    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 max-w-md w-full">
                        <h3 className="text-lg font-bold text-white mb-2">Delete Member</h3>
                        <p className="text-sm text-slate-400 mb-6">
                            Are you sure you want to delete <strong className="text-white">{deleteModal.member?.first_name} {deleteModal.member?.last_name}</strong>? This action cannot be undone.
                        </p>
                        <div className="flex gap-3">
                            <button
                                onClick={() => handleDelete(deleteModal.member.id)}
                                className="bg-rose-600 hover:bg-rose-700 text-white px-4 py-2 rounded-xl text-sm font-medium transition-colors"
                            >
                                Delete
                            </button>
                            <button
                                onClick={() => setDeleteModal({ isOpen: false, member: null })}
                                className="bg-slate-700 hover:bg-slate-600 text-slate-200 px-4 py-2 rounded-xl text-sm font-medium transition-colors"
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