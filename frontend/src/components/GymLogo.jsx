import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';
import { HeartIcon } from '@heroicons/react/24/outline';

export default function GymLogo({ className = "w-8 h-8", showFallback = true }) {
  const { isAuthenticated, user } = useAuth();
  const [logoUrl, setLogoUrl] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(false);

  useEffect(() => {
    if (isAuthenticated && user?.gym_id) {
      fetchGymLogo();
    }
  }, [isAuthenticated, user?.gym_id]);

  const fetchGymLogo = async () => {
    try {
      setLoading(true);
      setError(false);
      const response = await api.get('/api/gym/logo/info');
      if (response.data.logo_url) {
        setLogoUrl(response.data.logo_url);
      }
    } catch (err) {
      console.error('Failed to fetch gym logo:', err);
      setError(true);
    } finally {
      setLoading(false);
    }
  };

  const handleImageError = () => {
    setError(true);
    setLogoUrl(null);
  };

  if (loading) {
    return showFallback ? (
      <div className={`${className} bg-gray-200 rounded-lg flex items-center justify-center animate-pulse`}>
        <span className="text-gray-400 text-xs">...</span>
      </div>
    ) : null;
  }

  if (error || !logoUrl) {
    return showFallback ? (
      <div className={`${className} bg-orange-100 border border-orange-200 rounded-lg flex items-center justify-center`}>
        <HeartIcon className="text-orange-600" style={{ width: '70%', height: '70%' }} />
      </div>
    ) : null;
  }

  return (
    <img
      src={logoUrl}
      alt="Gym Logo"
      className={`${className} object-contain rounded-lg shadow-sm`}
      onError={handleImageError}
    />
  );
}