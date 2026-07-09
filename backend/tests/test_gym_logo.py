import pytest
import os
import tempfile
from io import BytesIO
from PIL import Image
from app import create_app
from app.extensions import db
from app.models import User, Gym

class TestGymLogo:
    def setup_method(self):
        """Set up test app and database"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.app.config['JWT_SECRET_KEY'] = 'test-jwt-secret-key'
        self.client = self.app.test_client()
        
        with self.app.app_context():
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
            
            self.gym_id = gym.id
            self.user_id = user.id
    
    def teardown_method(self):
        """Clean up after test"""
        with self.app.app_context():
            db.drop_all()
    
    def get_auth_headers(self):
        """Get JWT token for authenticated requests"""
        from flask_jwt_extended import create_access_token
        
        with self.app.app_context():
            token = create_access_token(
                identity=str(self.user_id),
                additional_claims={
                    'gym_id': self.gym_id,
                    'role': 'gym_owner'
                }
            )
            return {'Authorization': f'Bearer {token}'}
    
    def create_test_image(self):
        """Create a test image file"""
        img = Image.new('RGB', (100, 100), color='red')
        img_io = BytesIO()
        img.save(img_io, format='PNG')
        img_io.seek(0)
        return img_io
    
    def test_get_logo_info_no_logo(self):
        """Test getting logo info when no logo exists"""
        response = self.client.get('/api/gym/logo/info', headers=self.get_auth_headers())
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['has_logo'] is False
        assert data['logo_url'] is None
        assert 'gym' in data
    
    def test_upload_logo_success(self):
        """Test successful logo upload"""
        img_data = self.create_test_image()
        
        response = self.client.post(
            '/api/gym/logo/upload',
            headers=self.get_auth_headers(),
            data={'logo': (img_data, 'test_logo.png', 'image/png')},
            content_type='multipart/form-data'
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'Logo uploaded successfully' in data['message']
        assert 'logo_url' in data
        assert data['logo_url'].startswith('/static/gym_logos/')
    
    def test_upload_logo_no_file(self):
        """Test upload with no file provided"""
        response = self.client.post(
            '/api/gym/logo/upload',
            headers=self.get_auth_headers(),
            data={},
            content_type='multipart/form-data'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'No logo file provided' in data['error']
    
    def test_upload_logo_invalid_type(self):
        """Test upload with invalid file type"""
        txt_data = BytesIO(b"This is not an image")
        
        response = self.client.post(
            '/api/gym/logo/upload',
            headers=self.get_auth_headers(),
            data={'logo': (txt_data, 'test.txt', 'text/plain')},
            content_type='multipart/form-data'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'Invalid file type' in data['error']
    
    def test_remove_logo_no_logo(self):
        """Test removing logo when no logo exists"""
        response = self.client.delete('/api/gym/logo/remove', headers=self.get_auth_headers())
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'No logo to remove' in data['error']
    
    def test_upload_and_remove_logo(self):
        """Test complete logo upload and removal workflow"""
        # Upload logo first
        img_data = self.create_test_image()
        upload_response = self.client.post(
            '/api/gym/logo/upload',
            headers=self.get_auth_headers(),
            data={'logo': (img_data, 'test_logo.png', 'image/png')},
            content_type='multipart/form-data'
        )
        
        assert upload_response.status_code == 200
        
        # Verify logo exists
        info_response = self.client.get('/api/gym/logo/info', headers=self.get_auth_headers())
        assert info_response.status_code == 200
        info_data = info_response.get_json()
        assert info_data['has_logo'] is True
        
        # Remove logo
        remove_response = self.client.delete('/api/gym/logo/remove', headers=self.get_auth_headers())
        assert remove_response.status_code == 200
        
        # Verify logo is removed
        final_info_response = self.client.get('/api/gym/logo/info', headers=self.get_auth_headers())
        assert final_info_response.status_code == 200
        final_info_data = final_info_response.get_json()
        assert final_info_data['has_logo'] is False
    
    def test_unauthorized_access(self):
        """Test unauthorized access to logo endpoints"""
        # Test without auth token
        response = self.client.get('/api/gym/logo/info')
        assert response.status_code == 401  # JWT required
        
        response = self.client.post('/api/gym/logo/upload')
        assert response.status_code == 401  # JWT required
        
        response = self.client.delete('/api/gym/logo/remove')
        assert response.status_code == 401  # JWT required