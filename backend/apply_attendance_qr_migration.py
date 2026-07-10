#!/usr/bin/env python3
"""
Apply the attendance QR migration to the database
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db
from sqlalchemy import text

def apply_migration():
    """Apply the attendance QR migration"""
    app = create_app()
    
    with app.app_context():
        try:
            # Read the migration file
            migration_file = 'migrations/004_add_attendance_qr.sql'
            with open(migration_file, 'r') as f:
                migration_sql = f.read()
            
            # Split the migration into individual statements
            statements = [stmt.strip() for stmt in migration_sql.split(';') if stmt.strip()]
            
            # Execute each statement
            conn = db.engine.connect()
            for statement in statements:
                if statement.startswith('--') or not statement:
                    continue
                try:
                    conn.execute(text(statement))
                    conn.commit()
                    print(f"✓ Executed: {statement[:50]}...")
                except Exception as e:
                    if "Duplicate column name" in str(e):
                        print(f"⚠ Column already exists, skipping: {statement[:50]}...")
                    else:
                        print(f"✗ Error executing: {statement[:50]}...")
                        print(f"  Error: {e}")
                        raise
            conn.close()
            
            print("Migration completed successfully!")
            return True
            
        except Exception as e:
            print(f"Migration failed: {e}")
            return False

if __name__ == '__main__':
    success = apply_migration()
    sys.exit(0 if success else 1)
