"""
Test script to debug JWT token issue
"""
import requests
import pymysql
from app.config import Config

def test_jwt_token():
    """Test JWT token generation and validation"""
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
                port = 3303
        
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
            SELECT u.id, u.email, u.name, u.role, u.gym_id, g.name as gym_name, g.attendance_qr, g.status
            FROM users u
            JOIN gyms g ON u.gym_id = g.id
            WHERE u.role = 'gym_owner' AND g.attendance_qr IS NOT NULL
            LIMIT 1
        """)
        result = cursor.fetchone()
        
        if result:
            user_id, email, name, role, gym_id, gym_name, qr_code, gym_status = result
            print(f"Found gym owner: {name} ({email})")
            print(f"Gym: {gym_name} (ID: {gym_id})")
            print(f"QR Code: {qr_code}")
            print(f"Gym Status: {gym_status}")
            
            cursor.close()
            connection.close()
            
            # Login as gym owner
            response = requests.post('http://127.0.0.1:5000/api/auth/login', json={
                'email': email,
                'password': 'admin123'
            })
            
            print(f"\nLogin Response: {response.status_code}")
            print(f"Login Data: {response.json()}")
            
            if response.status_code == 200:
                token = response.json().get('token')
                print(f"\n✓ Login successful")
                print(f"Token: {token[:50]}...")  # Print first 50 chars
                print(f"Token length: {len(token)}")
                
                # Test QR info endpoint
                headers = {'Authorization': f'Bearer {token}'}
                print(f"\nAuthorization Header: Bearer {token[:50]}...")
                
                info_response = requests.get('http://127.0.0.1:5000/api/gym/qr/info', headers=headers)
                print(f"\nQR Info Response: {info_response.status_code}")
                print(f"QR Info Data: {info_response.text}")
            else:
                print(f"✗ Login failed: {response.status_code} - {response.text}")
        else:
            print("No gym owner found for gyms with QR codes")
            cursor.close()
            connection.close()
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=" * 60)
    print("JWT Token Debug Test")
    print("=" * 60)
    
    test_jwt_token()
    
    print("\n" + "=" * 60)
