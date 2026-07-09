import requests

BASE_URL = 'http://localhost:5000'

def test_manual_login():
    print("🔐 Testing manual member login...")
    
    # Use the member email we just fixed
    login_data = {
        "email": "member_6liedzn6@example.com",
        "password": "initialpass123"
    }
    
    response = requests.post(f'{BASE_URL}/api/auth/login', json=login_data)
    print(f"Login response status: {response.status_code}")
    print(f"Login response: {response.text}")
    
    if response.status_code == 200:
        data = response.json()
        user = data['user']
        print(f"\n✅ Login successful!")
        print(f"Role: {user['role']}")
        print(f"User type: {user['user_type']}")
        print(f"First time login: {user['first_time_login']}")
        print(f"Member ID: {user.get('member_id')}")
        print(f"Name: {user['name']}")
        
        # Test password change
        if user.get('first_time_login'):
            print(f"\n🔧 Testing password change for first-time login...")
            member_id = user['member_id']
            token = data['token']
            
            password_change_data = {
                "password": "newpassword123"
            }
            
            headers = {"Authorization": f"Bearer {token}"}
            change_response = requests.put(f'{BASE_URL}/api/members/{member_id}', 
                                         json=password_change_data, 
                                         headers=headers)
            
            print(f"Password change status: {change_response.status_code}")
            print(f"Password change response: {change_response.text}")
            
            if change_response.status_code == 200:
                print("✅ Password change successful!")
                
                # Test login with new password
                print(f"\n🔐 Testing login with new password...")
                new_login_data = {
                    "email": "member_6liedzn6@example.com",
                    "password": "newpassword123"
                }
                
                new_response = requests.post(f'{BASE_URL}/api/auth/login', json=new_login_data)
                print(f"New login status: {new_response.status_code}")
                
                if new_response.status_code == 200:
                    new_data = new_response.json()
                    new_user = new_data['user']
                    print(f"✅ New login successful!")
                    print(f"First time login: {new_user['first_time_login']}")
                    return True
    
    return False

if __name__ == "__main__":
    test_manual_login()