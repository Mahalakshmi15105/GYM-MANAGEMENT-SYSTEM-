from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from sqlalchemy import or_, desc
from app.extensions import db
from app.models import Payment, Member, MembershipPlan
from app.activity_logging import ActivityLogger
from app.currency_utils import get_gym_currency
from datetime import datetime
from decimal import Decimal, InvalidOperation
import uuid

payments_bp = Blueprint('payments', __name__)

def get_current_gym_id():
    """Extract gym_id from JWT token for multi-tenant isolation"""
    claims = get_jwt()
    return claims.get('gym_id')

@payments_bp.route('', methods=['GET'])
@jwt_required()
def list_payments():
    """List all payments for the current gym (multi-tenant filtered)"""
    gym_id = get_current_gym_id()
    if not gym_id:
        return jsonify({'error': 'Gym ID not found in token'}), 400
    
    # Get query parameters for filtering and search
    status_filter = request.args.get('status')
    method_filter = request.args.get('method')
    search_query = request.args.get('q', '').strip()
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # Base query with multi-tenant isolation and joins
    query = Payment.query.filter_by(gym_id=gym_id).join(Member, Payment.member_id == Member.id).outerjoin(MembershipPlan, Payment.membership_plan_id == MembershipPlan.id)
    
    # Apply status filter
    if status_filter and status_filter != 'All':
        query = query.filter(Payment.payment_status == status_filter)
    
    # Apply method filter
    if method_filter and method_filter != 'All':
        query = query.filter(Payment.payment_method == method_filter)
    
    # Apply date range filter
    if start_date:
        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d').date()
            query = query.filter(Payment.payment_date >= start_dt)
        except ValueError:
            pass
    
    if end_date:
        try:
            end_dt = datetime.strptime(end_date, '%Y-%m-%d').date()
            query = query.filter(Payment.payment_date <= end_dt)
        except ValueError:
            pass
    
    # Apply search filter
    if search_query:
        search_pattern = f"%{search_query}%"
        query = query.filter(
            or_(
                Member.first_name.ilike(search_pattern),
                Member.last_name.ilike(search_pattern),
                Member.phone.ilike(search_pattern),
                Payment.transaction_id.ilike(search_pattern),
                MembershipPlan.plan_name.ilike(search_pattern)
            )
        )
    
    # Order by payment date (newest first) and limit for safety
    payments = query.order_by(desc(Payment.payment_date), desc(Payment.created_at)).limit(100).all()
    
    # Log the view operation
    ActivityLogger.log_view('payment', view_type='list', gym_id=gym_id)
    
    return jsonify({
        'currency': get_gym_currency(gym_id),
        'payments': [payment.to_dict() for payment in payments]
    }), 200

@payments_bp.route('', methods=['POST'])
@jwt_required()
def create_payment():
    """Create a new payment for the current gym"""
    gym_id = get_current_gym_id()
    if not gym_id:
        return jsonify({'error': 'Gym ID not found in token'}), 400
    
    data = request.get_json() or {}
    
    # Required fields validation
    required_fields = ['member_id', 'payment_amount', 'payment_date', 'payment_method']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field.replace("_", " ").title()} is required'}), 400
    
    # Validate member exists and belongs to this gym
    member = Member.query.filter_by(id=data['member_id'], gym_id=gym_id).first()
    if not member:
        return jsonify({'error': 'Member not found in your gym'}), 400
    
    # Validate membership plan if provided
    membership_plan = None
    if data.get('membership_plan_id'):
        membership_plan = MembershipPlan.query.filter_by(
            id=data['membership_plan_id'], 
            gym_id=gym_id
        ).first()
        if not membership_plan:
            return jsonify({'error': 'Membership plan not found in your gym'}), 400
    
    # Validate payment amount
    try:
        payment_amount = Decimal(str(data['payment_amount']))
        if payment_amount <= 0:
            return jsonify({'error': 'Payment amount must be positive'}), 400
    except (InvalidOperation, ValueError, TypeError):
        return jsonify({'error': 'Payment amount must be a valid number'}), 400
    
    # Validate payment date
    try:
        payment_date = datetime.strptime(data['payment_date'], '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Payment date must be in YYYY-MM-DD format'}), 400
    
    # Validate payment method
    valid_methods = ['Cash', 'UPI', 'Card', 'Bank Transfer']
    if data['payment_method'] not in valid_methods:
        return jsonify({'error': f'Payment method must be one of: {", ".join(valid_methods)}'}), 400
    
    # Validate payment status
    valid_statuses = ['Paid', 'Pending', 'Failed']
    payment_status = data.get('payment_status', 'Paid')
    if payment_status not in valid_statuses:
        return jsonify({'error': f'Payment status must be one of: {", ".join(valid_statuses)}'}), 400
    
    try:
        # Generate transaction ID if not provided
        transaction_id = data.get('transaction_id', '')
        if not transaction_id:
            transaction_id = f"TXN{str(uuid.uuid4())[:8].upper()}"
        
        # Create new payment
        new_payment = Payment(
            gym_id=gym_id,
            member_id=data['member_id'],
            membership_plan_id=data.get('membership_plan_id'),
            payment_amount=payment_amount,
            payment_date=payment_date,
            payment_method=data['payment_method'],
            payment_status=payment_status,
            transaction_id=transaction_id,
            notes=data.get('notes', '')
        )
        
        db.session.add(new_payment)
        db.session.commit()
        
        # Log the create operation
        member_name = f"{member.first_name} {member.last_name}".strip()
        ActivityLogger.log_create(
            'payment',
            new_payment.id,
            entity_name=f"Payment for {member_name}",
            gym_id=gym_id,
            extra_data={
                'amount': float(payment_amount),
                'method': data['payment_method'],
                'status': payment_status,
                'member_name': member_name,
                'transaction_id': transaction_id
            }
        )
        
        return jsonify({
            'message': 'Payment recorded successfully',
            'payment': new_payment.to_dict(),
            'currency': get_gym_currency(gym_id)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to record payment: {str(e)}'}), 500

@payments_bp.route('/<int:payment_id>', methods=['GET'])
@jwt_required()
def get_payment(payment_id):
    """Get payment details by ID (multi-tenant filtered)"""
    gym_id = get_current_gym_id()
    if not gym_id:
        return jsonify({'error': 'Gym ID not found in token'}), 400
    
    payment = Payment.query.filter_by(id=payment_id, gym_id=gym_id).first()
    if not payment:
        return jsonify({'error': 'Payment not found'}), 404
    
    # Log the view operation
    member_name = f"{payment.member.first_name} {payment.member.last_name}".strip() if payment.member else "Unknown Member"
    ActivityLogger.log_view('payment', payment_id, entity_name=f"Payment for {member_name}", gym_id=gym_id)
    
    return jsonify({
        'payment': payment.to_dict(),
        'currency': get_gym_currency(gym_id)
    }), 200

@payments_bp.route('/<int:payment_id>', methods=['PUT'])
@jwt_required()
def update_payment(payment_id):
    """Update payment details (multi-tenant filtered)"""
    gym_id = get_current_gym_id()
    if not gym_id:
        return jsonify({'error': 'Gym ID not found in token'}), 400
    
    payment = Payment.query.filter_by(id=payment_id, gym_id=gym_id).first()
    if not payment:
        return jsonify({'error': 'Payment not found'}), 404
    
    data = request.get_json() or {}
    
    try:
        # Track changes for logging
        changes = {}
        
        # Validate and update payment amount if provided
        if 'payment_amount' in data:
            try:
                payment_amount = Decimal(str(data['payment_amount']))
                if payment_amount <= 0:
                    return jsonify({'error': 'Payment amount must be positive'}), 400
                if payment.payment_amount != payment_amount:
                    changes['payment_amount'] = {'old': float(payment.payment_amount), 'new': float(payment_amount)}
                    payment.payment_amount = payment_amount
            except (InvalidOperation, ValueError, TypeError):
                return jsonify({'error': 'Payment amount must be a valid number'}), 400
        
        # Validate and update payment date if provided
        if 'payment_date' in data:
            try:
                payment_date = datetime.strptime(data['payment_date'], '%Y-%m-%d').date()
                if payment.payment_date != payment_date:
                    changes['payment_date'] = {'old': payment.payment_date.isoformat(), 'new': payment_date.isoformat()}
                    payment.payment_date = payment_date
            except ValueError:
                return jsonify({'error': 'Payment date must be in YYYY-MM-DD format'}), 400
        
        # Validate and update payment method if provided
        if 'payment_method' in data:
            valid_methods = ['Cash', 'UPI', 'Card', 'Bank Transfer']
            if data['payment_method'] not in valid_methods:
                return jsonify({'error': f'Payment method must be one of: {", ".join(valid_methods)}'}), 400
            if payment.payment_method != data['payment_method']:
                changes['payment_method'] = {'old': payment.payment_method, 'new': data['payment_method']}
                payment.payment_method = data['payment_method']
        
        # Validate and update payment status if provided
        if 'payment_status' in data:
            valid_statuses = ['Paid', 'Pending', 'Failed']
            if data['payment_status'] not in valid_statuses:
                return jsonify({'error': f'Payment status must be one of: {", ".join(valid_statuses)}'}), 400
            if payment.payment_status != data['payment_status']:
                changes['payment_status'] = {'old': payment.payment_status, 'new': data['payment_status']}
                payment.payment_status = data['payment_status']
        
        # Update other fields
        for field in ['transaction_id', 'notes']:
            if field in data:
                old_value = getattr(payment, field)
                new_value = data[field]
                if old_value != new_value:
                    changes[field] = {'old': old_value, 'new': new_value}
                    setattr(payment, field, new_value)
        
        payment.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Log the update operation only if there were changes
        if changes:
            member_name = f"{payment.member.first_name} {payment.member.last_name}".strip() if payment.member else "Unknown Member"
            ActivityLogger.log_update(
                'payment',
                payment_id,
                changes=changes,
                entity_name=f"Payment for {member_name}",
                gym_id=gym_id
            )
        
        return jsonify({
            'message': 'Payment updated successfully',
            'payment': payment.to_dict(),
            'currency': get_gym_currency(gym_id)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update payment: {str(e)}'}), 500

@payments_bp.route('/<int:payment_id>', methods=['DELETE'])
@jwt_required()
def delete_payment(payment_id):
    """Delete payment (multi-tenant filtered)"""
    gym_id = get_current_gym_id()
    if not gym_id:
        return jsonify({'error': 'Gym ID not found in token'}), 400
    
    payment = Payment.query.filter_by(id=payment_id, gym_id=gym_id).first()
    if not payment:
        return jsonify({'error': 'Payment not found'}), 404
    
    try:
        # Store payment details for logging before deletion
        member_name = f"{payment.member.first_name} {payment.member.last_name}".strip() if payment.member else "Unknown Member"
        payment_details = {
            'amount': float(payment.payment_amount),
            'transaction_id': payment.transaction_id,
            'member_name': member_name
        }
        
        db.session.delete(payment)
        db.session.commit()
        
        # Log the delete operation (hard delete)
        ActivityLogger.log_delete(
            'payment',
            payment_id,
            entity_name=f"Payment for {member_name}",
            gym_id=gym_id,
            soft_delete=False
        )
        
        return jsonify({'message': 'Payment deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to delete payment: {str(e)}'}), 500

@payments_bp.route('/search', methods=['GET'])
@jwt_required()
def search_payments():
    """Search payments by various criteria (multi-tenant filtered)"""
    gym_id = get_current_gym_id()
    if not gym_id:
        return jsonify({'error': 'Gym ID not found in token'}), 400
    
    query_param = request.args.get('q', '').strip()
    if not query_param:
        return jsonify({'payments': []}), 200
    
    search_pattern = f"%{query_param}%"
    payments = Payment.query.filter_by(gym_id=gym_id).join(Member).outerjoin(MembershipPlan).filter(
        or_(
            Member.first_name.ilike(search_pattern),
            Member.last_name.ilike(search_pattern),
            Member.phone.ilike(search_pattern),
            Payment.transaction_id.ilike(search_pattern),
            MembershipPlan.plan_name.ilike(search_pattern)
        )
    ).order_by(desc(Payment.payment_date)).limit(20).all()
    
    # Log the search operation
    ActivityLogger.log_activity(
        'search',
        f"Searched payments for '{query_param}'",
        entity_type='payment',
        gym_id=gym_id,
        extra_data={'search_query': query_param, 'results_count': len(payments)}
    )
    
    return jsonify({
        'currency': get_gym_currency(gym_id),
        'payments': [payment.to_dict() for payment in payments]
    }), 200

@payments_bp.route('/members', methods=['GET'])
@jwt_required()
def get_members_for_payment():
    """Get all active members for payment dropdown (multi-tenant filtered)"""
    gym_id = get_current_gym_id()
    if not gym_id:
        return jsonify({'error': 'Gym ID not found in token'}), 400
    
    members = Member.query.filter_by(gym_id=gym_id, status='Active').order_by(Member.first_name.asc()).all()
    
    return jsonify({
        'currency': get_gym_currency(gym_id),
        'members': [{
            'id': member.id,
            'name': f"{member.first_name} {member.last_name}",
            'phone': member.phone,
            'membership_plan_name': member.membership_plan_name
        } for member in members]
    }), 200

@payments_bp.route('/membership-plans', methods=['GET'])
@jwt_required()
def get_membership_plans_for_payment():
    """Get all active membership plans for payment dropdown (multi-tenant filtered)"""
    gym_id = get_current_gym_id()
    if not gym_id:
        return jsonify({'error': 'Gym ID not found in token'}), 400
    
    plans = MembershipPlan.query.filter_by(gym_id=gym_id, status='Active').order_by(MembershipPlan.plan_name.asc()).all()
    
    return jsonify({
        'currency': get_gym_currency(gym_id),
        'membership_plans': [{
            'id': plan.id,
            'plan_name': plan.plan_name,
            'price': float(plan.price),
            'duration': plan.duration
        } for plan in plans]
    }), 200

@payments_bp.route('/receipt/<int:payment_id>', methods=['GET'])
@jwt_required()
def generate_receipt(payment_id):
    """Generate payment receipt data (multi-tenant filtered)"""
    gym_id = get_current_gym_id()
    if not gym_id:
        return jsonify({'error': 'Gym ID not found in token'}), 400
    
    payment = Payment.query.filter_by(id=payment_id, gym_id=gym_id).first()
    if not payment:
        return jsonify({'error': 'Payment not found'}), 404
    
    receipt_data = {
        'receipt_number': f"RCP{payment.id:06d}",
        'payment': payment.to_dict(),
        'gym_name': payment.gym.name if payment.gym else 'FlexiGym',
        'currency': get_gym_currency(gym_id),
        'generated_at': datetime.utcnow().isoformat()
    }
    
    # Log the receipt generation
    member_name = f"{payment.member.first_name} {payment.member.last_name}".strip() if payment.member else "Unknown Member"
    ActivityLogger.log_activity(
        'export',
        f"Generated payment receipt for {member_name}",
        entity_type='payment',
        entity_id=payment_id,
        gym_id=gym_id,
        extra_data={'receipt_number': receipt_data['receipt_number'], 'export_format': 'json'}
    )
    
    return jsonify(receipt_data), 200