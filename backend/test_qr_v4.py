"""
Test script to activate gym and reset password
"""
import pymysql
from app.config import Config
import bcrypt

def activate_gym_and_reset_password():
    """Activate gym and reset password for gym owner"""
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
            
            # Activate gym
            cursor.execute("""
                UPDATE gyms 
                SET status = 'active' 
                WHERE id = %s
            """, (gym_id,))
            
            # Reset password to 'admin123'
            new_password = 'admin123'
            hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
            
            cursor.execute("""
                UPDATE users 
                SET password_hash = %s 
                WHERE id = %s
            """, (hashed.decode('utf-8'), user_id))
            
            connection.commit()
            print(f"✓ Gym activated")
            print(f"✓ Password reset to 'admin123' for {email}")
            
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

if __name__ == "__main__":
    print("=" * 60)
    print("Activate Gym and Reset Password")
    print("=" * 60)
    
    email, gym_id = activate_gym_and_reset_password()
    
    if email and gym_id:
        print(f"\nYou can now login with:")
        print(f"Email: {email}")
        print(f"Password: admin123")
    else:
        print("\nCould not find gym owner with QR code")
    
    print("\n" + "=" * 60)
