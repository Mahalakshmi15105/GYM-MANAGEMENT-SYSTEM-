"""
Test script to verify QR code generation and display with gym owner
"""
import requests
import pymysql
from app.config import Config

def test_gym_owner_login():
    """Find a gym owner and login"""
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
        
        # Find a gym owner for a gym that has QR code
        print("\nFinding gym owner for gym with QR code...")
        cursor.execute("""
            SELECT u.id, u.email, u.name, u.role, u.gym_id, g.name as gym_name, g.attendance_qr
            FROM users u
            JOIN gyms g ON u.gym_id = g.id
            WHERE u.role = 'gym_owner' AND g.attendance_qr IS NOT NULL
            LIMIT 1
        """)
        result = cursor.fetchone()
        
        if result:
            user_id, email, name, role, gym_id, gym_name, qr_code = result
            print(f"Found gym owner: {name} ({email})")
            print(f"Gym: {gym_name} (ID: {gym_id})")
            print(f"QR Code: {qr_code}")
            
            cursor.close()
            connection.close()
            
            return email, gym_id
        else:
            print("No gym owner found for gyms with QR codes")
            cursor.close()
            connection.close()
            return None, None
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return None, None

def test_qr_endpoint_with_owner(email, gym_id):
    """Test the QR image endpoint with gym owner"""
    print(f"\nTesting QR image endpoint with gym owner: {email}")
    
    # Default password for gym owners (assuming it's the same)
    password = "admin123"
    
    try:
        # Login as gym owner
        response = requests.post('http://127.0.0.1:5000/api/auth/login', json={
            'email': email,
            'password': password
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
                print(f"✓ Image size: {len(image_response.content)} bytes")
            else:
                print(f"✗ QR image endpoint failed: {image_response.text}")
        else:
            print(f"✗ Login failed: {response.status_code} - {response.text}")
            print("Trying with default password...")
            
            # Try with a different password
            response = requests.post('http://127.0.0.1:5000/api/auth/login', json={
                'email': email,
                'password': 'password123'
            })
            
            if response.status_code == 200:
                token = response.json().get('access_token')
                print(f"✓ Login successful with password123")
                
                headers = {'Authorization': f'Bearer {token}'}
                image_response = requests.get('http://127.0.0.1:5000/api/gym/qr/image', headers=headers)
                print(f"\nQR Image Response: {image_response.status_code}")
                
                if image_response.status_code == 200:
                    print(f"✓ QR image endpoint successful")
                    with open('test_qr_image.png', 'wb') as f:
                        f.write(image_response.content)
                    print(f"✓ Image saved to test_qr_image.png")
                else:
                    print(f"✗ QR image endpoint failed: {image_response.text}")
            else:
                print(f"✗ Login still failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=" * 60)
    print("QR Code Verification Test with Gym Owner")
    print("=" * 60)
    
    email, gym_id = test_gym_owner_login()
    
    if email and gym_id:
        test_qr_endpoint_with_owner(email, gym_id)
    else:
        print("\nCould not find gym owner with QR code. Testing with admin...")
        # Try with admin anyway
        test_qr_endpoint_with_owner('admin@gym.com', None)
    
    print("\n" + "=" * 60)
    print("Test Complete")
    print("=" * 60)
