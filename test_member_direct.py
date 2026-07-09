import sys
sys.path.append('backend')

from app import create_app
from app.extensions import db, bcrypt
from app.models import Member, Gym, User
from datetime import datetime, timedelta

# Create app and test member creation directly
app = create_app()

with app.app_context():
    print("🔍 Testing direct member creation...")
    
    # First, create a gym for testing
    test_gym = Gym(name="Test Direct Gym", address="123 Test St", phone="+1234567890")
    db.session.add(test_gym)
    db.session.commit()
    
    gym_id = test_gym.id
    print(f"Created test gym with ID: {gym_id}")
    
    # Create member directly
    email = "test_direct@example.com"
    password = "testpass123"
    
    # Hash password
    password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    print(f"Password hash generated: {password_hash is not None}")
    print(f"Password hash length: {len(password_hash) if password_hash else 0}")
    
    # Set dates
    start_date = datetime.utcnow().date()
    end_date = start_date + timedelta(days=365)
    current_time = datetime.utcnow()
    
    # Create member
    member = Member(
        gym_id=gym_id,
        member_id="MEM12345678",
        first_name="Test",
        last_name="Direct",
        phone="+9876543210",
        email=email,
        password_hash=password_hash,
        password_changed=False,
        membership_start_date=start_date,
        membership_end_date=end_date,
        status="Active",
        created_at=current_time,
        updated_at=current_time
    )
    
    db.session.add(member)
    db.session.commit()
    
    print(f"✅ Member created with ID: {member.id}")
    print(f"Has account: {member.to_dict().get('has_account', 'Missing')}")
    print(f"Password changed: {member.to_dict().get('password_changed', 'Missing')}")
    
    # Test authentication
    from app.routes.auth import auth_bp
    print(f"\n🔐 Testing authentication...")
    
    # Check if member can authenticate
    found_member = Member.query.filter_by(email=email).first()
    if found_member:
        print(f"Found member: {found_member.email}")
        print(f"Password hash exists: {bool(found_member.password_hash)}")
        
        if found_member.password_hash and bcrypt.check_password_hash(found_member.password_hash, password):
            print("✅ Authentication successful!")
        else:
            print("❌ Authentication failed!")
    else:
        print("❌ Member not found!")
    
    # Clean up
    db.session.delete(member)
    db.session.delete(test_gym)
    db.session.commit()
    print("🧹 Cleaned up test data")