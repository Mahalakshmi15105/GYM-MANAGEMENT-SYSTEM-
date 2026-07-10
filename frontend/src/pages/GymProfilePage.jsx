import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';
import { useTranslation } from '../utils/i18n';
import {
  BuildingOfficeIcon,
  SwatchIcon,
  BoltIcon,
  ClipboardIcon,
  ArrowUpTrayIcon,
  InformationCircleIcon,
  LightBulbIcon,
} from '@heroicons/react/24/outline';

export default function GymProfilePage() {
  const { user } = useAuth();
  const { t } = useTranslation(user?.gym_id);
  const [gymInfo, setGymInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [uploading, setUploading] = useState(false);
  const [logoPreview, setLogoPreview] = useState(null);

  useEffect(() => {
    fetchGymInfo();
  }, []);

  const fetchGymInfo = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/gym/profile');
      setGymInfo(response.data);
      if (response.data.logo_url) {
        const baseURL = process.env.REACT_APP_API_URL || 'http://localhost:5000';
        setLogoPreview(`${baseURL}${response.data.logo_url}`);
      }
    } catch (err) {
      console.error('Failed to fetch gym info:', err);
      setError(err.response?.data?.error || t('messages.operationFailed'));
    } finally {
      setLoading(false);
    }
  };

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (!file) return;

    // Validate file type
    const allowedTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/svg+xml', 'image/webp'];
    if (!allowedTypes.includes(file.type)) {
      setError('Invalid file type. Please select PNG, JPG, JPEG, GIF, SVG, or WEBP files only.');
      return;
    }

    // Validate file size (5MB)
    if (file.size > 5 * 1024 * 1024) {
      setError('File size too large. Please select a file smaller than 5MB.');
      return;
    }

    // Show preview
    const reader = new FileReader();
    reader.onload = (e) => {
      setLogoPreview(e.target.result);
    };
    reader.readAsDataURL(file);

    // Upload file
    uploadLogo(file);
  };

  const uploadLogo = async (file) => {
    try {
      setUploading(true);
      setError('');
      setSuccess('');

      const formData = new FormData();
      formData.append('logo', file);

      const response = await api.post('/api/gym/logo/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setSuccess('Logo uploaded successfully!');
      
      // Build full URL for logo preview
      const baseURL = process.env.REACT_APP_API_URL || 'http://localhost:5000';
      setLogoPreview(`${baseURL}${response.data.logo_url}`);
      
      // Refresh gym info to get latest data
      await fetchGymInfo();
      
      // Clear success message after 3 seconds
      setTimeout(() => setSuccess(''), 3000);
      
    } catch (err) {
      console.error('Failed to upload logo:', err);
      setError(err.response?.data?.error || 'Failed to upload logo');
      // Reset preview on error
      if (gymInfo?.logo_url) {
        const baseURL = process.env.REACT_APP_API_URL || 'http://localhost:5000';
        setLogoPreview(`${baseURL}${gymInfo.logo_url}`);
      } else {
        setLogoPreview(null);
      }
    } finally {
      setUploading(false);
    }
  };

  const removeLogo = async () => {
    if (!window.confirm('Are you sure you want to remove the gym logo?')) return;

    try {
      setUploading(true);
      setError('');
      setSuccess('');

      await api.delete('/api/gym/logo/remove');

      setSuccess('Logo removed successfully!');
      setGymInfo(prev => ({ ...prev, logo_url: null, has_logo: false }));
      setLogoPreview(null);
      
      // Clear success message after 3 seconds
      setTimeout(() => setSuccess(''), 3000);
      
    } catch (err) {
      console.error('Failed to remove logo:', err);
      setError(err.response?.data?.error || 'Failed to remove logo');
    } finally {
      setUploading(false);
    }
  };

  if (loading) {
    return (
      <div className="space-y-8">
        <div className="flex items-center justify-center py-12">
          <div className="text-gray-600">{t('common.loading')}</div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm">
        <h1 className="text-2xl font-bold text-gray-900 mb-2 flex items-center gap-2">
          <BuildingOfficeIcon className="w-6 h-6 text-orange-500" /> {t('gymProfile.title')}
        </h1>
        <p className="text-gray-600">{t('gymProfile.subtitle')}</p>
      </div>

      {/* Success/Error Messages */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 text-sm p-4 rounded-xl">
          {error}
        </div>
      )}
      {success && (
        <div className="bg-green-50 border border-green-200 text-green-700 text-sm p-4 rounded-xl">
          {success}
        </div>
      )}

      {/* Logo Management Section */}
      <div className="bg-white border border-gray-200 p-6 rounded-2xl shadow-sm">
        <h2 className="text-lg font-bold text-gray-900 mb-6 flex items-center gap-2">
          <SwatchIcon className="w-5 h-5 text-orange-500" /> Gym Logo
        </h2>

        <div className="grid md:grid-cols-2 gap-8">
          {/* Logo Preview */}
          <div className="space-y-4">
            <h3 className="text-sm font-semibold text-gray-900 uppercase tracking-wider">Current Logo</h3>
            <div className="bg-gray-50 border-2 border-dashed border-gray-200 rounded-xl p-8 text-center">
              {logoPreview ? (
                <div className="space-y-4">
                  <img
                    src={logoPreview}
                    alt="Gym Logo"
                    className="max-w-full max-h-32 mx-auto object-contain rounded-lg shadow-sm"
                  />
                  <p className="text-xs text-gray-600">Current gym logo</p>
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="w-16 h-16 bg-orange-100 border border-orange-200 rounded-xl flex items-center justify-center mx-auto">
                    <BoltIcon className="w-8 h-8 text-orange-500" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-900">No logo uploaded</p>
                    <p className="text-xs text-gray-600">Upload a logo to personalize your gym</p>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Upload Controls */}
          <div className="space-y-6">
            <div>
              <h3 className="text-sm font-semibold text-gray-900 uppercase tracking-wider mb-4">Upload New Logo</h3>
              
              <div className="space-y-4">
                <div className="bg-blue-50 border border-blue-200 p-4 rounded-xl">
                  <h4 className="text-sm font-medium text-blue-900 mb-2 flex items-center gap-2">
                    <ClipboardIcon className="w-4 h-4" /> Requirements
                  </h4>
                  <ul className="text-xs text-blue-700 space-y-1">
                    <li>• File types: PNG, JPG, JPEG, GIF, SVG, WEBP</li>
                    <li>• Maximum size: 5MB</li>
                    <li>• Recommended: Square aspect ratio (1:1)</li>
                    <li>• Minimum resolution: 200x200 pixels</li>
                  </ul>
                </div>

                <div className="space-y-3">
                  <label
                    htmlFor="logo-upload"
                    className={`flex flex-col items-center justify-center w-full h-32 border-2 border-dashed rounded-xl cursor-pointer transition-colors ${
                      uploading
                        ? 'border-gray-300 bg-gray-50 cursor-not-allowed'
                        : 'border-orange-300 bg-orange-50 hover:bg-orange-100 hover:border-orange-400'
                    }`}
                  >
                    <div className="flex flex-col items-center justify-center space-y-2">
                      {uploading ? (
                        <>
                          <div className="w-6 h-6 border-2 border-orange-500 border-t-transparent rounded-full animate-spin"></div>
                          <p className="text-sm text-gray-600">Uploading...</p>
                        </>
                      ) : (
                        <>
                          <ArrowUpTrayIcon className="w-8 h-8 text-orange-500" />
                          <p className="text-sm font-medium text-gray-900">Click to upload logo</p>
                          <p className="text-xs text-gray-600">or drag and drop</p>
                        </>
                      )}
                    </div>
                    <input
                      id="logo-upload"
                      type="file"
                      className="hidden"
                      accept="image/png,image/jpeg,image/jpg,image/gif,image/svg+xml,image/webp"
                      onChange={handleFileSelect}
                      disabled={uploading}
                    />
                  </label>

                  {/* Remove Logo Button */}
                  {gymInfo?.has_logo && (
                    <button
                      onClick={removeLogo}
                      disabled={uploading}
                      className={`w-full py-3 px-4 rounded-xl text-sm font-medium transition-colors ${
                        uploading
                          ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                          : 'bg-red-50 text-red-600 hover:bg-red-100 border border-red-200 hover:border-red-300'
                      }`}
                    >
                      {uploading ? 'Processing...' : 'Remove Current Logo'}
                    </button>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>



      {/* Gym Information */}
      <div className="bg-white border border-gray-200 p-6 rounded-2xl shadow-sm">
        <h2 className="text-lg font-bold text-gray-900 mb-6 flex items-center gap-2">
          <InformationCircleIcon className="w-5 h-5 text-orange-500" /> Gym Information
        </h2>
        
        <div className="grid md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Gym Name</label>
            <div className="bg-gray-50 border border-gray-200 rounded-lg px-4 py-3 text-gray-900">
              {gymInfo?.gym?.name || 'Unknown Gym'}
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Gym ID</label>
            <div className="bg-gray-50 border border-gray-200 rounded-lg px-4 py-3 text-gray-600 font-mono text-sm">
              {gymInfo?.gym?.id || user?.gym_id || 'N/A'}
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Address</label>
            <div className="bg-gray-50 border border-gray-200 rounded-lg px-4 py-3 text-gray-900">
              {gymInfo?.gym?.address || 'No address specified'}
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Phone</label>
            <div className="bg-gray-50 border border-gray-200 rounded-lg px-4 py-3 text-gray-900">
              {gymInfo?.gym?.phone || 'No phone specified'}
            </div>
          </div>
        </div>

        <div className="mt-6 pt-6 border-t border-gray-200">
          <p className="text-xs text-gray-600">
            <span className="font-medium">Note:</span> To update gym name, address, or phone number, please contact support.
          </p>
        </div>
      </div>

      {/* Logo Usage Information */}
      <div className="bg-white border border-gray-200 p-6 rounded-2xl shadow-sm">
        <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
          <LightBulbIcon className="w-5 h-5 text-orange-500" /> Logo Usage
        </h2>
        
        <div className="grid md:grid-cols-2 gap-6">
          <div>
            <h3 className="font-semibold text-gray-900 mb-2">Where your logo appears:</h3>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• Sidebar navigation (next to gym name)</li>
              <li>• Dashboard header</li>
              <li>• Reports and printouts</li>
              <li>• Member-facing materials</li>
            </ul>
          </div>
          <div>
            <h3 className="font-semibold text-gray-900 mb-2">Best practices:</h3>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• Use high-quality images for crisp display</li>
              <li>• Square logos work best for sidebar display</li>
              <li>• Keep designs simple for small sizes</li>
              <li>• Test visibility on both light and dark backgrounds</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}