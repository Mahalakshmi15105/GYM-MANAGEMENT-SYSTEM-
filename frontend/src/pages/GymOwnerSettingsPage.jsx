import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import { useTranslation } from '../utils/i18n';
import { useCurrency } from '../utils/currency';
import {
  CogIcon,
  CurrencyDollarIcon,
  LanguageIcon,
  CheckCircleIcon,
  ExclamationCircleIcon,
  QrCodeIcon,
} from '@heroicons/react/24/outline';

export default function GymOwnerSettingsPage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const { t, languageOptions, setLanguage } = useTranslation();
  const { formatCurrency, currencyOptions, setCurrencyCode } = useCurrency();
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [gymData, setGymData] = useState(null);
  const [updating, setUpdating] = useState(false);

  useEffect(() => {
    fetchGymSettings();
  }, []);

  const fetchGymSettings = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/gym/profile');
      setGymData(response.data);
    } catch (err) {
      console.error('Failed to fetch gym settings:', err);
      setError(err.response?.data?.error || t('messages.operationFailed'));
    } finally {
      setLoading(false);
    }
  };

  const handleCurrencyUpdate = async (newCurrency) => {
    if (updating) return;
    
    try {
      setUpdating(true);
      setError('');
      setSuccess('');

      // Update the currency in the backend
      const response = await api.put('/api/gym/profile', {
        currency: newCurrency
      });

      // Update local storage and trigger re-render across the app
      setCurrencyCode(newCurrency);
      
      setGymData(response.data.gym);
      setSuccess(`Currency updated to ${newCurrency} successfully!`);
      
      // Clear success message after 3 seconds
      setTimeout(() => setSuccess(''), 3000);
      
    } catch (err) {
      console.error('Failed to update currency:', err);
      setError(err.response?.data?.error || 'Failed to update currency');
    } finally {
      setUpdating(false);
    }
  };

  const handleLanguageUpdate = async (newLanguage) => {
    if (updating) return;
    
    try {
      setUpdating(true);
      setError('');
      setSuccess('');

      // Update the language in the backend
      const response = await api.put('/api/gym/profile', {
        language: newLanguage
      });

      // Update local storage and trigger re-render across the app
      setLanguage(newLanguage);
      
      setGymData(response.data.gym);
      setSuccess(`Language updated to ${languageOptions.find(l => l.code === newLanguage)?.name || newLanguage} successfully!`);
      
      // Clear success message after 3 seconds
      setTimeout(() => setSuccess(''), 3000);
      
    } catch (err) {
      console.error('Failed to update language:', err);
      setError(err.response?.data?.error || 'Failed to update language');
    } finally {
      setUpdating(false);
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
          <CogIcon className="w-6 h-6 text-orange-500" /> Settings
        </h1>
        <p className="text-gray-600">Manage your gym's currency, language, and preferences</p>
      </div>

      {/* Success/Error Messages */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 text-sm p-4 rounded-xl flex items-center gap-2">
          <ExclamationCircleIcon className="w-5 h-5 text-red-500" />
          {error}
        </div>
      )}
      {success && (
        <div className="bg-green-50 border border-green-200 text-green-700 text-sm p-4 rounded-xl flex items-center gap-2">
          <CheckCircleIcon className="w-5 h-5 text-green-500" />
          {success}
        </div>
      )}

      {/* Currency Settings Section */}
      <div className="bg-white border border-gray-200 p-6 rounded-2xl shadow-sm">
        <h2 className="text-lg font-bold text-gray-900 mb-6 flex items-center gap-2">
          <CurrencyDollarIcon className="w-5 h-5 text-orange-500" /> Currency Settings
        </h2>
        
        <div className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Select your preferred currency
            </label>
            <p className="text-sm text-gray-600 mb-4">
              This currency will be used across your gym management system including membership plans, payments, reports, and receipts.
            </p>
            
            <select
              value={gymData?.currency || 'INR'}
              onChange={(e) => handleCurrencyUpdate(e.target.value)}
              disabled={updating}
              className="w-full max-w-md bg-gray-50 border border-gray-200 focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 rounded-lg px-4 py-3 text-sm text-gray-900 focus:outline-none transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {currencyOptions.map((currency) => (
                <option key={currency.code} value={currency.code}>
                  {currency.code} - {currency.label} ({currency.symbol})
                </option>
              ))}
            </select>
            
            <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <p className="text-sm text-blue-900">
                <span className="font-medium">Current Currency:</span> {gymData?.currency || 'INR'} ({currencyOptions.find(c => c.code === gymData?.currency)?.symbol || '₹'})
              </p>
              <p className="text-sm text-blue-700 mt-1">
                Example: {formatCurrency(1000)}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Language Settings Section */}
      <div className="bg-white border border-gray-200 p-6 rounded-2xl shadow-sm">
        <h2 className="text-lg font-bold text-gray-900 mb-6 flex items-center gap-2">
          <LanguageIcon className="w-5 h-5 text-orange-500" /> Language Settings
        </h2>
        
        <div className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Select your preferred language
            </label>
            <p className="text-sm text-gray-600 mb-4">
              This language will be used for the interface, reports, and all gym management features.
            </p>
            
            <select
              value={gymData?.language || 'en'}
              onChange={(e) => handleLanguageUpdate(e.target.value)}
              disabled={updating}
              className="w-full max-w-md bg-gray-50 border border-gray-200 focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 rounded-lg px-4 py-3 text-sm text-gray-900 focus:outline-none transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {languageOptions.map((language) => (
                <option key={language.code} value={language.code}>
                  {language.name} ({language.nativeName})
                </option>
              ))}
            </select>
            
            <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <p className="text-sm text-blue-900">
                <span className="font-medium">Current Language:</span> {languageOptions.find(l => l.code === gymData?.language)?.name || 'English'} 
                ({languageOptions.find(l => l.code === gymData?.language)?.nativeName || 'English'})
              </p>
              <p className="text-sm text-blue-700 mt-1">
                Language Code: {gymData?.language || 'en'}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Attendance QR Code Section */}
      <div className="bg-white border border-gray-200 p-6 rounded-2xl shadow-sm">
        <h2 className="text-lg font-bold text-gray-900 mb-6 flex items-center gap-2">
          <QrCodeIcon className="w-5 h-5 text-orange-500" /> Attendance QR Code
        </h2>
        
        <div className="space-y-4">
          <p className="text-sm text-gray-600">
            Manage your gym's attendance QR code. Members scan this code to check in at your gym.
          </p>
          
          <button
            onClick={() => navigate('/gym-qr')}
            className="bg-orange-600 hover:bg-orange-700 text-white font-medium py-3 px-6 rounded-xl transition-colors"
          >
            Manage QR Code
          </button>
          
          <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <p className="text-sm text-blue-900">
              <span className="font-medium">Status:</span> {gymData?.attendance_qr ? 'QR Code Active' : 'No QR Code Generated'}
            </p>
            {gymData?.attendance_qr && (
              <p className="text-sm text-blue-700 mt-1">
                QR Code: <span className="font-mono">{gymData.attendance_qr}</span>
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Settings Information */}
      <div className="bg-white border border-gray-200 p-6 rounded-2xl shadow-sm">
        <h2 className="text-lg font-bold text-gray-900 mb-4">Settings Information</h2>
        
        <div className="grid md:grid-cols-2 gap-6">
          <div>
            <h3 className="font-semibold text-gray-900 mb-2">Currency affects:</h3>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• Membership plan pricing</li>
              <li>• Payment records and receipts</li>
              <li>• Financial reports and analytics</li>
              <li>• Revenue calculations</li>
              <li>• Billing statements</li>
            </ul>
          </div>
          <div>
            <h3 className="font-semibold text-gray-900 mb-2">Language affects:</h3>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• Interface text and labels</li>
              <li>• Menu items and navigation</li>
              <li>• Reports and printouts</li>
              <li>• System notifications</li>
              <li>• Error and success messages</li>
            </ul>
          </div>
        </div>
        
        <div className="mt-6 pt-6 border-t border-gray-200">
          <p className="text-xs text-gray-600">
            <span className="font-medium">Note:</span> Changes to currency and language settings are applied immediately across your entire gym management system.
          </p>
        </div>
      </div>
    </div>
  );
}