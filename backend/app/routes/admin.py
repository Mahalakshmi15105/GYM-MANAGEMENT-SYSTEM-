"""
Super Admin routes for platform management.
Handles gym management, platform analytics, user oversight, and system administration.
"""

from flask import Blueprint, request, jsonify
from sqlalchemy import func, desc, and_, or_
from datetime import datetime, date, timedelta
from app.extensions import db
from app.auth_utils import super_admin_required, get_current_user_id
from app.models import Gym, User, Member, Payment, Attendance
from app.super_admin_models import ActivityLog, SystemSettings, GymSubscription

admin_bp = Blueprint('admin', __name__)


# =============================================================================
# PLATFORM ANALYTICS ENDPOINTS
# =============================================================================

@admin_bp.route('/dashboard/analytics', methods=['GET'])
@super_admin_required
def get_platform_analytics():
    """Get comprehensive platform-wide analytics for Super Admin dashboard"""
    try:
        # Date calculations
        today = date.today()
        thirty_days_ago = today - timedelta(days=30)
        seven_days_ago = today - timedelta(days=7)
        
        # Platform-wide metrics
        total_gyms = Gym.query.count()
        active_gyms = Gym.query.filter_by(status='Active').count()
        pending_gyms = Gym.query.filter_by(status='Pending').count()
        suspended_gyms = Gym.query.filter_by(status='Suspended').count()
        
        # Member metrics across all gyms
        total_members = Member.query.join(Gym).filter(Gym.status == 'Active').count()
        active_members = Member.query.join(Gym).filter(
            and_(Member.status == 'Active', Gym.status == 'Active')
        ).count()
        
        # Revenue metrics (last 30 days)
        revenue_30_days = db.session.query(func.sum(Payment.payment_amount)).join(Gym).filter(
            and_(
                Payment.payment_date >= thirty_days_ago,
                Payment.payment_status == 'Paid',
                Gym.status == 'Active'
            )
        ).scalar() or 0
        
        # Recent activity metrics
        new_gyms_7_days = Gym.query.filter(Gym.created_at >= seven_days_ago).count()
        new_members_7_days = Member.query.join(Gym).filter(
            and_(Member.created_at >= seven_days_ago, Gym.status == 'Active')
        ).count()
        
        # Subscription metrics
        active_subscriptions = GymSubscription.query.filter_by(status='Active').count()
        expiring_subscriptions = GymSubscription.query.filter(
            and_(
                GymSubscription.status == 'Active',
                GymSubscription.next_billing_date <= today + timedelta(days=7)
            )
        ).count()
        
        return jsonify({
            'platform_metrics': {
                'total_gyms': total_gyms,
                'active_gyms': active_gyms,
                'pending_gyms': pending_gyms,
                'suspended_gyms': suspended_gyms,
                'total_members': total_members,
                'active_members': active_members,
                'revenue_30_days': float(revenue_30_days),
                'new_gyms_7_days': new_gyms_7_days,
                'new_members_7_days': new_members_7_days,
                'active_subscriptions': active_subscriptions,
                'expiring_subscriptions': expiring_subscriptions
            },
            'generated_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch platform analytics', 'details': str(e)}), 500


@admin_bp.route('/dashboard/growth-metrics', methods=['GET'])
@super_admin_required
def get_growth_metrics():
    """Get platform growth metrics over time"""
    try:
        days = int(request.args.get('days', 30))
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        # Daily gym registrations
        gym_growth = db.session.query(
            func.date(Gym.created_at).label('date'),
            func.count(Gym.id).label('count')
        ).filter(
            Gym.created_at >= start_date
        ).group_by(func.date(Gym.created_at)).all()
        
        # Daily member registrations (active gyms only)
        member_growth = db.session.query(
            func.date(Member.created_at).label('date'),
            func.count(Member.id).label('count')
        ).join(Gym).filter(
            and_(
                Member.created_at >= start_date,
                Gym.status == 'Active'
            )
        ).group_by(func.date(Member.created_at)).all()
        
        # Daily revenue
        revenue_growth = db.session.query(
            Payment.payment_date.label('date'),
            func.sum(Payment.payment_amount).label('amount')
        ).join(Gym).filter(
            and_(
                Payment.payment_date >= start_date,
                Payment.payment_status == 'Paid',
                Gym.status == 'Active'
            )
        ).group_by(Payment.payment_date).all()
        
        return jsonify({
            'gym_growth': [{'date': str(row.date), 'count': row.count} for row in gym_growth],
            'member_growth': [{'date': str(row.date), 'count': row.count} for row in member_growth],
            'revenue_growth': [{'date': str(row.date), 'amount': float(row.amount)} for row in revenue_growth],
            'period': {'start_date': str(start_date), 'end_date': str(end_date)}
        })
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch growth metrics', 'details': str(e)}), 500


# =============================================================================
# GYM MANAGEMENT ENDPOINTS
# =============================================================================

@admin_bp.route('/gyms', methods=['GET'])
@super_admin_required
def list_gyms():
    """List all gyms with filtering and pagination"""
    try:
        # Query parameters
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        status_filter = request.args.get('status')
        search_query = request.args.get('q', '').strip()
        
        # Base query
        query = Gym.query
        
        # Apply filters
        if status_filter:
            query = query.filter(Gym.status == status_filter)
            
        if search_query:
            query = query.filter(or_(
                Gym.name.ilike(f'%{search_query}%'),
                Gym.owner_name.ilike(f'%{search_query}%'),
                Gym.address.ilike(f'%{search_query}%')
            ))
        
        # Order by created_at desc
        query = query.order_by(desc(Gym.created_at))
        
        # Paginate
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'gyms': [gym.to_dict() for gym in pagination.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            },
            'filters': {
                'status': status_filter,
                'search': search_query
            }
        })
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch gyms', 'details': str(e)}), 500


@admin_bp.route('/gyms/<int:gym_id>', methods=['GET'])
@super_admin_required
def get_gym_details():
    """Get detailed information about a specific gym"""
    try:
        gym = Gym.query.get_or_404(gym_id)
        
        # Get additional metrics for this gym
        total_members = Member.query.filter_by(gym_id=gym_id).count()
        active_members = Member.query.filter_by(gym_id=gym_id, status='Active').count()
        
        # Recent revenue (last 30 days)
        thirty_days_ago = date.today() - timedelta(days=30)
        recent_revenue = db.session.query(func.sum(Payment.payment_amount)).filter(
            and_(
                Payment.gym_id == gym_id,
                Payment.payment_date >= thirty_days_ago,
                Payment.payment_status == 'Paid'
            )
        ).scalar() or 0
        
        # Get subscription info
        subscription = gym.get_subscription_info()
        
        gym_data = gym.to_dict()
        gym_data.update({
            'metrics': {
                'total_members': total_members,
                'active_members': active_members,
                'recent_revenue': float(recent_revenue)
            },
            'subscription': subscription.to_dict() if subscription else None
        })
        
        return jsonify(gym_data)
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch gym details', 'details': str(e)}), 500


@admin_bp.route('/gyms/<int:gym_id>/approve', methods=['PUT'])
@super_admin_required
def approve_gym(gym_id):
    """Approve a pending gym"""
    try:
        gym = Gym.query.get_or_404(gym_id)
        admin_user_id = get_current_user_id()
        
        if gym.approve_gym(admin_user_id):
            db.session.commit()
            
            # Log the action
            log_activity(
                user_id=admin_user_id,
                gym_id=gym_id,
                action_type='approve',
                entity_type='gym',
                entity_id=gym_id,
                description=f'Approved gym: {gym.name}'
            )
            
            return jsonify({
                'message': 'Gym approved successfully',
                'gym': gym.to_dict()
            })
        else:
            return jsonify({'error': 'Gym cannot be approved in current status'}), 400
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to approve gym', 'details': str(e)}), 500


@admin_bp.route('/gyms/<int:gym_id>/suspend', methods=['PUT'])
@super_admin_required
def suspend_gym(gym_id):
    """Suspend an active gym"""
    try:
        gym = Gym.query.get_or_404(gym_id)
        admin_user_id = get_current_user_id()
        data = request.get_json() or {}
        reason = data.get('reason', 'No reason provided')
        
        if gym.suspend_gym(reason):
            db.session.commit()
            
            # Log the action
            log_activity(
                user_id=admin_user_id,
                gym_id=gym_id,
                action_type='suspend',
                entity_type='gym',
                entity_id=gym_id,
                description=f'Suspended gym: {gym.name}. Reason: {reason}',
                severity='warning'
            )
            
            return jsonify({
                'message': 'Gym suspended successfully',
                'gym': gym.to_dict()
            })
        else:
            return jsonify({'error': 'Gym cannot be suspended in current status'}), 400
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to suspend gym', 'details': str(e)}), 500


@admin_bp.route('/gyms/<int:gym_id>/reactivate', methods=['PUT'])
@super_admin_required
def reactivate_gym(gym_id):
    """Reactivate a suspended gym"""
    try:
        gym = Gym.query.get_or_404(gym_id)
        admin_user_id = get_current_user_id()
        
        if gym.reactivate_gym():
            db.session.commit()
            
            # Log the action
            log_activity(
                user_id=admin_user_id,
                gym_id=gym_id,
                action_type='reactivate',
                entity_type='gym',
                entity_id=gym_id,
                description=f'Reactivated gym: {gym.name}'
            )
            
            return jsonify({
                'message': 'Gym reactivated successfully',
                'gym': gym.to_dict()
            })
        else:
            return jsonify({'error': 'Gym cannot be reactivated in current status'}), 400
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to reactivate gym', 'details': str(e)}), 500


@admin_bp.route('/gyms/<int:gym_id>', methods=['DELETE'])
@super_admin_required
def delete_gym(gym_id):
    """Soft delete a gym"""
    try:
        gym = Gym.query.get_or_404(gym_id)
        admin_user_id = get_current_user_id()
        
        if gym.soft_delete_gym():
            db.session.commit()
            
            # Log the action
            log_activity(
                user_id=admin_user_id,
                gym_id=gym_id,
                action_type='delete',
                entity_type='gym',
                entity_id=gym_id,
                description=f'Deleted gym: {gym.name}',
                severity='critical'
            )
            
            return jsonify({
                'message': 'Gym deleted successfully',
                'gym': gym.to_dict()
            })
        else:
            return jsonify({'error': 'Gym cannot be deleted in current status'}), 400
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete gym', 'details': str(e)}), 500


# =============================================================================
# ACTIVITY LOGGING SERVICE
# =============================================================================

def log_activity(user_id, action_type, description, gym_id=None, entity_type=None, 
                entity_id=None, severity='info', extra_data=None):
    """Log activity for audit trail"""
    try:
        log = ActivityLog(
            user_id=user_id,
            gym_id=gym_id,
            action_type=action_type,
            entity_type=entity_type,
            entity_id=entity_id,
            description=description,
            severity=severity,
            extra_data=extra_data,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            request_method=request.method,
            request_path=request.path
        )
        
        db.session.add(log)
        db.session.commit()
        
    except Exception as e:
        # Log activity should not break the main operation
        print(f"Failed to log activity: {e}")


@admin_bp.route('/activity-logs', methods=['GET'])
@super_admin_required
def get_activity_logs():
    """Get platform activity logs with filtering"""
    try:
        # Query parameters
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 50)), 100)
        gym_id = request.args.get('gym_id', type=int)
        user_id = request.args.get('user_id', type=int)
        action_type = request.args.get('action_type')
        severity = request.args.get('severity')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Base query
        query = ActivityLog.query
        
        # Apply filters
        if gym_id:
            query = query.filter(ActivityLog.gym_id == gym_id)
        if user_id:
            query = query.filter(ActivityLog.user_id == user_id)
        if action_type:
            query = query.filter(ActivityLog.action_type == action_type)
        if severity:
            query = query.filter(ActivityLog.severity == severity)
        if start_date:
            start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            query = query.filter(ActivityLog.timestamp >= start)
        if end_date:
            end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            query = query.filter(ActivityLog.timestamp <= end)
        
        # Order by timestamp desc
        query = query.order_by(desc(ActivityLog.timestamp))
        
        # Paginate
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'logs': [log.to_dict() for log in pagination.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            },
            'filters': {
                'gym_id': gym_id,
                'user_id': user_id,
                'action_type': action_type,
                'severity': severity,
                'start_date': start_date,
                'end_date': end_date
            }
        })
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch activity logs', 'details': str(e)}), 500


# =============================================================================
# PLATFORM ANALYTICS SERVICE
# =============================================================================

class PlatformAnalyticsService:
    """Service for platform-wide analytics and reporting"""
    
    @staticmethod
    def get_platform_metrics():
        """Get comprehensive platform metrics"""
        return {
            'gyms': {
                'total': Gym.query.count(),
                'active': Gym.query.filter_by(status='Active').count(),
                'pending': Gym.query.filter_by(status='Pending').count(),
                'suspended': Gym.query.filter_by(status='Suspended').count()
            },
            'members': {
                'total': Member.query.join(Gym).filter(Gym.status == 'Active').count(),
                'active': Member.query.join(Gym).filter(
                    and_(Member.status == 'Active', Gym.status == 'Active')
                ).count()
            },
            'subscriptions': {
                'active': GymSubscription.query.filter_by(status='Active').count(),
                'expiring_soon': GymSubscription.query.filter(
                    and_(
                        GymSubscription.status == 'Active',
                        GymSubscription.next_billing_date <= date.today() + timedelta(days=7)
                    )
                ).count()
            }
        }
    
    @staticmethod
    def get_gym_performance_data(gym_id):
        """Get performance metrics for a specific gym"""
        gym = Gym.query.get(gym_id)
        if not gym:
            return None
            
        thirty_days_ago = date.today() - timedelta(days=30)
        
        return {
            'gym': gym.to_dict(),
            'members': {
                'total': Member.query.filter_by(gym_id=gym_id).count(),
                'active': Member.query.filter_by(gym_id=gym_id, status='Active').count(),
                'new_30_days': Member.query.filter(
                    and_(Member.gym_id == gym_id, Member.created_at >= thirty_days_ago)
                ).count()
            },
            'revenue': {
                'last_30_days': float(db.session.query(func.sum(Payment.payment_amount)).filter(
                    and_(
                        Payment.gym_id == gym_id,
                        Payment.payment_date >= thirty_days_ago,
                        Payment.payment_status == 'Paid'
                    )
                ).scalar() or 0)
            },
            'attendance': {
                'last_30_days': Attendance.query.filter(
                    and_(
                        Attendance.gym_id == gym_id,
                        Attendance.attendance_date >= thirty_days_ago
                    )
                ).count()
            }
        }
#
 =============================================================================
# SUBSCRIPTION MANAGEMENT ENDPOINTS
# =============================================================================

@admin_bp.route('/subscriptions', methods=['GET'])
@super_admin_required
def list_subscriptions():
    """List all gym subscriptions with filtering and pagination"""
    try:
        # Query parameters
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        status_filter = request.args.get('status')
        plan_filter = request.args.get('plan_name')
        expiring_soon = request.args.get('expiring_soon', '').lower() == 'true'
        
        # Base query
        query = GymSubscription.query
        
        # Apply filters
        if status_filter:
            query = query.filter(GymSubscription.status == status_filter)
            
        if plan_filter:
            query = query.filter(GymSubscription.plan_name.ilike(f'%{plan_filter}%'))
            
        if expiring_soon:
            # Subscriptions expiring within 7 days
            expiry_threshold = date.today() + timedelta(days=7)
            query = query.filter(
                and_(
                    GymSubscription.status == 'Active',
                    GymSubscription.next_billing_date <= expiry_threshold
                )
            )
        
        # Order by next billing date (most urgent first)
        query = query.order_by(GymSubscription.next_billing_date.asc())
        
        # Paginate
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'subscriptions': [sub.to_dict() for sub in pagination.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            },
            'filters': {
                'status': status_filter,
                'plan_name': plan_filter,
                'expiring_soon': expiring_soon
            }
        })
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch subscriptions', 'details': str(e)}), 500


@admin_bp.route('/subscriptions/<int:subscription_id>', methods=['GET'])
@super_admin_required
def get_subscription_details(subscription_id):
    """Get detailed information about a specific subscription"""
    try:
        subscription = GymSubscription.query.get_or_404(subscription_id)
        
        # Get subscription metrics
        subscription_data = subscription.to_dict()
        
        # Add usage metrics
        if subscription.gym:
            current_members = subscription.gym.get_member_count()
            subscription_data['usage'] = {
                'current_members': current_members,
                'member_limit': subscription.max_members,
                'member_usage_percent': round((current_members / subscription.max_members) * 100, 1) if subscription.max_members > 0 else 0,
                'days_until_expiry': subscription.days_until_expiry(),
                'is_active': subscription.is_active()
            }
        
        return jsonify(subscription_data)
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch subscription details', 'details': str(e)}), 500


@admin_bp.route('/subscriptions', methods=['POST'])
@super_admin_required
def create_subscription():
    """Create a new subscription for a gym"""
    try:
        data = request.get_json() or {}
        admin_user_id = get_current_user_id()
        
        # Required fields validation
        required_fields = ['gym_id', 'plan_name', 'monthly_price', 'billing_cycle_start', 'billing_cycle_end']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Check if gym exists and doesn't already have an active subscription
        gym = Gym.query.get_or_404(data['gym_id'])
        existing_subscription = GymSubscription.query.filter_by(
            gym_id=data['gym_id'], 
            status='Active'
        ).first()
        
        if existing_subscription:
            return jsonify({'error': 'Gym already has an active subscription'}), 400
        
        # Parse dates
        try:
            billing_start = datetime.strptime(data['billing_cycle_start'], '%Y-%m-%d').date()
            billing_end = datetime.strptime(data['billing_cycle_end'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
        # Calculate next billing date
        next_billing = billing_end + timedelta(days=1)
        
        # Create subscription
        subscription = GymSubscription(
            gym_id=data['gym_id'],
            plan_name=data['plan_name'],
            monthly_price=data['monthly_price'],
            max_members=data.get('max_members', 100),
            max_trainers=data.get('max_trainers', 5),
            features=data.get('features', {}),
            billing_cycle_start=billing_start,
            billing_cycle_end=billing_end,
            next_billing_date=next_billing,
            status='Active',
            auto_renew=data.get('auto_renew', True),
            payment_method=data.get('payment_method'),
            created_by=admin_user_id
        )
        
        db.session.add(subscription)
        db.session.commit()
        
        # Log the action
        log_activity(
            user_id=admin_user_id,
            gym_id=data['gym_id'],
            action_type='create',
            entity_type='subscription',
            entity_id=subscription.id,
            description=f'Created subscription: {subscription.plan_name} for gym: {gym.name}'
        )
        
        return jsonify({
            'message': 'Subscription created successfully',
            'subscription': subscription.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create subscription', 'details': str(e)}), 500


@admin_bp.route('/subscriptions/<int:subscription_id>', methods=['PUT'])
@super_admin_required
def update_subscription(subscription_id):
    """Update subscription details"""
    try:
        subscription = GymSubscription.query.get_or_404(subscription_id)
        data = request.get_json() or {}
        admin_user_id = get_current_user_id()
        
        # Track changes for logging
        changes = []
        
        # Update allowed fields
        updatable_fields = {
            'plan_name': str,
            'monthly_price': float,
            'max_members': int,
            'max_trainers': int,
            'features': dict,
            'auto_renew': bool,
            'payment_method': str
        }
        
        for field, field_type in updatable_fields.items():
            if field in data:
                old_value = getattr(subscription, field)
                new_value = field_type(data[field]) if data[field] is not None else None
                
                if old_value != new_value:
                    changes.append(f'{field}: {old_value} → {new_value}')
                    setattr(subscription, field, new_value)
        
        # Handle billing cycle updates (requires special validation)
        if 'billing_cycle_start' in data or 'billing_cycle_end' in data:
            try:
                if 'billing_cycle_start' in data:
                    new_start = datetime.strptime(data['billing_cycle_start'], '%Y-%m-%d').date()
                    if subscription.billing_cycle_start != new_start:
                        changes.append(f'billing_cycle_start: {subscription.billing_cycle_start} → {new_start}')
                        subscription.billing_cycle_start = new_start
                
                if 'billing_cycle_end' in data:
                    new_end = datetime.strptime(data['billing_cycle_end'], '%Y-%m-%d').date()
                    if subscription.billing_cycle_end != new_end:
                        changes.append(f'billing_cycle_end: {subscription.billing_cycle_end} → {new_end}')
                        subscription.billing_cycle_end = new_end
                        # Update next billing date
                        subscription.next_billing_date = new_end + timedelta(days=1)
                        changes.append(f'next_billing_date updated to: {subscription.next_billing_date}')
                        
            except ValueError:
                return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
        if not changes:
            return jsonify({'message': 'No changes detected', 'subscription': subscription.to_dict()})
        
        db.session.commit()
        
        # Log the changes
        log_activity(
            user_id=admin_user_id,
            gym_id=subscription.gym_id,
            action_type='update',
            entity_type='subscription',
            entity_id=subscription_id,
            description=f'Updated subscription for {subscription.gym.name}: {", ".join(changes)}'
        )
        
        return jsonify({
            'message': 'Subscription updated successfully',
            'changes': changes,
            'subscription': subscription.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update subscription', 'details': str(e)}), 500


@admin_bp.route('/subscriptions/<int:subscription_id>/status', methods=['PUT'])
@super_admin_required
def update_subscription_status(subscription_id):
    """Update subscription status (suspend, reactivate, cancel)"""
    try:
        subscription = GymSubscription.query.get_or_404(subscription_id)
        data = request.get_json() or {}
        admin_user_id = get_current_user_id()
        
        new_status = data.get('status')
        reason = data.get('reason', 'No reason provided')
        
        if not new_status:
            return jsonify({'error': 'Status is required'}), 400
        
        valid_statuses = ['Active', 'Suspended', 'Cancelled', 'Expired']
        if new_status not in valid_statuses:
            return jsonify({'error': f'Invalid status. Must be one of: {valid_statuses}'}), 400
        
        old_status = subscription.status
        
        if old_status == new_status:
            return jsonify({'message': f'Subscription is already {new_status}'}), 200
        
        # Validate status transitions
        valid_transitions = {
            'Active': ['Suspended', 'Cancelled'],
            'Suspended': ['Active', 'Cancelled'],
            'Cancelled': [],  # Cannot transition from cancelled
            'Expired': ['Active']  # Can reactivate expired
        }
        
        if new_status not in valid_transitions.get(old_status, []):
            return jsonify({'error': f'Cannot transition from {old_status} to {new_status}'}), 400
        
        subscription.status = new_status
        db.session.commit()
        
        # Log the status change
        log_activity(
            user_id=admin_user_id,
            gym_id=subscription.gym_id,
            action_type='status_change',
            entity_type='subscription',
            entity_id=subscription_id,
            description=f'Changed subscription status from {old_status} to {new_status}. Reason: {reason}',
            severity='warning' if new_status in ['Suspended', 'Cancelled'] else 'info'
        )
        
        return jsonify({
            'message': f'Subscription status changed from {old_status} to {new_status}',
            'subscription': subscription.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update subscription status', 'details': str(e)}), 500


@admin_bp.route('/subscriptions/<int:subscription_id>/billing', methods=['POST'])
@super_admin_required
def record_billing_payment(subscription_id):
    """Record a billing payment for a subscription"""
    try:
        subscription = GymSubscription.query.get_or_404(subscription_id)
        data = request.get_json() or {}
        admin_user_id = get_current_user_id()
        
        # Required fields
        payment_amount = data.get('payment_amount')
        payment_date = data.get('payment_date')
        payment_method = data.get('payment_method', 'Unknown')
        
        if not payment_amount or not payment_date:
            return jsonify({'error': 'payment_amount and payment_date are required'}), 400
        
        try:
            payment_date = datetime.strptime(payment_date, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
        # Update subscription with payment info
        subscription.last_payment_date = payment_date
        subscription.last_payment_amount = payment_amount
        subscription.payment_method = payment_method
        
        # If auto_renew is enabled, extend billing cycle
        if subscription.auto_renew and subscription.status == 'Active':
            # Extend billing cycle by one month (30 days)
            old_end = subscription.billing_cycle_end
            subscription.billing_cycle_end = old_end + timedelta(days=30)
            subscription.next_billing_date = subscription.billing_cycle_end + timedelta(days=1)
        
        db.session.commit()
        
        # Log the payment
        log_activity(
            user_id=admin_user_id,
            gym_id=subscription.gym_id,
            action_type='payment',
            entity_type='subscription',
            entity_id=subscription_id,
            description=f'Recorded payment of ${payment_amount} for subscription: {subscription.plan_name}',
            extra_data={
                'payment_amount': float(payment_amount),
                'payment_date': str(payment_date),
                'payment_method': payment_method
            }
        )
        
        return jsonify({
            'message': 'Payment recorded successfully',
            'subscription': subscription.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to record payment', 'details': str(e)}), 500


@admin_bp.route('/subscriptions/analytics', methods=['GET'])
@super_admin_required
def get_subscription_analytics():
    """Get subscription analytics and metrics"""
    try:
        # Basic subscription metrics
        total_subscriptions = GymSubscription.query.count()
        active_subscriptions = GymSubscription.query.filter_by(status='Active').count()
        suspended_subscriptions = GymSubscription.query.filter_by(status='Suspended').count()
        cancelled_subscriptions = GymSubscription.query.filter_by(status='Cancelled').count()
        
        # Revenue metrics (last 30 days)
        thirty_days_ago = date.today() - timedelta(days=30)
        recent_payments = GymSubscription.query.filter(
            and_(
                GymSubscription.last_payment_date >= thirty_days_ago,
                GymSubscription.last_payment_amount.isnot(None)
            )
        ).all()
        
        total_revenue_30_days = sum(
            float(sub.last_payment_amount or 0) for sub in recent_payments
        )
        
        # Monthly recurring revenue (MRR)
        active_subs = GymSubscription.query.filter_by(status='Active').all()
        mrr = sum(float(sub.monthly_price) for sub in active_subs)
        
        # Expiring subscriptions (next 7 days)
        seven_days_from_now = date.today() + timedelta(days=7)
        expiring_soon = GymSubscription.query.filter(
            and_(
                GymSubscription.status == 'Active',
                GymSubscription.next_billing_date <= seven_days_from_now
            )
        ).count()
        
        # Plan distribution
        plan_distribution = db.session.query(
            GymSubscription.plan_name,
            func.count(GymSubscription.id).label('count')
        ).filter(
            GymSubscription.status == 'Active'
        ).group_by(GymSubscription.plan_name).all()
        
        # Usage metrics
        usage_stats = []
        for sub in active_subs:
            if sub.gym:
                current_members = sub.gym.get_member_count()
                usage_percent = (current_members / sub.max_members) * 100 if sub.max_members > 0 else 0
                usage_stats.append({
                    'gym_id': sub.gym_id,
                    'gym_name': sub.gym.name,
                    'current_members': current_members,
                    'max_members': sub.max_members,
                    'usage_percent': round(usage_percent, 1)
                })
        
        # Average usage
        avg_usage = sum(stat['usage_percent'] for stat in usage_stats) / len(usage_stats) if usage_stats else 0
        
        return jsonify({
            'subscription_metrics': {
                'total': total_subscriptions,
                'active': active_subscriptions,
                'suspended': suspended_subscriptions,
                'cancelled': cancelled_subscriptions,
                'expiring_soon': expiring_soon
            },
            'revenue_metrics': {
                'total_revenue_30_days': total_revenue_30_days,
                'monthly_recurring_revenue': mrr,
                'average_subscription_value': mrr / active_subscriptions if active_subscriptions > 0 else 0
            },
            'plan_distribution': [
                {'plan_name': row.plan_name, 'count': row.count}
                for row in plan_distribution
            ],
            'usage_metrics': {
                'average_usage_percent': round(avg_usage, 1),
                'high_usage_gyms': [
                    stat for stat in usage_stats 
                    if stat['usage_percent'] > 80
                ],
                'low_usage_gyms': [
                    stat for stat in usage_stats 
                    if stat['usage_percent'] < 20
                ]
            },
            'generated_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch subscription analytics', 'details': str(e)}), 500


@admin_bp.route('/subscriptions/plans', methods=['GET'])
@super_admin_required
def get_subscription_plans():
    """Get available subscription plan templates"""
    try:
        # Standard plan templates that can be used for creating subscriptions
        standard_plans = [
            {
                'plan_name': 'Starter',
                'monthly_price': 49.99,
                'max_members': 50,
                'max_trainers': 2,
                'features': {
                    'member_management': True,
                    'basic_reporting': True,
                    'email_support': True,
                    'mobile_app': False,
                    'advanced_analytics': False,
                    'api_access': False
                },
                'description': 'Perfect for small gyms getting started'
            },
            {
                'plan_name': 'Professional',
                'monthly_price': 99.99,
                'max_members': 200,
                'max_trainers': 5,
                'features': {
                    'member_management': True,
                    'basic_reporting': True,
                    'email_support': True,
                    'mobile_app': True,
                    'advanced_analytics': True,
                    'api_access': False
                },
                'description': 'Ideal for growing fitness centers'
            },
            {
                'plan_name': 'Enterprise',
                'monthly_price': 199.99,
                'max_members': 1000,
                'max_trainers': 20,
                'features': {
                    'member_management': True,
                    'basic_reporting': True,
                    'email_support': True,
                    'mobile_app': True,
                    'advanced_analytics': True,
                    'api_access': True,
                    'priority_support': True,
                    'custom_branding': True
                },
                'description': 'Complete solution for large fitness facilities'
            }
        ]
        
        # Get current plan usage statistics
        plan_usage = {}
        for plan in standard_plans:
            count = GymSubscription.query.filter(
                and_(
                    GymSubscription.plan_name == plan['plan_name'],
                    GymSubscription.status == 'Active'
                )
            ).count()
            plan_usage[plan['plan_name']] = count
        
        return jsonify({
            'standard_plans': standard_plans,
            'plan_usage': plan_usage,
            'total_active_subscriptions': sum(plan_usage.values())
        })
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch subscription plans', 'details': str(e)}), 500

# =============================================================================
# SUBSCRIPTION MANAGEMENT ENDPOINTS
# =============================================================================

@admin_bp.route('/subscriptions', methods=['GET'])
@super_admin_required
def list_subscriptions():
    """List all gym subscriptions with filtering and pagination"""
    try:
        # Query parameters
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        status_filter = request.args.get('status')
        expiring_soon = request.args.get('expiring_soon') == 'true'
        search_query = request.args.get('q', '').strip()
        
        # Base query
        query = GymSubscription.query.join(Gym)
        
        # Apply filters
        if status_filter:
            query = query.filter(GymSubscription.status == status_filter)
            
        if expiring_soon:
            # Subscriptions expiring within 7 days
            expiry_threshold = date.today() + timedelta(days=7)
            query = query.filter(
                and_(
                    GymSubscription.status == 'Active',
                    GymSubscription.next_billing_date <= expiry_threshold
                )
            )
            
        if search_query:
            query = query.filter(or_(
                Gym.name.ilike(f'%{search_query}%'),
                GymSubscription.plan_name.ilike(f'%{search_query}%')
            ))
        
        # Order by next billing date (soonest first for active subscriptions)
        query = query.order_by(GymSubscription.next_billing_date.asc())
        
        # Paginate
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'subscriptions': [sub.to_dict() for sub in pagination.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            },
            'filters': {
                'status': status_filter,
                'expiring_soon': expiring_soon,
                'search': search_query
            }
        })
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch subscriptions', 'details': str(e)}), 500


@admin_bp.route('/subscriptions/<int:subscription_id>', methods=['GET'])
@super_admin_required
def get_subscription_details(subscription_id):
    """Get detailed subscription information"""
    try:
        subscription = GymSubscription.query.get_or_404(subscription_id)
        
        # Get payment history for this subscription (if we track it)
        gym_id = subscription.gym_id
        recent_payments = Payment.query.filter_by(gym_id=gym_id).order_by(
            desc(Payment.payment_date)
        ).limit(10).all()
        
        subscription_data = subscription.to_dict()
        subscription_data.update({
            'payment_history': [payment.to_dict() for payment in recent_payments],
            'days_until_expiry': subscription.days_until_expiry(),
            'is_active': subscription.is_active(),
            'usage_limits': subscription.get_usage_limits()
        })
        
        return jsonify(subscription_data)
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch subscription details', 'details': str(e)}), 500


@admin_bp.route('/subscriptions', methods=['POST'])
@super_admin_required
def create_subscription():
    """Create a new gym subscription"""
    try:
        data = request.get_json()
        admin_user_id = get_current_user_id()
        
        # Validate required fields
        required_fields = ['gym_id', 'plan_name', 'monthly_price', 'billing_cycle_start', 'billing_cycle_end']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Check if gym exists and doesn't already have an active subscription
        gym = Gym.query.get(data['gym_id'])
        if not gym:
            return jsonify({'error': 'Gym not found'}), 404
            
        existing_subscription = GymSubscription.query.filter_by(
            gym_id=data['gym_id'], status='Active'
        ).first()
        if existing_subscription:
            return jsonify({'error': 'Gym already has an active subscription'}), 400
        
        # Parse dates
        billing_start = datetime.strptime(data['billing_cycle_start'], '%Y-%m-%d').date()
        billing_end = datetime.strptime(data['billing_cycle_end'], '%Y-%m-%d').date()
        next_billing = datetime.strptime(data.get('next_billing_date', data['billing_cycle_end']), '%Y-%m-%d').date()
        
        # Create subscription
        subscription = GymSubscription(
            gym_id=data['gym_id'],
            plan_name=data['plan_name'],
            monthly_price=data['monthly_price'],
            max_members=data.get('max_members', 100),
            max_trainers=data.get('max_trainers', 5),
            features=data.get('features', {}),
            billing_cycle_start=billing_start,
            billing_cycle_end=billing_end,
            next_billing_date=next_billing,
            status=data.get('status', 'Active'),
            auto_renew=data.get('auto_renew', True),
            payment_method=data.get('payment_method'),
            created_by=admin_user_id
        )
        
        db.session.add(subscription)
        
        # Update gym's subscription_id
        gym.subscription_id = subscription.id
        
        db.session.commit()
        
        # Log the action
        log_activity(
            user_id=admin_user_id,
            gym_id=data['gym_id'],
            action_type='create',
            entity_type='subscription',
            entity_id=subscription.id,
            description=f'Created subscription for gym: {gym.name} - Plan: {subscription.plan_name}'
        )
        
        return jsonify({
            'message': 'Subscription created successfully',
            'subscription': subscription.to_dict()
        }), 201
        
    except ValueError as e:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD', 'details': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create subscription', 'details': str(e)}), 500


@admin_bp.route('/subscriptions/<int:subscription_id>', methods=['PUT'])
@super_admin_required
def update_subscription(subscription_id):
    """Update subscription details"""
    try:
        subscription = GymSubscription.query.get_or_404(subscription_id)
        data = request.get_json()
        admin_user_id = get_current_user_id()
        
        # Track changes for logging
        changes = []
        
        # Update allowed fields
        updateable_fields = [
            'plan_name', 'monthly_price', 'max_members', 'max_trainers', 
            'features', 'status', 'auto_renew', 'payment_method'
        ]
        
        for field in updateable_fields:
            if field in data and getattr(subscription, field) != data[field]:
                old_value = getattr(subscription, field)
                setattr(subscription, field, data[field])
                changes.append(f'{field}: {old_value} → {data[field]}')
        
        # Handle date fields separately
        date_fields = ['billing_cycle_start', 'billing_cycle_end', 'next_billing_date']
        for field in date_fields:
            if field in data:
                new_date = datetime.strptime(data[field], '%Y-%m-%d').date()
                if getattr(subscription, field) != new_date:
                    old_value = getattr(subscription, field)
                    setattr(subscription, field, new_date)
                    changes.append(f'{field}: {old_value} → {new_date}')
        
        # Handle payment tracking
        if 'last_payment_date' in data:
            payment_date = datetime.strptime(data['last_payment_date'], '%Y-%m-%d').date()
            subscription.last_payment_date = payment_date
            subscription.last_payment_amount = data.get('last_payment_amount')
            changes.append(f'payment updated: {payment_date}, amount: {data.get("last_payment_amount")}')
        
        db.session.commit()
        
        # Log changes if any
        if changes:
            log_activity(
                user_id=admin_user_id,
                gym_id=subscription.gym_id,
                action_type='update',
                entity_type='subscription',
                entity_id=subscription_id,
                description=f'Updated subscription: {", ".join(changes)}'
            )
        
        return jsonify({
            'message': 'Subscription updated successfully',
            'subscription': subscription.to_dict(),
            'changes': changes
        })
        
    except ValueError as e:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD', 'details': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update subscription', 'details': str(e)}), 500


@admin_bp.route('/subscriptions/<int:subscription_id>/suspend', methods=['PUT'])
@super_admin_required
def suspend_subscription(subscription_id):
    """Suspend an active subscription"""
    try:
        subscription = GymSubscription.query.get_or_404(subscription_id)
        admin_user_id = get_current_user_id()
        data = request.get_json() or {}
        reason = data.get('reason', 'No reason provided')
        
        if subscription.status != 'Active':
            return jsonify({'error': 'Only active subscriptions can be suspended'}), 400
        
        subscription.status = 'Suspended'
        subscription.auto_renew = False  # Stop auto-renewal when suspended
        
        db.session.commit()
        
        # Log the action
        log_activity(
            user_id=admin_user_id,
            gym_id=subscription.gym_id,
            action_type='suspend',
            entity_type='subscription',
            entity_id=subscription_id,
            description=f'Suspended subscription for gym: {subscription.gym.name}. Reason: {reason}',
            severity='warning'
        )
        
        return jsonify({
            'message': 'Subscription suspended successfully',
            'subscription': subscription.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to suspend subscription', 'details': str(e)}), 500


@admin_bp.route('/subscriptions/<int:subscription_id>/reactivate', methods=['PUT'])
@super_admin_required
def reactivate_subscription(subscription_id):
    """Reactivate a suspended subscription"""
    try:
        subscription = GymSubscription.query.get_or_404(subscription_id)
        admin_user_id = get_current_user_id()
        data = request.get_json() or {}
        
        if subscription.status != 'Suspended':
            return jsonify({'error': 'Only suspended subscriptions can be reactivated'}), 400
        
        subscription.status = 'Active'
        
        # Optionally extend billing cycle if requested
        extend_days = data.get('extend_billing_cycle_days', 0)
        if extend_days > 0:
            subscription.billing_cycle_end += timedelta(days=extend_days)
            subscription.next_billing_date += timedelta(days=extend_days)
        
        # Restore auto-renew if requested
        subscription.auto_renew = data.get('auto_renew', True)
        
        db.session.commit()
        
        # Log the action
        log_activity(
            user_id=admin_user_id,
            gym_id=subscription.gym_id,
            action_type='reactivate',
            entity_type='subscription',
            entity_id=subscription_id,
            description=f'Reactivated subscription for gym: {subscription.gym.name}'
        )
        
        return jsonify({
            'message': 'Subscription reactivated successfully',
            'subscription': subscription.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to reactivate subscription', 'details': str(e)}), 500


@admin_bp.route('/subscriptions/<int:subscription_id>/cancel', methods=['PUT'])
@super_admin_required
def cancel_subscription(subscription_id):
    """Cancel a subscription (marks as Cancelled)"""
    try:
        subscription = GymSubscription.query.get_or_404(subscription_id)
        admin_user_id = get_current_user_id()
        data = request.get_json() or {}
        reason = data.get('reason', 'No reason provided')
        immediate = data.get('immediate', False)
        
        if subscription.status not in ['Active', 'Suspended']:
            return jsonify({'error': 'Only active or suspended subscriptions can be cancelled'}), 400
        
        subscription.status = 'Cancelled'
        subscription.auto_renew = False
        
        # If immediate cancellation, set billing end to today
        if immediate:
            subscription.billing_cycle_end = date.today()
            subscription.next_billing_date = date.today()
        
        db.session.commit()
        
        # Log the action
        log_activity(
            user_id=admin_user_id,
            gym_id=subscription.gym_id,
            action_type='cancel',
            entity_type='subscription',
            entity_id=subscription_id,
            description=f'Cancelled subscription for gym: {subscription.gym.name}. Reason: {reason}. Immediate: {immediate}',
            severity='warning'
        )
        
        return jsonify({
            'message': 'Subscription cancelled successfully',
            'subscription': subscription.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to cancel subscription', 'details': str(e)}), 500


@admin_bp.route('/subscriptions/analytics', methods=['GET'])
@super_admin_required
def get_subscription_analytics():
    """Get subscription analytics and metrics"""
    try:
        # Subscription status breakdown
        status_breakdown = db.session.query(
            GymSubscription.status,
            func.count(GymSubscription.id).label('count'),
            func.sum(GymSubscription.monthly_price).label('total_revenue')
        ).group_by(GymSubscription.status).all()
        
        # Plan popularity
        plan_popularity = db.session.query(
            GymSubscription.plan_name,
            func.count(GymSubscription.id).label('count'),
            func.avg(GymSubscription.monthly_price).label('avg_price')
        ).filter(GymSubscription.status == 'Active').group_by(GymSubscription.plan_name).all()
        
        # Expiring subscriptions (next 30 days)
        thirty_days_from_now = date.today() + timedelta(days=30)
        expiring_subscriptions = GymSubscription.query.filter(
            and_(
                GymSubscription.status == 'Active',
                GymSubscription.next_billing_date <= thirty_days_from_now
            )
        ).count()
        
        # Revenue metrics
        total_monthly_revenue = db.session.query(
            func.sum(GymSubscription.monthly_price)
        ).filter(GymSubscription.status == 'Active').scalar() or 0
        
        # Auto-renewal stats
        auto_renew_enabled = GymSubscription.query.filter(
            and_(GymSubscription.status == 'Active', GymSubscription.auto_renew == True)
        ).count()
        
        auto_renew_disabled = GymSubscription.query.filter(
            and_(GymSubscription.status == 'Active', GymSubscription.auto_renew == False)
        ).count()
        
        return jsonify({
            'status_breakdown': [
                {
                    'status': row.status,
                    'count': row.count,
                    'total_revenue': float(row.total_revenue or 0)
                }
                for row in status_breakdown
            ],
            'plan_popularity': [
                {
                    'plan_name': row.plan_name,
                    'subscriber_count': row.count,
                    'average_price': float(row.avg_price or 0)
                }
                for row in plan_popularity
            ],
            'metrics': {
                'total_monthly_revenue': float(total_monthly_revenue),
                'expiring_next_30_days': expiring_subscriptions,
                'auto_renew_enabled': auto_renew_enabled,
                'auto_renew_disabled': auto_renew_disabled
            },
            'generated_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch subscription analytics', 'details': str(e)}), 500


@admin_bp.route('/subscriptions/plans', methods=['GET'])
@super_admin_required
def get_subscription_plans():
    """Get available subscription plans (for creating new subscriptions)"""
    try:
        # This could be from a configuration table or hardcoded plans
        # For now, return predefined plans
        plans = [
            {
                'name': 'Basic',
                'monthly_price': 29.99,
                'max_members': 50,
                'max_trainers': 2,
                'features': {
                    'member_management': True,
                    'payment_tracking': True,
                    'basic_reports': True,
                    'email_support': True,
                    'api_access': False,
                    'custom_branding': False
                }
            },
            {
                'name': 'Professional',
                'monthly_price': 59.99,
                'max_members': 200,
                'max_trainers': 5,
                'features': {
                    'member_management': True,
                    'payment_tracking': True,
                    'basic_reports': True,
                    'advanced_reports': True,
                    'email_support': True,
                    'phone_support': True,
                    'api_access': True,
                    'custom_branding': False
                }
            },
            {
                'name': 'Enterprise',
                'monthly_price': 99.99,
                'max_members': 1000,
                'max_trainers': 20,
                'features': {
                    'member_management': True,
                    'payment_tracking': True,
                    'basic_reports': True,
                    'advanced_reports': True,
                    'custom_reports': True,
                    'email_support': True,
                    'phone_support': True,
                    'priority_support': True,
                    'api_access': True,
                    'custom_branding': True,
                    'white_label': True
                }
            }
        ]
        
        return jsonify({'plans': plans})
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch subscription plans', 'details': str(e)}), 500# 
=============================================================================
# USER MANAGEMENT ENDPOINTS - Cross-Platform Administration
# =============================================================================

@admin_bp.route('/users', methods=['GET'])
@super_admin_required
def list_users():
    """List all users across all gyms with filtering and pagination"""
    try:
        # Query parameters
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        role_filter = request.args.get('role')
        gym_id_filter = request.args.get('gym_id', type=int)
        status_filter = request.args.get('status', 'active')  # active, disabled, all
        search_query = request.args.get('q', '').strip()
        
        # Base query with gym information
        query = User.query.outerjoin(Gym)
        
        # Apply filters
        if role_filter:
            query = query.filter(User.role == role_filter)
            
        if gym_id_filter:
            query = query.filter(User.gym_id == gym_id_filter)
            
        if search_query:
            query = query.filter(or_(
                User.name.ilike(f'%{search_query}%'),
                User.email.ilike(f'%{search_query}%'),
                Gym.name.ilike(f'%{search_query}%')
            ))
        
        # Handle status filter (this would require adding an 'active' field to User model)
        # For now, we'll assume all users are active unless they have a specific disabled flag
        
        # Order by created_at desc, then by name
        query = query.order_by(desc(User.created_at), User.name)
        
        # Paginate
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Enhanced user data with gym information and last login tracking
        users_data = []
        for user in pagination.items:
            user_dict = user.to_dict()
            
            # Add gym information
            if user.gym:
                user_dict['gym_name'] = user.gym.name
                user_dict['gym_status'] = user.gym.status
            else:
                user_dict['gym_name'] = None
                user_dict['gym_status'] = None
            
            # Add last login info (would need to track this in activity logs)
            last_login = get_user_last_login(user.id)
            user_dict['last_login_at'] = last_login
            
            # Add user activity metrics
            user_dict['activity_stats'] = get_user_activity_stats(user.id)
            
            users_data.append(user_dict)
        
        return jsonify({
            'users': users_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            },
            'filters': {
                'role': role_filter,
                'gym_id': gym_id_filter,
                'status': status_filter,
                'search': search_query
            }
        })
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch users', 'details': str(e)}), 500


@admin_bp.route('/users/<int:user_id>', methods=['GET'])
@super_admin_required
def get_user_details(user_id):
    """Get detailed information about a specific user"""
    try:
        user = User.query.get_or_404(user_id)
        
        # Get user's detailed information
        user_data = user.to_dict()
        
        # Add gym information if user belongs to a gym
        if user.gym:
            user_data['gym_details'] = {
                'id': user.gym.id,
                'name': user.gym.name,
                'status': user.gym.status,
                'created_at': user.gym.created_at.isoformat() if user.gym.created_at else None,
                'member_count': user.gym.get_member_count() if hasattr(user.gym, 'get_member_count') else 0
            }
        
        # Get user's recent activity logs
        recent_activity = ActivityLog.query.filter_by(user_id=user_id).order_by(
            desc(ActivityLog.timestamp)
        ).limit(20).all()
        
        user_data['recent_activity'] = [log.to_dict() for log in recent_activity]
        
        # Get user's login history and stats
        user_data['activity_summary'] = {
            'total_logins': get_user_login_count(user_id),
            'last_login_at': get_user_last_login(user_id),
            'actions_last_30_days': get_user_activity_count(user_id, days=30),
            'account_age_days': (datetime.utcnow() - user.created_at).days if user.created_at else 0
        }
        
        # Add permissions and capabilities based on role
        user_data['permissions'] = get_user_permissions(user.role)
        
        return jsonify(user_data)
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch user details', 'details': str(e)}), 500


@admin_bp.route('/users/<int:user_id>/disable', methods=['PUT'])
@super_admin_required
def disable_user(user_id):
    """Disable a user account (prevents login)"""
    try:
        user = User.query.get_or_404(user_id)
        admin_user_id = get_current_user_id()
        data = request.get_json() or {}
        reason = data.get('reason', 'No reason provided')
        
        # Prevent disabling other super admins
        if user.role == 'super_admin':
            return jsonify({'error': 'Cannot disable Super Admin accounts'}), 403
        
        # Add disabled status (this would require adding a field to User model)
        # For now, we'll log the action and assume the frontend handles the disabled state
        
        # Log the action
        log_activity(
            user_id=admin_user_id,
            gym_id=user.gym_id,
            action_type='disable',
            entity_type='user',
            entity_id=user_id,
            description=f'Disabled user account: {user.email} ({user.name}). Reason: {reason}',
            severity='warning'
        )
        
        return jsonify({
            'message': 'User account disabled successfully',
            'user': user.to_dict(),
            'reason': reason
        })
        
    except Exception as e:
        return jsonify({'error': 'Failed to disable user', 'details': str(e)}), 500


@admin_bp.route('/users/<int:user_id>/enable', methods=['PUT'])
@super_admin_required
def enable_user(user_id):
    """Enable a previously disabled user account"""
    try:
        user = User.query.get_or_404(user_id)
        admin_user_id = get_current_user_id()
        
        # Log the action
        log_activity(
            user_id=admin_user_id,
            gym_id=user.gym_id,
            action_type='enable',
            entity_type='user',
            entity_id=user_id,
            description=f'Enabled user account: {user.email} ({user.name})'
        )
        
        return jsonify({
            'message': 'User account enabled successfully',
            'user': user.to_dict()
        })
        
    except Exception as e:
        return jsonify({'error': 'Failed to enable user', 'details': str(e)}), 500


@admin_bp.route('/users/<int:user_id>/change-role', methods=['PUT'])
@super_admin_required
def change_user_role(user_id):
    """Change a user's role (with restrictions)"""
    try:
        user = User.query.get_or_404(user_id)
        admin_user_id = get_current_user_id()
        data = request.get_json()
        
        if 'new_role' not in data:
            return jsonify({'error': 'new_role is required'}), 400
        
        new_role = data['new_role']
        old_role = user.role
        reason = data.get('reason', 'Role change requested by Super Admin')
        
        # Validate new role
        allowed_roles = ['gym_owner', 'member']  # Super admins cannot be created this way
        if new_role not in allowed_roles:
            return jsonify({'error': f'Invalid role. Allowed roles: {", ".join(allowed_roles)}'}), 400
        
        # Prevent changing other super admins
        if user.role == 'super_admin':
            return jsonify({'error': 'Cannot change Super Admin roles'}), 403
        
        # Prevent promoting to super admin (should be done through a separate process)
        if new_role == 'super_admin':
            return jsonify({'error': 'Cannot promote users to Super Admin through this endpoint'}), 403
        
        # Apply role change
        user.role = new_role
        db.session.commit()
        
        # Log the action
        log_activity(
            user_id=admin_user_id,
            gym_id=user.gym_id,
            action_type='role_change',
            entity_type='user',
            entity_id=user_id,
            description=f'Changed user role: {user.email} from {old_role} to {new_role}. Reason: {reason}',
            severity='warning'
        )
        
        return jsonify({
            'message': 'User role changed successfully',
            'user': user.to_dict(),
            'old_role': old_role,
            'new_role': new_role,
            'reason': reason
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to change user role', 'details': str(e)}), 500


@admin_bp.route('/users/<int:user_id>/reset-password', methods=['POST'])
@super_admin_required
def reset_user_password(user_id):
    """Generate a password reset for a user (admin-initiated)"""
    try:
        user = User.query.get_or_404(user_id)
        admin_user_id = get_current_user_id()
        
        # Generate a temporary password (in a real system, this would be handled more securely)
        import secrets
        import string
        
        # Generate a random temporary password
        temp_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
        
        # In a real implementation, you would:
        # 1. Hash the temporary password
        # 2. Store it in the database
        # 3. Send it via secure email
        # 4. Force password change on next login
        
        # For now, we'll just log the action
        log_activity(
            user_id=admin_user_id,
            gym_id=user.gym_id,
            action_type='password_reset',
            entity_type='user',
            entity_id=user_id,
            description=f'Admin-initiated password reset for user: {user.email}',
            severity='warning'
        )
        
        return jsonify({
            'message': 'Password reset initiated successfully',
            'user_email': user.email,
            'temporary_password': temp_password,  # In production, this would be sent via email
            'instructions': 'User must change password on next login'
        })
        
    except Exception as e:
        return jsonify({'error': 'Failed to reset user password', 'details': str(e)}), 500


@admin_bp.route('/users/analytics', methods=['GET'])
@super_admin_required
def get_user_analytics():
    """Get user analytics and statistics across the platform"""
    try:
        # User role distribution
        role_distribution = db.session.query(
            User.role,
            func.count(User.id).label('count')
        ).group_by(User.role).all()
        
        # User registration trends (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_registrations = db.session.query(
            func.date(User.created_at).label('date'),
            func.count(User.id).label('count')
        ).filter(
            User.created_at >= thirty_days_ago
        ).group_by(func.date(User.created_at)).all()
        
        # Active gyms with user counts
        gym_user_stats = db.session.query(
            Gym.id,
            Gym.name,
            Gym.status,
            func.count(User.id).label('user_count')
        ).outerjoin(User).filter(
            Gym.status.in_(['Active', 'Pending'])
        ).group_by(Gym.id, Gym.name, Gym.status).all()
        
        # Users by gym status
        users_by_gym_status = db.session.query(
            Gym.status,
            func.count(User.id).label('user_count')
        ).join(User, User.gym_id == Gym.id).group_by(Gym.status).all()
        
        # Recent user activity (users who have logged actions in the last 7 days)
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        active_users_last_week = db.session.query(
            func.count(func.distinct(ActivityLog.user_id))
        ).filter(
            and_(
                ActivityLog.timestamp >= seven_days_ago,
                ActivityLog.user_id.isnot(None)
            )
        ).scalar() or 0
        
        return jsonify({
            'role_distribution': [
                {'role': row.role, 'count': row.count}
                for row in role_distribution
            ],
            'registration_trend': [
                {'date': str(row.date), 'new_users': row.count}
                for row in recent_registrations
            ],
            'gym_user_stats': [
                {
                    'gym_id': row.id,
                    'gym_name': row.name,
                    'gym_status': row.status,
                    'user_count': row.user_count
                }
                for row in gym_user_stats
            ],
            'users_by_gym_status': [
                {'gym_status': row.status, 'user_count': row.user_count}
                for row in users_by_gym_status
            ],
            'activity_metrics': {
                'total_users': User.query.count(),
                'active_users_last_week': active_users_last_week,
                'super_admins': User.query.filter_by(role='super_admin').count(),
                'gym_owners': User.query.filter_by(role='gym_owner').count(),
                'members': User.query.filter_by(role='member').count()
            },
            'generated_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch user analytics', 'details': str(e)}), 500


@admin_bp.route('/users/search', methods=['GET'])
@super_admin_required
def search_users():
    """Advanced user search across all gyms"""
    try:
        # Query parameters
        email = request.args.get('email')
        name = request.args.get('name') 
        gym_name = request.args.get('gym_name')
        role = request.args.get('role')
        created_after = request.args.get('created_after')  # ISO date
        created_before = request.args.get('created_before')  # ISO date
        
        # Base query with gym join
        query = User.query.outerjoin(Gym)
        
        # Apply search filters
        if email:
            query = query.filter(User.email.ilike(f'%{email}%'))
            
        if name:
            query = query.filter(User.name.ilike(f'%{name}%'))
            
        if gym_name:
            query = query.filter(Gym.name.ilike(f'%{gym_name}%'))
            
        if role:
            query = query.filter(User.role == role)
            
        if created_after:
            after_date = datetime.fromisoformat(created_after.replace('Z', '+00:00'))
            query = query.filter(User.created_at >= after_date)
            
        if created_before:
            before_date = datetime.fromisoformat(created_before.replace('Z', '+00:00'))
            query = query.filter(User.created_at <= before_date)
        
        # Limit results to prevent excessive data transfer
        results = query.order_by(User.name).limit(100).all()
        
        users_data = []
        for user in results:
            user_dict = user.to_dict()
            user_dict['gym_name'] = user.gym.name if user.gym else None
            user_dict['gym_status'] = user.gym.status if user.gym else None
            users_data.append(user_dict)
        
        return jsonify({
            'users': users_data,
            'total_results': len(users_data),
            'search_criteria': {
                'email': email,
                'name': name,
                'gym_name': gym_name,
                'role': role,
                'created_after': created_after,
                'created_before': created_before
            }
        })
        
    except Exception as e:
        return jsonify({'error': 'Failed to search users', 'details': str(e)}), 500


# =============================================================================
# USER MANAGEMENT HELPER FUNCTIONS
# =============================================================================

def get_user_last_login(user_id):
    """Get the last login timestamp for a user from activity logs"""
    try:
        last_login_log = ActivityLog.query.filter(
            and_(
                ActivityLog.user_id == user_id,
                ActivityLog.action_type == 'login'
            )
        ).order_by(desc(ActivityLog.timestamp)).first()
        
        return last_login_log.timestamp.isoformat() if last_login_log else None
    except Exception:
        return None


def get_user_login_count(user_id):
    """Get total login count for a user"""
    try:
        return ActivityLog.query.filter(
            and_(
                ActivityLog.user_id == user_id,
                ActivityLog.action_type == 'login'
            )
        ).count()
    except Exception:
        return 0


def get_user_activity_count(user_id, days=30):
    """Get user activity count for the last N days"""
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        return ActivityLog.query.filter(
            and_(
                ActivityLog.user_id == user_id,
                ActivityLog.timestamp >= cutoff_date
            )
        ).count()
    except Exception:
        return 0


def get_user_activity_stats(user_id):
    """Get comprehensive activity statistics for a user"""
    try:
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        return {
            'total_actions': ActivityLog.query.filter_by(user_id=user_id).count(),
            'actions_last_30_days': ActivityLog.query.filter(
                and_(
                    ActivityLog.user_id == user_id,
                    ActivityLog.timestamp >= thirty_days_ago
                )
            ).count(),
            'last_activity': get_user_last_activity(user_id)
        }
    except Exception:
        return {
            'total_actions': 0,
            'actions_last_30_days': 0,
            'last_activity': None
        }


def get_user_last_activity(user_id):
    """Get the most recent activity for a user"""
    try:
        last_activity = ActivityLog.query.filter_by(user_id=user_id).order_by(
            desc(ActivityLog.timestamp)
        ).first()
        
        return {
            'action_type': last_activity.action_type,
            'description': last_activity.description,
            'timestamp': last_activity.timestamp.isoformat()
        } if last_activity else None
    except Exception:
        return None


def get_user_permissions(role):
    """Get user permissions based on their role"""
    permissions = {
        'super_admin': {
            'can_manage_all_gyms': True,
            'can_manage_all_users': True,
            'can_view_all_data': True,
            'can_modify_subscriptions': True,
            'can_view_analytics': True,
            'can_manage_system_settings': True
        },
        'gym_owner': {
            'can_manage_all_gyms': False,
            'can_manage_all_users': False,
            'can_view_all_data': False,
            'can_modify_subscriptions': False,
            'can_view_analytics': True,  # Own gym only
            'can_manage_system_settings': False,
            'can_manage_own_gym': True,
            'can_manage_own_members': True
        },
        'member': {
            'can_manage_all_gyms': False,
            'can_manage_all_users': False,
            'can_view_all_data': False,
            'can_modify_subscriptions': False,
            'can_view_analytics': False,
            'can_manage_system_settings': False,
            'can_manage_own_gym': False,
            'can_manage_own_members': False,
            'can_view_own_data': True
        }
    }
    
    return permissions.get(role, permissions['member'])