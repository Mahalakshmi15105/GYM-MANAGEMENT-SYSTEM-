import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import Layout from '../components/Layout';
import LandingPage from '../pages/LandingPage';
import LoginPage from '../pages/LoginPage';
import RegisterPage from '../pages/RegisterPage';
import DashboardPlaceholder from '../pages/DashboardPlaceholder';
import MembersPage from '../pages/MembersPage';
import AddMemberPage from '../pages/AddMemberPage';
import ViewMemberPage from '../pages/ViewMemberPage';
import EditMemberPage from '../pages/EditMemberPage';

// Checks if the user is authenticated via JWT. Redirects to login if not.
function ProtectedRoute({ children }) {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? children : <Navigate to="/login" replace />;
}

// Prevents logged-in owners from accessing landing/login/register pages.
function PublicOnlyRoute({ children }) {
  const { isAuthenticated } = useAuth();
  return !isAuthenticated ? children : <Navigate to="/dashboard" replace />;
}

export default function AppRoutes() {
  return (
    <Routes>
      {/* Public Pages */}
      <Route path="/" element={<LandingPage />} />
      
      {/* Auth Pages (Public Guest Access Only) */}
      <Route
        path="/login"
        element={
          <PublicOnlyRoute>
            <LoginPage />
          </PublicOnlyRoute>
        }
      />
      <Route
        path="/register"
        element={
          <PublicOnlyRoute>
            <RegisterPage />
          </PublicOnlyRoute>
        }
      />

      {/* Protected SaaS Workspace Dashboard (JWT Token Required) */}
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        <Route path="dashboard" element={<DashboardPlaceholder />} />
        
        {/* Members Management */}
        <Route path="members" element={<MembersPage />} />
        <Route path="members/add" element={<AddMemberPage />} />
        <Route path="members/:id" element={<ViewMemberPage />} />
        <Route path="members/:id/edit" element={<EditMemberPage />} />
        
        {/* Sub-workspace placeholders with isolated scopes */}
        <Route
          path="attendance"
          element={
            <div className="bg-slate-900/40 p-6 rounded-2xl border border-slate-850">
              <h2 className="text-xl font-bold text-white mb-2">Attendance Checkins</h2>
              <p className="text-sm text-slate-400">
                Future member attendance scan feeds and monthly workout log sheets. Data queried is filtered strictly by the tenant's gym_id.
              </p>
            </div>
          }
        />
        <Route
          path="payments"
          element={
            <div className="bg-slate-900/40 p-6 rounded-2xl border border-slate-850">
              <h2 className="text-xl font-bold text-white mb-2">Billing & Payments</h2>
              <p className="text-sm text-slate-400">
                Future subscription plans configuration and member transaction histories. Data queried is filtered strictly by the tenant's gym_id.
              </p>
            </div>
          }
        />
        <Route
          path="plans"
          element={
            <div className="bg-slate-900/40 p-6 rounded-2xl border border-slate-850">
              <h2 className="text-xl font-bold text-white mb-2">Trainers & Membership Plans</h2>
              <p className="text-sm text-slate-400">
                Future training plans customization and gym package tiers. Data queried is filtered strictly by the tenant's gym_id.
              </p>
            </div>
          }
        />
        <Route
          path="settings"
          element={
            <div className="bg-slate-900/40 p-6 rounded-2xl border border-slate-850">
              <h2 className="text-xl font-bold text-white mb-2">Gym Workspace Settings</h2>
              <p className="text-sm text-slate-400">
                Configure gym metadata, logo customization, operational hours, and tenant preferences. Data queried is filtered strictly by the tenant's gym_id.
              </p>
            </div>
          }
        />
      </Route>

      {/* Catch-all redirect */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
