"""
Test script to verify database schema is synchronized with SQLAlchemy models
"""
import pymysql
from app.config import Config

def test_schema_sync():
    """Verify database schema matches SQLAlchemy models"""
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
        
        print("\n" + "=" * 60)
        print("Database Schema Verification")
        print("=" * 60)
        
        # Check members table columns
        print("\nMembers Table Columns:")
        cursor.execute("DESCRIBE members")
        members_columns = [row[0] for row in cursor.fetchall()]
        
        required_members_columns = [
            'id', 'gym_id', 'member_id', 'first_name', 'last_name', 'gender',
            'date_of_birth', 'phone', 'email', 'address', 'emergency_contact_name',
            'emergency_contact_phone', 'medical_notes', 'membership_plan_name',
            'membership_start_date', 'membership_end_date', 'status',
            'workout_duration_minutes', 'photo', 'created_at', 'updated_at',
            'password_hash', 'password_changed'
        ]
        
        for col in required_members_columns:
            if col in members_columns:
                print(f"  ✓ {col}")
            else:
                print(f"  ✗ {col} - MISSING!")
        
        # Check attendance table columns
        print("\nAttendance Table Columns:")
        cursor.execute("DESCRIBE attendance")
        attendance_columns = [row[0] for row in cursor.fetchall()]
        
        required_attendance_columns = [
            'id', 'gym_id', 'member_id', 'check_in_time', 'check_out_time',
            'expected_finish_time', 'timeout_notification_sent',
            'attendance_date', 'status', 'notes', 'created_at', 'updated_at'
        ]
        
        for col in required_attendance_columns:
            if col in attendance_columns:
                print(f"  ✓ {col}")
            else:
                print(f"  ✗ {col} - MISSING!")
        
        # Test a simple query to verify no SQL errors
        print("\nTesting SQL Queries:")
        try:
            cursor.execute("SELECT COUNT(*) FROM members")
            count = cursor.fetchone()[0]
            print(f"  ✓ Members table query successful - {count} members")
        except Exception as e:
            print(f"  ✗ Members table query failed: {str(e)}")
        
        try:
            cursor.execute("SELECT COUNT(*) FROM attendance")
            count = cursor.fetchone()[0]
            print(f"  ✓ Attendance table query successful - {count} records")
        except Exception as e:
            print(f"  ✗ Attendance table query failed: {str(e)}")
        
        # Check workout_duration_minutes values
        try:
            cursor.execute("""
                SELECT COUNT(*) FROM members 
                WHERE workout_duration_minutes IS NULL
            """)
            null_count = cursor.fetchone()[0]
            if null_count == 0:
                print(f"  ✓ All members have workout_duration_minutes set")
            else:
                print(f"  ⚠ {null_count} members have NULL workout_duration_minutes")
        except Exception as e:
            print(f"  ✗ Failed to check workout_duration_minutes: {str(e)}")
        
        cursor.close()
        connection.close()
        
        print("\n" + "=" * 60)
        print("✓ Database schema verification completed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    test_schema_sync()
