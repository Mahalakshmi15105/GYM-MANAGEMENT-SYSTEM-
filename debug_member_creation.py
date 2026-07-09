import requests
import random

BASE_URL = 'http://localhost:5000'

def debug_member_creation():
    print("🔍 Debugging member creation...")
    
    # Generate unique emails
    random_suffix = random.randint(10000, 99999)
    owner_email = f"debug_owner_{random_suffix}@example.com"
    member_email = f"debug_member_{random_suffix}@example.com"
    
    # Step 1: Register a gym owner
    print("\n1. Registering gym owner...")
    register_data = {
        "gym_name": "Debug Gym",
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
    
    # Step 2: Debug member creation with detailed logging
    print(f"\n2. Creating member for gym {gym_id}...")
    member_data = {
        "first_name": "Debug",
        "last_name": "Member",
        "phone": "+9876543210",
        "email": member_email,
        "password": "debugpass123",
        "status": "Active"
    }
    
    print(f"   Sending data: {member_data}")
    headers = {"Authorization": f"Bearer {owner_token}"}
    response = requests.post(f'{BASE_URL}/api/members', json=member_data, headers=headers)
    
    print(f"   Response status: {response.status_code}")
    print(f"   Response headers: {dict(response.headers)}")
    print(f"   Response body: {response.text}")
    
    if response.status_code == 201:
        member_response = response.json()
        member_data_response = member_response['member']
        print(f"\n✅ Member created successfully!")
        print(f"   Member ID: {member_data_response['id']}")
        print(f"   Email: {member_data_response['email']}")
        print(f"   Has account: {member_data_response.get('has_account', 'MISSING')}")
        print(f"   Password changed: {member_data_response.get('password_changed', 'MISSING')}")
        
        # Step 3: Try to login
        print(f"\n3. Testing login with password 'debugpass123'...")
        login_data = {
            "email": member_email,
            "password": "debugpass123"
        }
        
        login_response = requests.post(f'{BASE_URL}/api/auth/login', json=login_data)
        print(f"   Login response status: {login_response.status_code}")
        print(f"   Login response: {login_response.text}")
        
        return True
    else:
        print(f"❌ Failed to create member!")
        return False

if __name__ == "__main__":
    debug_member_creation()