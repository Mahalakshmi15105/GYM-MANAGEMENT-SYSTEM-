import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

// Enhanced protected route component with role-based access control
const ProtectedRoute = ({ children, requiredRole = null, requiredPermission = null }) => {
  const { isAuthenticated, user, hasPermission } = useAuth();
  const location = useLocation();

  // Check if user is authenticated
  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Check role requirement
  if (requiredRole && user?.role !== requiredRole) {
    return <Navigate to="/dashboard" replace />;
  }

  // Check permission requirement
  if (requiredPermission && !hasPermission(requiredPermission)) {
    return <Navigate to="/dashboard" replace />;
  }

  return children;
};

// Super Admin only route protection
export const SuperAdminRoute = ({ children }) => {
  return (
    <ProtectedRoute requiredRole="super_admin">
      {children}
    </ProtectedRoute>
  );
};

// Gym Owner or Super Admin route protection
export const GymOwnerRoute = ({ children }) => {
  const { isSuperAdmin, isGymOwner } = useAuth();
  
  if (!isSuperAdmin && !isGymOwner) {
    return <Navigate to="/dashboard" replace />;
  }
  
  return children;
};

// Permission-based route protection
export const PermissionRoute = ({ children, permission }) => {
  return (
    <ProtectedRoute requiredPermission={permission}>
      {children}
    </ProtectedRoute>
  );
};

// Member only route protection
export const MemberRoute = ({ children }) => {
  return (
    <ProtectedRoute requiredRole="member">
      {children}
    </ProtectedRoute>
  );
};

// Role-based component renderer
export const RoleBasedComponent = ({ 
  children, 
  allowedRoles = [], 
  requiredPermission = null,
  fallback = null 
}) => {
  const { user, hasPermission } = useAuth();

  // Check role access
  const hasRoleAccess = allowedRoles.length === 0 || allowedRoles.includes(user?.role);
  
  // Check permission access
  const hasPermissionAccess = !requiredPermission || hasPermission(requiredPermission);

  if (hasRoleAccess && hasPermissionAccess) {
    return children;
  }

  return fallback;
};

export default ProtectedRoute;