from flask import Blueprint, request, jsonify
from app.extensions import db, bcrypt
from app.models import Gym, User, Member
from flask_jwt_extended import create_access_token

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    
    gym_name = data.get('gym_name')
    gym_address = data.get('gym_address')
    gym_phone = data.get('gym_phone')
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    
    if not all([gym_name, gym_address, gym_phone, name, email, password]):
        return jsonify({'error': 'Missing required fields (gym_name, gym_address, gym_phone, name, email, password)'}), 400
        
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 400
        
    try:
        # Create Gym with user-provided data
        new_gym = Gym(name=gym_name, address=gym_address, phone=gym_phone)
        db.session.add(new_gym)
        db.session.flush() # Populate the Gym ID before commit
        
        # Create User linked to the gym as the owner
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(
            name=name,
            email=email,
            password_hash=hashed_password,
            role='gym_owner',
            gym_id=new_gym.id
        )
        db.session.add(new_user)
        db.session.commit()
        
        # Directly generate JWT token after registration
        access_token = create_access_token(
            identity=str(new_user.id),
            additional_claims={
                'role': new_user.role,
                'gym_id': new_user.gym_id,
                'email': new_user.email,
                'name': new_user.name,
                'gym_name': new_gym.name,
                'gym_address': new_gym.address,
                'gym_phone': new_gym.phone
            }
        )
        
        return jsonify({
            'message': 'Gym and Owner registered successfully',
            'token': access_token,
            'user': {
                'id': new_user.id,
                'name': new_user.name,
                'email': new_user.email,
                'role': new_user.role,
                'gym_id': new_user.gym_id,
                'gym_name': new_gym.name,
                'gym_address': new_gym.address,
                'gym_phone': new_gym.phone
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Registration failed', 'message': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400
        
    # Try to find user in Users table first (Super Admin, Gym Owner)
    user = User.query.filter_by(email=email).first()
    
    if user and bcrypt.check_password_hash(user.password_hash, password):
        # Handle User authentication (Super Admin, Gym Owner)
        gym = Gym.query.get(user.gym_id) if user.gym_id else None
        gym_name = gym.name if gym else None
        gym_address = gym.address if gym else None
        gym_phone = gym.phone if gym else None
        
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={
                'role': user.role,
                'user_type': 'user',  # Distinguish from member
                'gym_id': user.gym_id,
                'email': user.email,
                'name': user.name,
                'gym_name': gym_name,
                'gym_address': gym_address,
                'gym_phone': gym_phone
            }
        )
        
        return jsonify({
            'message': 'Login successful',
            'token': access_token,
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'role': user.role,
                'user_type': 'user',
                'gym_id': user.gym_id,
                'gym_name': gym_name,
                'gym_address': gym_address,
                'gym_phone': gym_phone
            }
        }), 200
    
    # If not found in Users table, try Members table
    member = Member.query.filter_by(email=email).first()
    
    if member and member.password_hash and bcrypt.check_password_hash(member.password_hash, password):
        # Handle Member authentication
        gym = Gym.query.get(member.gym_id) if member.gym_id else None
        gym_name = gym.name if gym else None
        gym_address = gym.address if gym else None
        gym_phone = gym.phone if gym else None
        
        # Check if this is first time login (password hasn't been changed from default)
        first_time_login = not member.password_changed
        
        access_token = create_access_token(
            identity=str(member.id),
            additional_claims={
                'role': 'member',
                'user_type': 'member',  # Distinguish from user
                'gym_id': member.gym_id,
                'member_id': member.id,
                'email': member.email,
                'name': f"{member.first_name} {member.last_name}".strip(),
                'first_name': member.first_name,
                'last_name': member.last_name,
                'gym_name': gym_name,
                'gym_address': gym_address,
                'gym_phone': gym_phone,
                'first_time_login': first_time_login
            }
        )
        
        return jsonify({
            'message': 'Login successful',
            'token': access_token,
            'user': {
                'id': member.id,
                'name': f"{member.first_name} {member.last_name}".strip(),
                'email': member.email,
                'role': 'member',
                'user_type': 'member',
                'gym_id': member.gym_id,
                'member_id': member.id,
                'first_name': member.first_name,
                'last_name': member.last_name,
                'gym_name': gym_name,
                'gym_address': gym_address,
                'gym_phone': gym_phone,
                'first_time_login': first_time_login
            }
        }), 200
    
    # If neither user nor member found with valid credentials
    return jsonify({'error': 'Invalid email or password'}), 401
