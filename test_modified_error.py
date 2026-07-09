import requests

BASE_URL = 'http://localhost:5000'

# Test if our modified error message appears
response = requests.post(f'{BASE_URL}/api/members', json={}, headers={})
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")