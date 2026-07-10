"""
Notification routes for managing user notifications
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from app.extensions import db
from app.models import Notification, Gym, User, Member
from datetime import datetime
from sqlalchemy import or_, and_

notifications_bp = Blueprint('notifications', __name__)


def get_current_user_info():
    """Extract user information from JWT token"""
    claims = get_jwt()
    return {
        'role': claims.get('role'),
        'user_id': claims.get('sub'),
        'gym_id': claims.get('gym_id'),
        'member_id': claims.get('member_id')
    }


@notifications_bp.route('', methods=['GET'])
@jwt_required()
def get_notifications():
    """Get notifications for the authenticated user"""
    user_info = get_current_user_info()
    role = user_info['role']
    user_id = int(user_info['user_id']) if user_info['user_id'] else None
    gym_id = user_info['gym_id']
    member_id = user_info['member_id']
    
    try:
        # Build query based on role
        query = Notification.query
        
        if role == 'super_admin':
            # Super Admin sees all gym subscription expiry notifications
            query = query.filter(
                Notification.recipient_role == 'super_admin',
                Notification.notification_type == 'gym_subscription_expiry'
            )
        elif role == 'gym_owner':
            # Gym Owner sees their own subscription expiry and member membership expiry
            query = query.filter(
                Notification.gym_id == gym_id,
                or_(
                    and_(
                        Notification.recipient_role == 'gym_owner',
                        Notification.recipient_id == user_id
                    ),
                    Notification.notification_type == 'member_membership_expiry'
                )
            )
        elif role == 'member':
            # Member sees their own membership expiry notifications
            query = query.filter(
                Notification.recipient_role == 'member',
                Notification.recipient_id == member_id
            )
        else:
            return jsonify({'error': 'Invalid role'}), 400
        
        # Get unread count
        unread_count = query.filter(Notification.is_read == False).count()
        
        # Get notifications, newest first
        notifications = query.order_by(Notification.created_at.desc()).limit(50).all()
        
        return jsonify({
            'notifications': [n.to_dict() for n in notifications],
            'unread_count': unread_count
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@notifications_bp.route('/unread-count', methods=['GET'])
@jwt_required()
def get_unread_count():
    """Get unread notification count for the authenticated user"""
    user_info = get_current_user_info()
    role = user_info['role']
    user_id = int(user_info['user_id']) if user_info['user_id'] else None
    gym_id = user_info['gym_id']
    member_id = user_info['member_id']
    
    try:
        query = Notification.query.filter(Notification.is_read == False)
        
        if role == 'super_admin':
            query = query.filter(
                Notification.recipient_role == 'super_admin',
                Notification.notification_type == 'gym_subscription_expiry'
            )
        elif role == 'gym_owner':
            query = query.filter(
                Notification.gym_id == gym_id,
                or_(
                    and_(
                        Notification.recipient_role == 'gym_owner',
                        Notification.recipient_id == user_id
                    ),
                    Notification.notification_type == 'member_membership_expiry'
                )
            )
        elif role == 'member':
            query = query.filter(
                Notification.recipient_role == 'member',
                Notification.recipient_id == member_id
            )
        
        count = query.count()
        
        return jsonify({'unread_count': count}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@notifications_bp.route('/<int:notification_id>/read', methods=['PATCH'])
@jwt_required()
def mark_as_read(notification_id):
    """Mark a specific notification as read"""
    user_info = get_current_user_info()
    role = user_info['role']
    user_id = int(user_info['user_id']) if user_info['user_id'] else None
    gym_id = user_info['gym_id']
    member_id = user_info['member_id']
    
    try:
        notification = Notification.query.get(notification_id)
        
        if not notification:
            return jsonify({'error': 'Notification not found'}), 404
        
        # Verify ownership
        if role == 'super_admin':
            if notification.recipient_role != 'super_admin':
                return jsonify({'error': 'Unauthorized'}), 403
        elif role == 'gym_owner':
            if notification.gym_id != gym_id:
                return jsonify({'error': 'Unauthorized'}), 403
        elif role == 'member':
            if notification.recipient_id != member_id:
                return jsonify({'error': 'Unauthorized'}), 403
        
        notification.is_read = True
        notification.delivered_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'message': 'Notification marked as read'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@notifications_bp.route('/mark-all-read', methods=['PATCH'])
@jwt_required()
def mark_all_as_read():
    """Mark all notifications as read for the authenticated user"""
    user_info = get_current_user_info()
    role = user_info['role']
    user_id = int(user_info['user_id']) if user_info['user_id'] else None
    gym_id = user_info['gym_id']
    member_id = user_info['member_id']
    
    try:
        query = Notification.query.filter(Notification.is_read == False)
        
        if role == 'super_admin':
            query = query.filter(
                Notification.recipient_role == 'super_admin',
                Notification.notification_type == 'gym_subscription_expiry'
            )
        elif role == 'gym_owner':
            query = query.filter(
                Notification.gym_id == gym_id,
                or_(
                    and_(
                        Notification.recipient_role == 'gym_owner',
                        Notification.recipient_id == user_id
                    ),
                    Notification.notification_type == 'member_membership_expiry'
                )
            )
        elif role == 'member':
            query = query.filter(
                Notification.recipient_role == 'member',
                Notification.recipient_id == member_id
            )
        
        notifications = query.all()
        
        for notification in notifications:
            notification.is_read = True
            notification.delivered_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({'message': 'All notifications marked as read'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
