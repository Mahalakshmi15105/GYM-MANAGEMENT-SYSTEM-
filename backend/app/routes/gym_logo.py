from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt
from werkzeug.utils import secure_filename
from app.extensions import db
from app.models import Gym
from app.activity_logging import ActivityLogger
import os
import uuid
from datetime import datetime

gym_logo_bp = Blueprint('gym_logo', __name__)

# Allowed file extensions for logos
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'svg', 'webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def get_current_gym_id():
    """Extract gym_id from JWT token for multi-tenant isolation"""
    claims = get_jwt()
    return claims.get('gym_id')

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def create_upload_directory():
    """Create upload directory if it doesn't exist"""
    upload_dir = os.path.join(current_app.root_path, 'static', 'gym_logos')
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir, exist_ok=True)
    return upload_dir

@gym_logo_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_logo():
    """Upload gym logo"""
    gym_id = get_current_gym_id()
    if not gym_id:
        return jsonify({'error': 'Gym ID not found in token'}), 400
    
    # Check if gym exists
    gym = Gym.query.filter_by(id=gym_id).first()
    if not gym:
        return jsonify({'error': 'Gym not found'}), 404
    
    # Check if file is present
    if 'logo' not in request.files:
        return jsonify({'error': 'No logo file provided'}), 400
    
    file = request.files['logo']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Validate file type
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Allowed: PNG, JPG, JPEG, GIF, SVG, WEBP'}), 400
    
    # Check file size
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    
    if file_size > MAX_FILE_SIZE:
        return jsonify({'error': 'File too large. Maximum size: 5MB'}), 400
    
    try:
        # Create upload directory
        upload_dir = create_upload_directory()
        
        # Generate unique filename
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"gym_{gym_id}_{uuid.uuid4().hex[:8]}.{file_extension}"
        file_path = os.path.join(upload_dir, unique_filename)
        
        # Remove old logo file if exists
        if gym.logo:
            old_file_path = os.path.join(current_app.root_path, 'static', gym.logo.lstrip('/'))
            if os.path.exists(old_file_path):
                try:
                    os.remove(old_file_path)
                except OSError:
                    pass  # Don't fail if old file can't be removed
        
        # Save new file
        file.save(file_path)
        
        # Update gym record
        relative_path = f"gym_logos/{unique_filename}"
        gym.logo = relative_path
        db.session.commit()
        
        # Log the activity
        ActivityLogger.log_activity(
            'logo_upload',
            f"Logo uploaded for gym: {gym.name}",
            entity_type='gym',
            entity_id=gym_id,
            gym_id=gym_id,
            extra_data={'filename': unique_filename, 'file_size': file_size}
        )
        
        # Build logo URL
        logo_url = f"/static/{relative_path}"
        
        return jsonify({
            'message': 'Logo uploaded successfully',
            'logo_url': logo_url,
            'has_logo': True,
            'gym': gym.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to upload logo: {str(e)}'}), 500

@gym_logo_bp.route('/remove', methods=['DELETE'])
@jwt_required()
def remove_logo():
    """Remove gym logo"""
    gym_id = get_current_gym_id()
    if not gym_id:
        return jsonify({'error': 'Gym ID not found in token'}), 400
    
    gym = Gym.query.filter_by(id=gym_id).first()
    if not gym:
        return jsonify({'error': 'Gym not found'}), 404
    
    if not gym.logo:
        return jsonify({'error': 'No logo to remove'}), 400
    
    try:
        # Remove file from filesystem
        file_path = os.path.join(current_app.root_path, 'static', gym.logo.lstrip('/'))
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except OSError:
                pass  # Don't fail if file can't be removed
        
        # Update gym record
        old_logo = gym.logo
        gym.logo = None
        db.session.commit()
        
        # Log the activity
        ActivityLogger.log_activity(
            'logo_remove',
            f"Logo removed for gym: {gym.name}",
            entity_type='gym',
            entity_id=gym_id,
            gym_id=gym_id,
            extra_data={'old_logo': old_logo}
        )
        
        return jsonify({
            'message': 'Logo removed successfully',
            'gym': gym.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to remove logo: {str(e)}'}), 500

@gym_logo_bp.route('/info', methods=['GET'])
@jwt_required()
def get_logo_info():
    """Get current gym logo information"""
    gym_id = get_current_gym_id()
    if not gym_id:
        return jsonify({'error': 'Gym ID not found in token'}), 400
    
    gym = Gym.query.filter_by(id=gym_id).first()
    if not gym:
        return jsonify({'error': 'Gym not found'}), 404
    
    logo_url = None
    if gym.logo:
        # Check if file exists
        file_path = os.path.join(current_app.root_path, 'static', gym.logo.lstrip('/'))
        if os.path.exists(file_path):
            logo_url = f"/static/{gym.logo}"
    
    return jsonify({
        'gym': gym.to_dict(),
        'logo_url': logo_url,
        'has_logo': gym.logo is not None and logo_url is not None
    }), 200