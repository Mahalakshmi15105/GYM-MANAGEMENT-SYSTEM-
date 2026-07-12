import requests
import json

BASE_URL = 'http://127.0.0.1:5000'

# Test the broadcast feature
def test_broadcast():
    # First, login as gym owner to get token
    login_data = {
        'email': 'owner@test.com',  # Replace with actual gym owner email
        'password': 'password123'   # Replace with actual password
    }
    
    print("Step 1: Logging in as Gym Owner...")
    try:
        response = requests.post(f'{BASE_URL}/api/auth/login', json=login_data)
        print(f"Login response status: {response.status_code}")
        if response.status_code == 200:
            token = response.json().get('access_token')
            print(f"Token received: {token[:50]}...")
            
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            # Test 1: Get broadcasts list
            print("\nStep 2: Getting broadcasts list...")
            response = requests.get(f'{BASE_URL}/api/broadcasts', headers=headers)
            print(f"Broadcasts list status: {response.status_code}")
            print(f"Response: {response.json()}")
            
            # Test 2: Get members for selection
            print("\nStep 3: Getting members for selection...")
            response = requests.get(f'{BASE_URL}/api/broadcasts/members', headers=headers)
            print(f"Members list status: {response.status_code}")
            print(f"Response: {response.json()}")
            
            # Test 3: Create a broadcast (without files for now)
            print("\nStep 4: Creating a test broadcast...")
            broadcast_data = {
                'subject': 'Test Announcement',
                'title': '🔥 Test Offer',
                'message': 'This is a test broadcast message.',
                'recipient_type': 'all'
            }
            
            response = requests.post(f'{BASE_URL}/api/broadcasts', 
                                    json=broadcast_data, 
                                    headers=headers)
            print(f"Create broadcast status: {response.status_code}")
            print(f"Response: {response.json()}")
            
            if response.status_code == 201:
                broadcast_id = response.json().get('broadcast', {}).get('id')
                print(f"Broadcast created with ID: {broadcast_id}")
                
                # Test 4: Get the specific broadcast
                print(f"\nStep 5: Getting broadcast {broadcast_id}...")
                response = requests.get(f'{BASE_URL}/api/broadcasts/{broadcast_id}', headers=headers)
                print(f"Get broadcast status: {response.status_code}")
                print(f"Response: {response.json()}")
                
                # Test 5: Get broadcasts list again to verify
                print("\nStep 6: Verifying broadcast in list...")
                response = requests.get(f'{BASE_URL}/api/broadcasts', headers=headers)
                print(f"Broadcasts list status: {response.status_code}")
                broadcasts = response.json().get('broadcasts', [])
                print(f"Total broadcasts: {len(broadcasts)}")
                for b in broadcasts:
                    print(f"  - {b['title']}: {b['subject']}")
                
                print("\n✅ Backend API tests completed successfully!")
            else:
                print(f"❌ Failed to create broadcast: {response.json()}")
        else:
            print(f"❌ Login failed: {response.json()}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == '__main__':
    test_broadcast()
