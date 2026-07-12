import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';
import { HeartIcon } from '@heroicons/react/24/outline';

export default function GymLogo({ 
  className = "w-8 h-8", 
  showFallback = true,
  showGymName = false,
  gymNameClassName = "text-sm font-medium text-gray-900",
  showPoweredBy = false
}) {
  const { isAuthenticated, user } = useAuth();
  const [logoUrl, setLogoUrl] = useState(null);
  const [gymName, setGymName] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(false);

  useEffect(() => {
    if (isAuthenticated && user?.gym_id) {
      fetchGymInfo();
    }
  }, [isAuthenticated, user?.gym_id]);

  const fetchGymInfo = async () => {
    try {
      setLoading(true);
      setError(false);
      const response = await api.get('/api/gym/profile');
      if (response.data.logo_url) {
        const baseURL = process.env.REACT_APP_API_URL || 'http://localhost:5000';
        setLogoUrl(`${baseURL}${response.data.logo_url}`);
      }
      if (response.data.gym?.name) {
        setGymName(response.data.gym.name);
      }
    } catch (err) {
      console.error('Failed to fetch gym info:', err);
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
      <div className="flex flex-col items-center">
        <div className={`${className} bg-gray-200 rounded-lg flex items-center justify-center animate-pulse`}>
          <span className="text-gray-400 text-xs">...</span>
        </div>
        {showGymName && <div className="h-4 w-24 bg-gray-200 rounded mt-2 animate-pulse"></div>}
        {showPoweredBy && <div className="h-3 w-20 bg-gray-200 rounded mt-1 animate-pulse"></div>}
      </div>
    ) : null;
  }

  if (error || !logoUrl) {
    return showFallback ? (
      <div className="flex flex-col items-center">
        <div className={`${className} bg-orange-100 border border-orange-200 rounded-lg flex items-center justify-center`}>
          <HeartIcon className="text-orange-600" style={{ width: '70%', height: '70%' }} />
        </div>
        {showGymName && <span className={gymNameClassName}>SmartGoNext Gym</span>}
        {showPoweredBy && <span className="text-xs text-gray-500 mt-1">Powered by SmartGoNext</span>}
      </div>
    ) : null;
  }

  return (
    <div className="flex flex-col items-center">
      <img
        src={logoUrl}
        alt="Gym Logo"
        className={`${className} object-contain rounded-lg shadow-sm`}
        onError={handleImageError}
      />
      {showGymName && gymName && (
        <span className={gymNameClassName}>{gymName}</span>
      )}
      {showPoweredBy && <span className="text-xs text-gray-500 mt-1">Powered by SmartGoNext</span>}
    </div>
  );
}