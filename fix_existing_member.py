import sys
sys.path.append('backend')

from app import create_app
from app.extensions import db, bcrypt
from app.models import Member

# Create app and fix the last created member
app = create_app()

with app.app_context():
    print("🔧 Fixing last created member...")
    
    # Get the last created member
    member = Member.query.order_by(Member.id.desc()).first()
    
    if member and not member.password_hash:
        print(f"Fixing member: {member.email}")
        
        # Set password hash for the expected password
        password = "initialpass123"  # From the test
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        
        member.password_hash = password_hash
        member.password_changed = False
        db.session.commit()
        
        print(f"✅ Fixed member password hash")
        print(f"Password hash exists: {bool(member.password_hash)}")
        print(f"Has account: {member.to_dict().get('has_account')}")
        
    else:
        print("No member to fix or member already has password hash")