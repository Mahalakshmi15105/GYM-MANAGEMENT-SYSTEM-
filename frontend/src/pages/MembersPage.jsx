import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useTranslation } from '../utils/i18n';
import BulkUploadModal from '../components/BulkUploadModal';
import api from '../services/api';
import { PlusIcon, KeyIcon, ArrowUpTrayIcon } from '@heroicons/react/24/outline';

export default function MembersPage() {
    const { user } = useAuth();
    const { t } = useTranslation(user?.gym_id);
    const [members, setMembers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [searchQuery, setSearchQuery] = useState('');
    const [statusFilter, setStatusFilter] = useState('All');
    const [deleteModal, setDeleteModal] = useState({ isOpen: false, member: null });
    const [actionModal, setActionModal] = useState({ isOpen: false, member: null, action: null });
    const [actionLoading, setActionLoading] = useState(false);
    const [bulkUploadModal, setBulkUploadModal] = useState({ isOpen: false });

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
        setActionLoading(true);
        try {
            await api.delete(`/api/members/${memberId}`);
            setMembers(members.filter(m => m.id !== memberId));
            setDeleteModal({ isOpen: false, member: null });
        } catch (err) {
            console.error(err);
            const errorMsg = err.response?.data?.message || err.response?.data?.error || 'Failed to delete member';
            setError(errorMsg);
            setDeleteModal({ isOpen: false, member: null });
        } finally {
            setActionLoading(false);
        }
    };

    const handleDeactivate = async (memberId) => {
        setActionLoading(true);
        try {
            await api.post(`/api/members/${memberId}/deactivate`);
            // Refresh members list
            await fetchMembers();
            setActionModal({ isOpen: false, member: null, action: null });
        } catch (err) {
            console.error(err);
            setError(err.response?.data?.error || 'Failed to deactivate member');
        } finally {
            setActionLoading(false);
        }
    };

    const handleReactivate = async (memberId) => {
        setActionLoading(true);
        try {
            await api.post(`/api/members/${memberId}/reactivate`);
            // Refresh members list
            await fetchMembers();
            setActionModal({ isOpen: false, member: null, action: null });
        } catch (err) {
            console.error(err);
            setError(err.response?.data?.error || 'Failed to reactivate member');
        } finally {
            setActionLoading(false);
        }
    };

    const filteredMembers = members.filter(member => {
        if (statusFilter !== 'All' && member.status !== statusFilter) return false;
        return true;
    });

    const formatDate = (dateString) => {
        if (!dateString) return '-';
        return new Date(dateString).toLocaleDateString('en-GB', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric'
        });
    };

    const getStatusColor = (status) => {
        switch (status) {
            case 'Active':
                return 'bg-green-50 text-green-700 border-green-200';
            case 'Expired':
                return 'bg-red-50 text-red-700 border-red-200';
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
                    <h1 className="text-2xl font-bold text-gray-900 mb-1">{t('members.title')}</h1>
                    <p className="text-sm text-gray-600">
                        Manage your gym members - Gym ID: {user?.gym_id}
                    </p>
                </div>
                <div className="flex items-center gap-3 self-start md:self-auto">
                    <Link
                        to="/members/add"
                        className="bg-orange-600 hover:bg-orange-700 text-white font-bold px-6 py-3 rounded-xl transition-all duration-200 text-center shadow-sm flex items-center gap-2"
                    >
                        <PlusIcon className="w-4 h-4" /> {t('members.addMember')}
                    </Link>
                    <button
                        onClick={() => setBulkUploadModal({ isOpen: true })}
                        className="bg-gray-700 hover:bg-gray-800 text-white font-bold px-6 py-3 rounded-xl transition-all duration-200 text-center shadow-sm flex items-center gap-2"
                    >
                        <ArrowUpTrayIcon className="w-4 h-4" /> Bulk Upload
                    </button>
                </div>
            </div>

            <div className="bg-white border border-gray-200 p-6 rounded-2xl shadow-sm">
                <div className="flex flex-col md:flex-row gap-4">
                    <div className="flex-1">
                        <input
                            type="text"
                            placeholder={t('members.searchMembers')}
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
                            <option value="All">{t('common.status')}</option>
                            <option value="Active">{t('common.active')}</option>
                            <option value="Expired">{t('common.inactive')}</option>
                            <option value="Inactive">{t('common.inactive')}</option>
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
                        {t('common.loading')}
                    </div>
                ) : filteredMembers.length === 0 ? (
                    <div className="p-8 text-center text-gray-500">
                        {searchQuery ? t('members.noMembersFound') : t('empty.noMembersDesc')}
                    </div>
                ) : (
                    <div className="overflow-x-auto">
                        <table className="w-full">
                            <thead>
                                <tr className="border-b border-gray-200 bg-gray-50">
                                    <th className="text-left px-6 py-4 text-xs font-semibold uppercase tracking-wider text-gray-600">
                                        Photo
                                    </th>
                                    <th className="text-left px-6 py-4 text-xs font-semibold uppercase tracking-wider text-gray-600">
                                        Member ID
                                    </th>
                                    <th className="text-left px-6 py-4 text-xs font-semibold uppercase tracking-wider text-gray-600">
                                        Full Name
                                    </th>
                                    <th className="text-left px-6 py-4 text-xs font-semibold uppercase tracking-wider text-gray-600">
                                        Phone
                                    </th>
                                    <th className="text-left px-6 py-4 text-xs font-semibold uppercase tracking-wider text-gray-600">
                                        Email
                                    </th>
                                    <th className="text-left px-6 py-4 text-xs font-semibold uppercase tracking-wider text-gray-600">
                                        Account
                                    </th>
                                    <th className="text-left px-6 py-4 text-xs font-semibold uppercase tracking-wider text-gray-600">
                                        Plan
                                    </th>
                                    <th className="text-left px-6 py-4 text-xs font-semibold uppercase tracking-wider text-gray-600">
                                        Joining Date
                                    </th>
                                    <th className="text-left px-6 py-4 text-xs font-semibold uppercase tracking-wider text-gray-600">
                                        Status
                                    </th>
                                    <th className="text-left px-6 py-4 text-xs font-semibold uppercase tracking-wider text-gray-600">
                                        {t('common.actions')}
                                    </th>
                                </tr>
                            </thead>
                            <tbody>
                                {filteredMembers.map((member) => (
                                    <tr key={member.id} className="border-b border-gray-100 hover:bg-gray-50">
                                        <td className="px-6 py-4">
                                            <div className="w-10 h-10 bg-orange-100 border border-orange-200 rounded-lg flex items-center justify-center">
                                                <span className="text-sm font-semibold text-orange-700">
                                                    {member.first_name?.charAt(0)?.toUpperCase() || '?'}
                                                </span>
                                            </div>
                                        </td>
                                        <td className="px-6 py-4 text-sm font-mono text-gray-700">
                                            {member.member_id}
                                        </td>
                                        <td className="px-6 py-4 text-sm text-gray-900 font-medium">
                                            {member.first_name} {member.last_name}
                                        </td>
                                        <td className="px-6 py-4 text-sm font-mono text-gray-700">
                                            {member.phone || '-'}
                                        </td>
                                        <td className="px-6 py-4 text-sm font-mono text-gray-700">
                                            {member.email || '-'}
                                        </td>
                                        <td className="px-6 py-4">
                                            {member.has_account ? (
                                                <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-semibold border bg-green-50 text-green-700 border-green-200">
                                                    <KeyIcon className="w-3 h-3" /> Active
                                                </span>
                                            ) : (
                                                <span className="inline-flex px-2 py-1 rounded-full text-xs font-semibold border bg-gray-50 text-gray-600 border-gray-200">
                                                    No Account
                                                </span>
                                            )}
                                        </td>
                                        <td className="px-6 py-4 text-sm text-gray-700">
                                            {member.membership_plan_name || '-'}
                                        </td>
                                        <td className="px-6 py-4 text-sm text-gray-700">
                                            {formatDate(member.created_at)}
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
                                                    className="bg-gray-100 hover:bg-gray-200 text-gray-700 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors"
                                                >
                                                    {t('common.view')}
                                                </Link>
                                                <Link
                                                    to={`/members/${member.id}/edit`}
                                                    className="bg-orange-600 hover:bg-orange-700 text-white px-3 py-1.5 rounded-lg text-xs font-medium transition-colors"
                                                >
                                                    {t('common.edit')}
                                                </Link>
                                                {member.status === 'Active' ? (
                                                    <button
                                                        onClick={() => setActionModal({ isOpen: true, member, action: 'deactivate' })}
                                                        className="bg-yellow-600 hover:bg-yellow-700 text-white px-3 py-1.5 rounded-lg text-xs font-medium transition-colors"
                                                    >
                                                        {t('members.suspendMember')}
                                                    </button>
                                                ) : (
                                                    <button
                                                        onClick={() => setActionModal({ isOpen: true, member, action: 'reactivate' })}
                                                        className="bg-green-600 hover:bg-green-700 text-white px-3 py-1.5 rounded-lg text-xs font-medium transition-colors"
                                                    >
                                                        {t('members.renewMembership')}
                                                    </button>
                                                )}
                                                <button
                                                    onClick={() => setDeleteModal({ isOpen: true, member })}
                                                    className="bg-red-600 hover:bg-red-700 text-white px-3 py-1.5 rounded-lg text-xs font-medium transition-colors"
                                                >
                                                    {t('common.delete')}
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
                        <h3 className="text-lg font-bold text-gray-900 mb-2">Delete Member</h3>
                        <p className="text-sm text-gray-600 mb-6">
                            Are you sure you want to delete <strong className="text-gray-900">{deleteModal.member?.first_name} {deleteModal.member?.last_name}</strong>? This action cannot be undone.
                        </p>
                        <div className="flex gap-3">
                            <button
                                onClick={() => handleDelete(deleteModal.member.id)}
                                disabled={actionLoading}
                                className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-xl text-sm font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                {actionLoading ? 'Deleting...' : 'Delete'}
                            </button>
                            <button
                                onClick={() => setDeleteModal({ isOpen: false, member: null })}
                                className="bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-2 rounded-xl text-sm font-medium transition-colors"
                            >
                                Cancel
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {actionModal.isOpen && (
                <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
                    <div className="bg-white border border-gray-200 rounded-2xl p-6 max-w-md w-full shadow-lg">
                        <h3 className="text-lg font-bold text-gray-900 mb-2">
                            {actionModal.action === 'deactivate' ? 'Deactivate Member' : 'Reactivate Member'}
                        </h3>
                        <p className="text-sm text-gray-600 mb-6">
                            {actionModal.action === 'deactivate' 
                                ? `Are you sure you want to deactivate <strong className="text-gray-900">${actionModal.member?.first_name} ${actionModal.member?.last_name}</strong>? They will not be able to log in, but all historical data will be preserved.`
                                : `Are you sure you want to reactivate <strong className="text-gray-900">${actionModal.member?.first_name} ${actionModal.member?.last_name}</strong>? They will be able to log in again.`
                            }
                        </p>
                        <div className="flex gap-3">
                            <button
                                onClick={() => actionModal.action === 'deactivate' ? handleDeactivate(actionModal.member.id) : handleReactivate(actionModal.member.id)}
                                disabled={actionLoading}
                                className={`${
                                    actionModal.action === 'deactivate' 
                                        ? 'bg-yellow-600 hover:bg-yellow-700' 
                                        : 'bg-green-600 hover:bg-green-700'
                                } text-white px-4 py-2 rounded-xl text-sm font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed`}
                            >
                                {actionLoading 
                                    ? (actionModal.action === 'deactivate' ? 'Deactivating...' : 'Reactivating...')
                                    : (actionModal.action === 'deactivate' ? 'Deactivate' : 'Reactivate')
                                }
                            </button>
                            <button
                                onClick={() => setActionModal({ isOpen: false, member: null, action: null })}
                                className="bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-2 rounded-xl text-sm font-medium transition-colors"
                            >
                                Cancel
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {bulkUploadModal.isOpen && (
                <BulkUploadModal
                    isOpen={bulkUploadModal.isOpen}
                    onClose={() => setBulkUploadModal({ isOpen: false })}
                    onImportComplete={() => {
                        setBulkUploadModal({ isOpen: false });
                        fetchMembers();
                    }}
                />
            )}
        </div>
    );
}