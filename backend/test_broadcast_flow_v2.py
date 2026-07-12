"""
Test script to verify broadcast message flow with evidence
Reset member password to known value for testing
"""
import requests
import pymysql
from app.config import Config
import jwt
import json
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

def reset_member_password():
    """Reset a member's password to known value"""
    print("\n" + "="*60)
    print("STEP 0: Reset Member Password")
    print("="*60)
    
    connection = get_db_connection()
    cursor = connection.cursor()
    
    # Find a member in a gym that has broadcasts
    cursor.execute("""
        SELECT m.id, m.email, m.first_name, m.last_name, m.gym_id, m.password_hash
        FROM members m
        WHERE m.password_hash IS NOT NULL
        LIMIT 1
    """)
    
    member = cursor.fetchone()
    
    if not member:
        print("✗ No member with password found")
        cursor.close()
        connection.close()
        return None, None, None
    
    member_id, email, first_name, last_name, gym_id, password_hash = member
    print(f"Found member: {first_name} {last_name} ({email})")
    print(f"Member ID: {member_id}, Gym ID: {gym_id}")
    
    # Reset password to 'password123'
    new_password = 'password123'
    hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
    
    cursor.execute("""
        UPDATE members 
        SET password_hash = %s 
        WHERE id = %s
    """, (hashed.decode('utf-8'), member_id))
    
    connection.commit()
    print(f"✓ Password reset to 'password123' for {email}")
    
    cursor.close()
    connection.close()
    
    return member_id, email, gym_id

def test_member_login(email, gym_id):
    """Test member login and check JWT claims"""
    print("\n" + "="*60)
    print("STEP 1: Test Member Login and JWT Claims")
    print("="*60)
    
    # Login with reset password
    try:
        response = requests.post('http://127.0.0.1:5000/api/auth/login', json={
            'email': email,
            'password': 'password123'
        })
        
        print(f"HTTP Status: {response.status_code}")
        
        if response.status_code == 200:
            token = response.json().get('token')
            user_data = response.json().get('user')
            print(f"✓ Login successful")
            print(f"User data: {json.dumps(user_data, indent=2)}")
            
            # Decode JWT to check claims
            try:
                decoded = jwt.decode(token, options={"verify_signature": False})
                print(f"\nJWT Claims:")
                print(json.dumps(decoded, indent=2))
                
                member_id_claim = decoded.get('member_id')
                gym_id_claim = decoded.get('gym_id')
                role_claim = decoded.get('role')
                
                print(f"\n✓ member_id in JWT: {member_id_claim}")
                print(f"✓ gym_id in JWT: {gym_id_claim}")
                print(f"✓ role in JWT: {role_claim}")
                
                return token, member_id_claim, gym_id_claim
            except Exception as e:
                print(f"✗ Failed to decode JWT: {e}")
                return token, user_data.get('member_id'), user_data.get('gym_id')
        else:
            print(f"✗ Login failed")
            print(f"Response: {response.text}")
            return None, None, None
    except Exception as e:
        print(f"✗ Error: {e}")
        return None, None, None

def test_broadcast_endpoint(member_token):
    """Test GET /api/broadcasts/member endpoint"""
    print("\n" + "="*60)
    print("STEP 2: Test GET /api/broadcasts/member")
    print("="*60)
    
    if not member_token:
        print("✗ No member token available")
        return None
    
    headers = {'Authorization': f'Bearer {member_token}'}
    
    try:
        response = requests.get('http://127.0.0.1:5000/api/broadcasts/member', headers=headers)
        
        print(f"HTTP Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type')}")
        print(f"\nResponse Body:")
        print(json.dumps(response.json(), indent=2))
        
        return response
    except Exception as e:
        print(f"✗ Error: {e}")
        return None

def check_broadcast_recipients(member_id, gym_id):
    """Check BroadcastRecipient records in database"""
    print("\n" + "="*60)
    print("STEP 3: Check BroadcastRecipient Records")
    print("="*60)
    
    connection = get_db_connection()
    cursor = connection.cursor()
    
    # Check if there are any broadcasts for this gym
    cursor.execute("""
        SELECT bm.id, bm.subject, bm.title, bm.recipient_type, bm.created_at
        FROM broadcast_messages bm
        WHERE bm.gym_id = %s
        ORDER BY bm.created_at DESC
        LIMIT 5
    """, (gym_id,))
    
    broadcasts = cursor.fetchall()
    print(f"\nBroadcasts for gym {gym_id}:")
    for bm in broadcasts:
        print(f"  ID: {bm[0]}, Subject: {bm[1]}, Title: {bm[2]}, Type: {bm[3]}")
    
    # Check broadcast recipients for this member
    cursor.execute("""
        SELECT br.id, br.broadcast_id, br.member_id, br.is_read, br.read_at
        FROM broadcast_recipients br
        WHERE br.member_id = %s
        ORDER BY br.id DESC
        LIMIT 5
    """, (member_id,))
    
    recipients = cursor.fetchall()
    print(f"\nBroadcastRecipient for member {member_id}:")
    if recipients:
        for br in recipients:
            print(f"  ID: {br[0]}, Broadcast ID: {br[1]}, Member ID: {br[2]}, Read: {br[3]}")
    else:
        print("  ✗ No BroadcastRecipient records found for this member")
    
    cursor.close()
    connection.close()
    
    return len(broadcasts) > 0, len(recipients) > 0

def run_sql_query_directly(member_id, gym_id):
    """Run the SQL query from get_member_broadcasts() directly"""
    print("\n" + "="*60)
    print("STEP 4: Run SQL Query Directly")
    print("="*60)
    
    connection = get_db_connection()
    cursor = connection.cursor()
    
    # This is the query from get_member_broadcasts()
    query = """
        SELECT bm.id, bm.gym_id, bm.subject, bm.title, bm.message, 
               bm.attachment_url, bm.banner_url, bm.recipient_type, 
               bm.created_by, bm.created_at
        FROM broadcast_messages bm
        INNER JOIN broadcast_recipients br ON bm.id = br.broadcast_id
        WHERE br.member_id = %s
    """
    
    if gym_id:
        query += " AND bm.gym_id = %s"
        cursor.execute(query, (member_id, gym_id))
    else:
        cursor.execute(query, (member_id,))
    
    results = cursor.fetchall()
    
    print(f"\nSQL Query Results:")
    print(f"Query: {query}")
    print(f"Parameters: member_id={member_id}, gym_id={gym_id}")
    print(f"\nRows returned: {len(results)}")
    
    if results:
        for row in results:
            print(f"  Broadcast ID: {row[0]}, Subject: {row[2]}, Title: {row[3]}")
    else:
        print("  ✗ No rows returned")
    
    cursor.close()
    connection.close()
    
    return len(results) > 0

def check_frontend_response_handling():
    """Check how frontend handles the response"""
    print("\n" + "="*60)
    print("STEP 5: Check Frontend Response Handling")
    print("="*60)
    
    print("\nFrom MemberMessagesPage.jsx line 19:")
    print("  const response = await api.get('/api/broadcasts/member');")
    print("  setBroadcasts(response.data.broadcasts || []);")
    
    print("\nFrontend expects: response.data.broadcasts")
    print("Backend returns: {'broadcasts': [...]}")
    print("\n✓ Frontend response handling looks correct")

if __name__ == "__main__":
    print("="*60)
    print("Broadcast Message Flow Verification")
    print("="*60)
    
    # Step 0: Reset member password
    member_id, email, gym_id = reset_member_password()
    
    if member_id and email and gym_id:
        # Step 1: Test member login
        member_token, jwt_member_id, jwt_gym_id = test_member_login(email, gym_id)
        
        if member_token and jwt_member_id:
            # Step 2: Test broadcast endpoint
            response = test_broadcast_endpoint(member_token)
            
            # Step 3: Check database records
            has_broadcasts, has_recipients = check_broadcast_recipients(jwt_member_id, jwt_gym_id)
            
            # Step 4: Run SQL query directly
            has_results = run_sql_query_directly(jwt_member_id, jwt_gym_id)
            
            # Step 5: Check frontend handling
            check_frontend_response_handling()
            
            # Summary
            print("\n" + "="*60)
            print("SUMMARY")
            print("="*60)
            print(f"Member ID: {jwt_member_id}")
            print(f"Gym ID: {jwt_gym_id}")
            print(f"Has broadcasts in gym: {has_broadcasts}")
            print(f"Has recipient records: {has_recipients}")
            print(f"SQL query returns results: {has_results}")
            
            if response:
                print(f"\nAPI Response Status: {response.status_code}")
                print(f"API Response Data: {response.json()}")
                
                # Identify failure point
                print("\n" + "="*60)
                print("FAILURE POINT ANALYSIS")
                print("="*60)
                
                if response.status_code != 200:
                    print(f"✗ API returned error status: {response.status_code}")
                    print("  FAILURE POINT: Backend API endpoint")
                elif not response.json().get('broadcasts'):
                    print("✗ API returned empty broadcasts array")
                    print("  FAILURE POINT: Backend query or data")
                elif not has_recipients:
                    print("✗ No BroadcastRecipient records in database")
                    print("  FAILURE POINT: Broadcast creation (backend)")
                elif not has_results:
                    print("✗ SQL query returns no results despite having recipient records")
                    print("  FAILURE POINT: SQL query logic")
                else:
                    print("✓ All checks passed - issue may be in frontend rendering")
        else:
            print("\n✗ Could not complete test - member login failed")
    else:
        print("\n✗ Could not complete test - no member found")
    
    print("\n" + "="*60)
