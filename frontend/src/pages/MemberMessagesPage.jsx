import { useState, useEffect } from 'react';
import { PhotoIcon, PaperClipIcon, CheckCircleIcon } from '@heroicons/react/24/outline';
import api from '../services/api';

export default function MemberMessagesPage() {
  const [broadcasts, setBroadcasts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedBroadcast, setSelectedBroadcast] = useState(null);

  useEffect(() => {
    fetchBroadcasts();
  }, []);

  const fetchBroadcasts = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/broadcasts/member');
      setBroadcasts(response.data.broadcasts);
    } catch (error) {
      console.error('Failed to fetch broadcasts:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleViewBroadcast = async (broadcast) => {
    setSelectedBroadcast(broadcast);
    
    // Mark as read if not already read
    if (!broadcast.is_read) {
      try {
        await api.post(`/api/broadcasts/member/${broadcast.id}/read`);
        // Update local state
        setBroadcasts(prev => prev.map(b => 
          b.id === broadcast.id 
            ? { ...b, is_read: true, read_at: new Date().toISOString() }
            : b
        ));
      } catch (error) {
        console.error('Failed to mark as read:', error);
      }
    }
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
      {!selectedBroadcast ? (
        <>
          <div className="mb-6">
            <h1 className="text-2xl font-bold text-gray-900">Messages</h1>
            <p className="text-gray-600 mt-1">Announcements from your gym</p>
          </div>

          {broadcasts.length === 0 ? (
            <div className="text-center py-12 bg-gray-50 rounded-xl">
              <p className="text-gray-500">No messages yet</p>
              <p className="text-sm text-gray-400 mt-1">Check back later for announcements</p>
            </div>
          ) : (
            <div className="space-y-4">
              {broadcasts.map((broadcast) => (
                <div
                  key={broadcast.id}
                  onClick={() => handleViewBroadcast(broadcast)}
                  className={`bg-white border rounded-xl p-4 cursor-pointer transition-shadow hover:shadow-md ${
                    !broadcast.is_read ? 'border-orange-300 bg-orange-50' : 'border-gray-200'
                  }`}
                >
                  <div className="flex items-start gap-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-sm font-medium text-orange-600">Gym Owner</span>
                        {!broadcast.is_read && (
                          <span className="bg-orange-500 text-white text-xs px-2 py-0.5 rounded-full">New</span>
                        )}
                      </div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-1">{broadcast.title}</h3>
                      <p className="text-sm text-gray-600 mb-2">{broadcast.subject}</p>
                      <div className="flex items-center gap-3 text-sm text-gray-500">
                        <span>{formatDate(broadcast.created_at)}</span>
                        {broadcast.banner_url && <PhotoIcon className="h-4 w-4" />}
                        {broadcast.attachment_url && <PaperClipIcon className="h-4 w-4" />}
                      </div>
                    </div>
                    {broadcast.is_read && (
                      <CheckCircleIcon className="h-5 w-5 text-green-500 flex-shrink-0" />
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </>
      ) : (
        <div>
          <button
            onClick={() => setSelectedBroadcast(null)}
            className="mb-4 text-orange-600 hover:text-orange-700 font-medium flex items-center gap-1"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Back to Messages
          </button>

          <div className="bg-white border border-gray-200 rounded-xl p-6">
            <div className="mb-4">
              <span className="text-sm font-medium text-orange-600">Gym Owner</span>
              <h1 className="text-2xl font-bold text-gray-900 mt-1">{selectedBroadcast.title}</h1>
              <p className="text-sm text-gray-500 mt-1">{formatDate(selectedBroadcast.created_at)}</p>
            </div>

            {selectedBroadcast.banner_url && (
              <img
                src={`http://127.0.0.1:5000${selectedBroadcast.banner_url}`}
                alt="Banner"
                className="w-full h-64 object-cover rounded-lg mb-4"
              />
            )}

            <div className="mb-4">
              <p className="text-sm text-gray-600 mb-2">Subject: {selectedBroadcast.subject}</p>
              <p className="text-gray-900 whitespace-pre-wrap text-lg">{selectedBroadcast.message}</p>
            </div>

            {selectedBroadcast.attachment_url && (
              <div className="mt-6 p-4 bg-gray-50 rounded-lg">
                <div className="flex items-center gap-2">
                  <PaperClipIcon className="h-5 w-5 text-gray-600" />
                  <a
                    href={`http://127.0.0.1:5000${selectedBroadcast.attachment_url}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-orange-600 hover:text-orange-700 font-medium"
                  >
                    Download Attachment
                  </a>
                </div>
              </div>
            )}

            <div className="mt-6 pt-4 border-t border-gray-200 text-sm text-gray-500">
              This is a read-only announcement. You cannot reply to this message.
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
