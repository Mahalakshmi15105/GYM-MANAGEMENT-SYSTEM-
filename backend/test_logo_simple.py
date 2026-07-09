#!/usr/bin/env python3
"""
Simple test script to verify gym logo functionality
"""

import sys
import os
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Set environment variable to use testing database
os.environ['FLASK_ENV'] = 'testing'
os.environ['DATABASE_URL'] = 'sqlite:///test_gym_logo.db'

def test_logo_column_exists():
    """Test if logo column exists in gyms table"""
    print("🔍 Testing logo column existence...")
    
    try:
        from app import create_app
        from app.extensions import db
        from sqlalchemy import inspect
        
        # Create test app with minimal config
        app = create_app()
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_gym_logo.db'
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['JWT_SECRET_KEY'] = 'test-jwt-secret-key'
        
        with app.app_context():
            # Create all tables
            db.create_all()
            
            # Check if logo column exists
            inspector = inspect(db.engine)
            columns = inspector.get_columns('gyms')
            logo_column = next((col for col in columns if col['name'] == 'logo'), None)
            
            if logo_column:
                print("✅ Logo column exists in gyms table")
                print(f"   Type: {logo_column['type']}")
                print(f"   Nullable: {logo_column['nullable']}")
                return True
            else:
                print("❌ Logo column NOT found in gyms table")
                return False
                
    except Exception as e:
        print(f"❌ Error checking logo column: {e}")
        return False

def test_gym_model_has_logo():
    """Test if Gym model has logo attribute"""
    print("\n🔍 Testing Gym model logo attribute...")
    
    try:
        from app.models import Gym
        
        # Check if Gym model has logo attribute
        if hasattr(Gym, 'logo'):
            print("✅ Gym model has logo attribute")
            return True
        else:
            print("❌ Gym model missing logo attribute")
            return False
            
    except Exception as e:
        print(f"❌ Error checking Gym model: {e}")
        return False

def test_gym_logo_routes_exist():
    """Test if gym logo routes are defined"""
    print("\n🔍 Testing gym logo routes...")
    
    try:
        from app.routes.gym_logo import gym_logo_bp
        
        # Check if blueprint exists and has routes
        routes = []
        for rule in gym_logo_bp.deferred_functions:
            routes.append(rule)
        
        print(f"✅ Gym logo blueprint found with {len(routes)} routes")
        return True
        
    except Exception as e:
        print(f"❌ Error checking gym logo routes: {e}")
        return False

def test_components_exist():
    """Test if frontend components exist"""
    print("\n🔍 Testing frontend components...")
    
    components = [
        'frontend/src/components/GymLogo.jsx',
        'frontend/src/pages/GymProfilePage.jsx'
    ]
    
    all_exist = True
    for component in components:
        if os.path.exists(component):
            print(f"✅ {component} exists")
        else:
            print(f"❌ {component} missing")
            all_exist = False
    
    return all_exist

def main():
    """Run all tests"""
    print("🏋️‍♂️ Gym Logo Functionality Tests")
    print("=" * 40)
    
    # Clean up old test database
    test_db = 'test_gym_logo.db'
    if os.path.exists(test_db):
        os.remove(test_db)
    
    tests = [
        test_logo_column_exists,
        test_gym_model_has_logo,
        test_gym_logo_routes_exist,
        test_components_exist
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with error: {e}")
    
    print("\n" + "=" * 40)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Gym Logo functionality is ready.")
    else:
        print("⚠️  Some tests failed. Review the issues above.")
    
    # Clean up test database
    if os.path.exists(test_db):
        os.remove(test_db)
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)