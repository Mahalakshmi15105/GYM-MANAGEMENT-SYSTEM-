from flask import Blueprint, request, jsonify, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.models import db, BroadcastMessage, BroadcastRecipient, Member, User, Gym, Notification
from app.activity_logging import ActivityLogger
from datetime import datetime
import os
import uuid
from werkzeug.utils import secure_filename

broadcasts_bp = Blueprint('broadcasts', __name__)


def get_current_gym_id():
    """Extract gym_id from JWT token for multi-tenant isolation"""
    claims = get_jwt()
    return claims.get('gym_id')


def get_current_user_id():
    """Extract user_id from JWT token (for Gym Owners)"""
    from flask_jwt_extended import get_jwt_identity
    identity = get_jwt_identity()
    if identity:
        return int(identity)
    return None

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

# Upload directories
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'broadcasts')
ATTACHMENT_FOLDER = os.path.join(UPLOAD_FOLDER, 'attachments')
BANNER_FOLDER = os.path.join(UPLOAD_FOLDER, 'banners')

# Create upload directories if they don't exist
os.makedirs(ATTACHMENT_FOLDER, exist_ok=True)
os.makedirs(BANNER_FOLDER, exist_ok=True)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@broadcasts_bp.route('', methods=['GET'])
@jwt_required()
def get_broadcasts():
    """Get all broadcasts for the current gym (Gym Owner only)"""
    gym_id = get_current_gym_id()
    if not gym_id:
        return jsonify({'error': 'Gym ID not found in token'}), 400
    
    try:
        broadcasts = BroadcastMessage.query.filter_by(gym_id=gym_id).order_by(BroadcastMessage.created_at.desc()).all()
        return jsonify({
            'broadcasts': [broadcast.to_dict() for broadcast in broadcasts]
        }), 200
    except Exception as e:
        return jsonify({'error': f'Failed to fetch broadcasts: {str(e)}'}), 500


@broadcasts_bp.route('/<int:broadcast_id>', methods=['GET'])
@jwt_required()
def get_broadcast(broadcast_id):
    """Get a specific broadcast by ID"""
    gym_id = get_current_gym_id()
    if not gym_id:
        return jsonify({'error': 'Gym ID not found in token'}), 400
    
    try:
        broadcast = BroadcastMessage.query.filter_by(id=broadcast_id, gym_id=gym_id).first()
        if not broadcast:
            return jsonify({'error': 'Broadcast not found'}), 404
        
        return jsonify({
            'broadcast': broadcast.to_dict()
        }), 200
    except Exception as e:
        return jsonify({'error': f'Failed to fetch broadcast: {str(e)}'}), 500


@broadcasts_bp.route('', methods=['POST'])
@jwt_required()
def create_broadcast():
    """Create a new broadcast message (Gym Owner only)"""
    gym_id = get_current_gym_id()
    user_id = get_current_user_id()
    
    if not gym_id or not user_id:
        return jsonify({'error': 'Authentication required'}), 400
    
    try:
        data = request.form.to_dict()
        
        # Validate required fields
        if not data.get('subject'):
            return jsonify({'error': 'Subject is required'}), 400
        if not data.get('title'):
            return jsonify({'error': 'Offer Title is required'}), 400
        if not data.get('message'):
            return jsonify({'error': 'Message is required'}), 400
        if not data.get('recipient_type'):
            return jsonify({'error': 'Recipient Type is required'}), 400
        
        recipient_type = data.get('recipient_type')
        if recipient_type not in ['all', 'active', 'expiring', 'selected']:
            return jsonify({'error': 'Invalid recipient type'}), 400
        
        # Handle selected members
        selected_member_ids = []
        if recipient_type == 'selected':
            if not data.get('selected_members'):
                return jsonify({'error': 'Selected members are required when recipient type is selected'}), 400
            try:
                selected_member_ids = [int(mid.strip()) for mid in data.get('selected_members').split(',')]
            except ValueError:
                return jsonify({'error': 'Invalid member IDs'}), 400
        
        # Handle file uploads
        attachment_url = None
        banner_url = None
        
        # Attachment upload
        if 'attachment' in request.files:
            attachment_file = request.files['attachment']
            if attachment_file and attachment_file.filename:
                if not allowed_file(attachment_file.filename):
                    return jsonify({'error': 'Invalid file type. Only PNG, JPG, JPEG, and PDF are allowed'}), 400
                if attachment_file.content_length > MAX_FILE_SIZE:
                    return jsonify({'error': 'File size exceeds 10 MB limit'}), 400
                
                filename = secure_filename(f"{uuid.uuid4()}_{attachment_file.filename}")
                attachment_path = os.path.join(ATTACHMENT_FOLDER, filename)
                attachment_file.save(attachment_path)
                attachment_url = f"/static/broadcasts/attachments/{filename}"
        
        # Banner upload
        if 'banner' in request.files:
            banner_file = request.files['banner']
            if banner_file and banner_file.filename:
                if not allowed_file(banner_file.filename):
                    return jsonify({'error': 'Invalid file type. Only PNG, JPG, JPEG, and PDF are allowed'}), 400
                if banner_file.content_length > MAX_FILE_SIZE:
                    return jsonify({'error': 'File size exceeds 10 MB limit'}), 400
                
                filename = secure_filename(f"{uuid.uuid4()}_{banner_file.filename}")
                banner_path = os.path.join(BANNER_FOLDER, filename)
                banner_file.save(banner_path)
                banner_url = f"/static/broadcasts/banners/{filename}"
        
        # Create broadcast message
        broadcast = BroadcastMessage(
            gym_id=gym_id,
            subject=data['subject'],
            title=data['title'],
            message=data['message'],
            attachment_url=attachment_url,
            banner_url=banner_url,
            recipient_type=recipient_type,
            created_by=user_id
        )
        
        db.session.add(broadcast)
        db.session.flush()  # Get the broadcast ID
        
        # Determine recipients
        recipients_query = Member.query.filter_by(gym_id=gym_id)
        
        if recipient_type == 'active':
            recipients_query = recipients_query.filter_by(status='Active')
        elif recipient_type == 'expiring':
            # Members whose membership expires within 7 days
            from datetime import timedelta
            expiry_date = datetime.utcnow().date() + timedelta(days=7)
            recipients_query = recipients_query.filter(
                Member.membership_end_date <= expiry_date,
                Member.status == 'Active'
            )
        elif recipient_type == 'selected':
            recipients_query = recipients_query.filter(Member.id.in_(selected_member_ids))
        
        recipients = recipients_query.all()
        
        print(f"DEBUG: Found {len(recipients)} recipients for broadcast")
        for member in recipients:
            print(f"DEBUG: Recipient - ID: {member.id}, Name: {member.first_name} {member.last_name}, Email: {member.email}")
        
        # Create recipient mappings
        for member in recipients:
            recipient = BroadcastRecipient(
                broadcast_id=broadcast.id,
                member_id=member.id
            )
            db.session.add(recipient)
            
            # Create notification for each recipient
            notification = Notification(
                gym_id=gym_id,
                recipient_role='member',
                recipient_id=member.id,
                notification_type='broadcast_message',
                title=f"New message from Gym Owner: {data['subject']}",
                message=data['title'],
                reference_id=broadcast.id
            )
            db.session.add(notification)
        
        db.session.commit()
        print(f"DEBUG: Broadcast {broadcast.id} created with {len(recipients)} recipients")
        
        # Log activity
        ActivityLogger.log_create(
            'broadcast',
            broadcast.id,
            entity_name=data['subject'],
            gym_id=gym_id,
            extra_data={'recipient_count': len(recipients), 'recipient_type': recipient_type}
        )
        
        return jsonify({
            'message': 'Broadcast sent successfully',
            'broadcast': broadcast.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to create broadcast: {str(e)}'}), 500


@broadcasts_bp.route('/<int:broadcast_id>', methods=['DELETE'])
@jwt_required()
def delete_broadcast(broadcast_id):
    """Delete a broadcast (Gym Owner only)"""
    gym_id = get_current_gym_id()
    if not gym_id:
        return jsonify({'error': 'Gym ID not found in token'}), 400
    
    try:
        broadcast = BroadcastMessage.query.filter_by(id=broadcast_id, gym_id=gym_id).first()
        if not broadcast:
            return jsonify({'error': 'Broadcast not found'}), 404
        
        # Delete associated files
        if broadcast.attachment_url:
            try:
                attachment_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), broadcast.attachment_url.lstrip('/'))
                if os.path.exists(attachment_path):
                    os.remove(attachment_path)
            except Exception as e:
                print(f"Error deleting attachment: {e}")
        
        if broadcast.banner_url:
            try:
                banner_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), broadcast.banner_url.lstrip('/'))
                if os.path.exists(banner_path):
                    os.remove(banner_path)
            except Exception as e:
                print(f"Error deleting banner: {e}")
        
        # Delete broadcast (cascade will delete recipients)
        db.session.delete(broadcast)
        db.session.commit()
        
        # Log activity
        ActivityLogger.log_delete(
            'broadcast',
            broadcast_id,
            entity_name=broadcast.subject,
            gym_id=gym_id
        )
        
        return jsonify({'message': 'Broadcast deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to delete broadcast: {str(e)}'}), 500


@broadcasts_bp.route('/member', methods=['GET'])
@jwt_required()
def get_member_broadcasts():
    """Get all broadcasts for the current member"""
    try:
        # Get member from JWT
        from flask_jwt_extended import get_jwt
        claims = get_jwt()
        member_id = claims.get('member_id')
        
        if not member_id:
            return jsonify({'error': 'Member ID not found in token'}), 400
        
        # Get all broadcasts where this member is a recipient
        recipient_records = BroadcastRecipient.query.filter_by(member_id=member_id).all()
        broadcast_ids = [r.broadcast_id for r in recipient_records]
        
        broadcasts = BroadcastMessage.query.filter(BroadcastMessage.id.in_(broadcast_ids)).order_by(BroadcastMessage.created_at.desc()).all()
        
        # Add read status to each broadcast
        result = []
        for broadcast in broadcasts:
            recipient = next((r for r in recipient_records if r.broadcast_id == broadcast.id), None)
            broadcast_dict = broadcast.to_dict()
            broadcast_dict['is_read'] = recipient.is_read if recipient else False
            broadcast_dict['read_at'] = recipient.read_at.isoformat() if recipient and recipient.read_at else None
            result.append(broadcast_dict)
        
        return jsonify({
            'broadcasts': result
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to fetch broadcasts: {str(e)}'}), 500


@broadcasts_bp.route('/member/<int:broadcast_id>/read', methods=['POST'])
@jwt_required()
def mark_broadcast_as_read(broadcast_id):
    """Mark a broadcast as read by the current member"""
    try:
        # Get member from JWT
        from flask_jwt_extended import get_jwt
        claims = get_jwt()
        member_id = claims.get('member_id')
        
        if not member_id:
            return jsonify({'error': 'Member ID not found in token'}), 400
        
        # Find the recipient record
        recipient = BroadcastRecipient.query.filter_by(
            broadcast_id=broadcast_id,
            member_id=member_id
        ).first()
        
        if not recipient:
            return jsonify({'error': 'Broadcast not found or not sent to this member'}), 404
        
        # Mark as read
        recipient.is_read = True
        recipient.read_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'message': 'Broadcast marked as read'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to mark broadcast as read: {str(e)}'}), 500


@broadcasts_bp.route('/members', methods=['GET'])
@jwt_required()
def get_members_for_selection():
    """Get all members for the current gym (for recipient selection)"""
    gym_id = get_current_gym_id()
    if not gym_id:
        return jsonify({'error': 'Gym ID not found in token'}), 400
    
    try:
        search = request.args.get('search', '')
        
        query = Member.query.filter_by(gym_id=gym_id)
        
        if search:
            query = query.filter(
                db.or_(
                    Member.first_name.ilike(f'%{search}%'),
                    Member.last_name.ilike(f'%{search}%'),
                    Member.email.ilike(f'%{search}%'),
                    Member.phone.ilike(f'%{search}%')
                )
            )
        
        members = query.order_by(Member.first_name, Member.last_name).all()
        
        return jsonify({
            'members': [
                {
                    'id': m.id,
                    'name': f"{m.first_name} {m.last_name}".strip(),
                    'email': m.email,
                    'phone': m.phone,
                    'status': m.status
                }
                for m in members
            ]
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to fetch members: {str(e)}'}), 500
