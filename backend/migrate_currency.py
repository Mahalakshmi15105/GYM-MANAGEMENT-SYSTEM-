#!/usr/bin/env python3
"""
Quick migration to add currency column to gyms table
"""

from app import create_app
from app.extensions import db
from sqlalchemy import text

def migrate():
    app = create_app()
    with app.app_context():
        try:
            # Add currency column
            db.session.execute(text("ALTER TABLE gyms ADD COLUMN currency VARCHAR(3) DEFAULT 'INR'"))
            db.session.commit()
            print("✓ Added currency column")
            
            # Update existing gyms
            db.session.execute(text("UPDATE gyms SET currency = 'INR' WHERE currency IS NULL"))
            db.session.commit()
            print("✓ Updated existing gyms")
            
            print("Migration completed successfully!")
            
        except Exception as e:
            db.session.rollback()
            print(f"Migration failed: {e}")

if __name__ == "__main__":
    migrate()