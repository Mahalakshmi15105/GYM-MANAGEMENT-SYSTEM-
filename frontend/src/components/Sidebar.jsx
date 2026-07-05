import React from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Sidebar({ isOpen, setIsOpen }) {
  const { user, logout } = useAuth();

  const links = [
    { name: 'Dashboard', path: '/dashboard', icon: '📊' },
    { name: 'Members', path: '/members', icon: '👥' },
    { name: 'Membership Plans', path: '/membership-plans', icon: '💳' },
    { name: 'Payments', path: '/payments', icon: '💰' },
    { name: 'Attendance', path: '/attendance', icon: '📅' },
    { name: 'Trainers & Plans', path: '/plans', icon: '💪' },
    { name: 'Settings', path: '/settings', icon: '⚙️' },
  ];

  return (
    <>
      {/* Mobile background overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-slate-950/60 backdrop-blur-sm z-40 lg:hidden transition-opacity duration-300"
          onClick={() => setIsOpen(false)}
        />
      )}

      <aside
        className={`w-64 bg-white border-r border-gray-200 flex flex-col h-screen fixed left-0 top-0 text-gray-800 z-50 transition-transform duration-300 shadow-lg ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        } lg:translate-x-0`}
      >
        {/* Brand logo & mobile close */}
        <div className="p-6 border-b border-gray-200 flex items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <span className="text-2xl">🏋️‍♂️</span>
            <span className="text-xl font-bold text-orange-500">
              FlexiGym
            </span>
          </div>
          <button
            onClick={() => setIsOpen(false)}
            className="lg:hidden text-gray-400 hover:text-gray-600 p-1 focus:outline-none text-lg"
          >
            ✕
          </button>
        </div>

        {/* Navigation menu */}
        <nav className="flex-1 p-4 space-y-1.5 overflow-y-auto">
          {links.map((link) => (
            <NavLink
              key={link.name}
              to={link.path}
              onClick={() => setIsOpen(false)} // Close sidebar on nav click on mobile
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200 ${
                  isActive
                    ? 'bg-orange-500 text-white shadow-md'
                    : 'hover:bg-orange-50 hover:text-orange-600'
                }`
              }
            >
              <span className="text-lg">{link.icon}</span>
              <span>{link.name}</span>
            </NavLink>
          ))}
        </nav>

        {/* Logged in User Profile area */}
        <div className="p-4 border-t border-gray-200 bg-gray-50">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 rounded-xl bg-orange-100 border border-orange-200 flex items-center justify-center font-bold text-orange-600 uppercase">
              {user?.name?.charAt(0) || 'U'}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-semibold text-gray-900 truncate">{user?.name}</p>
              <p className="text-xs text-gray-600 truncate capitalize">{user?.role?.replace('_', ' ')}</p>
            </div>
          </div>
          <button
            onClick={logout}
            className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl text-xs font-bold bg-gray-200 hover:bg-red-50 hover:text-red-600 border border-gray-200 hover:border-red-200 transition-all duration-200"
          >
            <span>🚪</span> Log Out
          </button>
        </div>
      </aside>
    </>
  );
}
