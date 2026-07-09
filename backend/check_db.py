#!/usr/bin/env python3
"""Simple database connection test"""

import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app import create_app
from app.extensions import db

def test_db():
    app = create_app()
    
    with app.app_context():
        try:
            from sqlalchemy import text
            with db.engine.begin() as conn:
                result = conn.execute(text("SELECT 1"))
                print("OK: Database connection successful")
            
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"OK: Found tables: {tables}")
            return True
            
        except Exception as e:
            print(f"ERROR: Database connection failed: {e}")
            import traceback
            print(traceback.format_exc())
            return False

if __name__ == "__main__":
    test_db()
