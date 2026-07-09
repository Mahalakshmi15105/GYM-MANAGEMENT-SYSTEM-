import React from 'react';
import { useAuth } from '../context/AuthContext';
import GymLogo from './GymLogo';
import { Bars3Icon, ShieldCheckIcon } from '@heroicons/react/24/outline';

export default function Navbar({ onMenuClick }) {
  const { user, isSuperAdmin } = useAuth();

  return (
    <header className="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-4 sm:px-6 lg:px-8 sticky top-0 z-10 text-gray-800 w-full shadow-sm">
      <div className="flex items-center gap-3">
        {/* Toggle menu button on mobile/tablet */}
        <button
          onClick={onMenuClick}
          className="lg:hidden text-gray-600 hover:text-orange-600 p-1.5 focus:outline-none hover:bg-orange-50 rounded-lg transition-colors duration-200"
          aria-label="Open menu"
        >
          <Bars3Icon className="w-6 h-6 text-orange-600" />
        </button>
        
        <div className="flex items-center gap-3">
          {!isSuperAdmin ? <GymLogo className="w-7 h-7 lg:hidden" /> : <ShieldCheckIcon className="w-6 h-6 lg:hidden text-red-600" />}
          <div>
            <h2 className="text-sm sm:text-base font-semibold text-gray-900">
              {isSuperAdmin ? 'Platform Administration' : 'Gym Workspace'}
            </h2>
            {!isSuperAdmin && user?.gym_id && (
              <div className="text-xs bg-orange-50 text-orange-700 px-2.5 py-1 rounded-xl border border-orange-200 font-mono hidden sm:block mt-1">
                Tenant Gym ID: {user.gym_id}
              </div>
            )}
          </div>
        </div>
      </div>
      
      <div className="flex items-center gap-4">
        {/* Connection status */}
        <div className="flex items-center gap-2 text-xs bg-green-50 text-green-700 px-3 py-1 rounded-xl border border-green-200">
          <span className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse"></span>
          Connected
        </div>
      </div>
    </header>
  );
}
