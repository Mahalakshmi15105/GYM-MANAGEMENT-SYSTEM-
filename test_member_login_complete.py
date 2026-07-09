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

# Test the complete member login flow
BASE_URL = 'http://localhost:5000'

def test_member_login_flow():
    print("🔄 Testing complete Member Login Flow...")
    
    # Generate unique emails for this test
    owner_email = generate_unique_email("owner")
    member_email = generate_unique_email("member")
    
    # Step 1: Register a gym owner first
    print("\n1. Registering gym owner...")
    register_data = {
        "gym_name": "Test Gym for Member Login",
        "gym_address": "123 Test Street",
        "gym_phone": "+1234567890",
        "name": "Test Owner",
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
    print("\n2. Creating member account...")
    from datetime import datetime, timedelta
    start_date = datetime.now().strftime('%Y-%m-%d')
    end_date = (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d')
    
    member_data = {
        "first_name": "Test",
        "last_name": "Member",
        "phone": "+1111111111",
        "email": member_email,
        "password": "initialpass123",
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
    member_id = member_response['member']['id']
    print(f"✅ Member created successfully. Member ID: {member_id}")
    print(f"   Has account: {member_response['member'].get('has_account', False)}")
    print(f"   Password changed: {member_response['member'].get('password_changed', False)}")
    
    # Step 3: Test member login (first time)
    print("\n3. Testing member first-time login...")
    login_data = {
        "email": member_email,
        "password": "initialpass123"
    }
    
    response = requests.post(f'{BASE_URL}/api/auth/login', json=login_data)
    if response.status_code != 200:
        print(f"❌ Failed member login: {response.status_code}")
        print(response.text)
        return False
    
    login_response = response.json()
    member_token = login_response['token']
    print(f"✅ Member login successful!")
    print(f"   Role: {login_response['user']['role']}")
    print(f"   User type: {login_response['user']['user_type']}")
    print(f"   First time login: {login_response['user']['first_time_login']}")
    print(f"   Member ID: {login_response['user']['member_id']}")
    print(f"   Name: {login_response['user']['name']}")
    
    # Step 4: Test member password change
    print("\n4. Testing member password change...")
    password_change_data = {
        "password": "newpassword123"
    }
    
    member_headers = {"Authorization": f"Bearer {member_token}"}
    response = requests.put(f'{BASE_URL}/api/members/{member_id}', json=password_change_data, headers=member_headers)
    if response.status_code != 200:
        print(f"❌ Failed to change member password: {response.status_code}")
        print(response.text)
        return False
    
    print("✅ Member password changed successfully!")
    updated_member = response.json()['member']
    print(f"   Password changed: {updated_member.get('password_changed', False)}")
    
    # Step 5: Test login with new password
    print("\n5. Testing login with new password...")
    new_login_data = {
        "email": member_email,
        "password": "newpassword123"
    }
    
    response = requests.post(f'{BASE_URL}/api/auth/login', json=new_login_data)
    if response.status_code != 200:
        print(f"❌ Failed login with new password: {response.status_code}")
        print(response.text)
        return False
    
    new_login_response = response.json()
    print("✅ Login with new password successful!")
    print(f"   First time login: {new_login_response['user']['first_time_login']}")
    
    # Step 6: Verify old password doesn't work
    print("\n6. Verifying old password doesn't work...")
    old_login_data = {
        "email": member_email,
        "password": "initialpass123"
    }
    
    response = requests.post(f'{BASE_URL}/api/auth/login', json=old_login_data)
    if response.status_code == 401:
        print("✅ Old password correctly rejected!")
    else:
        print(f"❌ Old password should have been rejected but got: {response.status_code}")
        return False
    
    print("\n🎉 All member login flow tests passed!")
    return True

if __name__ == "__main__":
    try:
        success = test_member_login_flow()
        if success:
            print("\n✅ Member Login Flow Test: PASSED")
            sys.exit(0)
        else:
            print("\n❌ Member Login Flow Test: FAILED")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)