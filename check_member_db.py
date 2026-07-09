import sys
sys.path.append('backend')

from app import create_app
from app.extensions import db
from app.models import Member

# Create app and check the last created member
app = create_app()

with app.app_context():
    print("🔍 Checking last created member in database...")
    
    # Get the last created member
    member = Member.query.order_by(Member.id.desc()).first()
    
    if member:
        print(f"Member ID: {member.id}")
        print(f"Email: {member.email}")
        print(f"First name: {member.first_name}")
        print(f"Password hash exists: {bool(member.password_hash)}")
        print(f"Password hash length: {len(member.password_hash) if member.password_hash else 0}")
        print(f"Password changed: {member.password_changed}")
        print(f"Membership start date: {member.membership_start_date}")
        print(f"Membership end date: {member.membership_end_date}")
        print(f"Has account (from to_dict): {member.to_dict().get('has_account')}")
        
        if member.password_hash:
            print(f"Password hash preview: {member.password_hash[:20]}...")
        else:
            print("Password hash is None or empty")
    else:
        print("No members found in database")