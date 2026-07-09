#!/usr/bin/env python3
"""Create a test super admin"""

import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app import create_app
from app.extensions import db, bcrypt
from app.models import User

def create_super_admin():
    app = create_app()
    
    with app.app_context():
        # Check if super admin already exists
        super_admin_email = "superadmin@flexigym.com"
        existing = User.query.filter_by(email=super_admin_email).first()
        if existing:
            print("Super admin already exists")
            return
        
        # Create super admin
        password_hash = bcrypt.generate_password_hash("SuperPass123!").decode('utf-8')
        super_admin = User(
            name="Super Admin",
            email=super_admin_email,
            password_hash=password_hash,
            role="super_admin",
            gym_id=None  # Super admin has no gym
        )
        db.session.add(super_admin)
        db.session.commit()
        print("Created super admin: superadmin@flexigym.com / SuperPass123!")

if __name__ == "__main__":
    create_super_admin()
