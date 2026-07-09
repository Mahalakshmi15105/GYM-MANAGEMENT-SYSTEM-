#!/usr/bin/env python3
"""
Test Member model changes
"""
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db, bcrypt
from app.models import Member, Gym, User

def test_member_model():
    """Test Member model with password_hash field"""
    print("🧪 Testing Member model changes...")
    
    app = create_app()
    
    with app.app_context():
        try:
            # Test 1: Check if password_hash column exists
            print("1. Checking Member model structure...")
            member_columns = [column.name for column in Member.__table__.columns]
            
            if 'password_hash' in member_columns:
                print("✅ password_hash field exists in Member model")
            else:
                print("❌ password_hash field missing in Member model")
                return False
            
            # Test 2: Check database table
            try:
                from sqlalchemy import text
                result = db.session.execute(text("DESCRIBE members"))
                db_columns = [row[0] for row in result.fetchall()]
                
                if 'password_hash' in db_columns:
                    print("✅ password_hash column exists in database")
                else:
                    print("❌ password_hash column missing in database")
                    return False
            except Exception as e:
                print(f"⚠️  Could not check database structure: {e}")
            
            # Test 3: Test Member.to_dict() excludes password_hash
            print("2. Testing Member.to_dict() method...")
            
            # Create a test gym first
            test_gym = Gym(
                name="Test Gym",
                status="Active",
                currency="USD",
                language="en"
            )
            db.session.add(test_gym)
            db.session.flush()  # Get the ID without committing
            
            # Create a test member with password
            password_hash = bcrypt.generate_password_hash("testpass123").decode('utf-8')
            
            test_member = Member(
                gym_id=test_gym.id,
                member_id="TEST001",
                first_name="Test",
                last_name="Member", 
                phone="1234567890",
                email="test@example.com",
                password_hash=password_hash,
                membership_start_date=db.func.current_date(),
                membership_end_date=db.func.current_date(),
                status="Active"
            )
            
            db.session.add(test_member)
            db.session.flush()
            
            # Test to_dict method
            member_dict = test_member.to_dict()
            
            if 'password_hash' not in member_dict:
                print("✅ password_hash properly excluded from to_dict()")
            else:
                print("❌ password_hash exposed in to_dict() - security issue!")
                return False
                
            if 'has_account' in member_dict and member_dict['has_account'] == True:
                print("✅ has_account field properly set to True")
            else:
                print("❌ has_account field missing or incorrect")
                return False
            
            # Test 4: Test member without password
            test_member_no_pass = Member(
                gym_id=test_gym.id,
                member_id="TEST002", 
                first_name="No Password",
                last_name="Member",
                phone="0987654321",
                email="nopass@example.com",
                password_hash=None,
                membership_start_date=db.func.current_date(),
                membership_end_date=db.func.current_date(),
                status="Active"
            )
            
            db.session.add(test_member_no_pass)
            db.session.flush()
            
            member_dict_no_pass = test_member_no_pass.to_dict()
            
            if member_dict_no_pass.get('has_account') == False:
                print("✅ has_account properly set to False for member without password")
            else:
                print("❌ has_account should be False for member without password")
                return False
            
            # Clean up
            db.session.rollback()
            
            print("\n✅ All Member model tests passed!")
            return True
            
        except Exception as e:
            print(f"\n❌ Test failed: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    success = test_member_model()
    sys.exit(0 if success else 1)