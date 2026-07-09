#!/usr/bin/env python3
"""
Add password_hash field to members table for Member Account Creation feature
"""
import os
import sys
from sqlalchemy import text

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db

def add_member_password_field():
    """Add password_hash field to members table"""
    app = create_app()
    
    with app.app_context():
        try:
            # Check if password_hash column already exists
            try:
                result = db.session.execute(text("DESCRIBE members"))
                columns = [row[0] for row in result.fetchall()]
                if 'password_hash' in columns:
                    print("✓ Password hash field already exists in members table")
                    return True
            except:
                pass
            
            # Add password_hash column
            try:
                db.session.execute(text("ALTER TABLE members ADD COLUMN password_hash VARCHAR(255) NULL"))
                print("✓ Added password_hash column to members table")
            except Exception as e:
                if "Duplicate column" in str(e):
                    print("✓ Password hash column already exists")
                else:
                    raise e
            
            db.session.commit()
            print("\n✅ Member password field added successfully!")
            return True
            
        except Exception as e:
            print(f"\n❌ Failed to add member password field: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    success = add_member_password_field()
    sys.exit(0 if success else 1)