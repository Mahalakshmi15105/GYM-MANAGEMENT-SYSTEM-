#!/usr/bin/env python3
"""
Database migration script to add the logo column to the gyms table.
This script safely adds the missing logo column using SQLAlchemy's modern API.
"""

import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app import create_app
from app.extensions import db
from sqlalchemy import text, inspect

def check_column_exists(table_name, column_name):
    """Check if a column exists in a table"""
    inspector = inspect(db.engine)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns

def add_logo_column():
    """Add the logo column to the gyms table if it doesn't exist"""
    app = create_app()
    
    with app.app_context():
        try:
            # Check if the logo column already exists
            if check_column_exists('gyms', 'logo'):
                print("✅ Logo column already exists in gyms table")
                return True
            
            print("🔧 Adding logo column to gyms table...")
            
            # Use SQLAlchemy's text() with modern API
            with db.engine.begin() as conn:
                # Add the logo column
                conn.execute(text("ALTER TABLE gyms ADD COLUMN logo VARCHAR(500) NULL"))
                print("✅ Logo column added successfully")
                
                # Add comment for clarity (optional, may not work on all MySQL versions)
                try:
                    conn.execute(text("ALTER TABLE gyms MODIFY COLUMN logo VARCHAR(500) NULL COMMENT 'Path to gym logo image file'"))
                    print("✅ Column comment added successfully")
                except Exception as comment_error:
                    print(f"⚠️  Could not add column comment (non-critical): {comment_error}")
            
            # Verify the column was added
            if check_column_exists('gyms', 'logo'):
                print("✅ Logo column verification passed")
                return True
            else:
                print("❌ Logo column verification failed")
                return False
                
        except Exception as e:
            print(f"❌ Error adding logo column: {e}")
            return False

if __name__ == "__main__":
    print("🏋️‍♂️ Gym Logo Column Migration Script")
    print("=" * 40)
    
    success = add_logo_column()
    
    if success:
        print("\n🎉 Migration completed successfully!")
        print("The gym logo functionality should now work properly.")
    else:
        print("\n💥 Migration failed!")
        print("Please check the error messages above and try again.")
    
    sys.exit(0 if success else 1)