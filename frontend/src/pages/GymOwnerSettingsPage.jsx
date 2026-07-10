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
  const { t, languageOptions, setLanguage } = useTranslation(user?.gym_id);
  const { formatCurrency, currencyOptions, setCurrencyCode } = useCurrency(user?.gym_id);
  
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
      setGymData(response.data.gym);
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

      // Update local storage with gym-specific key and trigger re-render across the app
      setCurrencyCode(newCurrency);
      
      setGymData(response.data.gym);
      setSuccess(t('messages.currencyUpdated', { currency: newCurrency }));
      
      // Clear success message after 3 seconds
      setTimeout(() => setSuccess(''), 3000);
      
    } catch (err) {
      console.error('Failed to update currency:', err);
      setError(err.response?.data?.error || t('messages.operationFailed'));
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

      // Update local storage with gym-specific key and trigger re-render across the app
      setLanguage(newLanguage);
      
      setGymData(response.data.gym);
      setSuccess(t('messages.languageUpdated', { language: languageOptions.find(l => l.code === newLanguage)?.name || newLanguage }));
      
      // Clear success message after 3 seconds
      setTimeout(() => setSuccess(''), 3000);
      
    } catch (err) {
      console.error('Failed to update language:', err);
      setError(err.response?.data?.error || t('messages.operationFailed'));
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
          <CogIcon className="w-6 h-6 text-orange-500" /> {t('nav.settings')}
        </h1>
        <p className="text-gray-600">{t('settings.description')}</p>
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
          <CurrencyDollarIcon className="w-5 h-5 text-orange-500" /> {t('settings.currencySettings')}
        </h2>
        
        <div className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {t('settings.selectCurrency')}
            </label>
            <p className="text-sm text-gray-600 mb-4">
              {t('settings.currencyDescription')}
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
                <span className="font-medium">{t('settings.currentCurrency')}:</span> {gymData?.currency || 'INR'} ({currencyOptions.find(c => c.code === gymData?.currency)?.symbol || '₹'})
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
          <LanguageIcon className="w-5 h-5 text-orange-500" /> {t('settings.languageSettings')}
        </h2>
        
        <div className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {t('settings.selectLanguage')}
            </label>
            <p className="text-sm text-gray-600 mb-4">
              {t('settings.languageDescription')}
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
                <span className="font-medium">{t('settings.currentLanguage')}:</span> {languageOptions.find(l => l.code === gymData?.language)?.name || 'English'} 
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
          <QrCodeIcon className="w-5 h-5 text-orange-500" /> {t('settings.qrCode')}
        </h2>
        
        <div className="space-y-4">
          <p className="text-sm text-gray-600">
            {t('settings.qrCodeDescription')}
          </p>
          
          <button
            onClick={() => navigate('/gym-qr')}
            className="bg-orange-600 hover:bg-orange-700 text-white font-medium py-3 px-6 rounded-xl transition-colors"
          >
            {t('settings.manageQrCode')}
          </button>
          
          <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <p className="text-sm text-blue-900">
              <span className="font-medium">{t('settings.status')}:</span> {gymData?.attendance_qr ? t('settings.qrActive') : t('settings.noQrCode')}
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
        <h2 className="text-lg font-bold text-gray-900 mb-4">{t('settings.settingsInfo')}</h2>
        
        <div className="grid md:grid-cols-2 gap-6">
          <div>
            <h3 className="font-semibold text-gray-900 mb-2">{t('settings.currencyAffects')}:</h3>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• {t('settings.membershipPricing')}</li>
              <li>• {t('settings.paymentRecords')}</li>
              <li>• {t('settings.financialReports')}</li>
              <li>• {t('settings.revenueCalculations')}</li>
              <li>• {t('settings.billingStatements')}</li>
            </ul>
          </div>
          <div>
            <h3 className="font-semibold text-gray-900 mb-2">{t('settings.languageAffects')}:</h3>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• {t('settings.interfaceText')}</li>
              <li>• {t('settings.menuNavigation')}</li>
              <li>• {t('settings.reportsPrintouts')}</li>
              <li>• {t('settings.notifications')}</li>
              <li>• {t('settings.messages')}</li>
            </ul>
          </div>
        </div>
        
        <div className="mt-6 pt-6 border-t border-gray-200">
          <p className="text-xs text-gray-600">
            <span className="font-medium">{t('common.note')}:</span> {t('settings.immediateApplication')}
          </p>
        </div>
      </div>
    </div>
  );
}