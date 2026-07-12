import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';
import {
  QrCodeIcon,
  ArrowLeftIcon,
  DocumentArrowDownIcon,
  PrinterIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';

export default function GymQRPage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  
  const [qrData, setQrData] = useState(null);
  const [qrImageUrl, setQrImageUrl] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  useEffect(() => {
    fetchQRData();
  }, []);

  const fetchQRData = async () => {
    try {
      const response = await api.get('/api/gym/qr/info');
      setQrData(response.data);
      
      // Fetch QR image as blob and convert to base64 URL
      if (response.data.has_qr) {
        const imageResponse = await api.get('/api/gym/qr/image', {
          responseType: 'blob'
        });
        const imageUrl = URL.createObjectURL(imageResponse.data);
        setQrImageUrl(imageUrl);
      }
    } catch (err) {
      console.error('Failed to fetch QR data:', err);
      setError(err.response?.data?.error || 'Failed to load QR data');
    } finally {
      setLoading(false);
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
      setError('Failed to download QR code');
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
      setError('Failed to generate printable QR');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading QR code...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <button
              onClick={() => navigate('/settings')}
              className="flex items-center gap-2 text-gray-600 hover:text-gray-900"
            >
              <ArrowLeftIcon className="w-5 h-5" />
              Back to Settings
            </button>
            <h1 className="text-xl font-bold text-gray-900">Attendance QR Code</h1>
            <div className="w-20"></div>
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-xl mb-6 flex items-start gap-3">
            <ExclamationTriangleIcon className="w-5 h-5 flex-shrink-0 mt-0.5" />
            <p className="text-sm">{error}</p>
          </div>
        )}

        {successMessage && (
          <div className="bg-green-50 border border-green-200 text-green-700 p-4 rounded-xl mb-6 flex items-start gap-3">
            <CheckCircleIcon className="w-5 h-5 flex-shrink-0 mt-0.5" />
            <p className="text-sm">{successMessage}</p>
          </div>
        )}

        <div className="space-y-6">
          {/* QR Code Display */}
          <div className="bg-white border border-gray-200 rounded-2xl p-8 shadow-sm">
            <div className="text-center">
              <div className="mx-auto w-16 h-16 bg-orange-100 rounded-full flex items-center justify-center mb-6">
                <QrCodeIcon className="w-10 h-10 text-orange-600" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Your Gym's Attendance QR Code</h2>
              <p className="text-gray-600 mb-6">
                Display this QR code at your gym entrance for members to scan and check in
              </p>

              {qrData?.has_qr ? (
                <>
                  <div className="bg-gray-50 border-2 border-dashed border-gray-300 rounded-xl p-8 mb-6 flex flex-col items-center">
                    <p className="text-xs text-gray-600 uppercase tracking-wider mb-4">QR Code</p>
                    {qrImageUrl && (
                      <img 
                        src={qrImageUrl} 
                        alt="Gym Attendance QR Code" 
                        className="w-64 h-64 object-contain mb-4"
                        onError={() => setError('Failed to load QR image')}
                      />
                    )}
                    <p className="text-xs text-gray-500 mt-2">
                      Scan this QR code to check in at {qrData.gym?.name || 'your gym'}
                    </p>
                  </div>

                  <div className="flex flex-col sm:flex-row gap-3 justify-center">
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
                </>
              ) : (
                <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-6">
                  <p className="text-yellow-800 text-sm">
                    No QR code generated yet. Please contact support to generate your gym's attendance QR code.
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Instructions */}
          <div className="bg-blue-50 border border-blue-200 rounded-xl p-6">
            <h3 className="font-semibold text-blue-900 mb-3">How to Use the Attendance QR Code</h3>
            <ol className="text-sm text-blue-800 space-y-2 list-decimal list-inside">
              <li>Print the QR code and display it prominently at your gym entrance</li>
              <li>Members will scan this QR code using their member app to check in</li>
              <li>Each member can only check in once per day</li>
              <li>The system automatically records the check-in time and date</li>
            </ol>
          </div>

          {/* Security Info */}
          <div className="bg-gray-50 border border-gray-200 rounded-xl p-6">
            <h3 className="font-semibold text-gray-900 mb-3">Security Information</h3>
            <ul className="text-sm text-gray-700 space-y-2">
              <li>• Each gym has a unique QR code</li>
              <li>• Members can only check in at their own gym</li>
              <li>• The QR code is validated against the gym's database</li>
              <li>• Keep your QR code secure and display it in a visible location</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
