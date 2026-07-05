import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import Layout from '../components/Layout';
import LandingPage from '../pages/LandingPage';
import LoginPage from '../pages/LoginPage';
import RegisterPage from '../pages/RegisterPage';
import DashboardPage from '../pages/DashboardPage';
import MembersPage from '../pages/MembersPage';
import AddMemberPage from '../pages/AddMemberPage';
import ViewMemberPage from '../pages/ViewMemberPage';
import EditMemberPage from '../pages/EditMemberPage';
import MembershipPlansPage from '../pages/MembershipPlansPage';
import AddMembershipPlanPage from '../pages/AddMembershipPlanPage';
import ViewMembershipPlanPage from '../pages/ViewMembershipPlanPage';
import EditMembershipPlanPage from '../pages/EditMembershipPlanPage';
import PaymentsPage from '../pages/PaymentsPage';
import AddPaymentPage from '../pages/AddPaymentPage';
import ViewPaymentPage from '../pages/ViewPaymentPage';
import EditPaymentPage from '../pages/EditPaymentPage';
import AttendancePage from '../pages/AttendancePage';
import CheckInPage from '../pages/CheckInPage';
import ViewAttendancePage from '../pages/ViewAttendancePage';
import EditAttendancePage from '../pages/EditAttendancePage';
import AttendanceReportsPage from '../pages/AttendanceReportsPage';

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
        <Route path="dashboard" element={<DashboardPage />} />
        
        {/* Members Management */}
        <Route path="members" element={<MembersPage />} />
        <Route path="members/add" element={<AddMemberPage />} />
        <Route path="members/:id" element={<ViewMemberPage />} />
        <Route path="members/:id/edit" element={<EditMemberPage />} />
        
        {/* Membership Plans Management */}
        <Route path="membership-plans" element={<MembershipPlansPage />} />
        <Route path="membership-plans/add" element={<AddMembershipPlanPage />} />
        <Route path="membership-plans/:id" element={<ViewMembershipPlanPage />} />
        <Route path="membership-plans/:id/edit" element={<EditMembershipPlanPage />} />
        
        {/* Payments Management */}
        <Route path="payments" element={<PaymentsPage />} />
        <Route path="payments/add" element={<AddPaymentPage />} />
        <Route path="payments/:id" element={<ViewPaymentPage />} />
        <Route path="payments/:id/edit" element={<EditPaymentPage />} />
        
        {/* Attendance Management */}
        <Route path="attendance" element={<AttendancePage />} />
        <Route path="attendance/checkin" element={<CheckInPage />} />
        <Route path="attendance/reports" element={<AttendanceReportsPage />} />
        <Route path="attendance/:id" element={<ViewAttendancePage />} />
        <Route path="attendance/:id/edit" element={<EditAttendancePage />} />
        
        {/* Sub-workspace placeholders with isolated scopes */}
        <Route
          path="plans"
          element={
            <div className="bg-white border border-gray-200 p-6 rounded-2xl shadow-sm">
              <h2 className="text-xl font-bold text-gray-900 mb-2">Trainers & Training Plans</h2>
              <p className="text-sm text-gray-600">
                Future training plans customization and personal trainer management. Data queried is filtered strictly by the tenant's gym_id.
              </p>
              <p className="text-xs text-gray-500 mt-4">
                Note: Membership Plans, Payments, and Attendance are now available as separate modules in the sidebar.
              </p>
            </div>
          }
        />
        <Route
          path="settings"
          element={
            <div className="bg-white border border-gray-200 p-6 rounded-2xl shadow-sm">
              <h2 className="text-xl font-bold text-gray-900 mb-2">Gym Workspace Settings</h2>
              <p className="text-sm text-gray-600">
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
