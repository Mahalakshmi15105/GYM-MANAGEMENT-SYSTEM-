"""
Test script to verify QR code generation and display
"""
import requests
import pymysql
from app.config import Config

def test_gym_has_qr():
    """Check if gym has QR code generated"""
    try:
        # Parse database URL
        db_url = Config.SQLALCHEMY_DATABASE_URI
        if 'mysql+pymysql://' in db_url:
            db_url = db_url.replace('mysql+pymysql://', '')
            user_pass, host_port_db = db_url.split('@')
            user, password = user_pass.split(':')
            host_port, database = host_port_db.split('/')
            if ':' in host_port:
                host, port = host_port.split(':')
                port = int(port)
            else:
                host = host_port
                port = 3306
        
        print(f"Connecting to MySQL: {host}:{port}/{database}")
        
        # Connect to MySQL
        connection = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )
        
        cursor = connection.cursor()
        
        # Check gyms table for attendance_qr
        print("\nChecking gyms for attendance_qr...")
        cursor.execute("SELECT id, name, attendance_qr FROM gyms")
        gyms = cursor.fetchall()
        
        for gym in gyms:
            gym_id, name, qr = gym
            print(f"Gym ID: {gym_id}, Name: {name}, QR: {qr if qr else 'NULL'}")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

def test_qr_endpoint():
    """Test the QR image endpoint"""
    print("\nTesting QR image endpoint...")
    
    # First, try to login to get a token
    try:
        response = requests.post('http://127.0.0.1:5000/api/auth/login', json={
            'email': 'admin@gym.com',
            'password': 'admin123'
        })
        
        if response.status_code == 200:
            token = response.json().get('access_token')
            print(f"✓ Login successful")
            
            # Test QR info endpoint
            headers = {'Authorization': f'Bearer {token}'}
            info_response = requests.get('http://127.0.0.1:5000/api/gym/qr/info', headers=headers)
            print(f"\nQR Info Response: {info_response.status_code}")
            print(f"QR Info Data: {info_response.json()}")
            
            # Test QR image endpoint
            image_response = requests.get('http://127.0.0.1:5000/api/gym/qr/image', headers=headers)
            print(f"\nQR Image Response: {image_response.status_code}")
            print(f"Content-Type: {image_response.headers.get('Content-Type')}")
            print(f"Content-Length: {image_response.headers.get('Content-Length')}")
            
            if image_response.status_code == 200:
                print(f"✓ QR image endpoint successful")
                # Save image to file
                with open('test_qr_image.png', 'wb') as f:
                    f.write(image_response.content)
                print(f"✓ Image saved to test_qr_image.png")
            else:
                print(f"✗ QR image endpoint failed: {image_response.text}")
        else:
            print(f"✗ Login failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=" * 60)
    print("QR Code Verification Test")
    print("=" * 60)
    
    test_gym_has_qr()
    test_qr_endpoint()
    
    print("\n" + "=" * 60)
    print("Test Complete")
    print("=" * 60)
