#!/usr/bin/env python3
"""
Add password_changed field to members table
"""
import os
import sys
from sqlalchemy import text

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db

def add_password_changed_field():
    """Add password_changed field to members table"""
    app = create_app()
    
    with app.app_context():
        try:
            # Check if password_changed column already exists
            try:
                result = db.session.execute(text("DESCRIBE members"))
                columns = [row[0] for row in result.fetchall()]
                if 'password_changed' in columns:
                    print("✓ Password changed field already exists in members table")
                    return True
            except:
                pass
            
            # Add password_changed column
            try:
                db.session.execute(text("ALTER TABLE members ADD COLUMN password_changed BOOLEAN DEFAULT FALSE NOT NULL"))
                print("✓ Added password_changed column to members table")
            except Exception as e:
                if "Duplicate column" in str(e):
                    print("✓ Password changed column already exists")
                else:
                    raise e
            
            db.session.commit()
            print("\n✅ Member password_changed field added successfully!")
            return True
            
        except Exception as e:
            print(f"\n❌ Failed to add password_changed field: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    success = add_password_changed_field()
    sys.exit(0 if success else 1)