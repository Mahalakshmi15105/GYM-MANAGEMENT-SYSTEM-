"""
Gym QR Code management routes for gym owners to manage their attendance QR codes
"""

from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt
from app.extensions import db
from app.models import Gym
from app.activity_logging import ActivityLogger
import uuid
import qrcode
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

gym_qr_bp = Blueprint('gym_qr', __name__)

def get_current_gym_id():
    """Extract gym_id from JWT token for multi-tenant isolation"""
    claims = get_jwt()
    gym_id = claims.get('gym_id')
    return int(gym_id) if gym_id else None


@gym_qr_bp.route('/info', methods=['GET'])
@jwt_required()
def get_qr_info():
    """Get current gym QR code information"""
    # Debug logging
    print(f"[QR INFO] Authorization header: {request.headers.get('Authorization')}")
    from flask_jwt_extended import get_jwt_identity
    print(f"[QR INFO] JWT identity: {get_jwt_identity()}")
    print(f"[QR INFO] JWT claims: {get_jwt()}")
    
    gym_id = get_current_gym_id()
    print(f"[QR INFO] Extracted gym_id: {gym_id}")
    
    if not gym_id:
        return jsonify({'error': 'Gym ID not found in token'}), 400
    
    gym = Gym.query.filter_by(id=gym_id).first()
    if not gym:
        return jsonify({'error': 'Gym not found'}), 404
    
    return jsonify({
        'gym': gym.to_dict(),
        'has_qr': bool(gym.attendance_qr),
        'qr_code': gym.attendance_qr
    }), 200


@gym_qr_bp.route('/regenerate', methods=['POST'])
@jwt_required()
def regenerate_qr():
    """Regenerate gym QR code (gym owner only)"""
    gym_id = get_current_gym_id()
    if not gym_id:
        return jsonify({'error': 'Gym ID not found in token'}), 400
    
    gym = Gym.query.filter_by(id=gym_id).first()
    if not gym:
        return jsonify({'error': 'Gym not found'}), 404
    
    try:
        # Generate new unique QR code
        new_qr = f"GYM{str(uuid.uuid4())[:12].upper()}"
        
        # Ensure QR is unique across all gyms
        while Gym.query.filter_by(attendance_qr=new_qr).first():
            new_qr = f"GYM{str(uuid.uuid4())[:12].upper()}"
        
        old_qr = gym.attendance_qr
        gym.attendance_qr = new_qr
        db.session.commit()
        
        # Log the activity
        ActivityLogger.log_activity(
            'qr_regenerate',
            f"Regenerated gym QR code from {old_qr} to {new_qr}",
            entity_type='gym',
            entity_id=gym_id,
            gym_id=gym_id,
            extra_data={'old_qr': old_qr, 'new_qr': new_qr}
        )
        
        return jsonify({
            'message': 'QR code regenerated successfully',
            'gym': gym.to_dict(),
            'qr_code': new_qr
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to regenerate QR code: {str(e)}'}), 500


@gym_qr_bp.route('/verify', methods=['POST'])
@jwt_required()
def verify_qr():
    """Verify if a QR code belongs to the current gym (for member scanning)"""
    gym_id = get_current_gym_id()
    if not gym_id:
        return jsonify({'error': 'Gym ID not found in token'}), 400
    
    data = request.get_json() or {}
    qr_code = data.get('qr_code')
    
    if not qr_code:
        return jsonify({'error': 'QR code is required'}), 400
    
    gym = Gym.query.filter_by(id=gym_id).first()
    if not gym:
        return jsonify({'error': 'Gym not found'}), 404
    
    # Verify the QR code matches the gym's QR
    if gym.attendance_qr == qr_code:
        return jsonify({
            'valid': True,
            'gym_id': gym.id,
            'gym_name': gym.name
        }), 200
    else:
        return jsonify({
            'valid': False,
            'error': 'QR code does not match this gym'
        }), 400


@gym_qr_bp.route('/image', methods=['GET'])
@jwt_required()
def get_qr_image():
    """Generate and serve QR code image for the gym"""
    # Debug logging
    print(f"[QR IMAGE] Authorization header: {request.headers.get('Authorization')}")
    from flask_jwt_extended import get_jwt_identity
    print(f"[QR IMAGE] JWT identity: {get_jwt_identity()}")
    print(f"[QR IMAGE] JWT claims: {get_jwt()}")
    
    gym_id = get_current_gym_id()
    print(f"[QR IMAGE] Extracted gym_id: {gym_id}")
    
    if not gym_id:
        return jsonify({'error': 'Gym ID not found in token'}), 400
    
    gym = Gym.query.filter_by(id=gym_id).first()
    if not gym:
        return jsonify({'error': 'Gym not found'}), 404
    
    if not gym.attendance_qr:
        return jsonify({'error': 'No QR code generated for this gym'}), 404
    
    try:
        # Generate QR code with URL encoding
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        
        # Encode URL instead of plain text
        # In production, use actual domain
        frontend_url = 'http://localhost:3000'  # TODO: Configure from environment
        qr_data = f"{frontend_url}/login?gym={gym.attendance_qr}"
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        # Create QR image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Save to BytesIO
        img_io = BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)
        
        response = send_file(img_io, mimetype='image/png')
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        return response
        
    except Exception as e:
        return jsonify({'error': f'Failed to generate QR image: {str(e)}'}), 500


@gym_qr_bp.route('/printable', methods=['GET'])
@jwt_required()
def get_printable_qr():
    """Generate a printable QR code page with gym logo and name"""
    from flask import current_app
    import os
    
    gym_id = get_current_gym_id()
    if not gym_id:
        return jsonify({'error': 'Gym ID not found in token'}), 400
    
    gym = Gym.query.filter_by(id=gym_id).first()
    if not gym:
        return jsonify({'error': 'Gym not found'}), 404
    
    if not gym.attendance_qr:
        return jsonify({'error': 'No QR code generated for this gym'}), 404
    
    try:
        # Generate QR code with URL encoding
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=15,
            border=4,
        )
        
        # Encode URL instead of plain text
        frontend_url = 'http://localhost:3000'  # TODO: Configure from environment
        qr_data = f"{frontend_url}/login?gym={gym.attendance_qr}"
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        # Create QR image
        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        # Create printable page
        page_width, page_height = 800, 1000
        page = Image.new('RGB', (page_width, page_height), 'white')
        draw = ImageDraw.Draw(page)
        
        # Try to use a default font, fall back to basic if not available
        try:
            title_font = ImageFont.truetype("arial.ttf", 48)
            subtitle_font = ImageFont.truetype("arial.ttf", 24)
            instruction_font = ImageFont.truetype("arial.ttf", 18)
        except:
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
            instruction_font = ImageFont.load_default()
        
        # Add gym logo if exists
        logo_y = 50
        if gym.logo:
            try:
                logo_path = os.path.join(current_app.root_path, 'static', gym.logo.lstrip('/'))
                if os.path.exists(logo_path):
                    logo_img = Image.open(logo_path)
                    # Resize logo to fit
                    logo_size = 100
                    logo_img = logo_img.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
                    logo_x = (page_width - logo_size) // 2
                    page.paste(logo_img, (logo_x, logo_y))
                    logo_y += logo_size + 20
            except Exception as logo_error:
                print(f"Failed to load gym logo: {logo_error}")
        
        # Add gym name
        gym_name = gym.name
        title_bbox = draw.textbbox((0, 0), gym_name, font=title_font)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = (page_width - title_width) // 2
        draw.text((title_x, logo_y), gym_name, fill='black', font=title_font)
        
        # Add subtitle
        subtitle = "Attendance QR Code"
        subtitle_bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
        subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
        subtitle_x = (page_width - subtitle_width) // 2
        draw.text((subtitle_x, logo_y + 70), subtitle, fill='gray', font=subtitle_font)
        
        # Center QR code
        qr_size = 400
        qr_x = (page_width - qr_size) // 2
        qr_y = logo_y + 150
        qr_img = qr_img.resize((qr_size, qr_size))
        page.paste(qr_img, (qr_x, qr_y))
        
        # Add instructions
        instructions = [
            "Scan this QR code to check in",
            "Use the SmartGoNext Gym member app",
            "One check-in per day",
        ]
        
        instruction_y = qr_y + qr_size + 30
        for instruction in instructions:
            inst_bbox = draw.textbbox((0, 0), instruction, font=instruction_font)
            inst_width = inst_bbox[2] - inst_bbox[0]
            inst_x = (page_width - inst_width) // 2
            draw.text((inst_x, instruction_y), instruction, fill='gray', font=instruction_font)
            instruction_y += 30
        
        # Add footer
        footer = f"Generated by SmartGoNext Gym - Gym ID: {gym.id}"
        footer_bbox = draw.textbbox((0, 0), footer, font=instruction_font)
        footer_width = footer_bbox[2] - footer_bbox[0]
        footer_x = (page_width - footer_width) // 2
        draw.text((footer_x, page_height - 50), footer, fill='lightgray', font=instruction_font)
        
        # Save to BytesIO
        img_io = BytesIO()
        page.save(img_io, 'PNG')
        img_io.seek(0)
        
        return send_file(img_io, mimetype='image/png', as_attachment=False, download_name=f'gym-{gym.id}-printable-qr.png')
        
    except Exception as e:
        return jsonify({'error': f'Failed to generate printable QR: {str(e)}'}), 500
