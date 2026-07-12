"""
Activity logging service for the Gym Management SaaS platform.
Provides comprehensive logging for all user actions and system events.
"""

from datetime import datetime
from flask import request, g
from app.extensions import db
from app.super_admin_models import ActivityLog
from app.auth_utils import get_current_user_id, get_current_gym_id, get_current_user_role


class ActivityLogger:
    """
    Centralized service for logging all user activities and system events.
    Automatically captures request context and user information.
    """
    
    @staticmethod
    def log_activity(
        action_type, 
        description, 
        entity_type=None, 
        entity_id=None,
        gym_id=None,
        user_id=None,
        severity='info',
        extra_data=None,
        **kwargs
    ):
        """
        Log an activity with comprehensive context information.
        
        Args:
            action_type (str): Type of action (create, update, delete, login, etc.)
            description (str): Human-readable description of the action
            entity_type (str, optional): Type of entity affected (member, payment, gym, etc.)
            entity_id (int, optional): ID of the affected entity
            gym_id (int, optional): Gym ID context (auto-detected if not provided)
            user_id (int, optional): User ID (auto-detected if not provided)
            severity (str): Log severity (info, warning, error, critical)
            extra_data (dict, optional): Additional metadata for the log entry
            **kwargs: Additional keyword arguments (e.g., details as alias for extra_data)
            
        Returns:
            bool: True if logged successfully, False otherwise
        """
        try:
            # Support 'details' as an alias for extra_data
            if extra_data is None and 'details' in kwargs:
                extra_data = kwargs['details']
            
            # Auto-detect user and gym context if not provided
            if user_id is None:
                user_id = get_current_user_id()
            
            if gym_id is None:
                gym_id = get_current_gym_id()
            
            # Create activity log entry
            activity_log = ActivityLog(
                user_id=user_id,
                gym_id=gym_id,
                action_type=action_type,
                entity_type=entity_type,
                entity_id=entity_id,
                description=description,
                ip_address=ActivityLogger._get_client_ip(),
                user_agent=ActivityLogger._get_user_agent(),
                request_method=ActivityLogger._get_request_method(),
                request_path=ActivityLogger._get_request_path(),
                extra_data=extra_data,
                severity=severity,
                timestamp=datetime.utcnow()
            )
            
            db.session.add(activity_log)
            db.session.commit()
            
            return True
            
        except Exception as e:
            # Activity logging should never break the main operation
            print(f"Failed to log activity: {e}")
            return False
    
    @staticmethod
    def log_authentication(action, user_id, success=True, details=None, **kwargs):
        """
        Log authentication events (login, logout, failed attempts).
        
        Args:
            action (str): Authentication action (login, logout, failed_login)
            user_id (int): User ID attempting authentication
            success (bool): Whether the authentication was successful
            details (str, optional): Additional details about the authentication
            **kwargs: Additional keyword arguments
        """
        severity = 'info' if success else 'warning'
        description = f"User authentication: {action}"
        
        if details:
            description += f" - {details}"
        
        extra_data = {
            'success': success,
            'auth_action': action
        }
        
        ActivityLogger.log_activity(
            action_type='authentication',
            description=description,
            entity_type='user',
            entity_id=user_id,
            user_id=user_id,
            severity=severity,
            extra_data=extra_data,
            **kwargs
        )
    
    @staticmethod
    def log_create(entity_type, entity_id=None, entity_name=None, gym_id=None, extra_data=None, **kwargs):
        """
        Log creation of new entities.
        
        Args:
            entity_type (str): Type of entity created (member, payment, etc.)
            entity_id (int, optional): ID of the created entity
            entity_name (str, optional): Name/title of the created entity
            gym_id (int, optional): Gym context (auto-detected if not provided)
            extra_data (dict, optional): Additional entity data
            **kwargs: Additional keyword arguments (e.g., details)
        """
        description = f"Created {entity_type}"
        if entity_name:
            description += f": {entity_name}"
        
        ActivityLogger.log_activity(
            action_type='create',
            description=description,
            entity_type=entity_type,
            entity_id=entity_id,
            gym_id=gym_id,
            severity='info',
            extra_data=extra_data,
            **kwargs
        )
    
    @staticmethod
    def log_update(entity_type, entity_id=None, changes=None, entity_name=None, gym_id=None, **kwargs):
        """
        Log updates to existing entities.
        
        Args:
            entity_type (str): Type of entity updated
            entity_id (int, optional): ID of the updated entity
            changes (dict, optional): Dictionary of changed fields and values
            entity_name (str, optional): Name/title of the updated entity
            gym_id (int, optional): Gym context (auto-detected if not provided)
            **kwargs: Additional keyword arguments (e.g., details)
        """
        description = f"Updated {entity_type}"
        if entity_name:
            description += f": {entity_name}"
        
        extra_data = {}
        if changes:
            extra_data['changes'] = changes
            # Add changed fields to description for readability
            changed_fields = list(changes.keys())
            if changed_fields:
                description += f" (modified: {', '.join(changed_fields)})"
        
        ActivityLogger.log_activity(
            action_type='update',
            description=description,
            entity_type=entity_type,
            entity_id=entity_id,
            gym_id=gym_id,
            severity='info',
            extra_data=extra_data,
            **kwargs
        )
    
    @staticmethod
    def log_delete(entity_type, entity_id=None, entity_name=None, gym_id=None, soft_delete=True, **kwargs):
        """
        Log deletion of entities.
        
        Args:
            entity_type (str): Type of entity deleted
            entity_id (int, optional): ID of the deleted entity
            entity_name (str, optional): Name/title of the deleted entity
            gym_id (int, optional): Gym context (auto-detected if not provided)
            soft_delete (bool): Whether this was a soft delete (recoverable)
            **kwargs: Additional keyword arguments (e.g., details)
        """
        delete_type = "soft deleted" if soft_delete else "permanently deleted"
        description = f"Deleted {entity_type}"
        if entity_name:
            description += f": {entity_name}"
        
        severity = 'warning' if soft_delete else 'critical'
        
        extra_data = {
            'soft_delete': soft_delete,
            'recoverable': soft_delete
        }
        
        ActivityLogger.log_activity(
            action_type='delete',
            description=description,
            entity_type=entity_type,
            entity_id=entity_id,
            gym_id=gym_id,
            severity=severity,
            extra_data=extra_data,
            **kwargs
        )
    
    @staticmethod
    def log_view(entity_type, entity_id=None, entity_name=None, gym_id=None, view_type='detail', **kwargs):
        """
        Log when entities are viewed (for sensitive data tracking).
        
        Args:
            entity_type (str): Type of entity viewed
            entity_id (int, optional): ID of the viewed entity (None for list views)
            entity_name (str, optional): Name/title of the viewed entity
            gym_id (int, optional): Gym context (auto-detected if not provided)
            view_type (str): Type of view (list, detail, report, export)
            **kwargs: Additional keyword arguments
        """
        if view_type == 'list':
            description = f"Viewed {entity_type} list"
        elif entity_name:
            description = f"Viewed {entity_type}: {entity_name}"
        else:
            description = f"Viewed {entity_type} details"
        
        extra_data = {
            'view_type': view_type
        }
        
        ActivityLogger.log_activity(
            action_type='view',
            description=description,
            entity_type=entity_type,
            entity_id=entity_id,
            gym_id=gym_id,
            severity='info',
            extra_data=extra_data,
            **kwargs
        )
    
    @staticmethod
    def log_export(entity_type, export_format='csv', record_count=None, gym_id=None, **kwargs):
        """
        Log data export operations.
        
        Args:
            entity_type (str): Type of data exported
            export_format (str): Format of export (csv, pdf, excel)
            record_count (int, optional): Number of records exported
            gym_id (int, optional): Gym context (auto-detected if not provided)
            **kwargs: Additional keyword arguments
        """
        description = f"Exported {entity_type} data"
        if record_count:
            description += f" ({record_count} records)"
        description += f" as {export_format.upper()}"
        
        extra_data = {
            'export_format': export_format,
            'record_count': record_count
        }
        
        ActivityLogger.log_activity(
            action_type='export',
            description=description,
            entity_type=entity_type,
            gym_id=gym_id,
            severity='info',
            extra_data=extra_data,
            **kwargs
        )
    
    @staticmethod
    def log_system_event(event_type, description, severity='info', extra_data=None, **kwargs):
        """
        Log system-level events (not tied to specific users or entities).
        
        Args:
            event_type (str): Type of system event
            description (str): Description of the event
            severity (str): Event severity (info, warning, error, critical)
            extra_data (dict, optional): Additional event metadata
            **kwargs: Additional keyword arguments
        """
        ActivityLogger.log_activity(
            action_type='system',
            description=description,
            entity_type='system',
            severity=severity,
            extra_data=extra_data,
            user_id=None,  # System events have no specific user
            gym_id=None,   # System events are platform-wide
            **kwargs
        )
    
    @staticmethod
    def log_super_admin_action(action_type, description, target_gym_id=None, 
                              entity_type=None, entity_id=None, severity='info', **kwargs):
        """
        Log Super Admin specific actions with special handling.
        
        Args:
            action_type (str): Type of Super Admin action
            description (str): Description of the action
            target_gym_id (int, optional): Gym being affected by the action
            entity_type (str, optional): Type of entity being managed
            entity_id (int, optional): ID of the entity being managed
            severity (str): Action severity
            **kwargs: Additional keyword arguments
        """
        extra_data = {
            'super_admin_action': True,
            'target_gym_id': target_gym_id
        }
        
        ActivityLogger.log_activity(
            action_type=action_type,
            description=f"[SUPER ADMIN] {description}",
            entity_type=entity_type,
            entity_id=entity_id,
            gym_id=target_gym_id,  # Log under the affected gym's context
            severity=severity,
            extra_data=extra_data,
            **kwargs
        )
    
    # Helper methods for request context
    
    @staticmethod
    def _get_client_ip():
        """Get the client's IP address from the request."""
        if not request:
            return None
        
        # Check for forwarded IP first (for proxy/load balancer setups)
        if request.headers.get('X-Forwarded-For'):
            return request.headers.get('X-Forwarded-For').split(',')[0].strip()
        elif request.headers.get('X-Real-IP'):
            return request.headers.get('X-Real-IP')
        else:
            return request.remote_addr
    
    @staticmethod
    def _get_user_agent():
        """Get the user agent from the request."""
        if not request:
            return None
        return request.headers.get('User-Agent')
    
    @staticmethod
    def _get_request_method():
        """Get the HTTP method from the request."""
        if not request:
            return None
        return request.method
    
    @staticmethod
    def _get_request_path():
        """Get the request path."""
        if not request:
            return None
        return request.path


# Convenience functions for common logging operations
def log_activity(action_type, description, **kwargs):
    """Convenience wrapper for ActivityLogger.log_activity"""
    return ActivityLogger.log_activity(action_type, description, **kwargs)

def log_create(entity_type, entity_id=None, entity_name=None, **kwargs):
    """Convenience wrapper for ActivityLogger.log_create"""
    return ActivityLogger.log_create(entity_type, entity_id, entity_name, **kwargs)

def log_update(entity_type, entity_id=None, changes=None, entity_name=None, **kwargs):
    """Convenience wrapper for ActivityLogger.log_update"""
    return ActivityLogger.log_update(entity_type, entity_id, changes, entity_name, **kwargs)

def log_delete(entity_type, entity_id=None, entity_name=None, **kwargs):
    """Convenience wrapper for ActivityLogger.log_delete"""
    return ActivityLogger.log_delete(entity_type, entity_id, entity_name, **kwargs)

def log_authentication(action, user_id, success=True, details=None):
    """Convenience wrapper for ActivityLogger.log_authentication"""
    return ActivityLogger.log_authentication(action, user_id, success, details)

def log_admin_action(action_type, description, target_gym_id=None, 
                    entity_type=None, entity_id=None, severity='info'):
    """Convenience wrapper for logging Super Admin actions"""
    return ActivityLogger.log_super_admin_action(
        action_type, description, target_gym_id, entity_type, entity_id, severity
    )

def log_user_action(action_type, user_id, description, entity_type=None, 
                   entity_id=None, gym_id=None):
    """Convenience wrapper for logging specific user actions"""
    return ActivityLogger.log_activity(
        action_type=action_type,
        description=description,
        entity_type=entity_type,
        entity_id=entity_id,
        gym_id=gym_id,
        user_id=user_id,
        severity='info'
    )