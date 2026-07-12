import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import Layout from "../components/Layout";
import ProtectedRoute, {
  SuperAdminRoute,
  GymOwnerRoute,
  MemberRoute,
} from "../components/ProtectedRoute";
import LandingPage from "../pages/LandingPage";
import LoginPage from "../pages/LoginPage";
import RegisterPage from "../pages/RegisterPage";
import DashboardPage from "../pages/DashboardPage";
import MembersPage from "../pages/MembersPage";
import AddMemberPage from "../pages/AddMemberPage";
import ViewMemberPage from "../pages/ViewMemberPage";
import EditMemberPage from "../pages/EditMemberPage";
import MembershipPlansPage from "../pages/MembershipPlansPage";
import AddMembershipPlanPage from "../pages/AddMembershipPlanPage";
import ViewMembershipPlanPage from "../pages/ViewMembershipPlanPage";
import EditMembershipPlanPage from "../pages/EditMembershipPlanPage";
import PaymentsPage from "../pages/PaymentsPage";
import AddPaymentPage from "../pages/AddPaymentPage";
import ViewPaymentPage from "../pages/ViewPaymentPage";
import EditPaymentPage from "../pages/EditPaymentPage";
import AttendancePage from "../pages/AttendancePage";
import CheckInPage from "../pages/CheckInPage";
import ViewAttendancePage from "../pages/ViewAttendancePage";
import EditAttendancePage from "../pages/EditAttendancePage";
import AttendanceReportsPage from "../pages/AttendanceReportsPage";
import ActivityLogs from "../pages/ActivityLogs";
import SuperAdminDashboard from "../pages/SuperAdminDashboard";
import GymManagement from "../pages/GymManagement";
import SubscriptionManagement from "../pages/SubscriptionManagement";
import UserManagement from "../pages/UserManagement";
import SystemSettings from "../pages/SystemSettings";
import GymProfilePage from "../pages/GymProfilePage";
import GymOwnerSettingsPage from "../pages/GymOwnerSettingsPage";
import ReportsPage from "../pages/ReportsPage";
import MemberDashboard from "../pages/MemberDashboard";
import MemberChangePassword from "../pages/MemberChangePassword";
import GymQRPage from "../pages/GymQRPage";
import BroadcastMessagesPage from "../pages/BroadcastMessagesPage";
import MemberMessagesPage from "../pages/MemberMessagesPage";

// Prevents logged-in users from accessing landing/login/register pages.
function PublicOnlyRoute({ children }) {
  const { isAuthenticated, user } = useAuth();
  
  if (!isAuthenticated) {
    return children;
  }
  
  // Redirect based on user role
  if (user?.role === 'super_admin') {
    return <Navigate to="/admin/dashboard" replace />;
  } else if (user?.role === 'gym_owner') {
    return <Navigate to="/dashboard" replace />;
  } else if (user?.role === 'member') {
    return <Navigate to="/member/dashboard" replace />;
  }
  
  return <Navigate to="/dashboard" replace />;
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

        {/* Super Admin Routes - Requires super_admin role */}
        <Route
          path="admin/*"
          element={
            <SuperAdminRoute>
              <Routes>
                <Route index element={<Navigate to="dashboard" replace />} />
                <Route path="dashboard" element={<SuperAdminDashboard />} />
                <Route path="gyms" element={<GymManagement />} />
                <Route
                  path="subscriptions"
                  element={<SubscriptionManagement />}
                />
                <Route path="users" element={<UserManagement />} />
                <Route path="settings" element={<SystemSettings />} />
                <Route path="logs" element={<ActivityLogs />} />
              </Routes>
            </SuperAdminRoute>
          }
        />

        {/* Member Routes - Requires member role */}
        <Route
          path="member/*"
          element={
            <MemberRoute>
              <Routes>
                <Route index element={<Navigate to="dashboard" replace />} />
                <Route path="dashboard" element={<MemberDashboard />} />
                <Route path="change-password" element={<MemberChangePassword />} />
              </Routes>
            </MemberRoute>
          }
        />

        {/* Gym Management Routes - Requires gym_owner or super_admin role */}
        <Route
          path="members"
          element={
            <GymOwnerRoute>
              <MembersPage />
            </GymOwnerRoute>
          }
        />
        <Route
          path="members/add"
          element={
            <GymOwnerRoute>
              <AddMemberPage />
            </GymOwnerRoute>
          }
        />
        <Route
          path="members/:id"
          element={
            <GymOwnerRoute>
              <ViewMemberPage />
            </GymOwnerRoute>
          }
        />
        <Route
          path="members/:id/edit"
          element={
            <GymOwnerRoute>
              <EditMemberPage />
            </GymOwnerRoute>
          }
        />

        {/* Membership Plans Management */}
        <Route
          path="membership-plans"
          element={
            <GymOwnerRoute>
              <MembershipPlansPage />
            </GymOwnerRoute>
          }
        />
        <Route
          path="membership-plans/add"
          element={
            <GymOwnerRoute>
              <AddMembershipPlanPage />
            </GymOwnerRoute>
          }
        />
        <Route
          path="membership-plans/:id"
          element={
            <GymOwnerRoute>
              <ViewMembershipPlanPage />
            </GymOwnerRoute>
          }
        />
        <Route
          path="membership-plans/:id/edit"
          element={
            <GymOwnerRoute>
              <EditMembershipPlanPage />
            </GymOwnerRoute>
          }
        />

        {/* Payments Management */}
        <Route
          path="payments"
          element={
            <GymOwnerRoute>
              <PaymentsPage />
            </GymOwnerRoute>
          }
        />
        <Route
          path="payments/add"
          element={
            <GymOwnerRoute>
              <AddPaymentPage />
            </GymOwnerRoute>
          }
        />
        <Route
          path="payments/:id"
          element={
            <GymOwnerRoute>
              <ViewPaymentPage />
            </GymOwnerRoute>
          }
        />
        <Route
          path="payments/:id/edit"
          element={
            <GymOwnerRoute>
              <EditPaymentPage />
            </GymOwnerRoute>
          }
        />

        {/* Attendance Management */}
        <Route
          path="attendance"
          element={
            <GymOwnerRoute>
              <AttendancePage />
            </GymOwnerRoute>
          }
        />
        <Route
          path="attendance/checkin"
          element={
            <GymOwnerRoute>
              <CheckInPage />
            </GymOwnerRoute>
          }
        />
        <Route
          path="attendance/reports"
          element={
            <GymOwnerRoute>
              <AttendanceReportsPage />
            </GymOwnerRoute>
          }
        />
        <Route
          path="reports"
          element={
            <GymOwnerRoute>
              <ReportsPage />
            </GymOwnerRoute>
          }
        />

        {/* Broadcast Messages */}
        <Route
          path="broadcasts"
          element={
            <GymOwnerRoute>
              <BroadcastMessagesPage />
            </GymOwnerRoute>
          }
        />
        <Route
          path="attendance/:id"
          element={
            <GymOwnerRoute>
              <ViewAttendancePage />
            </GymOwnerRoute>
          }
        />
        <Route
          path="attendance/:id/edit"
          element={
            <GymOwnerRoute>
              <EditAttendancePage />
            </GymOwnerRoute>
          }
        />

        {/* Sub-workspace placeholders with isolated scopes */}
        <Route
          path="plans"
          element={
            <div className="bg-white border border-gray-200 p-6 rounded-2xl shadow-sm">
              <h2 className="text-xl font-bold text-gray-900 mb-2">
                Trainers & Training Plans
              </h2>
              <p className="text-sm text-gray-600">
                Future training plans customization and personal trainer
                management. Data queried is filtered strictly by the tenant's
                gym_id.
              </p>
              <p className="text-xs text-gray-500 mt-4">
                Note: Membership Plans, Payments, and Attendance are now
                available as separate modules in the sidebar.
              </p>
            </div>
          }
        />
        <Route
          path="gym-profile"
          element={
            <GymOwnerRoute>
              <GymProfilePage />
            </GymOwnerRoute>
          }
        />
        <Route
          path="settings"
          element={
            <GymOwnerRoute>
              <GymOwnerSettingsPage />
            </GymOwnerRoute>
          }
        />
        <Route
          path="gym-qr"
          element={
            <GymOwnerRoute>
              <GymQRPage />
            </GymOwnerRoute>
          }
        />
      </Route>

      {/* Member Routes - Separate from Layout */}
      <Route
        path="/member/dashboard"
        element={
          <MemberRoute>
            <MemberDashboard />
          </MemberRoute>
        }
      />
      <Route
        path="/member/messages"
        element={
          <MemberRoute>
            <MemberMessagesPage />
          </MemberRoute>
        }
      />
      <Route
        path="/member/change-password"
        element={
          <MemberRoute>
            <MemberChangePassword />
          </MemberRoute>
        }
      />

      {/* Catch-all redirect */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
