import { useState, useEffect } from 'react';
import { PlusIcon, MagnifyingGlassIcon, TrashIcon, PaperClipIcon, PhotoIcon, CheckCircleIcon } from '@heroicons/react/24/outline';
import api from '../services/api';
import BroadcastModal from '../components/BroadcastModal';

export default function BroadcastMessagesPage() {
  const [broadcasts, setBroadcasts] = useState([]);
  const [filteredBroadcasts, setFilteredBroadcasts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [selectedBroadcast, setSelectedBroadcast] = useState(null);
  const [viewingBroadcast, setViewingBroadcast] = useState(null);

  useEffect(() => {
    fetchBroadcasts();
  }, []);

  useEffect(() => {
    const filtered = broadcasts.filter(broadcast =>
      broadcast.subject.toLowerCase().includes(searchTerm.toLowerCase()) ||
      broadcast.title.toLowerCase().includes(searchTerm.toLowerCase())
    );
    setFilteredBroadcasts(filtered);
  }, [searchTerm, broadcasts]);

  const fetchBroadcasts = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/broadcasts');
      setBroadcasts(response.data.broadcasts);
      setFilteredBroadcasts(response.data.broadcasts);
    } catch (error) {
      console.error('Failed to fetch broadcasts:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (broadcastId) => {
    if (!window.confirm('Are you sure you want to delete this broadcast?')) return;

    try {
      await api.delete(`/api/broadcasts/${broadcastId}`);
      setBroadcasts(broadcasts.filter(b => b.id !== broadcastId));
      setFilteredBroadcasts(filteredBroadcasts.filter(b => b.id !== broadcastId));
    } catch (error) {
      console.error('Failed to delete broadcast:', error);
      alert('Failed to delete broadcast');
    }
  };

  const handleView = (broadcast) => {
    setViewingBroadcast(broadcast);
  };

  const getRecipientTypeLabel = (type) => {
    const labels = {
      'all': 'All Members',
      'active': 'Active Members',
      'expiring': 'Expiring Members',
      'selected': 'Selected Members'
    };
    return labels[type] || type;
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-500"></div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Broadcast Messages</h1>
        <p className="text-gray-600 mt-1">Send announcements to your members</p>
      </div>

      {/* Header with Search and New Button */}
      <div className="flex flex-col sm:flex-row gap-4 mb-6">
        <div className="relative flex-1">
          <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
          <input
            type="text"
            placeholder="Search broadcasts..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 w-full"
          />
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="flex items-center gap-2 bg-orange-500 hover:bg-orange-600 text-white px-4 py-2 rounded-lg font-medium transition-colors"
        >
          <PlusIcon className="h-5 w-5" />
          New Broadcast
        </button>
      </div>

      {/* Broadcasts List */}
      {filteredBroadcasts.length === 0 ? (
        <div className="text-center py-12 bg-gray-50 rounded-xl">
          <p className="text-gray-500">No broadcasts found</p>
          {searchTerm && (
            <p className="text-sm text-gray-400 mt-1">Try a different search term</p>
          )}
          {!searchTerm && broadcasts.length === 0 && (
            <button
              onClick={() => setShowModal(true)}
              className="mt-4 text-orange-600 hover:text-orange-700 font-medium"
            >
              Create your first broadcast
            </button>
          )}
        </div>
      ) : (
        <div className="space-y-4">
          {filteredBroadcasts.map((broadcast) => (
            <div
              key={broadcast.id}
              className="bg-white border border-gray-200 rounded-xl p-4 hover:shadow-md transition-shadow cursor-pointer"
              onClick={() => handleView(broadcast)}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <h3 className="text-lg font-semibold text-gray-900">{broadcast.title}</h3>
                    {broadcast.banner_url && (
                      <PhotoIcon className="h-4 w-4 text-orange-500" />
                    )}
                    {broadcast.attachment_url && (
                      <PaperClipIcon className="h-4 w-4 text-orange-500" />
                    )}
                  </div>
                  <p className="text-sm text-gray-600 mb-2">{broadcast.subject}</p>
                  <div className="flex flex-wrap gap-4 text-sm text-gray-500">
                    <span>Sent to: {getRecipientTypeLabel(broadcast.recipient_type)}</span>
                    <span>Date: {formatDate(broadcast.created_at)}</span>
                    <span>Recipients: {broadcast.total_recipients}</span>
                    <span className="flex items-center gap-1">
                      <CheckCircleIcon className="h-4 w-4 text-green-500" />
                      Read: {broadcast.read_count}
                    </span>
                  </div>
                </div>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    handleDelete(broadcast.id);
                  }}
                  className="p-2 text-gray-400 hover:text-red-600 transition-colors"
                  title="Delete broadcast"
                >
                  <TrashIcon className="h-5 w-5" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* New Broadcast Modal */}
      {showModal && (
        <BroadcastModal
          isOpen={showModal}
          onClose={() => {
            setShowModal(false);
            setSelectedBroadcast(null);
          }}
          onSuccess={fetchBroadcasts}
        />
      )}

      {/* View Broadcast Modal */}
      {viewingBroadcast && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white border border-gray-200 rounded-2xl p-6 max-w-3xl w-full max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-gray-900">{viewingBroadcast.title}</h2>
              <button
                onClick={() => setViewingBroadcast(null)}
                className="text-gray-400 hover:text-gray-600 transition-colors"
              >
                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {viewingBroadcast.banner_url && (
              <img
                src={`http://127.0.0.1:5000${viewingBroadcast.banner_url}`}
                alt="Banner"
                className="w-full h-48 object-cover rounded-lg mb-4"
              />
            )}

            <div className="mb-4">
              <p className="text-sm text-gray-600 mb-2">Subject: {viewingBroadcast.subject}</p>
              <p className="text-gray-900 whitespace-pre-wrap">{viewingBroadcast.message}</p>
            </div>

            {viewingBroadcast.attachment_url && (
              <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                <div className="flex items-center gap-2">
                  <PaperClipIcon className="h-5 w-5 text-gray-600" />
                  <a
                    href={`http://127.0.0.1:5000${viewingBroadcast.attachment_url}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-orange-600 hover:text-orange-700 font-medium"
                  >
                    Download Attachment
                  </a>
                </div>
              </div>
            )}

            <div className="mt-6 pt-4 border-t border-gray-200">
              <div className="flex flex-wrap gap-4 text-sm text-gray-500">
                <span>Sent to: {getRecipientTypeLabel(viewingBroadcast.recipient_type)}</span>
                <span>Date: {formatDate(viewingBroadcast.created_at)}</span>
                <span>Recipients: {viewingBroadcast.total_recipients}</span>
                <span>Read: {viewingBroadcast.read_count}</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
