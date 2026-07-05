"""
Authentication utilities for the Gym Management SaaS platform.
Provides centralized JWT token handling and role-based access control.
"""

from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt, verify_jwt_in_request


def get_current_gym_id():
    """
    Extract gym_id from JWT token for multi-tenant isolation.
    Returns None for Super Admins who don't belong to any specific gym.
    """
    claims = get_jwt()
    return claims.get('gym_id')


def get_current_user_role():
    """
    Extract user role from JWT token.
    Returns the role string (gym_owner, member, super_admin).
    """
    claims = get_jwt()
    return claims.get('role')


def get_current_user_id():
    """
    Extract user ID from JWT token identity.
    Returns the user ID as a string.
    """
    claims = get_jwt()
    return claims.get('sub')  # JWT standard identity claim


def get_current_user_claims():
    """
    Get all JWT claims for the current user.
    Returns the complete claims dictionary.
    """
    return get_jwt()


def super_admin_required(f):
    """
    Decorator that requires Super Admin role to access the endpoint.
    Validates JWT token and ensures user has super_admin role.
    
    Usage:
        @super_admin_required
        def admin_only_endpoint():
            pass
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # Verify JWT token is present and valid
            verify_jwt_in_request()
            
            # Get user role from JWT claims
            user_role = get_current_user_role()
            
            if user_role != 'super_admin':
                return jsonify({
                    'error': 'Super Admin access required',
                    'code': 'SUPER_ADMIN_REQUIRED',
                    'details': 'This action requires Super Admin privileges'
                }), 403
                
            return f(*args, **kwargs)
            
        except Exception as e:
            return jsonify({
                'error': 'Authentication failed',
                'code': 'AUTH_ERROR',
                'details': str(e)
            }), 401
            
    return decorated_function


def gym_owner_or_admin_required(f):
    """
    Decorator that requires either gym_owner or super_admin role.
    Useful for endpoints that both gym owners and super admins should access.
    
    Usage:
        @gym_owner_or_admin_required
        def owner_or_admin_endpoint():
            pass
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # Verify JWT token is present and valid
            verify_jwt_in_request()
            
            # Get user role from JWT claims
            user_role = get_current_user_role()
            
            if user_role not in ['gym_owner', 'super_admin']:
                return jsonify({
                    'error': 'Insufficient privileges',
                    'code': 'INSUFFICIENT_PRIVILEGES',
                    'details': 'This action requires gym owner or super admin privileges'
                }), 403
                
            return f(*args, **kwargs)
            
        except Exception as e:
            return jsonify({
                'error': 'Authentication failed',
                'code': 'AUTH_ERROR',
                'details': str(e)
            }), 401
            
    return decorated_function


def validate_gym_access(gym_id):
    """
    Validate that the current user has access to the specified gym.
    Super Admins have access to all gyms.
    Gym owners only have access to their own gym.
    
    Args:
        gym_id (int): The gym ID to validate access for
        
    Returns:
        bool: True if access is allowed, False otherwise
    """
    user_role = get_current_user_role()
    
    # Super admins have access to all gyms
    if user_role == 'super_admin':
        return True
        
    # Gym owners only have access to their own gym
    current_gym_id = get_current_gym_id()
    return current_gym_id == gym_id


def require_gym_access(gym_id):
    """
    Check gym access and return appropriate error response if access is denied.
    
    Args:
        gym_id (int): The gym ID to validate access for
        
    Returns:
        tuple: (None, None) if access allowed, (error_response, status_code) if denied
    """
    if not validate_gym_access(gym_id):
        return jsonify({
            'error': 'Access denied',
            'code': 'GYM_ACCESS_DENIED',
            'details': 'You do not have access to this gym'
        }), 403
        
    return None, None


def get_role_permissions(role):
    """
    Get the permissions for a specific role.
    
    Args:
        role (str): The role name (super_admin, gym_owner, member)
        
    Returns:
        dict: Dictionary containing role permissions
    """
    permissions = {
        'super_admin': {
            'can_manage_all_gyms': True,
            'can_manage_users': True,
            'can_view_analytics': True,
            'can_manage_subscriptions': True,
            'can_manage_settings': True,
            'can_view_logs': True,
            'can_access_gym_data': True
        },
        'gym_owner': {
            'can_manage_all_gyms': False,
            'can_manage_users': False,
            'can_view_analytics': True,
            'can_manage_subscriptions': False,
            'can_manage_settings': False,
            'can_view_logs': False,
            'can_access_gym_data': True
        },
        'member': {
            'can_manage_all_gyms': False,
            'can_manage_users': False,
            'can_view_analytics': False,
            'can_manage_subscriptions': False,
            'can_manage_settings': False,
            'can_view_logs': False,
            'can_access_gym_data': False
        }
    }
    
    return permissions.get(role, permissions['member'])


def has_permission(permission):
    """
    Check if the current user has a specific permission.
    
    Args:
        permission (str): The permission to check
        
    Returns:
        bool: True if the user has the permission, False otherwise
    """
    user_role = get_current_user_role()
    if not user_role:
        return False
        
    role_permissions = get_role_permissions(user_role)
    return role_permissions.get(permission, False)