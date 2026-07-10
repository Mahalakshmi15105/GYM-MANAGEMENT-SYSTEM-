from app import create_app
from app.extensions import db
from app.models import Gym
import requests

app = create_app()

with app.app_context():
    # Get a gym with QR code
    gym = Gym.query.first()
    if not gym:
        print("No gym found in database")
    else:
        print(f"Testing QR endpoint for gym: {gym.name}")
        print(f"QR Code: {gym.attendance_qr}")
        
        # Create a test token (you'd normally get this from login)
        # For testing, we'll just check if the endpoint exists
        print("\nTesting if endpoint is accessible...")
        
        # Test the endpoint directly
        with app.test_client() as client:
            # First, we need to simulate a JWT token
            # For now, let's just check if the route exists
            print("Available routes:")
            for rule in app.url_map.iter_rules():
                if 'qr' in str(rule):
                    print(f"  {rule.endpoint}: {rule.methods} {rule.rule}")
