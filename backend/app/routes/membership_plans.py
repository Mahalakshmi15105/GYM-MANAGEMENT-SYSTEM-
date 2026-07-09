from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from sqlalchemy import or_
from app.extensions import db
from app.models import MembershipPlan
from app.activity_logging import ActivityLogger
from app.currency_utils import get_gym_currency
from datetime import datetime
from decimal import Decimal, InvalidOperation

membership_plans_bp = Blueprint('membership_plans', __name__)

def get_current_gym_id():
    """Extract gym_id from JWT token for multi-tenant isolation"""
    claims = get_jwt()
    return claims.get('gym_id')

@membership_plans_bp.route('', methods=['GET'])
@jwt_required()
def list_membership_plans():
    """List all membership plans for the current gym (multi-tenant filtered)"""
    gym_id = get_current_gym_id()
    if not gym_id:
        return jsonify({'error': 'Gym ID not found in token'}), 400
    
    # Get query parameters for filtering and search
    status_filter = request.args.get('status')
    search_query = request.args.get('q', '').strip()
    
    # Base query with multi-tenant isolation
    query = MembershipPlan.query.filter_by(gym_id=gym_id)
    
    # Apply status filter
    if status_filter and status_filter != 'All':
        query = query.filter(MembershipPlan.status == status_filter)
    
    # Apply search filter
    if search_query:
        search_pattern = f"%{search_query}%"
        query = query.filter(
            or_(
                MembershipPlan.plan_name.ilike(search_pattern),
                MembershipPlan.description.ilike(search_pattern)
            )
        )
    
    # Order by created date (newest first) and limit for safety
    plans = query.order_by(MembershipPlan.created_at.desc()).limit(100).all()
    
    # Log the view operation
    ActivityLogger.log_view('membership_plan', view_type='list', gym_id=gym_id)
    
    return jsonify({
        'membership_plans': [plan.to_dict() for plan in plans]
    }), 200

@membership_plans_bp.route('', methods=['POST'])
@jwt_required()
def create_membership_plan():
    """Create a new membership plan for the current gym"""
    gym_id = get_current_gym_id()
    if not gym_id:
        return jsonify({'error': 'Gym ID not found in token'}), 400
    
    data = request.get_json() or {}
    
    # Required fields validation
    if not data.get('plan_name') or not data.get('duration') or not data.get('price'):
        return jsonify({'error': 'Plan name, duration, and price are required'}), 400
    
    # Validate duration
    try:
        duration = int(data['duration'])
        if duration <= 0:
            return jsonify({'error': 'Duration must be a positive number'}), 400
    except (ValueError, TypeError):
        return jsonify({'error': 'Duration must be a valid number'}), 400
    
    # Validate price
    try:
        price = Decimal(str(data['price']))
        if price < 0:
            return jsonify({'error': 'Price cannot be negative'}), 400
    except (InvalidOperation, ValueError, TypeError):
        return jsonify({'error': 'Price must be a valid number'}), 400
    
    # Check unique constraint within gym
    existing_plan = MembershipPlan.query.filter_by(
        gym_id=gym_id, 
        plan_name=data['plan_name']
    ).first()
    if existing_plan:
        return jsonify({'error': 'A plan with this name already exists in your gym'}), 400
    
    try:
        # Create new membership plan
        new_plan = MembershipPlan(
            gym_id=gym_id,
            plan_name=data['plan_name'],
            duration=duration,
            price=price,
            description=data.get('description', ''),
            status=data.get('status', 'Active')
        )
        
        db.session.add(new_plan)
        db.session.commit()
        
        # Log the create operation
        ActivityLogger.log_create(
            'membership_plan',
            new_plan.id,
            entity_name=new_plan.plan_name,
            gym_id=gym_id,
            extra_data={
                'duration': duration,
                'price': float(price),
                'status': new_plan.status
            }
        )
        
        return jsonify({
            'message': 'Membership plan created successfully',
            'membership_plan': new_plan.to_dict(),
            'currency': get_gym_currency(gym_id)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to create membership plan: {str(e)}'}), 500

@membership_plans_bp.route('/<int:plan_id>', methods=['GET'])
@jwt_required()
def get_membership_plan(plan_id):
    """Get membership plan details by ID (multi-tenant filtered)"""
    gym_id = get_current_gym_id()
    if not gym_id:
        return jsonify({'error': 'Gym ID not found in token'}), 400
    
    plan = MembershipPlan.query.filter_by(id=plan_id, gym_id=gym_id).first()
    if not plan:
        return jsonify({'error': 'Membership plan not found'}), 404
    
    # Log the view operation
    ActivityLogger.log_view('membership_plan', plan_id, entity_name=plan.plan_name, gym_id=gym_id)
    
    return jsonify({
        'membership_plan': plan.to_dict(),
        'currency': get_gym_currency(gym_id)
    }), 200

@membership_plans_bp.route('/<int:plan_id>', methods=['PUT'])
@jwt_required()
def update_membership_plan(plan_id):
    """Update membership plan details (multi-tenant filtered)"""
    gym_id = get_current_gym_id()
    if not gym_id:
        return jsonify({'error': 'Gym ID not found in token'}), 400
    
    plan = MembershipPlan.query.filter_by(id=plan_id, gym_id=gym_id).first()
    if not plan:
        return jsonify({'error': 'Membership plan not found'}), 404
    
    data = request.get_json() or {}
    
    try:
        # Track changes for logging
        changes = {}
        
        # Validate and update duration if provided
        if 'duration' in data:
            try:
                duration = int(data['duration'])
                if duration <= 0:
                    return jsonify({'error': 'Duration must be a positive number'}), 400
                if plan.duration != duration:
                    changes['duration'] = {'old': plan.duration, 'new': duration}
                    plan.duration = duration
            except (ValueError, TypeError):
                return jsonify({'error': 'Duration must be a valid number'}), 400
        
        # Validate and update price if provided
        if 'price' in data:
            try:
                price = Decimal(str(data['price']))
                if price < 0:
                    return jsonify({'error': 'Price cannot be negative'}), 400
                if plan.price != price:
                    changes['price'] = {'old': float(plan.price), 'new': float(price)}
                    plan.price = price
            except (InvalidOperation, ValueError, TypeError):
                return jsonify({'error': 'Price must be a valid number'}), 400
        
        # Update basic fields
        for field in ['plan_name', 'description', 'status']:
            if field in data:
                old_value = getattr(plan, field)
                new_value = data[field]
                if old_value != new_value:
                    changes[field] = {'old': old_value, 'new': new_value}
                    setattr(plan, field, new_value)
        
        plan.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Log the update operation only if there were changes
        if changes:
            ActivityLogger.log_update(
                'membership_plan',
                plan_id,
                changes=changes,
                entity_name=plan.plan_name,
                gym_id=gym_id
            )
        
        return jsonify({
            'message': 'Membership plan updated successfully',
            'membership_plan': plan.to_dict(),
            'currency': get_gym_currency(gym_id)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update membership plan: {str(e)}'}), 500

@membership_plans_bp.route('/<int:plan_id>', methods=['DELETE'])
@jwt_required()
def delete_membership_plan(plan_id):
    """Delete membership plan (multi-tenant filtered)"""
    gym_id = get_current_gym_id()
    if not gym_id:
        return jsonify({'error': 'Gym ID not found in token'}), 400
    
    plan = MembershipPlan.query.filter_by(id=plan_id, gym_id=gym_id).first()
    if not plan:
        return jsonify({'error': 'Membership plan not found'}), 404
    
    try:
        # Store plan name for logging before deletion
        plan_name = plan.plan_name
        
        db.session.delete(plan)
        db.session.commit()
        
        # Log the delete operation (hard delete)
        ActivityLogger.log_delete(
            'membership_plan',
            plan_id,
            entity_name=plan_name,
            gym_id=gym_id,
            soft_delete=False
        )
        
        return jsonify({'message': 'Membership plan deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to delete membership plan: {str(e)}'}), 500

@membership_plans_bp.route('/search', methods=['GET'])
@jwt_required()
def search_membership_plans():
    """Search membership plans by various criteria (multi-tenant filtered)"""
    gym_id = get_current_gym_id()
    if not gym_id:
        return jsonify({'error': 'Gym ID not found in token'}), 400
    
    query_param = request.args.get('q', '').strip()
    if not query_param:
        return jsonify({'membership_plans': []}), 200
    
    search_pattern = f"%{query_param}%"
    plans = MembershipPlan.query.filter_by(gym_id=gym_id).filter(
        or_(
            MembershipPlan.plan_name.ilike(search_pattern),
            MembershipPlan.description.ilike(search_pattern)
        )
    ).order_by(MembershipPlan.plan_name.asc()).limit(20).all()
    
    # Log the search operation
    ActivityLogger.log_activity(
        'search',
        f"Searched membership plans for '{query_param}'",
        entity_type='membership_plan',
        gym_id=gym_id,
        extra_data={'search_query': query_param, 'results_count': len(plans)}
    )
    
    return jsonify({
        'currency': get_gym_currency(gym_id),
        'membership_plans': [plan.to_dict() for plan in plans]
    }), 200