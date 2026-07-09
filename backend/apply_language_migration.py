#!/usr/bin/env python3
"""
Apply language migration to add language field to gym table
"""
import os
import sys
from sqlalchemy import text

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db

def apply_language_migration():
    """Apply the language migration"""
    app = create_app()
    
    with app.app_context():
        try:
            migration_path = os.path.join(os.path.dirname(__file__), 'migrations', '003_add_language_to_gym.sql')
            
            with open(migration_path, 'r') as f:
                migration_sql = f.read()
            
            # Split by statements and execute each
            statements = [stmt.strip() for stmt in migration_sql.split(';') if stmt.strip()]
            
            for statement in statements:
                if statement.strip():
                    try:
                        db.session.execute(text(statement))
                        print(f"✓ Executed: {statement[:50]}...")
                    except Exception as e:
                        if "already exists" in str(e) or "duplicate" in str(e).lower():
                            print(f"⚠ Skipped (already exists): {statement[:50]}...")
                        else:
                            print(f"✗ Failed: {statement[:50]}...")
                            print(f"  Error: {e}")
            
            db.session.commit()
            print("\n✅ Language migration applied successfully!")
            return True
            
        except Exception as e:
            print(f"\n❌ Migration failed: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    success = apply_language_migration()
    sys.exit(0 if success else 1)