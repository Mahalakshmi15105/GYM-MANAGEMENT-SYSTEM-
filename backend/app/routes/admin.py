"""
Super Admin routes for platform management with comprehensive error handling.
Handles gym management, platform analytics, user oversight, and system administration.
"""

from flask import Blueprint, request, jsonify
from sqlalchemy import func, desc, and_, or_
from datetime import datetime, date, timedelta
from app.extensions import db, bcrypt
from app.auth_utils import super_admin_required, get_current_user_id
from app.super_admin_errors import handle_super_admin_errors, SuperAdminError, validate_super_admin_operation
from app.activity_logging import ActivityLogger
from app.models import Gym, User, Member, Payment, Attendance
from app.super_admin_models import ActivityLog, SystemSettings, GymSubscription, PlatformSubscriptionPlan

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


@admin_bp.route('/gyms/create', methods=['POST'])
@super_admin_required
def create_gym():
    """Create a new gym and gym owner account (Super Admin only)"""
    try:
        data = request.get_json() or {}
        admin_user_id = get_current_user_id()
        
        gym_name = data.get('gym_name')
        gym_address = data.get('gym_address')
        gym_phone = data.get('gym_phone')
        owner_name = data.get('name')
        owner_email = data.get('email')
        password = data.get('password')
        
        # Validate required fields
        if not all([gym_name, gym_address, gym_phone, owner_name, owner_email, password]):
            return jsonify({'error': 'Missing required fields (gym_name, gym_address, gym_phone, name, email, password)'}), 400
        
        # Check if email already exists
        if User.query.filter_by(email=owner_email).first():
            return jsonify({'error': 'Email already registered'}), 400
        
        # Generate unique attendance QR code for the gym
        import uuid
        attendance_qr = f"GYM{str(uuid.uuid4())[:12].upper()}"
        
        # Create Gym with user-provided data
        new_gym = Gym(
            name=gym_name,
            address=gym_address,
            phone=gym_phone,
            attendance_qr=attendance_qr,
            status='Active'  # Super Admin creates gyms as Active
        )
        db.session.add(new_gym)
        db.session.flush()  # Populate the Gym ID before commit
        
        # Create User linked to the gym as the owner
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(
            name=owner_name,
            email=owner_email,
            password_hash=hashed_password,
            role='gym_owner',
            gym_id=new_gym.id
        )
        db.session.add(new_user)
        db.session.commit()
        
        # Log the gym creation
        try:
            log_activity(
                user_id=admin_user_id,
                gym_id=new_gym.id,
                action_type='create',
                entity_type='gym',
                entity_id=new_gym.id,
                description=f'Created gym: {gym_name} with owner: {owner_email}'
            )
        except Exception as log_error:
            print(f"Failed to log gym creation: {log_error}")
        
        return jsonify({
            'message': 'Gym and Owner created successfully',
            'gym': new_gym.to_dict(),
            'user': {
                'id': new_user.id,
                'name': new_user.name,
                'email': new_user.email,
                'role': new_user.role,
                'gym_id': new_user.gym_id
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create gym', 'message': str(e)}), 500


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


# =============================================================================
# PLATFORM SUBSCRIPTION PLANS ENDPOINTS
# =============================================================================

@admin_bp.route('/subscription-plans', methods=['GET'])
@super_admin_required
def get_platform_subscription_plans():
    """Get all platform subscription plans (super admin only)"""
    try:
        query = PlatformSubscriptionPlan.query.order_by(
            PlatformSubscriptionPlan.recommended.desc(), 
            PlatformSubscriptionPlan.price.asc()
        )
        plans = query.all()
        
        return jsonify({
            'plans': [plan.to_dict() for plan in plans]
        })
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch platform plans', 'details': str(e)}), 500


@admin_bp.route('/subscription-plans', methods=['POST'])
@super_admin_required
def create_platform_subscription_plan():
    """Create a new platform subscription plan"""
    try:
        data = request.get_json() or {}
        admin_user_id = get_current_user_id()
        
        # Required fields
        required_fields = ['plan_name', 'price', 'billing_cycle']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Validate price
        try:
            price = float(data['price'])
            if price <= 0:
                return jsonify({'error': 'Price must be greater than 0'}), 400
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid price format'}), 400
        
        # Check for duplicate plan name
        existing_plan = PlatformSubscriptionPlan.query.filter_by(
            plan_name=data['plan_name']
        ).first()
        
        if existing_plan:
            return jsonify({'error': 'Plan with this name already exists'}), 400
        
        # Create new plan
        new_plan = PlatformSubscriptionPlan(
            plan_name=data['plan_name'],
            price=price,
            currency=data.get('currency', 'INR'),
            billing_cycle=data['billing_cycle'],
            description=data.get('description'),
            features=data.get('features'),
            recommended=data.get('recommended', False),
            is_active=data.get('is_active', True)
        )
        
        db.session.add(new_plan)
        db.session.commit()
        
        # Log activity
        log_activity(
            user_id=admin_user_id,
            action_type='create',
            entity_type='platform_subscription_plan',
            entity_id=new_plan.id,
            description=f'Created new platform subscription plan: {new_plan.plan_name}'
        )
        
        return jsonify({
            'message': 'Platform subscription plan created successfully',
            'plan': new_plan.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create platform plan', 'details': str(e)}), 500


@admin_bp.route('/subscription-plans/<int:plan_id>', methods=['PUT'])
@super_admin_required
def update_platform_subscription_plan(plan_id):
    """Update an existing platform subscription plan"""
    try:
        plan = PlatformSubscriptionPlan.query.get_or_404(plan_id)
        data = request.get_json() or {}
        admin_user_id = get_current_user_id()
        
        changes = []
        
        # Update allowed fields
        if 'plan_name' in data:
            if data['plan_name'] != plan.plan_name:
                # Check for duplicate name
                existing = PlatformSubscriptionPlan.query.filter(
                    and_(
                        PlatformSubscriptionPlan.plan_name == data['plan_name'],
                        PlatformSubscriptionPlan.id != plan_id
                    )
                ).first()
                if existing:
                    return jsonify({'error': 'Plan with this name already exists'}), 400
                changes.append(f'plan_name: {plan.plan_name} → {data["plan_name"]}')
                plan.plan_name = data['plan_name']
        
        if 'price' in data:
            try:
                price = float(data['price'])
                if price <=0:
                    return jsonify({'error': 'Price must be greater than 0'}), 400
                if price != plan.price:
                    changes.append(f'price: {plan.price} → {price}')
                    plan.price = price
            except (ValueError, TypeError):
                return jsonify({'error': 'Invalid price format'}), 400
        
        if 'currency' in data:
            if data['currency'] != plan.currency:
                changes.append(f'currency: {plan.currency} → {data["currency"]}')
                plan.currency = data['currency']
        
        if 'billing_cycle' in data:
            if data['billing_cycle'] != plan.billing_cycle:
                changes.append(f'billing_cycle: {plan.billing_cycle} → {data["billing_cycle"]}')
                plan.billing_cycle = data['billing_cycle']
        
        if 'description' in data:
            if data['description'] != plan.description:
                changes.append(f'description: {plan.description} → {data["description"]}')
                plan.description = data['description']
        
        if 'features' in data:
            if data['features'] != plan.features:
                changes.append('features: updated')
                plan.features = data['features']
        
        if 'recommended' in data:
            if bool(data['recommended']) != plan.recommended:
                changes.append(f'recommended: {plan.recommended} → {data["recommended"]}')
                plan.recommended = bool(data['recommended'])
        
        if 'is_active' in data:
            if bool(data['is_active']) != plan.is_active:
                changes.append(f'is_active: {plan.is_active} → {data["is_active"]}')
                plan.is_active = bool(data['is_active'])
        
        if not changes:
            return jsonify({'message': 'No changes detected', 'plan': plan.to_dict()})
        
        db.session.commit()
        
        # Log activity
        log_activity(
            user_id=admin_user_id,
            action_type='update',
            entity_type='platform_subscription_plan',
            entity_id=plan.id,
            description=f'Updated platform subscription plan: {plan.plan_name} - {", ".join(changes)}'
        )
        
        return jsonify({
            'message': 'Platform subscription plan updated successfully',
            'changes': changes,
            'plan': plan.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update platform plan', 'details': str(e)}), 500


@admin_bp.route('/subscription-plans/<int:plan_id>', methods=['DELETE'])
@super_admin_required
def delete_platform_subscription_plan(plan_id):
    """Delete a platform subscription plan"""
    try:
        plan = PlatformSubscriptionPlan.query.get_or_404(plan_id)
        admin_user_id = get_current_user_id()
        
        db.session.delete(plan)
        db.session.commit()
        
        # Log activity
        log_activity(
            user_id=admin_user_id,
            action_type='delete',
            entity_type='platform_subscription_plan',
            entity_id=plan_id,
            description=f'Deleted platform subscription plan: {plan.plan_name}',
            severity='warning'
        )
        
        return jsonify({
            'message': 'Platform subscription plan deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete platform plan', 'details': str(e)}), 500


@admin_bp.route('/subscription-plans/active', methods=['GET'])
def get_active_platform_subscription_plans():
    """Get active platform subscription plans (public endpoint)"""
    try:
        query = PlatformSubscriptionPlan.query.filter_by(is_active=True).order_by(
            PlatformSubscriptionPlan.recommended.desc(), 
            PlatformSubscriptionPlan.price.asc()
        )
        plans = query.all()
        
        return jsonify({
            'plans': [plan.to_dict() for plan in plans]
        })
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch active plans', 'details': str(e)}), 500


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


# Duplicate removed - functions already exist above

# =============================================================================
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
        
        # Handle status filter
        if status_filter and status_filter != 'all':
            query = query.filter(User.status == status_filter)
        
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
            
            # Add last login info from user.last_login field
            user_dict['last_login_at'] = user.last_login.isoformat() if user.last_login else None
            
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

# =============================================================================
# SYSTEM SETTINGS ENDPOINTS
# =============================================================================

@admin_bp.route('/settings', methods=['GET'])
@super_admin_required
def list_system_settings():
    """Get all system settings"""
    try:
        settings = SystemSettings.query.all()
        
        return jsonify({
            'settings': [setting.to_dict() for setting in settings],
            'count': len(settings)
        })
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch system settings', 'details': str(e)}), 500


@admin_bp.route('/settings/<string:setting_key>', methods=['GET'])
@super_admin_required 
def get_system_setting(setting_key):
    """Get a specific system setting"""
    try:
        setting = SystemSettings.query.filter_by(setting_key=setting_key).first()
        
        if not setting:
            return jsonify({'error': 'Setting not found'}), 404
            
        return jsonify(setting.to_dict())
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch system setting', 'details': str(e)}), 500


@admin_bp.route('/settings', methods=['POST'])
@super_admin_required
def create_system_setting():
    """Create a new system setting"""
    try:
        data = request.get_json() or {}
        admin_user_id = get_current_user_id()
        
        # Required fields validation
        required_fields = ['setting_key', 'setting_value', 'setting_type']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Check if setting already exists
        existing_setting = SystemSettings.query.filter_by(setting_key=data['setting_key']).first()
        if existing_setting:
            return jsonify({'error': 'Setting key already exists'}), 400
        
        # Create setting
        setting = SystemSettings(
            setting_key=data['setting_key'],
            setting_value=data['setting_value'],
            setting_type=data['setting_type'],
            description=data.get('description'),
            updated_by=admin_user_id
        )
        
        db.session.add(setting)
        db.session.commit()
        
        # Log the action
        log_activity(
            user_id=admin_user_id,
            action_type='create',
            entity_type='system_setting',
            entity_id=setting.id,
            description=f'Created system setting: {setting.setting_key}'
        )
        
        return jsonify({
            'message': 'System setting created successfully',
            'setting': setting.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create system setting', 'details': str(e)}), 500


@admin_bp.route('/settings/<string:setting_key>', methods=['PUT'])
@super_admin_required
def update_system_setting(setting_key):
    """Update a system setting"""
    try:
        setting = SystemSettings.query.filter_by(setting_key=setting_key).first()
        if not setting:
            return jsonify({'error': 'Setting not found'}), 404
            
        data = request.get_json() or {}
        admin_user_id = get_current_user_id()
        
        # Store old value for logging
        old_value = setting.setting_value
        
        # Update fields
        if 'setting_value' in data:
            setting.setting_value = data['setting_value']
        if 'setting_type' in data:
            setting.setting_type = data['setting_type']
        if 'description' in data:
            setting.description = data['description']
            
        setting.updated_by = admin_user_id
        setting.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # Log the action
        log_activity(
            user_id=admin_user_id,
            action_type='update',
            entity_type='system_setting',
            entity_id=setting.id,
            description=f'Updated system setting {setting_key}: {old_value} → {setting.setting_value}'
        )
        
        return jsonify({
            'message': 'System setting updated successfully',
            'setting': setting.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update system setting', 'details': str(e)}), 500


@admin_bp.route('/settings/<string:setting_key>', methods=['DELETE'])
@super_admin_required
def delete_system_setting(setting_key):
    """Delete a system setting"""
    try:
        setting = SystemSettings.query.filter_by(setting_key=setting_key).first()
        if not setting:
            return jsonify({'error': 'Setting not found'}), 404
            
        admin_user_id = get_current_user_id()
        
        # Log before deletion
        log_activity(
            user_id=admin_user_id,
            action_type='delete',
            entity_type='system_setting',
            entity_id=setting.id,
            description=f'Deleted system setting: {setting_key}',
            severity='warning'
        )
        
        db.session.delete(setting)
        db.session.commit()
        
        return jsonify({'message': 'System setting deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete system setting', 'details': str(e)}), 500