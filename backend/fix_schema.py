"""
Script to fix database schema by adding missing columns
"""
import pymysql
from app.config import Config

def fix_database_schema():
    """Add missing columns to database tables"""
    try:
        # Parse database URL
        db_url = Config.SQLALCHEMY_DATABASE_URI
        # Format: mysql+pymysql://user:password@host:port/database
        # Extract components
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
        
        # Check if workout_duration_minutes column exists in members table
        cursor.execute("SHOW COLUMNS FROM members LIKE 'workout_duration_minutes'")
        result = cursor.fetchone()
        
        if result:
            print("✓ Column workout_duration_minutes already exists in members table")
        else:
            print("✗ Column workout_duration_minutes NOT found in members table")
            print("  Adding workout_duration_minutes column...")
            cursor.execute("""
                ALTER TABLE members 
                ADD COLUMN workout_duration_minutes INT DEFAULT 120 NULL
            """)
            print("  ✓ Added workout_duration_minutes column with default value 120")
        
        # Check if expected_finish_time column exists in attendance table
        cursor.execute("SHOW COLUMNS FROM attendance LIKE 'expected_finish_time'")
        result = cursor.fetchone()
        
        if result:
            print("✓ Column expected_finish_time already exists in attendance table")
        else:
            print("✗ Column expected_finish_time NOT found in attendance table")
            print("  Adding expected_finish_time column...")
            cursor.execute("""
                ALTER TABLE attendance 
                ADD COLUMN expected_finish_time DATETIME NULL
            """)
            print("  ✓ Added expected_finish_time column")
        
        # Check if timeout_notification_sent column exists in attendance table
        cursor.execute("SHOW COLUMNS FROM attendance LIKE 'timeout_notification_sent'")
        result = cursor.fetchone()
        
        if result:
            print("✓ Column timeout_notification_sent already exists in attendance table")
        else:
            print("✗ Column timeout_notification_sent NOT found in attendance table")
            print("  Adding timeout_notification_sent column...")
            cursor.execute("""
                ALTER TABLE attendance 
                ADD COLUMN timeout_notification_sent BOOLEAN DEFAULT FALSE
            """)
            print("  ✓ Added timeout_notification_sent column with default value FALSE")
        
        # Update existing members to have default value if NULL
        cursor.execute("""
            UPDATE members 
            SET workout_duration_minutes = 120 
            WHERE workout_duration_minutes IS NULL
        """)
        updated_rows = cursor.rowcount
        print(f"✓ Updated {updated_rows} existing members with default workout duration (120 minutes)")
        
        # Commit changes
        connection.commit()
        print("\n✓ Database schema updated successfully!")
        
        # Verify the schema
        print("\nVerifying members table structure:")
        cursor.execute("DESCRIBE members")
        for row in cursor.fetchall():
            print(f"  {row[0]}: {row[1]}")
        
        print("\nVerifying attendance table structure:")
        cursor.execute("DESCRIBE attendance")
        for row in cursor.fetchall():
            print(f"  {row[0]}: {row[1]}")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    if fix_database_schema():
        print("\n✓ Schema fix completed successfully!")
        print("Please restart the backend server.")
    else:
        print("\n✗ Schema fix failed!")
