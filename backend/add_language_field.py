#!/usr/bin/env python3
"""
Add language field to gym table
"""
import os
import sys
from sqlalchemy import text

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db

def add_language_field():
    """Add language field to gym table"""
    app = create_app()
    
    with app.app_context():
        try:
            # Check if language column already exists
            try:
                result = db.session.execute(text("DESCRIBE gyms"))
                columns = [row[0] for row in result.fetchall()]
                if 'language' in columns:
                    print("✓ Language field already exists in gyms table")
                    return True
            except:
                pass
            
            # Add language column
            try:
                db.session.execute(text("ALTER TABLE gyms ADD COLUMN language VARCHAR(5) DEFAULT 'en'"))
                print("✓ Added language column to gyms table")
            except Exception as e:
                if "Duplicate column" in str(e):
                    print("✓ Language column already exists")
                else:
                    raise e
            
            # Update existing records
            try:
                db.session.execute(text("UPDATE gyms SET language = 'en' WHERE language IS NULL"))
                print("✓ Updated existing gyms with default language")
            except Exception as e:
                print(f"⚠ Could not update existing records: {e}")
            
            db.session.commit()
            print("\n✅ Language field added successfully!")
            return True
            
        except Exception as e:
            print(f"\n❌ Failed to add language field: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    success = add_language_field()
    sys.exit(0 if success else 1)