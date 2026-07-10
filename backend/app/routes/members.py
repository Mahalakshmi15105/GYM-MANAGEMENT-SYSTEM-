from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from sqlalchemy import or_
from app.extensions import db, bcrypt
from app.models import Member
from app.activity_logging import ActivityLogger
from datetime import datetime

members_bp = Blueprint('members', __name__)

def get_current_gym_id():
    """Extract gym_id from JWT token for multi-tenant isolation"""
    claims = get_jwt()
    return claims.get('gym_id')

@members_bp.route('', methods=['GET'])
@jwt_required()
def list_members():
    """List all members for the current gym (multi-tenant filtered)"""
    gym_id = get_current_gym_id()
    if not gym_id:
        return jsonify({'error': 'Gym ID not found in token'}), 400
    
    # Get query parameters for filtering and search
    status_filter = request.args.get('status')
    search_query = request.args.get('q', '').strip()
    
    # Base query with multi-tenant isolation
    query = Member.query.filter_by(gym_id=gym_id)
    
    # Apply status filter
    if status_filter and status_filter != 'All':
        query = query.filter(Member.status == status_filter)
    
    # Apply search filter
    if search_query:
        search_pattern = f"%{search_query}%"
        query = query.filter(
            or_(
                Member.first_name.ilike(search_pattern),
                Member.last_name.ilike(search_pattern),
                Member.email.ilike(search_pattern),
                Member.phone.ilike(search_pattern),
                Member.member_id.ilike(search_pattern)
            )
        )
    
    # Order by created date (newest first) and limit for safety
    members = query.order_by(Member.created_at.desc()).limit(100).all()
    
    # Log the view operation
    ActivityLogger.log_view('member', view_type='list', gym_id=gym_id)
    
    return jsonify({
        'members': [member.to_dict() for member in members]
    }), 200

@members_bp.route('', methods=['POST'])
@jwt_required()
def create_member():
    """Create a new member for the current gym"""
    gym_id = get_current_gym_id()
    if not gym_id:
        return jsonify({'error': 'Gym ID not found in token'}), 400
    
    data = request.get_json() or {}
    
    # Required fields validation
    if not data.get('first_name') or not data.get('phone'):
        return jsonify({'error': 'First name and phone are required'}), 400
    
    # Check unique constraints within gym
    if data.get('email'):
        existing_email = Member.query.filter_by(gym_id=gym_id, email=data['email']).first()
        if existing_email:
            return jsonify({'error': 'Email already exists for a member in this gym'}), 400
        
    existing_phone = Member.query.filter_by(gym_id=gym_id, phone=data['phone']).first()
    if existing_phone:
        return jsonify({'error': 'Phone number already exists for a member in this gym'}), 400
    
    try:
        # Parse dates
        start_date = None
        end_date = None
        dob = None
        
        if data.get('membership_start_date'):
            start_date = datetime.strptime(data['membership_start_date'], '%Y-%m-%d').date()
        if data.get('membership_end_date'):
            end_date = datetime.strptime(data['membership_end_date'], '%Y-%m-%d').date()
        if data.get('date_of_birth'):
            dob = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
        
        # Generate unique member_id
        import uuid
        member_id = f"MEM{str(uuid.uuid4())[:8].upper()}"
        
        # Ensure member_id is unique within gym
        while Member.query.filter_by(gym_id=gym_id, member_id=member_id).first():
            member_id = f"MEM{str(uuid.uuid4())[:8].upper()}"
        
        # Hash password if provided
        password_hash = None
        if data.get('password'):
            password_hash = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        
        # Create new member
        new_member = Member(
            gym_id=gym_id,
            member_id=member_id,
            first_name=data['first_name'],
            last_name=data.get('last_name', ''),
            gender=data.get('gender', ''),
            date_of_birth=dob,
            phone=data['phone'],
            email=data.get('email', ''),
            password_hash=password_hash,
            password_changed=False,  # Force first-time password change
            address=data.get('address', ''),
            emergency_contact_name=data.get('emergency_contact_name', ''),
            emergency_contact_phone=data.get('emergency_contact_phone', ''),
            medical_notes=data.get('medical_notes', ''),
            membership_plan_name=data.get('membership_plan_name', ''),
            membership_start_date=start_date,
            membership_end_date=end_date,
            status=data.get('status', 'Active')
        )
        
        db.session.add(new_member)
        db.session.commit()
        
        # Log the create operation
        member_name = f"{new_member.first_name} {new_member.last_name}".strip()
        ActivityLogger.log_create(
            'member', 
            new_member.id, 
            entity_name=member_name,
            gym_id=gym_id,
            extra_data={'phone': new_member.phone, 'email': new_member.email}
        )
        
        return jsonify({
            'message': 'Member created successfully',
            'member': new_member.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to create member: {str(e)}'}), 500


@members_bp.route('/<int:member_id>', methods=['GET'])
@jwt_required()
def get_member(member_id):
    """Get a specific member by ID (multi-tenant filtered)"""
    gym_id = get_current_gym_id()
    if not gym_id:
        return jsonify({'error': 'Gym ID not found in token'}), 400
    
    member = Member.query.filter_by(id=member_id, gym_id=gym_id).first()
    if not member:
        return jsonify({'error': 'Member not found'}), 404
    
    # Log the view operation
    ActivityLogger.log_view('member', entity_id=member_id, gym_id=gym_id)
    
    return jsonify({'member': member.to_dict()}), 200


@members_bp.route('/<int:member_id>', methods=['PUT'])
@jwt_required()
def update_member(member_id):
    """Update a member (multi-tenant filtered)"""
    gym_id = get_current_gym_id()
    if not gym_id:
        return jsonify({'error': 'Gym ID not found in token'}), 400
    
    member = Member.query.filter_by(id=member_id, gym_id=gym_id).first()
    if not member:
        return jsonify({'error': 'Member not found'}), 404
    
    data = request.get_json() or {}
    
    try:
        # Parse dates if provided
        if data.get('date_of_birth'):
            member.date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
        if data.get('membership_start_date'):
            member.membership_start_date = datetime.strptime(data['membership_start_date'], '%Y-%m-%d').date()
        if data.get('membership_end_date'):
            member.membership_end_date = datetime.strptime(data['membership_end_date'], '%Y-%m-%d').date()
        
        # Update allowed fields
        if 'first_name' in data:
            member.first_name = data['first_name']
        if 'last_name' in data:
            member.last_name = data['last_name']
        if 'gender' in data:
            member.gender = data['gender']
        if 'phone' in data:
            # Check unique constraint if phone is being changed
            if data['phone'] != member.phone:
                existing_phone = Member.query.filter_by(gym_id=gym_id, phone=data['phone']).first()
                if existing_phone:
                    return jsonify({'error': 'Phone number already exists for a member in this gym'}), 400
            member.phone = data['phone']
        if 'email' in data:
            # Check unique constraint if email is being changed
            if data['email'] != member.email:
                existing_email = Member.query.filter_by(gym_id=gym_id, email=data['email']).first()
                if existing_email:
                    return jsonify({'error': 'Email already exists for a member in this gym'}), 400
            member.email = data['email']
        if 'address' in data:
            member.address = data['address']
        if 'emergency_contact_name' in data:
            member.emergency_contact_name = data['emergency_contact_name']
        if 'emergency_contact_phone' in data:
            member.emergency_contact_phone = data['emergency_contact_phone']
        if 'medical_notes' in data:
            member.medical_notes = data['medical_notes']
        if 'membership_plan_name' in data:
            member.membership_plan_name = data['membership_plan_name']
        if 'status' in data:
            member.status = data['status']
        
        # Handle password update
        if data.get('password'):
            member.password_hash = bcrypt.generate_password_hash(data['password']).decode('utf-8')
            member.password_changed = True
        
        member.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Log the update operation
        member_name = f"{member.first_name} {member.last_name}".strip()
        ActivityLogger.log_update('member', member_id, entity_name=member_name, gym_id=gym_id)
        
        return jsonify({
            'message': 'Member updated successfully',
            'member': member.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update member: {str(e)}'}), 500


@members_bp.route('/<int:member_id>', methods=['DELETE'])
@jwt_required()
def delete_member(member_id):
    """Delete a member (multi-tenant filtered) - only allowed if no related records exist"""
    from app.models import Attendance, Payment
    
    gym_id = get_current_gym_id()
    if not gym_id:
        return jsonify({'error': 'Gym ID not found in token'}), 400
    
    member = Member.query.filter_by(id=member_id, gym_id=gym_id).first()
    if not member:
        return jsonify({'error': 'Member not found'}), 404
    
    try:
        # Check for related records
        attendance_count = Attendance.query.filter_by(member_id=member_id, gym_id=gym_id).count()
        payment_count = Payment.query.filter_by(member_id=member_id, gym_id=gym_id).count()
        
        if attendance_count > 0 or payment_count > 0:
            return jsonify({
                'error': 'Cannot delete member with historical records',
                'message': f'This member has {attendance_count} attendance records and {payment_count} payment records. Please deactivate the member instead to preserve historical data.'
            }), 400
        
        member_name = f"{member.first_name} {member.last_name}".strip()
        
        db.session.delete(member)
        db.session.commit()
        
        # Log the delete operation
        ActivityLogger.log_delete('member', member_id, entity_name=member_name, gym_id=gym_id)
        
        return jsonify({'message': 'Member deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        # Return user-friendly error message
        return jsonify({
            'error': 'Failed to delete member',
            'message': 'This member cannot be deleted. Please deactivate the member instead to preserve historical data.'
        }), 400


@members_bp.route('/<int:member_id>/deactivate', methods=['POST'])
@jwt_required()
def deactivate_member(member_id):
    """Deactivate a member (multi-tenant filtered) - preserves historical data"""
    gym_id = get_current_gym_id()
    if not gym_id:
        return jsonify({'error': 'Gym ID not found in token'}), 400
    
    member = Member.query.filter_by(id=member_id, gym_id=gym_id).first()
    if not member:
        return jsonify({'error': 'Member not found'}), 404
    
    if member.status == 'Inactive':
        return jsonify({'error': 'Member is already inactive'}), 400
    
    try:
        member.status = 'Inactive'
        member.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Log the deactivate operation (don't fail if logging fails)
        try:
            member_name = f"{member.first_name} {member.last_name}".strip()
            ActivityLogger.log_update(
                'member', 
                member_id, 
                entity_name=member_name, 
                gym_id=gym_id,
                changes={'status': 'Active -> Inactive'}
            )
        except Exception as log_error:
            # Log failure but don't fail the operation
            print(f"Failed to log deactivate operation: {log_error}")
        
        return jsonify({
            'message': 'Member deactivated successfully',
            'member': member.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to deactivate member: {str(e)}'}), 500


@members_bp.route('/<int:member_id>/reactivate', methods=['POST'])
@jwt_required()
def reactivate_member(member_id):
    """Reactivate a previously deactivated member (multi-tenant filtered)"""
    gym_id = get_current_gym_id()
    if not gym_id:
        return jsonify({'error': 'Gym ID not found in token'}), 400
    
    member = Member.query.filter_by(id=member_id, gym_id=gym_id).first()
    if not member:
        return jsonify({'error': 'Member not found'}), 404
    
    if member.status != 'Inactive':
        return jsonify({'error': 'Member is not inactive'}), 400
    
    try:
        member.status = 'Active'
        member.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Log the reactivate operation (don't fail if logging fails)
        try:
            member_name = f"{member.first_name} {member.last_name}".strip()
            ActivityLogger.log_update(
                'member', 
                member_id, 
                entity_name=member_name, 
                gym_id=gym_id,
                changes={'status': 'Inactive -> Active'}
            )
        except Exception as log_error:
            # Log failure but don't fail the operation
            print(f"Failed to log reactivate operation: {log_error}")
        
        return jsonify({
            'message': 'Member reactivated successfully',
            'member': member.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to reactivate member: {str(e)}'}), 500


@members_bp.route('/search', methods=['GET'])
@jwt_required()
def search_members():
    """Search members by name, email, phone, or member_id"""
    gym_id = get_current_gym_id()
    if not gym_id:
        return jsonify({'error': 'Gym ID not found in token'}), 400
    
    query_param = request.args.get('q', '').strip()
    if not query_param:
        return jsonify({'members': []}), 200
    
    search_pattern = f"%{query_param}%"
    members = Member.query.filter_by(gym_id=gym_id).filter(
        or_(
            Member.first_name.ilike(search_pattern),
            Member.last_name.ilike(search_pattern),
            Member.email.ilike(search_pattern),
            Member.phone.ilike(search_pattern),
            Member.member_id.ilike(search_pattern)
        )
    ).order_by(Member.first_name.asc()).limit(20).all()
    
    return jsonify({
        'members': [member.to_dict() for member in members]
    }), 200


@members_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_member():
    """Get current logged-in member's data (for member dashboard)"""
    claims = get_jwt()
    member_id = claims.get('member_id')
    gym_id = claims.get('gym_id')
    
    if not member_id or claims.get('role') != 'member':
        return jsonify({'error': 'Access denied'}), 403
    
    member = Member.query.filter_by(id=member_id, gym_id=gym_id).first()
    if not member:
        return jsonify({'error': 'Member not found'}), 404
    
    from app.models import Attendance, Payment, Gym
    from sqlalchemy import func
    from datetime import date, timedelta
    
    # Get gym info
    gym = Gym.query.get(gym_id)
    
    # Calculate attendance stats
    today = date.today()
    today_attendance = Attendance.query.filter_by(
        member_id=member_id, 
        gym_id=gym_id,
        attendance_date=today
    ).first()
    
    total_visits = Attendance.query.filter_by(member_id=member_id, gym_id=gym_id).count()
    
    # Monthly visits (current month)
    month_start = today.replace(day=1)
    monthly_visits = Attendance.query.filter(
        Attendance.member_id == member_id,
        Attendance.gym_id == gym_id,
        Attendance.attendance_date >= month_start
    ).count()
    
    # Last check-in
    last_attendance = Attendance.query.filter_by(
        member_id=member_id, 
        gym_id=gym_id
    ).order_by(Attendance.check_in_time.desc()).first()
    
    # Attendance history (last 10 records)
    attendance_history = Attendance.query.filter_by(
        member_id=member_id, 
        gym_id=gym_id
    ).order_by(Attendance.check_in_time.desc()).limit(10).all()
    
    # Payment stats
    total_paid = db.session.query(func.sum(Payment.payment_amount)).filter(
        Payment.member_id == member_id,
        Payment.gym_id == gym_id,
        Payment.payment_status == 'Paid'
    ).scalar() or 0
    
    pending_amount = db.session.query(func.sum(Payment.payment_amount)).filter(
        Payment.member_id == member_id,
        Payment.gym_id == gym_id,
        Payment.payment_status == 'Pending'
    ).scalar() or 0
    
    # Last payment
    last_payment = Payment.query.filter_by(
        member_id=member_id,
        gym_id=gym_id,
        payment_status='Paid'
    ).order_by(Payment.payment_date.desc()).first()
    
    # Payment history (last 10 records)
    payment_history = Payment.query.filter_by(
        member_id=member_id,
        gym_id=gym_id
    ).order_by(Payment.payment_date.desc()).limit(10).all()
    
    # Calculate remaining membership days
    remaining_days = None
    if member.membership_end_date:
        remaining_days = (member.membership_end_date - today).days
        if remaining_days < 0:
            remaining_days = 0
    
    return jsonify({
        'member': member.to_dict(),
        'gym': gym.to_dict() if gym else None,
        'attendance': {
            'today_status': today_attendance.status if today_attendance else 'Not Checked In',
            'total_visits': total_visits,
            'monthly_visits': monthly_visits,
            'last_check_in': last_attendance.check_in_time.isoformat() if last_attendance else None,
            'history': [att.to_dict() for att in attendance_history]
        },
        'payments': {
            'total_paid': float(total_paid),
            'pending_amount': float(pending_amount),
            'last_payment': last_payment.to_dict() if last_payment else None,
            'history': [pay.to_dict() for pay in payment_history]
        },
        'membership': {
            'remaining_days': remaining_days,
            'is_expiring_soon': remaining_days is not None and remaining_days <= 7
        }
    }), 200
