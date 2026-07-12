import { useState, useEffect } from 'react';
import { XMarkIcon, PhotoIcon, PaperClipIcon, ChevronDownIcon } from '@heroicons/react/24/outline';
import api from '../services/api';

export default function BroadcastModal({ isOpen, onClose, onSuccess }) {
  const [formData, setFormData] = useState({
    subject: '',
    title: '',
    message: '',
    recipient_type: 'all',
    selected_members: []
  });
  const [attachment, setAttachment] = useState(null);
  const [banner, setBanner] = useState(null);
  const [members, setMembers] = useState([]);
  const [memberSearch, setMemberSearch] = useState('');
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (isOpen) {
      fetchMembers();
    }
  }, [isOpen]);

  const fetchMembers = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/broadcasts/members');
      setMembers(response.data.members);
    } catch (error) {
      console.error('Failed to fetch members:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleFileChange = (e, type) => {
    const file = e.target.files[0];
    if (file) {
      // Validate file size (10 MB)
      if (file.size > 10 * 1024 * 1024) {
        setError('File size exceeds 10 MB limit');
        return;
      }
      // Validate file type
      const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'application/pdf'];
      if (!allowedTypes.includes(file.type)) {
        setError('Invalid file type. Only JPG, PNG, and PDF are allowed');
        return;
      }
      
      if (type === 'attachment') {
        setAttachment(file);
      } else if (type === 'banner') {
        setBanner(file);
      }
      setError('');
    }
  };

  const handleMemberToggle = (memberId) => {
    setFormData(prev => {
      const selected = prev.selected_members.includes(memberId)
        ? prev.selected_members.filter(id => id !== memberId)
        : [...prev.selected_members, memberId];
      return { ...prev, selected_members: selected };
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    // Validation
    if (!formData.subject.trim()) {
      setError('Subject is required');
      return;
    }
    if (!formData.title.trim()) {
      setError('Offer Title is required');
      return;
    }
    if (!formData.message.trim()) {
      setError('Message is required');
      return;
    }
    if (formData.recipient_type === 'selected' && formData.selected_members.length === 0) {
      setError('Please select at least one member');
      return;
    }

    setSubmitting(true);

    const data = new FormData();
    data.append('subject', formData.subject);
    data.append('title', formData.title);
    data.append('message', formData.message);
    data.append('recipient_type', formData.recipient_type);
    if (formData.recipient_type === 'selected') {
      data.append('selected_members', formData.selected_members.join(','));
    }
    if (attachment) {
      data.append('attachment', attachment);
    }
    if (banner) {
      data.append('banner', banner);
    }

    try {
      const response = await api.post('/api/broadcasts', data, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      onSuccess();
      onClose();
      // Reset form
      setFormData({
        subject: '',
        title: '',
        message: '',
        recipient_type: 'all',
        selected_members: []
      });
      setAttachment(null);
      setBanner(null);
    } catch (error) {
      console.error('Failed to create broadcast:', error);
      setError(error.response?.data?.error || 'Failed to send broadcast');
    } finally {
      setSubmitting(false);
    }
  };

  const handleClose = () => {
    setFormData({
      subject: '',
      title: '',
      message: '',
      recipient_type: 'all',
      selected_members: []
    });
    setAttachment(null);
    setBanner(null);
    setError('');
    onClose();
  };

  if (!isOpen) return null;

  const filteredMembers = members.filter(member =>
    member.name.toLowerCase().includes(memberSearch.toLowerCase()) ||
    member.email.toLowerCase().includes(memberSearch.toLowerCase()) ||
    member.phone.includes(memberSearch)
  );

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white border border-gray-200 rounded-2xl p-6 max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold text-gray-900">New Broadcast</h2>
          <button
            onClick={handleClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
            disabled={submitting}
          >
            <XMarkIcon className="w-6 h-6" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Subject */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Subject *
            </label>
            <input
              type="text"
              name="subject"
              value={formData.subject}
              onChange={handleInputChange}
              placeholder="Gym Announcement"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
              disabled={submitting}
            />
          </div>

          {/* Offer Title */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Offer Title *
            </label>
            <input
              type="text"
              name="title"
              value={formData.title}
              onChange={handleInputChange}
              placeholder="🔥 Independence Day Offer"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
              disabled={submitting}
            />
          </div>

          {/* Message */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Message *
            </label>
            <textarea
              name="message"
              value={formData.message}
              onChange={handleInputChange}
              placeholder="Get 20% OFF on all yearly memberships. Offer valid till 15 July. Visit reception today."
              rows={4}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
              disabled={submitting}
            />
          </div>

          {/* Attachment */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Attachment (Optional)
            </label>
            <div className="flex items-center gap-4">
              <label className="flex-1 flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg cursor-pointer hover:bg-gray-50">
                <PaperClipIcon className="h-5 w-5 text-gray-600" />
                <span className="text-sm text-gray-600">
                  {attachment ? attachment.name : 'Choose file (PDF, JPG, PNG)'}
                </span>
                <input
                  type="file"
                  accept=".pdf,.jpg,.jpeg,.png"
                  onChange={(e) => handleFileChange(e, 'attachment')}
                  className="hidden"
                  disabled={submitting}
                />
              </label>
              {attachment && (
                <button
                  type="button"
                  onClick={() => setAttachment(null)}
                  className="text-red-600 hover:text-red-700 text-sm"
                  disabled={submitting}
                >
                  Remove
                </button>
              )}
            </div>
            <p className="text-xs text-gray-500 mt-1">Maximum file size: 10 MB</p>
          </div>

          {/* Banner Image */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Banner Image (Optional)
            </label>
            <div className="flex items-center gap-4">
              <label className="flex-1 flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg cursor-pointer hover:bg-gray-50">
                <PhotoIcon className="h-5 w-5 text-gray-600" />
                <span className="text-sm text-gray-600">
                  {banner ? banner.name : 'Choose image (JPG, PNG)'}
                </span>
                <input
                  type="file"
                  accept=".jpg,.jpeg,.png"
                  onChange={(e) => handleFileChange(e, 'banner')}
                  className="hidden"
                  disabled={submitting}
                />
              </label>
              {banner && (
                <button
                  type="button"
                  onClick={() => setBanner(null)}
                  className="text-red-600 hover:text-red-700 text-sm"
                  disabled={submitting}
                >
                  Remove
                </button>
              )}
            </div>
            {banner && (
              <img
                src={URL.createObjectURL(banner)}
                alt="Banner preview"
                className="mt-2 w-full h-32 object-cover rounded-lg"
              />
            )}
          </div>

          {/* Recipient Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Recipient Selection *
            </label>
            <div className="space-y-2">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="radio"
                  name="recipient_type"
                  value="all"
                  checked={formData.recipient_type === 'all'}
                  onChange={handleInputChange}
                  className="text-orange-500 focus:ring-orange-500"
                  disabled={submitting}
                />
                <span>All Members</span>
              </label>
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="radio"
                  name="recipient_type"
                  value="active"
                  checked={formData.recipient_type === 'active'}
                  onChange={handleInputChange}
                  className="text-orange-500 focus:ring-orange-500"
                  disabled={submitting}
                />
                <span>Active Members</span>
              </label>
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="radio"
                  name="recipient_type"
                  value="expiring"
                  checked={formData.recipient_type === 'expiring'}
                  onChange={handleInputChange}
                  className="text-orange-500 focus:ring-orange-500"
                  disabled={submitting}
                />
                <span>Expiring Members</span>
              </label>
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="radio"
                  name="recipient_type"
                  value="selected"
                  checked={formData.recipient_type === 'selected'}
                  onChange={handleInputChange}
                  className="text-orange-500 focus:ring-orange-500"
                  disabled={submitting}
                />
                <span>Selected Members</span>
              </label>
            </div>

            {/* Selected Members List */}
            {formData.recipient_type === 'selected' && (
              <div className="mt-4">
                <input
                  type="text"
                  placeholder="Search members..."
                  value={memberSearch}
                  onChange={(e) => setMemberSearch(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 mb-2"
                  disabled={submitting}
                />
                <div className="max-h-48 overflow-y-auto border border-gray-200 rounded-lg p-2">
                  {loading ? (
                    <div className="text-center py-4 text-gray-500">Loading members...</div>
                  ) : filteredMembers.length === 0 ? (
                    <div className="text-center py-4 text-gray-500">No members found</div>
                  ) : (
                    filteredMembers.map((member) => (
                      <label
                        key={member.id}
                        className="flex items-center gap-2 p-2 hover:bg-gray-50 rounded cursor-pointer"
                      >
                        <input
                          type="checkbox"
                          checked={formData.selected_members.includes(member.id)}
                          onChange={() => handleMemberToggle(member.id)}
                          className="text-orange-500 focus:ring-orange-500"
                          disabled={submitting}
                        />
                        <div className="flex-1">
                          <div className="font-medium text-gray-900">{member.name}</div>
                          <div className="text-xs text-gray-500">{member.email}</div>
                        </div>
                        <span className={`text-xs px-2 py-1 rounded ${
                          member.status === 'Active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                        }`}>
                          {member.status}
                        </span>
                      </label>
                    ))
                  )}
                </div>
                <p className="text-sm text-gray-600 mt-2">
                  {formData.selected_members.length} member(s) selected
                </p>
              </div>
            )}
          </div>

          {/* Error Display */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-sm text-red-700">
              {error}
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex gap-3 pt-4">
            <button
              type="submit"
              disabled={submitting}
              className="flex-1 bg-orange-500 hover:bg-orange-600 disabled:bg-gray-300 disabled:cursor-not-allowed text-white px-6 py-3 rounded-xl font-medium transition-colors"
            >
              {submitting ? 'Sending...' : 'Send Broadcast'}
            </button>
            <button
              type="button"
              onClick={handleClose}
              disabled={submitting}
              className="bg-gray-100 hover:bg-gray-200 disabled:bg-gray-50 disabled:cursor-not-allowed text-gray-700 px-6 py-3 rounded-xl font-medium transition-colors"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
