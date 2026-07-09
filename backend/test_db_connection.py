#!/usr/bin/env python3
"""
Test database connection and registration workflow
"""

import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app import create_app
from app.extensions import db
from app.models import User, Gym

def test_db_connection():
    """Test basic database connection"""
    app = create_app()
    
    with app.app_context():
        try:
            # Test basic connection using modern SQLAlchemy API
            from sqlalchemy import text
            with db.engine.begin() as conn:
                result = conn.execute(text("SELECT 1"))
                print("✅ Database connection successful")
            
            # Test table existence
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"✅ Found tables: {tables}")
            
            # Test if required tables exist
            required_tables = ['gyms', 'users']
            missing_tables = [table for table in required_tables if table not in tables]
            
            if missing_tables:
                print(f"⚠️  Missing tables: {missing_tables}")
                print("Creating missing tables...")
                db.create_all()
                print("✅ Tables created successfully")
            else:
                print("✅ All required tables exist")
            
            return True
            
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False

def test_registration_workflow():
    """Test the registration workflow"""
    app = create_app()
    
    with app.app_context():
        try:
            # Clean up any existing test data
            test_email = "test@testgym.com"
            existing_user = User.query.filter_by(email=test_email).first()
            if existing_user:
                db.session.delete(existing_user)
                if existing_user.gym_id:
                    existing_gym = Gym.query.get(existing_user.gym_id)
                    if existing_gym:
                        db.session.delete(existing_gym)
                db.session.commit()
            
            # Create test gym
            test_gym = Gym(
                name="Test Gym",
                address="123 Test Street",
                phone="555-0123"
            )
            db.session.add(test_gym)
            db.session.flush()  # Get the ID
            
            # Create test user
            from app.extensions import bcrypt
            password_hash = bcrypt.generate_password_hash("testpass123").decode('utf-8')
            test_user = User(
                name="Test Owner",
                email=test_email,
                password_hash=password_hash,
                role="gym_owner",
                gym_id=test_gym.id
            )
            db.session.add(test_user)
            db.session.commit()
            
            print("✅ Test registration workflow successful")
            
            # Clean up
            db.session.delete(test_user)
            db.session.delete(test_gym)
            db.session.commit()
            
            return True
            
        except Exception as e:
            print(f"❌ Registration workflow failed: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    print("🏋️‍♂️ Testing Gym Registration System")
    print("=" * 40)
    
    # Test database connection
    if test_db_connection():
        # Test registration workflow
        test_registration_workflow()
    else:
        print("❌ Cannot proceed with registration test due to database connection issues")