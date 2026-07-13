"""
Gym Settings routes for gym owners to manage their gym settings including currency and language
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from app.extensions import db
from app.models import Gym
from app.activity_logging import ActivityLogger

gym_settings_bp = Blueprint('gym_settings', __name__)


def get_current_gym_id():
    """Extract gym_id from JWT token"""
    claims = get_jwt()
    return claims.get('gym_id')


@gym_settings_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_gym_profile():
    """Get current gym profile including currency and language"""
    gym_id = get_current_gym_id()
    if not gym_id:
        return jsonify({'error': 'Gym ID not found in token'}), 400
    
    gym = Gym.query.get(gym_id)
    if not gym:
        return jsonify({'error': 'Gym not found'}), 404
    
    # Build logo URL if logo exists
    logo_url = None
    has_logo = False
    if gym.logo:
        logo_url = f"/static/{gym.logo}"
        has_logo = True
    
    return jsonify({
        'gym': gym.to_dict(),
        'logo_url': logo_url,
        'has_logo': has_logo
    }), 200


@gym_settings_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_gym_profile():
    """Update gym profile including currency and language"""
    gym_id = get_current_gym_id()
    if not gym_id:
        return jsonify({'error': 'Gym ID not found in token'}), 400
    
    gym = Gym.query.get(gym_id)
    if not gym:
        return jsonify({'error': 'Gym not found'}), 404
    
    data = request.get_json() or {}
    changes = []
    
    # Supported languages
    SUPPORTED_LANGUAGES = ['en', 'ta', 'hi', 'ja', 'fr', 'de', 'es', 'ar', 'zh', 'ko', 'pt', 'it', 'ru']
    
    # Update allowed fields
    if 'name' in data and data['name'] != gym.name:
        old_name = gym.name
        gym.name = data['name']
        changes.append(f"name: {old_name} → {data['name']}")
    
    if 'address' in data and data['address'] != gym.address:
        gym.address = data['address']
        changes.append("address updated")
    
    if 'phone' in data and data['phone'] != gym.phone:
        gym.phone = data['phone']
        changes.append("phone updated")
    
    if 'currency' in data and data['currency'] != gym.currency:
        old_currency = gym.currency or 'INR'
        new_currency = data['currency'].upper()
        gym.currency = new_currency
        changes.append(f"currency: {old_currency} → {new_currency}")
    
    if 'language' in data and data['language'] != gym.language:
        new_language = data['language'].lower()
        if new_language in SUPPORTED_LANGUAGES:
            old_language = gym.language or 'en'
            gym.language = new_language
            changes.append(f"language: {old_language} → {new_language}")
        else:
            return jsonify({'error': f'Language {new_language} is not supported'}), 400
    
    if 'show_gym_status' in data and data['show_gym_status'] != gym.show_gym_status:
        old_status = gym.show_gym_status
        gym.show_gym_status = bool(data['show_gym_status'])
        changes.append(f"show_gym_status: {old_status} → {gym.show_gym_status}")
    
    if changes:
        db.session.commit()
        
        # Log the activity
        ActivityLogger.log_activity(
            'update',
            f"Updated gym profile: {', '.join(changes)}",
            entity_type='gym',
            entity_id=gym_id,
            gym_id=gym_id
        )
        
        return jsonify({
            'message': 'Gym profile updated successfully',
            'gym': gym.to_dict(),
            'changes': changes
        }), 200
    
    return jsonify({
        'message': 'No changes detected',
        'gym': gym.to_dict()
    }), 200


@gym_settings_bp.route('/status', methods=['GET'])
@jwt_required()
def get_gym_status():
    """Get gym operational status and display preference"""
    gym_id = get_current_gym_id()
    if not gym_id:
        return jsonify({'error': 'Gym ID not found in token'}), 400
    
    gym = Gym.query.get(gym_id)
    if not gym:
        return jsonify({'error': 'Gym not found'}), 404
    
    return jsonify({
        'operational_status': gym.operational_status,
        'show_gym_status': gym.show_gym_status
    }), 200


@gym_settings_bp.route('/status', methods=['PUT'])
@jwt_required()
def update_gym_status():
    """Update gym operational status (Open/Closed)"""
    gym_id = get_current_gym_id()
    if not gym_id:
        return jsonify({'error': 'Gym ID not found in token'}), 400
    
    gym = Gym.query.get(gym_id)
    if not gym:
        return jsonify({'error': 'Gym not found'}), 404
    
    data = request.get_json() or {}
    operational_status = data.get('operational_status')
    
    if operational_status not in ['Open', 'Closed']:
        return jsonify({'error': 'operational_status must be either "Open" or "Closed"'}), 400
    
    old_status = gym.operational_status
    gym.operational_status = operational_status
    db.session.commit()
    
    # Log the activity
    ActivityLogger.log_activity(
        'update',
        f"Updated gym operational status: {old_status} → {operational_status}",
        entity_type='gym',
        entity_id=gym_id,
        gym_id=gym_id
    )
    
    return jsonify({
        'message': 'Gym status updated successfully',
        'operational_status': gym.operational_status
    }), 200
