"""
Migration script to add missing columns for Gym Status feature
"""
from app import create_app
from app.extensions import db

def add_missing_columns():
    """Add missing columns to database tables if they don't exist"""
    app = create_app()
    
    with app.app_context():
        try:
            # Check and add last_login column to users table
            result = db.session.execute(db.text("""
                SELECT COUNT(*) 
                FROM information_schema.columns 
                WHERE table_schema = DATABASE() 
                AND table_name = 'users' 
                AND column_name = 'last_login'
            """))
            column_exists = result.scalar()
            
            if column_exists:
                print("Column 'last_login' already exists in users table")
            else:
                db.session.execute(db.text("""
                    ALTER TABLE users 
                    ADD COLUMN last_login DATETIME NULL
                """))
                db.session.commit()
                print("Successfully added 'last_login' column to users table")
            
            # Check and add status column to users table
            result = db.session.execute(db.text("""
                SELECT COUNT(*) 
                FROM information_schema.columns 
                WHERE table_schema = DATABASE() 
                AND table_name = 'users' 
                AND column_name = 'status'
            """))
            column_exists = result.scalar()
            
            if column_exists:
                print("Column 'status' already exists in users table")
            else:
                db.session.execute(db.text("""
                    ALTER TABLE users 
                    ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'Active'
                """))
                db.session.commit()
                print("Successfully added 'status' column to users table")
            
            # Check and add show_gym_status column to members table
            result = db.session.execute(db.text("""
                SELECT COUNT(*) 
                FROM information_schema.columns 
                WHERE table_schema = DATABASE() 
                AND table_name = 'members' 
                AND column_name = 'show_gym_status'
            """))
            column_exists = result.scalar()
            
            if column_exists:
                print("Column 'show_gym_status' already exists in members table")
            else:
                db.session.execute(db.text("""
                    ALTER TABLE members 
                    ADD COLUMN show_gym_status BOOLEAN NOT NULL DEFAULT TRUE
                """))
                db.session.commit()
                print("Successfully added 'show_gym_status' column to members table")
            
            # Check and add operational_status column to gyms table
            result = db.session.execute(db.text("""
                SELECT COUNT(*) 
                FROM information_schema.columns 
                WHERE table_schema = DATABASE() 
                AND table_name = 'gyms' 
                AND column_name = 'operational_status'
            """))
            column_exists = result.scalar()
            
            if column_exists:
                print("Column 'operational_status' already exists in gyms table")
            else:
                db.session.execute(db.text("""
                    ALTER TABLE gyms 
                    ADD COLUMN operational_status VARCHAR(20) NOT NULL DEFAULT 'Closed'
                """))
                db.session.commit()
                print("Successfully added 'operational_status' column to gyms table")
                
            print("\nAll missing columns have been added successfully!")
                
        except Exception as e:
            print(f"Error: {e}")
            db.session.rollback()
            raise

if __name__ == "__main__":
    add_missing_columns()
