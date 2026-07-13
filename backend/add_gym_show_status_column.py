"""
Migration script to add show_gym_status column to gyms table
Run this script to update the database schema
"""

from app import create_app, db

def add_show_gym_status_column():
    """Add show_gym_status column to gyms table"""
    app = create_app()
    
    with app.app_context():
        try:
            # Check if column already exists
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('gyms')]
            
            if 'show_gym_status' in columns:
                print("Column 'show_gym_status' already exists in gyms table.")
                return
            
            # Add the column
            print("Adding show_gym_status column to gyms table...")
            with db.engine.connect() as conn:
                conn.execute(db.text('ALTER TABLE gyms ADD COLUMN show_gym_status BOOLEAN NOT NULL DEFAULT TRUE'))
                conn.commit()
            print("Successfully added show_gym_status column to gyms table.")
            
            # Verify the column was added
            inspector = inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('gyms')]
            if 'show_gym_status' in columns:
                print("Verification successful: show_gym_status column exists.")
            else:
                print("Verification failed: show_gym_status column not found.")
                
        except Exception as e:
            print(f"Error adding column: {e}")
            raise

if __name__ == '__main__':
    add_show_gym_status_column()
