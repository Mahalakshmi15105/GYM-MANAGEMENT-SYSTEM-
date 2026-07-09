import requests
import random

BASE_URL = 'http://localhost:5000'

def create_and_test():
    print("🔧 Creating owner and testing member routes...")
    
    # Generate unique email
    random_suffix = random.randint(10000, 99999)
    owner_email = f"test_owner_{random_suffix}@example.com"
    
    # Step 1: Register a gym owner
    register_data = {
        "gym_name": "Route Test Gym",
        "gym_address": "123 Route Test St",
        "gym_phone": "+1234567890",
        "name": "Route Test Owner",
        "email": owner_email,
        "password": "password123"
    }
    
    response = requests.post(f'{BASE_URL}/api/auth/register', json=register_data)
    if response.status_code != 201:
        print(f"❌ Failed to register: {response.status_code}")
        print(response.text)
        return
        
    owner_data = response.json()
    token = owner_data['token']
    headers = {"Authorization": f"Bearer {token}"}
    print(f"✅ Owner created: {owner_email}")
    
    # Test member routes
    print(f"\n1. Testing GET /api/members")
    response = requests.get(f'{BASE_URL}/api/members', headers=headers)
    print(f"GET /api/members - Status: {response.status_code}")
    
    if response.status_code == 200:
        print(f"✅ Members route works")
        
        # Try to get the specific member we know exists (ID 12)
        print(f"\n2. Testing GET /api/members/12")
        response = requests.get(f'{BASE_URL}/api/members/12', headers=headers)
        print(f"GET /api/members/12 - Status: {response.status_code}")
        
        if response.status_code == 404:
            print("Member 12 not found (different gym)")
        elif response.status_code == 200:
            print("✅ Member 12 found")
            
        # Test PUT on member 12
        print(f"\n3. Testing PUT /api/members/12")
        update_data = {"password": "newpassword123"}
        response = requests.put(f'{BASE_URL}/api/members/12', 
                              json=update_data, headers=headers)
        print(f"PUT /api/members/12 - Status: {response.status_code}")
        print(f"Response: {response.text}")
    else:
        print(f"❌ Members route failed: {response.text}")

if __name__ == "__main__":
    create_and_test()