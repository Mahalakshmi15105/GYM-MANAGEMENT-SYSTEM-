"""
Investigate broadcast message flow - Database and API verification
NO CODE CHANGES - Only investigation
"""
import pymysql
from app.config import Config
import json

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

def investigate_database():
    """Check database for broadcast and recipient records"""
    print("\n" + "="*60)
    print("STEP 1: Database Investigation")
    print("="*60)
    
    connection = get_db_connection()
    cursor = connection.cursor()
    
    # Check all broadcasts
    cursor.execute("""
        SELECT bm.id, bm.gym_id, bm.subject, bm.title, bm.recipient_type, bm.created_at
        FROM broadcast_messages bm
        ORDER BY bm.created_at DESC
        LIMIT 10
    """)
    
    broadcasts = cursor.fetchall()
    print(f"\nTotal broadcasts in database: {len(broadcasts)}")
    print("\nRecent broadcasts:")
    for bm in broadcasts:
        print(f"  ID: {bm[0]}, Gym ID: {bm[1]}, Subject: {bm[2]}, Title: {bm[3]}, Type: {bm[4]}")
    
    # Check broadcast recipients
    cursor.execute("""
        SELECT br.id, br.broadcast_id, br.member_id, br.is_read, br.read_at
        FROM broadcast_recipients br
        ORDER BY br.id DESC
        LIMIT 20
    """)
    
    recipients = cursor.fetchall()
    print(f"\nTotal broadcast recipients in database: {len(recipients)}")
    print("\nRecent broadcast recipients:")
    for br in recipients:
        print(f"  ID: {br[0]}, Broadcast ID: {br[1]}, Member ID: {br[2]}, Read: {br[3]}")
    
    # Check notifications for broadcasts
    cursor.execute("""
        SELECT n.id, n.gym_id, n.recipient_role, n.recipient_id, n.notification_type, n.title, n.reference_id
        FROM notifications n
        WHERE n.notification_type = 'broadcast_message'
        ORDER BY n.created_at DESC
        LIMIT 10
    """)
    
    notifications = cursor.fetchall()
    print(f"\nTotal broadcast notifications in database: {len(notifications)}")
    print("\nRecent broadcast notifications:")
    for n in notifications:
        print(f"  ID: {n[0]}, Gym ID: {n[1]}, Recipient: {n[2]}:{n[3]}, Type: {n[4]}, Ref ID: {n[6]}")
    
    # Get a specific broadcast and its recipients
    if broadcasts:
        broadcast_id = broadcasts[0][0]
        gym_id = broadcasts[0][1]
        
        print(f"\n" + "="*60)
        print(f"Detailed analysis for Broadcast ID {broadcast_id}")
        print("="*60)
        
        # Get recipients for this broadcast
        cursor.execute("""
            SELECT br.id, br.member_id, br.is_read, m.first_name, m.last_name, m.email
            FROM broadcast_recipients br
            JOIN members m ON br.member_id = m.id
            WHERE br.broadcast_id = %s
        """, (broadcast_id,))
        
        broadcast_recipients = cursor.fetchall()
        print(f"\nRecipients for broadcast {broadcast_id}: {len(broadcast_recipients)}")
        for br in broadcast_recipients:
            print(f"  Member ID: {br[1]}, Name: {br[3]} {br[4]}, Email: {br[5]}, Read: {br[2]}")
        
        # Get notifications for this broadcast
        cursor.execute("""
            SELECT n.id, n.recipient_id, n.title, n.message, n.is_read
            FROM notifications n
            WHERE n.notification_type = 'broadcast_message' AND n.reference_id = %s
        """, (broadcast_id,))
        
        broadcast_notifications = cursor.fetchall()
        print(f"\nNotifications for broadcast {broadcast_id}: {len(broadcast_notifications)}")
        for n in broadcast_notifications:
            print(f"  Notification ID: {n[0]}, Recipient ID: {n[1]}, Title: {n[2]}, Read: {n[4]}")
        
        cursor.close()
        connection.close()
        
        return broadcast_id, gym_id, broadcast_recipients[0][1] if broadcast_recipients else None
    
    cursor.close()
    connection.close()
    return None, None, None

def test_member_messages_api():
    """Test the member messages API endpoint"""
    print("\n" + "="*60)
    print("STEP 2: Test Member Messages API")
    print("="*60)
    
    # First, get a member with password
    connection = get_db_connection()
    cursor = connection.cursor()
    
    cursor.execute("""
        SELECT m.id, m.email, m.gym_id
        FROM members m
        WHERE m.password_hash IS NOT NULL
        LIMIT 1
    """)
    
    member = cursor.fetchone()
    
    if not member:
        print("✗ No member with password found")
        cursor.close()
        connection.close()
        return None
    
    member_id, email, gym_id = member
    print(f"Found member: {email} (ID: {member_id}, Gym ID: {gym_id})")
    
    cursor.close()
    connection.close()
    
    # Now test the API (we'll need to login first, but let's just check the endpoint exists)
    import requests
    
    try:
        # Try without auth first to see if endpoint exists
        response = requests.get('http://127.0.0.1:5000/api/broadcasts/member')
        print(f"\nWithout auth - Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        return member_id, gym_id
    except Exception as e:
        print(f"✗ Error: {e}")
        return None

def test_notification_api():
    """Test the notification API endpoint"""
    print("\n" + "="*60)
    print("STEP 3: Test Notification API")
    print("="*60)
    
    import requests
    
    try:
        # Try without auth first
        response = requests.get('http://127.0.0.1:5000/api/notifications')
        print(f"\nWithout auth - Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"✗ Error: {e}")

def compare_api_queries():
    """Compare the SQL queries used by both APIs"""
    print("\n" + "="*60)
    print("STEP 4: Compare API SQL Queries")
    print("="*60)
    
    print("\nNOTIFICATION API Query (from notifications.py line 58-63):")
    print("""
    elif role == 'member':
        query = query.filter(
            Notification.recipient_role == 'member',
            Notification.recipient_id == member_id
        )
    """)
    print("Table: notifications")
    print("Filter: recipient_role='member' AND recipient_id=member_id")
    
    print("\nMESSAGES API Query (from broadcasts.py line 299-306):")
    print("""
    query = BroadcastMessage.query.join(BroadcastRecipient).filter(
        BroadcastRecipient.member_id == member_id
    )
    
    if gym_id:
        query = query.filter(BroadcastMessage.gym_id == gym_id)
    """)
    print("Tables: broadcast_messages JOIN broadcast_recipients")
    print("Filter: broadcast_recipients.member_id = member_id AND broadcast_messages.gym_id = gym_id")
    
    print("\nKEY DIFFERENCE:")
    print("- Notifications: Direct query on notifications table by recipient_id")
    print("- Messages: JOIN query on broadcast_messages + broadcast_recipients by member_id AND gym_id")

if __name__ == "__main__":
    print("="*60)
    print("Broadcast Message Flow Investigation")
    print("="*60)
    
    # Step 1: Database investigation
    broadcast_id, gym_id, member_id = investigate_database()
    
    # Step 2: Test member messages API
    test_member_messages_api()
    
    # Step 3: Test notification API
    test_notification_api()
    
    # Step 4: Compare API queries
    compare_api_queries()
    
    print("\n" + "="*60)
    print("INVESTIGATION COMPLETE")
    print("="*60)
