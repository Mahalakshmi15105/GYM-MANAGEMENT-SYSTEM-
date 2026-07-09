import requests

BASE_URL = 'http://localhost:5000'

def test_member_routes():
    print("🔍 Testing member routes...")
    
    # First login as gym owner to get token
    owner_login = {
        "email": "owner_6liedzn6@example.com", 
        "password": "password123"
    }
    
    response = requests.post(f'{BASE_URL}/api/auth/login', json=owner_login)
    if response.status_code != 200:
        print(f"❌ Failed to login as owner: {response.status_code}")
        print(response.text)
        return
    
    token = response.json()['token']
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test getting member list
    print(f"\n1. Testing GET /api/members")
    response = requests.get(f'{BASE_URL}/api/members', headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        members = response.json()
        print(f"Found {len(members)} members")
        if members:
            member_id = members[0]['id']
            print(f"First member ID: {member_id}")
            
            # Test getting specific member
            print(f"\n2. Testing GET /api/members/{member_id}")
            response = requests.get(f'{BASE_URL}/api/members/{member_id}', headers=headers)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            
            # Test updating member
            print(f"\n3. Testing PUT /api/members/{member_id}")
            update_data = {"first_name": "Updated"}
            response = requests.put(f'{BASE_URL}/api/members/{member_id}', 
                                  json=update_data, headers=headers)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            
    else:
        print(f"Response: {response.text}")

if __name__ == "__main__":
    test_member_routes()