import React from 'react';
import { useAuth } from '../context/AuthContext';
import {
  HandWave,
  ShieldCheck,
  Users,
  Calendar,
  CurrencyDollar,
  CreditCard,
  BuildingOffice
} from '@heroicons/react/24/outline';

export default function DashboardPlaceholder() {
  const { user } = useAuth();

  return (
    <div className="space-y-8">
      {/* Welcome header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white p-6 rounded-2xl border border-gray-200 shadow-sm">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 mb-1 flex items-center gap-2">
            Hello, {user?.name || 'Gym Owner'} <HandWave className="w-6 h-6 text-orange-500" />
          </h1>
          <p className="text-sm text-gray-600">
            Welcome to your SmartGoNext Gym workspace dashboard. Here is your gym status.
          </p>
        </div>
        <div className="flex items-center gap-2 text-xs bg-orange-50 text-orange-700 px-3.5 py-2 rounded-xl border border-orange-200 font-bold self-start md:self-auto">
          <ShieldCheck className="w-4 h-4" /> Multi-Tenant Active (Gym ID: {user?.gym_id})
        </div>
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Card 1 */}
        <div className="bg-white border border-gray-200 p-6 rounded-2xl shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <span className="text-xs uppercase font-extrabold tracking-wider text-gray-600">Total Members</span>
            <Users className="w-6 h-6 text-orange-500" />
          </div>
          <p className="text-3xl font-black text-gray-900">0</p>
          <div className="mt-2 text-xs text-gray-500 flex items-center gap-1">
            <span className="text-orange-600 font-semibold">Ready</span> to onboard members
          </div>
        </div>

        {/* Card 2 */}
        <div className="bg-white border border-gray-200 p-6 rounded-2xl shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <span className="text-xs uppercase font-extrabold tracking-wider text-gray-600">Today's Check-ins</span>
            <Calendar className="w-6 h-6 text-orange-500" />
          </div>
          <p className="text-3xl font-black text-gray-900">0</p>
          <div className="mt-2 text-xs text-gray-500 flex items-center gap-1">
            <span className="text-orange-600 font-semibold">Ready</span> to track attendance
          </div>
        </div>

        {/* Card 3 */}
        <div className="bg-white border border-gray-200 p-6 rounded-2xl shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <span className="text-xs uppercase font-extrabold tracking-wider text-gray-600">Total Payments</span>
            <CurrencyDollar className="w-6 h-6 text-orange-500" />
          </div>
          <p className="text-3xl font-black text-gray-900">$0.00</p>
          <div className="mt-2 text-xs text-gray-500 flex items-center gap-1">
            <span className="text-orange-600 font-semibold">Ready</span> to record payments
          </div>
        </div>

        {/* Card 4 */}
        <div className="bg-white border border-gray-200 p-6 rounded-2xl shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <span className="text-xs uppercase font-extrabold tracking-wider text-gray-600">Membership Plans</span>
            <CreditCard className="w-6 h-6 text-orange-500" />
          </div>
          <p className="text-3xl font-black text-gray-900">0</p>
          <div className="mt-2 text-xs text-gray-500 flex items-center gap-1">
            <span className="text-orange-600 font-semibold">Ready</span> to create plans
          </div>
        </div>
      </div>

      {/* Profile details */}
      <div className="grid md:grid-cols-3 gap-8">
        <div className="bg-white border border-gray-200 p-6 rounded-2xl shadow-sm md:col-span-2">
          <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
            <BuildingOffice className="w-5 h-5 text-orange-500" /> Gym Profile Details
          </h2>
          <div className="space-y-4">
            <div className="grid grid-cols-3 py-2.5 border-b border-gray-200 text-sm">
              <span className="text-gray-600 font-medium">Gym Name</span>
              <span className="text-gray-900 col-span-2 font-semibold text-orange-600">{user?.gym_name || 'My Fitness Club'}</span>
            </div>
            <div className="grid grid-cols-3 py-2.5 border-b border-gray-200 text-sm">
              <span className="text-gray-600 font-medium">Gym Address</span>
              <span className="text-gray-900 col-span-2">{user?.gym_address || 'Not Provided'}</span>
            </div>
            <div className="grid grid-cols-3 py-2.5 border-b border-gray-200 text-sm">
              <span className="text-gray-600 font-medium">Gym Phone</span>
              <span className="text-gray-900 col-span-2 font-mono">{user?.gym_phone || 'Not Provided'}</span>
            </div>
            <div className="grid grid-cols-3 py-2.5 border-b border-gray-200 text-sm">
              <span className="text-gray-600 font-medium">Owner Name</span>
              <span className="text-gray-900 col-span-2">{user?.name}</span>
            </div>
            <div className="grid grid-cols-3 py-2.5 text-sm">
              <span className="text-gray-600 font-medium">Logged-in Email</span>
              <span className="text-gray-900 col-span-2 font-mono">{user?.email}</span>
            </div>
          </div>
        </div>

        <div className="bg-white border border-gray-200 p-6 rounded-2xl shadow-sm">
          <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
            <ShieldCheck className="w-5 h-5 text-orange-500" /> SaaS Data Isolation
          </h2>
          <p className="text-sm text-gray-600 leading-relaxed mb-4">
            All member lists, checkins, transactions, and configs inside this workspace are locked to:
          </p>
          <div className="bg-gray-50 p-4 rounded-xl border border-gray-200 text-xs font-mono text-orange-600">
            WHERE gym_id = {user?.gym_id || 'NULL'}
          </div>
        </div>
      </div>
    </div>
  );
}
