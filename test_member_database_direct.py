#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

import random
import string
from datetime import datetime, timedelta

def generate_unique_email(prefix="test"):
    """Generate a unique email for testing"""
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"{prefix}_{random_suffix}@example.com"

def test_member_password_directly():
    print("🔍 Testing Member Password Creation Directly in Database...")
    
    try:
        from app import create_app
        from app.models import Gym, User, Member
        from app.extensions import db, bcrypt
        
        app = create_app()
        
        with app.app_context():
            # Generate unique test data
            owner_email = generate_unique_email("owner")
            member_email = generate_unique_email("member")
            test_password = "testpass123"
            
            print(f"\n1. Creating test gym and owner...")
            
            # Create a test gym
            gym = Gym(
                name="Test Database Gym",
                address="123 Test DB Street",
                phone="+1234567890"
            )
            db.session.add(gym)
            db.session.flush()
            gym_id = gym.id
            print(f"   Created gym with ID: {gym_id}")
            
            # Create gym owner
            owner_password_hash = bcrypt.generate_password_hash("ownerpass123").decode('utf-8')
            owner = User(
                name="Test Owner",
                email=owner_email,
                password_hash=owner_password_hash,
                role='gym_owner',
                gym_id=gym_id
            )
            db.session.add(owner)
            db.session.flush()
            print(f"   Created gym owner with ID: {owner.id}")
            
            print(f"\n2. Creating member with password...")
            print(f"   Email: {member_email}")
            print(f"   Password: {test_password}")
            
            # Hash the member password
            member_password_hash = bcrypt.generate_password_hash(test_password).decode('utf-8')
            print(f"   Generated password hash: {member_password_hash[:20]}...")
            print(f"   Hash length: {len(member_password_hash)}")
            
            # Create member with hashed password
            member = Member(
                gym_id=gym_id,
                member_id=f"MEM{random.randint(1000, 9999)}",
                first_name="Test",
                last_name="Member",
                phone="+1111111111",
                email=member_email,
                password_hash=member_password_hash,
                password_changed=False,
                membership_start_date=datetime.now().date(),
                membership_end_date=(datetime.now() + timedelta(days=365)).date(),
                status="Active",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            db.session.add(member)
            db.session.commit()
            
            print(f"   Created member with ID: {member.id}")
            print(f"   Member email: {member.email}")
            print(f"   Has password hash: {bool(member.password_hash)}")
            print(f"   Password changed: {member.password_changed}")
            
            print(f"\n3. Testing password verification...")
            
            # Test password verification
            password_valid = bcrypt.check_password_hash(member.password_hash, test_password)
            print(f"   Password verification result: {password_valid}")
            
            # Test with wrong password
            wrong_password_valid = bcrypt.check_password_hash(member.password_hash, "wrongpass")
            print(f"   Wrong password verification result: {wrong_password_valid}")
            
            print(f"\n4. Testing member lookup by email...")
            
            # Test finding member by email
            found_member = Member.query.filter_by(email=member_email).first()
            if found_member:
                print(f"   ✅ Member found by email")
                print(f"   Member ID: {found_member.id}")
                print(f"   Email matches: {found_member.email == member_email}")
                print(f"   Has password hash: {bool(found_member.password_hash)}")
                
                # Test password verification on found member
                found_password_valid = bcrypt.check_password_hash(found_member.password_hash, test_password)
                print(f"   Password verification on found member: {found_password_valid}")
            else:
                print(f"   ❌ Member not found by email")
                return False
            
            print(f"\n5. Simulating login logic...")
            
            # Simulate the login logic from auth.py
            login_email = member_email
            login_password = test_password
            
            print(f"   Login attempt with email: {login_email}")
            print(f"   Login attempt with password: {login_password}")
            
            # Try to find user in Users table first (should not find)
            user = User.query.filter_by(email=login_email).first()
            print(f"   Found in Users table: {bool(user)}")
            
            # Try to find member in Members table
            member_found = Member.query.filter_by(email=login_email).first()
            print(f"   Found in Members table: {bool(member_found)}")
            
            if member_found and member_found.password_hash:
                password_check = bcrypt.check_password_hash(member_found.password_hash, login_password)
                print(f"   Password check result: {password_check}")
                
                if password_check:
                    print("   ✅ Login should succeed!")
                    return True
                else:
                    print("   ❌ Password verification failed")
                    return False
            else:
                print("   ❌ Member not found or no password hash")
                return False
                
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        success = test_member_password_directly()
        if success:
            print("\n✅ Direct Database Test: PASSED - Member password creation and verification works")
            sys.exit(0)
        else:
            print("\n❌ Direct Database Test: FAILED")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)