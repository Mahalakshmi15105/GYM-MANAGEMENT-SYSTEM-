"""
Test script to verify API endpoints are working after schema fix
"""
import requests
import json

BASE_URL = 'http://127.0.0.1:5000'

def test_login():
    """Test login to get token"""
    print("Testing login...")
    try:
        response = requests.post(f'{BASE_URL}/api/auth/login', json={
            'email': 'admin@gym.com',
            'password': 'admin123'
        })
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token')
            print(f"✓ Login successful")
            return token
        else:
            print(f"✗ Login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"✗ Login error: {str(e)}")
        return None

def test_members_api(token):
    """Test members list API"""
    print("\nTesting Members API...")
    try:
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(f'{BASE_URL}/api/members', headers=headers)
        if response.status_code == 200:
            data = response.json()
            members = data.get('members', [])
            print(f"✓ Members API successful - Found {len(members)} members")
            if members:
                print(f"  First member: {members[0].get('first_name')} {members[0].get('last_name')}")
                print(f"  Workout duration: {members[0].get('workout_duration_minutes')} minutes")
            return True
        else:
            print(f"✗ Members API failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"✗ Members API error: {str(e)}")
        return False

def test_analytics_api(token):
    """Test dashboard analytics API"""
    print("\nTesting Analytics API...")
    try:
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(f'{BASE_URL}/api/analytics/dashboard', headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Analytics API successful")
            print(f"  Total members: {data.get('total_members', 'N/A')}")
            print(f"  Active members: {data.get('active_members', 'N/A')}")
            print(f"  Total attendance: {data.get('total_attendance', 'N/A')}")
            return True
        else:
            print(f"✗ Analytics API failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"✗ Analytics API error: {str(e)}")
        return False

def test_attendance_api(token):
    """Test attendance API"""
    print("\nTesting Attendance API...")
    try:
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(f'{BASE_URL}/api/attendance', headers=headers)
        if response.status_code == 200:
            data = response.json()
            attendance = data.get('attendance', [])
            print(f"✓ Attendance API successful - Found {len(attendance)} records")
            return True
        else:
            print(f"✗ Attendance API failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"✗ Attendance API error: {str(e)}")
        return False

def test_qr_api(token):
    """Test QR code generation API"""
    print("\nTesting QR Code API...")
    try:
        headers = {'Authorization': f'Bearer {token}'}
        # First get a member ID
        members_response = requests.get(f'{BASE_URL}/api/members', headers=headers)
        if members_response.status_code == 200:
            members = members_response.json().get('members', [])
            if members:
                member_id = members[0].get('id')
                response = requests.get(f'{BASE_URL}/api/members/{member_id}/qr', headers=headers)
                if response.status_code == 200:
                    print(f"✓ QR Code API successful")
                    return True
                else:
                    print(f"✗ QR Code API failed: {response.status_code} - {response.text}")
                    return False
        print("✗ No members found to test QR code")
        return False
    except Exception as e:
        print(f"✗ QR Code API error: {str(e)}")
        return False

def main():
    print("=" * 60)
    print("API Testing After Schema Fix")
    print("=" * 60)
    
    token = test_login()
    if not token:
        print("\n✗ Cannot proceed without authentication token")
        return
    
    results = []
    results.append(("Members API", test_members_api(token)))
    results.append(("Analytics API", test_analytics_api(token)))
    results.append(("Attendance API", test_attendance_api(token)))
    results.append(("QR Code API", test_qr_api(token)))
    
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name}: {status}")
    
    all_passed = all(result for _, result in results)
    print("=" * 60)
    if all_passed:
        print("✓ All tests passed!")
    else:
        print("✗ Some tests failed")

if __name__ == "__main__":
    main()
