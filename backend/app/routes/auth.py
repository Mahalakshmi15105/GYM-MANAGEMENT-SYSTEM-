from flask import Blueprint, request, jsonify
from app.extensions import db, bcrypt
from app.models import Gym, User
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
        
    user = User.query.filter_by(email=email).first()
    
    if not user or not bcrypt.check_password_hash(user.password_hash, password):
        return jsonify({'error': 'Invalid email or password'}), 401
        
    gym = Gym.query.get(user.gym_id) if user.gym_id else None
    gym_name = gym.name if gym else None
    gym_address = gym.address if gym else None
    gym_phone = gym.phone if gym else None
    
    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={
            'role': user.role,
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
            'gym_id': user.gym_id,
            'gym_name': gym_name,
            'gym_address': gym_address,
            'gym_phone': gym_phone
        }
    }), 200
