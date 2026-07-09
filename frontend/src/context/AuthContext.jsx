import React, { createContext, useState, useEffect, useContext } from 'react';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const storedToken = localStorage.getItem('flexigym_token');
    const storedUser = localStorage.getItem('flexigym_user');

    if (storedToken && storedUser) {
      try {
        const parsedUser = JSON.parse(storedUser);
        
        // Validate token expiry and role consistency
        if (isTokenExpired(storedToken)) {
          logout();
          return;
        }
        
        // Validate token claims match stored user data
        const tokenClaims = getTokenClaims(storedToken);
        if (!validateTokenUserMatch(tokenClaims, parsedUser)) {
          console.warn('Token claims do not match stored user data, logging out for security');
          logout();
          return;
        }
        
        setToken(storedToken);
        setUser(parsedUser);
      } catch (e) {
        console.error('Error parsing stored user data:', e);
        localStorage.removeItem('flexigym_user');
        localStorage.removeItem('flexigym_token');
      }
    }
    setLoading(false);
  }, []);

  const login = (newToken, newUser) => {
    setToken(newToken);
    setUser(newUser);
    localStorage.setItem('flexigym_token', newToken);
    localStorage.setItem('flexigym_user', JSON.stringify(newUser));
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('flexigym_token');
    localStorage.removeItem('flexigym_user');
  };

  // Enhanced authentication checks
  const isAuthenticated = !!token && !!user;
  
  // Role-based checks
  const isSuperAdmin = user?.role === 'super_admin';
  const isGymOwner = user?.role === 'gym_owner';
  const isMember = user?.role === 'member';
  
  // Permission checks
  const hasPermission = (permission) => {
    if (!user) return false;
    
    const permissions = getRolePermissions(user.role);
    return permissions[permission] || false;
  };
  
  // Check if user can access admin features
  const canAccessAdminFeatures = isSuperAdmin;
  
  // Check if user can access gym management
  const canAccessGymManagement = isSuperAdmin || isGymOwner;
  
  // Get user's gym information
  const getUserGym = () => {
    if (!user) return null;
    
    return {
      id: user.gym_id,
      name: user.gym_name,
      address: user.gym_address,
      phone: user.gym_phone
    };
  };
  
  // Check if user belongs to a specific gym
  const belongsToGym = (gymId) => {
    if (isSuperAdmin) return true; // Super admins can access all gyms
    return user?.gym_id === gymId;
  };
  
  // Get user display information
  const getUserDisplayInfo = () => {
    if (!user) return null;
    
    return {
      name: user.name,
      email: user.email,
      role: user.role,
      roleDisplay: getRoleDisplayName(user.role),
      initials: getInitials(user.name),
      gym: getUserGym(),
      isSuperAdmin,
      isGymOwner,
      isMember
    };
  };

  return (
    <AuthContext.Provider value={{ 
      user, 
      token, 
      loading, 
      login, 
      logout, 
      isAuthenticated,
      // Role checks
      isSuperAdmin,
      isGymOwner,
      isMember,
      // Permission checks
      hasPermission,
      canAccessAdminFeatures,
      canAccessGymManagement,
      // Utility functions
      getUserGym,
      belongsToGym,
      getUserDisplayInfo
    }}>
      {!loading && children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// Helper functions
const isTokenExpired = (token) => {
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    const currentTime = Date.now() / 1000;
    return payload.exp < currentTime;
  } catch (e) {
    return true; // If we can't parse the token, consider it expired
  }
};

const getTokenClaims = (token) => {
  try {
    return JSON.parse(atob(token.split('.')[1]));
  } catch (e) {
    return null;
  }
};

const validateTokenUserMatch = (tokenClaims, userData) => {
  if (!tokenClaims || !userData) return false;
  
  // Validate essential fields match between token and stored user data
  const roleMatches = tokenClaims.role === userData.role;
  
  // Skip gym_id validation for super admin
  if (tokenClaims.role === 'super_admin' || userData.role === 'super_admin') {
    return roleMatches;
  }
  
  // For other roles, compare gym_id with String coercion to avoid type mismatches
  const gymIdMatches = String(tokenClaims.gym_id) === String(userData.gym_id);
  
  return roleMatches && gymIdMatches;
};

const getRolePermissions = (role) => {
  const permissions = {
    'super_admin': {
      'canManageAllGyms': true,
      'canManageAllUsers': true,
      'canViewAllData': true,
      'canModifySubscriptions': true,
      'canViewAnalytics': true,
      'canManageSystemSettings': true,
      'canAccessAdminPanel': true
    },
    'gym_owner': {
      'canManageAllGyms': false,
      'canManageAllUsers': false,
      'canViewAllData': false,
      'canModifySubscriptions': false,
      'canViewAnalytics': true,
      'canManageSystemSettings': false,
      'canAccessAdminPanel': false,
      'canManageOwnGym': true,
      'canManageOwnMembers': true
    },
    'member': {
      'canManageAllGyms': false,
      'canManageAllUsers': false,
      'canViewAllData': false,
      'canModifySubscriptions': false,
      'canViewAnalytics': false,
      'canManageSystemSettings': false,
      'canAccessAdminPanel': false,
      'canManageOwnGym': false,
      'canManageOwnMembers': false,
      'canViewOwnData': true
    }
  };
  
  return permissions[role] || permissions['member'];
};

const getRoleDisplayName = (role) => {
  const roleNames = {
    'super_admin': 'Super Administrator',
    'gym_owner': 'Gym Owner',
    'member': 'Member'
  };
  
  return roleNames[role] || 'User';
};

const getInitials = (name) => {
  if (!name) return 'U';
  
  return name
    .split(' ')
    .map(part => part.charAt(0).toUpperCase())
    .join('')
    .substring(0, 2);
};
