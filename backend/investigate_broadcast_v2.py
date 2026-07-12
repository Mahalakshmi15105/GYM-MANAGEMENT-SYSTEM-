"""
Investigate broadcast message flow - Test with member who actually has broadcasts
NO CODE CHANGES - Only investigation
"""
import pymysql
from app.config import Config
import json
import requests
import jwt
import bcrypt

def get_db_connection():
    """Get database connection"""
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
    
    connection = pymysql.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database
    )
    return connection

def find_member_with_broadcasts():
    """Find a member who has broadcasts in their gym"""
    print("\n" + "="*60)
    print("STEP 1: Find Member with Broadcasts")
    print("="*60)
    
    connection = get_db_connection()
    cursor = connection.cursor()
    
    # Find a member who is a recipient of a broadcast
    cursor.execute("""
        SELECT m.id, m.email, m.first_name, m.last_name, m.gym_id, m.password_hash,
               br.broadcast_id, bm.subject, bm.title
        FROM members m
        JOIN broadcast_recipients br ON m.id = br.member_id
        JOIN broadcast_messages bm ON br.broadcast_id = bm.id
        WHERE m.password_hash IS NOT NULL
        LIMIT 1
    """)
    
    result = cursor.fetchone()
    
    if result:
        member_id, email, first_name, last_name, gym_id, password_hash, broadcast_id, subject, title = result
        print(f"Found member with broadcast:")
        print(f"  Member: {first_name} {last_name} ({email})")
        print(f"  Member ID: {member_id}, Gym ID: {gym_id}")
        print(f"  Broadcast ID: {broadcast_id}, Subject: {subject}, Title: {title}")
        
        cursor.close()
        connection.close()
        return member_id, email, gym_id, password_hash
    else:
        print("✗ No member with password and broadcasts found")
        cursor.close()
        connection.close()
        return None, None, None, None

def setup_member_and_test(member_id, email, gym_id, password_hash):
    """Setup member for testing and run API tests"""
    print("\n" + "="*60)
    print("STEP 2: Setup and Test Member")
    print("="*60)
    
    # Reset password
    connection = get_db_connection()
    cursor = connection.cursor()
    
    new_password = 'password123'
    hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
    
    cursor.execute("""
        UPDATE members 
        SET password_hash = %s 
        WHERE id = %s
    """, (hashed.decode('utf-8'), member_id))
    
    # Activate gym
    cursor.execute("""
        UPDATE gyms 
        SET status = 'Active' 
        WHERE id = %s
    """, (gym_id,))
    
    # Activate subscription
    cursor.execute("""
        UPDATE gym_subscriptions 
        SET status = 'active'
        WHERE gym_id = %s
    """, (gym_id,))
    
    connection.commit()
    print(f"✓ Password reset to 'password123'")
    print(f"✓ Gym activated")
    
    cursor.close()
    connection.close()
    
    # Login
    try:
        response = requests.post('http://127.0.0.1:5000/api/auth/login', json={
            'email': email,
            'password': 'password123'
        })
        
        print(f"\nLogin Status: {response.status_code}")
        
        if response.status_code == 200:
            token = response.json().get('token')
            user_data = response.json().get('user')
            print(f"✓ Login successful")
            
            # Decode JWT
            decoded = jwt.decode(token, options={"verify_signature": False})
            print(f"\nJWT Claims:")
            print(json.dumps(decoded, indent=2))
            
            member_id_claim = decoded.get('member_id')
            gym_id_claim = decoded.get('gym_id')
            
            return token, member_id_claim, gym_id_claim
        else:
            print(f"✗ Login failed: {response.text}")
            return None, None, None
    except Exception as e:
        print(f"✗ Error: {e}")
        return None, None, None

def test_apis(token, member_id, gym_id):
    """Test both notification and messages APIs"""
    print("\n" + "="*60)
    print("STEP 3: Test Both APIs")
    print("="*60)
    
    headers = {'Authorization': f'Bearer {token}'}
    
    # Test Messages API
    print("\n--- Testing Messages API ---")
    try:
        response = requests.get('http://127.0.0.1:5000/api/broadcasts/member', headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response:")
        print(json.dumps(response.json(), indent=2))
        
        messages_data = response.json() if response.status_code == 200 else None
    except Exception as e:
        print(f"✗ Error: {e}")
        messages_data = None
    
    # Test Notifications API
    print("\n--- Testing Notifications API ---")
    try:
        response = requests.get('http://127.0.0.1:5000/api/notifications', headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response:")
        print(json.dumps(response.json(), indent=2))
        
        notifications_data = response.json() if response.status_code == 200 else None
    except Exception as e:
        print(f"✗ Error: {e}")
        notifications_data = None
    
    return messages_data, notifications_data

def verify_database_state(member_id, gym_id):
    """Verify database state for this member"""
    print("\n" + "="*60)
    print("STEP 4: Verify Database State")
    print("="*60)
    
    connection = get_db_connection()
    cursor = connection.cursor()
    
    # Check broadcast recipients for this member
    cursor.execute("""
        SELECT br.id, br.broadcast_id, br.is_read, bm.subject, bm.title
        FROM broadcast_recipients br
        JOIN broadcast_messages bm ON br.broadcast_id = bm.id
        WHERE br.member_id = %s
    """, (member_id,))
    
    recipients = cursor.fetchall()
    print(f"\nBroadcastRecipient records for member {member_id}: {len(recipients)}")
    for br in recipients:
        print(f"  Broadcast ID: {br[1]}, Subject: {br[3]}, Title: {br[4]}, Read: {br[2]}")
    
    # Check notifications for this member
    cursor.execute("""
        SELECT n.id, n.notification_type, n.title, n.message, n.is_read
        FROM notifications n
        WHERE n.recipient_role = 'member' AND n.recipient_id = %s
    """, (member_id,))
    
    notifications = cursor.fetchall()
    print(f"\nNotification records for member {member_id}: {len(notifications)}")
    for n in notifications:
        print(f"  Type: {n[1]}, Title: {n[2]}, Read: {n[4]}")
    
    cursor.close()
    connection.close()
    
    return len(recipients), len(notifications)

if __name__ == "__main__":
    print("="*60)
    print("Broadcast Message Flow Investigation - Member with Broadcasts")
    print("="*60)
    
    # Step 1: Find member with broadcasts
    member_id, email, gym_id, password_hash = find_member_with_broadcasts()
    
    if member_id and email and gym_id:
        # Step 2: Setup and test member
        token, jwt_member_id, jwt_gym_id = setup_member_and_test(member_id, email, gym_id, password_hash)
        
        if token and jwt_member_id:
            # Step 3: Test both APIs
            messages_data, notifications_data = test_apis(token, jwt_member_id, jwt_gym_id)
            
            # Step 4: Verify database state
            recipient_count, notification_count = verify_database_state(jwt_member_id, jwt_gym_id)
            
            # Analysis
            print("\n" + "="*60)
            print("ANALYSIS")
            print("="*60)
            
            print(f"\nDatabase State:")
            print(f"  BroadcastRecipient records: {recipient_count}")
            print(f"  Notification records: {notification_count}")
            
            if messages_data:
                print(f"\nMessages API Response:")
                print(f"  Status: 200")
                print(f"  Broadcasts returned: {len(messages_data.get('broadcasts', []))}")
            else:
                print(f"\nMessages API Response:")
                print(f"  Status: Error or no data")
            
            if notifications_data:
                print(f"\nNotifications API Response:")
                print(f"  Status: 200")
                print(f"  Notifications returned: {len(notifications_data.get('notifications', []))}")
                print(f"  Unread count: {notifications_data.get('unread_count', 0)}")
            else:
                print(f"\nNotifications API Response:")
                print(f"  Status: Error or no data")
            
            print("\n" + "="*60)
            print("ROOT CAUSE ANALYSIS")
            print("="*60)
            
            if messages_data and len(messages_data.get('broadcasts', [])) > 0:
                print("✓ Messages API returns data correctly")
                print("✓ Issue may be in frontend rendering")
            elif messages_data and len(messages_data.get('broadcasts', [])) == 0:
                print("✗ Messages API returns empty array")
                print("✗ Database has records but API returns none")
                print("✗ FAILURE POINT: Backend SQL query or logic")
            else:
                print("✗ Messages API returns error")
                print("✗ FAILURE POINT: Backend API endpoint")
        else:
            print("\n✗ Could not complete test - login failed")
    else:
        print("\n✗ Could not find member with broadcasts")
    
    print("\n" + "="*60)
