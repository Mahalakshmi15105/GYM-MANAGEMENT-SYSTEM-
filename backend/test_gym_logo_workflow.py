#!/usr/bin/env python3
"""
Comprehensive test to verify the complete gym logo workflow:
- Upload logo → Display → Replace → Remove
"""

import pytest
import os
import tempfile
from io import BytesIO
from PIL import Image
from app import create_app
from app.extensions import db
from app.models import User, Gym

def test_complete_gym_logo_workflow():
    """Test the complete gym logo workflow"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['JWT_SECRET_KEY'] = 'test-jwt-secret-key'
    client = app.test_client()
    
    with app.app_context():
        db.create_all()
        
        # Create test gym
        gym = Gym(name="Test Gym", address="123 Test St", phone="555-0123")
        db.session.add(gym)
        db.session.commit()
        
        # Create test user
        user = User(
            name="Test Owner",
            email="owner@testgym.com",
            password_hash="test_hash",
            role="gym_owner",
            gym_id=gym.id
        )
        db.session.add(user)
        db.session.commit()
        
        # Get JWT token
        from flask_jwt_extended import create_access_token
        token = create_access_token(
            identity=str(user.id),
            additional_claims={'gym_id': gym.id, 'role': 'gym_owner'}
        )
        headers = {'Authorization': f'Bearer {token}'}
        
        print("🏋️‍♂️ Testing Complete Gym Logo Workflow")
        print("=" * 50)
        
        # Step 1: Verify no logo initially
        print("Step 1: Checking initial state (no logo)...")
        response = client.get('/api/gym/logo/info', headers=headers)
        assert response.status_code == 200
        data = response.get_json()
        assert data['has_logo'] is False
        assert data['logo_url'] is None
        print("✅ Initial state confirmed: No logo")
        
        # Step 2: Upload first logo
        print("\nStep 2: Uploading first logo...")
        img = Image.new('RGB', (100, 100), color='red')
        img_io = BytesIO()
        img.save(img_io, format='PNG')
        img_io.seek(0)
        
        response = client.post(
            '/api/gym/logo/upload',
            headers=headers,
            data={'logo': (img_io, 'test_logo.png', 'image/png')},
            content_type='multipart/form-data'
        )
        assert response.status_code == 200
        upload_data = response.get_json()
        assert 'Logo uploaded successfully' in upload_data['message']
        assert 'logo_url' in upload_data
        first_logo_url = upload_data['logo_url']
        print(f"✅ First logo uploaded: {first_logo_url}")
        
        # Step 3: Verify logo exists
        print("\nStep 3: Verifying logo exists...")
        response = client.get('/api/gym/logo/info', headers=headers)
        assert response.status_code == 200
        data = response.get_json()
        assert data['has_logo'] is True
        assert data['logo_url'] == first_logo_url
        print("✅ Logo confirmed in database")
        
        # Step 4: Replace with new logo
        print("\nStep 4: Replacing with new logo...")
        img2 = Image.new('RGB', (150, 150), color='blue')
        img2_io = BytesIO()
        img2.save(img2_io, format='PNG')
        img2_io.seek(0)
        
        response = client.post(
            '/api/gym/logo/upload',
            headers=headers,
            data={'logo': (img2_io, 'new_logo.png', 'image/png')},
            content_type='multipart/form-data'
        )
        assert response.status_code == 200
        replace_data = response.get_json()
        second_logo_url = replace_data['logo_url']
        assert second_logo_url != first_logo_url  # Should be different URL
        print(f"✅ Logo replaced: {second_logo_url}")
        
        # Step 5: Verify replacement worked
        print("\nStep 5: Verifying logo replacement...")
        response = client.get('/api/gym/logo/info', headers=headers)
        assert response.status_code == 200
        data = response.get_json()
        assert data['has_logo'] is True
        assert data['logo_url'] == second_logo_url
        print("✅ Logo replacement confirmed")
        
        # Step 6: Remove logo
        print("\nStep 6: Removing logo...")
        response = client.delete('/api/gym/logo/remove', headers=headers)
        assert response.status_code == 200
        remove_data = response.get_json()
        assert 'Logo removed successfully' in remove_data['message']
        print("✅ Logo removed successfully")
        
        # Step 7: Verify logo is gone
        print("\nStep 7: Verifying logo removal...")
        response = client.get('/api/gym/logo/info', headers=headers)
        assert response.status_code == 200
        data = response.get_json()
        assert data['has_logo'] is False
        assert data['logo_url'] is None
        print("✅ Logo removal confirmed")
        
        # Step 8: Test error cases
        print("\nStep 8: Testing error cases...")
        
        # Try to remove non-existent logo
        response = client.delete('/api/gym/logo/remove', headers=headers)
        assert response.status_code == 400
        assert 'No logo to remove' in response.get_json()['error']
        print("✅ Error handling for removing non-existent logo")
        
        # Try to upload invalid file
        invalid_file = BytesIO(b"This is not an image")
        response = client.post(
            '/api/gym/logo/upload',
            headers=headers,
            data={'logo': (invalid_file, 'test.txt', 'text/plain')},
            content_type='multipart/form-data'
        )
        assert response.status_code == 400
        assert 'Invalid file type' in response.get_json()['error']
        print("✅ Error handling for invalid file type")
        
        # Test unauthorized access
        response = client.get('/api/gym/logo/info')
        assert response.status_code == 401
        print("✅ Unauthorized access protection")
        
        db.drop_all()
        print("\n🎉 Complete Gym Logo Workflow Test PASSED!")
        print("All functionality working correctly:")
        print("- Upload logo ✅")
        print("- Display logo ✅") 
        print("- Replace logo ✅")
        print("- Remove logo ✅")
        print("- Error handling ✅")
        print("- Security ✅")

if __name__ == "__main__":
    test_complete_gym_logo_workflow()