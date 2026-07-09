#!/usr/bin/env python3
"""
Test Member routes for account creation
"""
import sys
import os
import json

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db, bcrypt
from app.models import Member, Gym, User
from flask_jwt_extended import create_access_token

def test_member_routes():
    """Test Member routes with account creation"""
    print("🧪 Testing Member routes...")
    
    app = create_app()
    
    with app.app_context():
        try:
            # Setup test data
            print("1. Setting up test data...")
            
            # Create test gym and user
            test_gym = Gym(
                name="Test Gym API",
                status="Active", 
                currency="USD",
                language="en"
            )
            db.session.add(test_gym)
            db.session.flush()
            
            password_hash = bcrypt.generate_password_hash("ownerpass123").decode('utf-8')
            test_user = User(
                name="Test Owner",
                email="testowner@example.com",
                password_hash=password_hash,
                role="gym_owner",
                gym_id=test_gym.id
            )
            db.session.add(test_user)
            db.session.commit()
            
            # Create JWT token
            token = create_access_token(
                identity=str(test_user.id),
                additional_claims={
                    'role': 'gym_owner',
                    'gym_id': test_gym.id
                }
            )
            
            print("✅ Test data setup complete")
            
            # Test 2: Create member with account
            print("2. Testing member account creation...")
            
            with app.test_client() as client:
                member_data = {
                    "first_name": "API Test",
                    "last_name": "Member",
                    "phone": "5551234567",
                    "email": "apimember@example.com",
                    "password": "memberpass123",
                    "membership_start_date": "2024-01-01",
                    "membership_end_date": "2024-12-31",
                    "status": "Active"
                }
                
                headers = {
                    'Authorization': f'Bearer {token}',
                    'Content-Type': 'application/json'
                }
                
                response = client.post('/api/members', 
                                     data=json.dumps(member_data),
                                     headers=headers)
                
                if response.status_code == 201:
                    member_response = response.get_json()
                    member = member_response.get('member', {})
                    
                    print("✅ Member account created via API")
                    print(f"   Email: {member.get('email')}")
                    print(f"   Has Account: {member.get('has_account')}")
                    
                    if 'password_hash' in member:
                        print("❌ Security issue: password_hash in API response!")
                        return False
                        
                    if not member.get('has_account'):
                        print("❌ has_account should be True")
                        return False
                        
                    member_id = member.get('id')
                    
                else:
                    print(f"❌ Member creation failed: {response.status_code}")
                    print(f"Response: {response.get_data(as_text=True)}")
                    return False
                
                # Test 3: Get member details
                print("3. Testing member details API...")
                response = client.get(f'/api/members/{member_id}', headers=headers)
                
                if response.status_code == 200:
                    member = response.get_json()
                    print("✅ Member details retrieved via API")
                    
                    if 'password_hash' in member:
                        print("❌ Security issue: password_hash in get response!")
                        return False
                        
                    if not member.get('has_account'):
                        print("❌ has_account should be True in get response")
                        return False
                        
                else:
                    print(f"❌ Member get failed: {response.status_code}")
                    return False
                
                # Test 4: Update member password
                print("4. Testing password update API...")
                update_data = {"password": "newpass456"}
                
                response = client.put(f'/api/members/{member_id}',
                                    data=json.dumps(update_data),
                                    headers=headers)
                
                if response.status_code == 200:
                    print("✅ Member password updated via API")
                else:
                    print(f"❌ Password update failed: {response.status_code}")
                    print(f"Response: {response.get_data(as_text=True)}")
                    return False
                
                # Test 5: Duplicate email validation
                print("5. Testing duplicate email validation...")
                duplicate_data = {
                    "first_name": "Duplicate",
                    "last_name": "Test", 
                    "phone": "5559999999",
                    "email": "apimember@example.com",  # Same email
                    "password": "somepass123",
                    "membership_start_date": "2024-01-01",
                    "membership_end_date": "2024-12-31",
                    "status": "Active"
                }
                
                response = client.post('/api/members',
                                     data=json.dumps(duplicate_data),
                                     headers=headers)
                
                if response.status_code == 400:
                    error_msg = response.get_data(as_text=True)
                    if 'already exists' in error_msg.lower():
                        print("✅ Duplicate email validation working")
                    else:
                        print(f"❌ Wrong duplicate email error: {error_msg}")
                        return False
                else:
                    print(f"❌ Duplicate email should return 400, got: {response.status_code}")
                    return False
                
                # Test 6: Validation tests
                print("6. Testing validation...")
                
                # Missing email
                invalid_data = {
                    "first_name": "Invalid",
                    "phone": "5551111111",
                    "password": "pass123",
                    "membership_start_date": "2024-01-01",
                    "membership_end_date": "2024-12-31"
                }
                
                response = client.post('/api/members',
                                     data=json.dumps(invalid_data),
                                     headers=headers)
                
                if response.status_code == 400:
                    print("✅ Missing email validation working")
                else:
                    print(f"❌ Missing email should return 400, got: {response.status_code}")
                    return False
                
                # Short password
                short_pass_data = {
                    "first_name": "Short",
                    "phone": "5552222222", 
                    "email": "short@example.com",
                    "password": "123",  # Too short
                    "membership_start_date": "2024-01-01",
                    "membership_end_date": "2024-12-31"
                }
                
                response = client.post('/api/members',
                                     data=json.dumps(short_pass_data),
                                     headers=headers)
                
                if response.status_code == 400:
                    print("✅ Short password validation working")
                else:
                    print(f"❌ Short password should return 400, got: {response.status_code}")
                    return False
            
            # Clean up
            db.session.rollback()
            
            print("\n✅ All Member routes tests passed!")
            return True
            
        except Exception as e:
            print(f"\n❌ Test failed: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            return False

if __name__ == "__main__":
    success = test_member_routes()
    sys.exit(0 if success else 1)