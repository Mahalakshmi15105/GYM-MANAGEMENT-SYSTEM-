#!/usr/bin/env python3
"""
Simple test for registration endpoint without Super Admin dependencies
"""

import os
import sys
import json
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app import create_app

def test_registration_endpoint():
    """Test registration endpoint directly"""
    app = create_app()
    client = app.test_client()
    
    # Test data
    test_data = {
        "gym_name": "Test Gym Registration",
        "gym_address": "123 Test Street, Test City",
        "gym_phone": "555-0123",
        "name": "Test Owner",
        "email": "testowner@testgym.com",
        "password": "testpass123"
    }
    
    try:
        print("🔄 Testing registration endpoint...")
        
        # Make registration request
        response = client.post(
            '/api/auth/register',
            data=json.dumps(test_data),
            content_type='application/json'
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.get_json()}")
        
        if response.status_code == 201:
            print("✅ Registration successful!")
            return True
        else:
            print(f"❌ Registration failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Registration test failed: {e}")
        return False

def test_basic_db_connection():
    """Test basic database connection without creating tables"""
    app = create_app()
    
    with app.app_context():
        try:
            from sqlalchemy import text
            from app.extensions import db
            
            # Simple connection test
            with db.engine.begin() as conn:
                result = conn.execute(text("SELECT 1 as test"))
                row = result.fetchone()
                if row[0] == 1:
                    print("✅ Basic database connection works")
                    return True
                    
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False

if __name__ == "__main__":
    print("🏋️‍♂️ Testing Registration System (Simplified)")
    print("=" * 50)
    
    # Test basic connection
    if test_basic_db_connection():
        test_registration_endpoint()
    else:
        print("Cannot test registration due to database connection issues")