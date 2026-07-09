#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

import requests
import json
import random
import string

def generate_unique_email(prefix="test"):
    """Generate a unique email for testing"""
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"{prefix}_{random_suffix}@example.com"

# Test the member login issue
BASE_URL = 'http://localhost:5000'

def test_member_login_debug():
    print("🔍 Debugging Member Login Issue...")
    
    # Generate unique emails for this test
    owner_email = generate_unique_email("owner")
    member_email = generate_unique_email("member")
    test_password = "testpass123"
    
    # Step 1: Register a gym owner first
    print("\n1. Registering gym owner...")
    register_data = {
        "gym_name": "Debug Test Gym",
        "gym_address": "123 Debug Street",
        "gym_phone": "+1234567890",
        "name": "Debug Owner",
        "email": owner_email,
        "password": "password123"
    }
    
    response = requests.post(f'{BASE_URL}/api/auth/register', json=register_data)
    if response.status_code != 201:
        print(f"❌ Failed to register gym owner: {response.status_code}")
        print(response.text)
        return False
    
    owner_data = response.json()
    owner_token = owner_data['token']
    gym_id = owner_data['user']['gym_id']
    print(f"✅ Gym owner registered successfully. Gym ID: {gym_id}")
    
    # Step 2: Create a member account
    print(f"\n2. Creating member with email: {member_email} and password: {test_password}")
    from datetime import datetime, timedelta
    start_date = datetime.now().strftime('%Y-%m-%d')
    end_date = (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d')
    
    member_data = {
        "first_name": "Debug",
        "last_name": "Member", 
        "phone": "+1111111111",
        "email": member_email,
        "password": test_password,
        "membership_start_date": start_date,
        "membership_end_date": end_date,
        "status": "Active"
    }
    
    headers = {"Authorization": f"Bearer {owner_token}"}
    response = requests.post(f'{BASE_URL}/api/members', json=member_data, headers=headers)
    if response.status_code != 201:
        print(f"❌ Failed to create member: {response.status_code}")
        print(response.text)
        return False
    
    member_response = response.json()
    member_created = member_response['member']
    member_id = member_created['id']
    print(f"✅ Member created successfully:")
    print(f"   Member ID: {member_id}")
    print(f"   Email: {member_created['email']}")
    print(f"   Has account: {member_created.get('has_account', False)}")
    print(f"   Password changed: {member_created.get('password_changed', False)}")
    
    # Step 3: Check member in database directly
    print(f"\n3. Checking member in database...")
    try:
        from app.models import Member
        from app.extensions import bcrypt
        from app import create_app
        
        app = create_app()
        with app.app_context():
            db_member = Member.query.filter_by(email=member_email).first()
            if db_member:
                print(f"✅ Member found in database:")
                print(f"   ID: {db_member.id}")
                print(f"   Email: {db_member.email}")
                print(f"   Password hash exists: {bool(db_member.password_hash)}")
                print(f"   Password hash length: {len(db_member.password_hash) if db_member.password_hash else 0}")
                print(f"   Password changed: {db_member.password_changed}")
                
                # Test password verification
                if db_member.password_hash:
                    password_valid = bcrypt.check_password_hash(db_member.password_hash, test_password)
                    print(f"   Password verification: {password_valid}")
                else:
                    print("   ❌ No password hash found!")
            else:
                print("❌ Member not found in database!")
                return False
                
    except Exception as e:
        print(f"❌ Database check failed: {e}")
        return False
    
    # Step 4: Test member login attempt
    print(f"\n4. Testing member login with credentials:")
    print(f"   Email: {member_email}")
    print(f"   Password: {test_password}")
    
    login_data = {
        "email": member_email,
        "password": test_password
    }
    
    response = requests.post(f'{BASE_URL}/api/auth/login', json=login_data)
    print(f"   Login response status: {response.status_code}")
    print(f"   Login response: {response.text}")
    
    if response.status_code == 200:
        print("✅ Member login successful!")
        login_response = response.json()
        print(f"   Role: {login_response['user']['role']}")
        print(f"   User type: {login_response['user']['user_type']}")
        return True
    else:
        print("❌ Member login failed!")
        return False

if __name__ == "__main__":
    try:
        success = test_member_login_debug()
        if success:
            print("\n✅ Debug Test: PASSED")
            sys.exit(0)
        else:
            print("\n❌ Debug Test: FAILED")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)