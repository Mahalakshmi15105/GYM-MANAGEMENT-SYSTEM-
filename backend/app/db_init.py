"""
Database initialization module.
Handles automatic database creation, migrations, and seeding.
All functions are idempotent - safe to run multiple times.
"""

import pymysql
from sqlalchemy import inspect, text
from app.extensions import db, bcrypt
from app.models import User
from app.super_admin_models import PlatformSubscriptionPlan
import os


def create_database_if_not_exists():
    """Create MySQL database if it doesn't exist."""
    try:
        # Parse database URL
        database_url = os.getenv('DATABASE_URL', 'mysql+pymysql://root:password@localhost:3306/gym_db')
        
        # Extract connection details
        # Format: mysql+pymysql://user:password@host:port/database
        if 'mysql+pymysql://' in database_url:
            url_part = database_url.replace('mysql+pymysql://', '')
            # Split by @ to separate auth from host:port/database
            if '@' in url_part:
                auth_part, host_db_part = url_part.rsplit('@', 1)
                
                # Parse auth (user:password)
                if ':' in auth_part:
                    username, password = auth_part.split(':', 1)
                else:
                    username = auth_part
                    password = ''
                
                # Parse host:port/database
                if '/' in host_db_part:
                    host_port_part, db_name = host_db_part.split('/', 1)
                    
                    # Parse host:port
                    if ':' in host_port_part:
                        host, port_str = host_port_part.split(':', 1)
                        port = int(port_str)
                    else:
                        host = host_port_part
                        port = 3306  # Default MySQL port
                else:
                    host = host_db_part
                    port = 3306
                    db_name = 'gym_db'
            else:
                print("Could not parse DATABASE_URL format: missing @ separator")
                return False
        else:
            print("Could not parse DATABASE_URL format: missing mysql+pymysql:// prefix")
            return False
        
        # Connect without specifying database
        connection = pymysql.connect(
            host=host,
            port=port,
            user=username,
            password=password
        )
        
        cursor = connection.cursor()
        
        # Check if database exists
        cursor.execute(f"SHOW DATABASES LIKE '{db_name}'")
        result = cursor.fetchone()
        
        if not result:
            cursor.execute(f"CREATE DATABASE {db_name}")
            print(f"✓ Created database: {db_name}")
        else:
            print(f"✓ Database already exists: {db_name}")
        
        cursor.close()
        connection.close()
        return True
        
    except Exception as e:
        print(f"✗ Error creating database: {e}")
        return False


def apply_sql_migration(migration_sql, migration_name):
    """Apply a SQL migration safely (idempotent)."""
    try:
        # Split into individual statements
        statements = [stmt.strip() for stmt in migration_sql.split(';') if stmt.strip() and not stmt.strip().startswith('--')]
        
        for statement in statements:
            try:
                db.session.execute(text(statement))
                db.session.commit()
            except Exception as e:
                # Ignore duplicate column/index errors (idempotent)
                error_str = str(e).lower()
                if any(keyword in error_str for keyword in ["duplicate column", "duplicate entry", "duplicate key", "already exists"]):
                    pass  # Already exists, skip
                else:
                    # Rollback on other errors
                    db.session.rollback()
                    print(f"  ⚠ Skipping statement due to error: {str(e)[:100]}")
        
        print(f"✓ Applied migration: {migration_name}")
        return True
        
    except Exception as e:
        print(f"✗ Error applying migration {migration_name}: {e}")
        db.session.rollback()
        return False


def apply_all_migrations():
    """Apply all required SQL migrations in order."""
    migrations = [
        ('001_create_super_admin_tables.sql', 'Create Super Admin Tables'),
        ('002_enhance_gym_model.sql', 'Enhance Gym Model'),
        ('003_add_gym_currency.sql', 'Add Gym Currency'),
        ('003_add_gym_logo.sql', 'Add Gym Logo'),
        ('003_add_language_to_gym.sql', 'Add Language to Gym'),
        ('004_add_attendance_qr.sql', 'Add Attendance QR'),
    ]
    
    for filename, description in migrations:
        try:
            migration_path = os.path.join(os.path.dirname(__file__), '..', 'migrations', filename)
            with open(migration_path, 'r') as f:
                migration_sql = f.read()
            apply_sql_migration(migration_sql, description)
        except FileNotFoundError:
            print(f"⚠ Migration file not found: {filename}")
        except Exception as e:
            print(f"✗ Error reading migration {filename}: {e}")


def add_missing_columns():
    """Add any missing columns that newer features require (idempotent)."""
    column_additions = [
        # Members table
        ("members", "password_hash", "VARCHAR(255) NULL"),
        ("members", "created_at", "DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP"),
        ("members", "updated_at", "DATETIME NULL"),
        
        # Users table  
        ("users", "last_login", "DATETIME NULL"),
        
        # Gyms table
        ("gyms", "show_gym_status", "BOOLEAN DEFAULT TRUE"),
    ]
    
    inspector = inspect(db.engine)
    
    for table_name, column_name, column_def in column_additions:
        try:
            # Check if table exists
            if table_name not in inspector.get_table_names():
                continue
                
            # Check if column exists
            columns = [col['name'] for col in inspector.get_columns(table_name)]
            
            if column_name not in columns:
                db.session.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_def}"))
                db.session.commit()
                print(f"✓ Added column {column_name} to {table_name}")
            else:
                print(f"✓ Column {column_name} already exists in {table_name}")
                
        except Exception as e:
            if "Duplicate column" in str(e):
                pass  # Already exists
            else:
                print(f"✗ Error adding column {column_name} to {table_name}: {e}")
                db.session.rollback()


def create_super_admin_if_not_exists():
    """Create default super admin if doesn't exist (idempotent)."""
    try:
        super_admin_email = "superadmin@flexigym.com"
        existing = User.query.filter_by(email=super_admin_email).first()
        
        if existing:
            print("✓ Super admin already exists")
            return True
        
        password_hash = bcrypt.generate_password_hash("SuperPass123!").decode('utf-8')
        super_admin = User(
            name="Super Admin",
            email=super_admin_email,
            password_hash=password_hash,
            role="super_admin",
            gym_id=None
        )
        db.session.add(super_admin)
        db.session.commit()
        print("✓ Created super admin: superadmin@flexigym.com / SuperPass123!")
        return True
        
    except Exception as e:
        db.session.rollback()
        print(f"✗ Error creating super admin: {e}")
        return False


def seed_platform_plans_if_not_exists():
    """Seed default platform subscription plans if they don't exist (idempotent)."""
    try:
        existing_plans = PlatformSubscriptionPlan.query.all()
        if existing_plans:
            print("✓ Platform plans already exist")
            return True
        
        plans = [
            PlatformSubscriptionPlan(
                plan_name="Basic",
                price=499.00,
                currency="INR",
                billing_cycle="monthly",
                description="Perfect for small gyms",
                features=[
                    "Basic Member Management",
                    "Attendance Tracking",
                    "Payment Processing",
                    "Basic Reports"
                ],
                recommended=False,
                is_active=True
            ),
            PlatformSubscriptionPlan(
                plan_name="Pro",
                price=999.00,
                currency="INR",
                billing_cycle="monthly",
                description="Ideal for medium gyms",
                features=[
                    "Everything in Basic",
                    "Advanced Reports",
                    "Trainer Management",
                    "Notifications",
                    "Analytics Dashboard"
                ],
                recommended=True,
                is_active=True
            ),
            PlatformSubscriptionPlan(
                plan_name="Enterprise",
                price=2499.00,
                currency="INR",
                billing_cycle="monthly",
                description="Built for large gym chains",
                features=[
                    "Everything in Pro",
                    "Multi-Branch Support",
                    "Priority Support",
                    "Custom Branding",
                    "Advanced Analytics",
                    "API Access"
                ],
                recommended=False,
                is_active=True
            )
        ]
        
        for plan in plans:
            db.session.add(plan)
        
        db.session.commit()
        print("✓ Seeded platform subscription plans")
        return True
        
    except Exception as e:
        db.session.rollback()
        print(f"✗ Error seeding platform plans: {e}")
        return False


def populate_member_created_at_if_null():
    """Populate created_at for members where it's NULL (idempotent)."""
    try:
        from app.models import Member
        from datetime import datetime
        
        members_without_created_at = Member.query.filter(Member.created_at.is_(None)).all()
        
        if not members_without_created_at:
            print("✓ All members have created_at")
            return True
        
        for member in members_without_created_at:
            if member.membership_start_date:
                member.created_at = datetime.combine(member.membership_start_date, datetime.min.time())
            else:
                member.created_at = datetime.utcnow()
        
        db.session.commit()
        print(f"✓ Populated created_at for {len(members_without_created_at)} members")
        return True
        
    except Exception as e:
        db.session.rollback()
        print(f"✗ Error populating member created_at: {e}")
        return False


def initialize_database(app):
    """
    Run all database initialization steps in order.
    This function is idempotent - safe to run multiple times.
    """
    print("\n" + "="*60)
    print("DATABASE INITIALIZATION")
    print("="*60 + "\n")
    
    with app.app_context():
        # Step 1: Create database if it doesn't exist
        print("Step 1: Creating database if needed...")
        create_database_if_not_exists()
        print()
        
        # Step 2: Create all tables from models
        print("Step 2: Creating tables from models...")
        try:
            db.create_all()
            print("✓ Database tables verified/created successfully.")
        except Exception as e:
            print(f"✗ Error creating tables: {e}")
        print()
        
        # Step 3: Apply SQL migrations
        print("Step 3: Applying SQL migrations...")
        apply_all_migrations()
        print()
        
        # Step 4: Add missing columns
        print("Step 4: Adding missing columns...")
        add_missing_columns()
        print()
        
        # Step 5: Create super admin
        print("Step 5: Creating super admin if needed...")
        create_super_admin_if_not_exists()
        print()
        
        # Step 6: Seed platform plans
        print("Step 6: Seeding platform plans if needed...")
        seed_platform_plans_if_not_exists()
        print()
        
        # Step 7: Populate member created_at
        print("Step 7: Populating member created_at if needed...")
        populate_member_created_at_if_null()
        print()
        
        print("="*60)
        print("DATABASE INITIALIZATION COMPLETE")
        print("="*60 + "\n")
