"""
Unit tests for authentication utilities.
Tests Super Admin decorators, role validation, and JWT claim handling.
"""

import unittest
from unittest.mock import patch, MagicMock
from flask import Flask, jsonify
from flask_jwt_extended import JWTManager, create_access_token

from app.auth_utils import (
    get_current_gym_id,
    get_current_user_role,
    get_current_user_id,
    get_current_user_claims,
    super_admin_required,
    gym_owner_or_admin_required,
    validate_gym_access,
    require_gym_access
)


class TestAuthUtils(unittest.TestCase):
    
    def setUp(self):
        """Set up test Flask app with JWT extension."""
        self.app = Flask(__name__)
        self.app.config['JWT_SECRET_KEY'] = 'test-secret-key'
        self.app.config['TESTING'] = True
        
        self.jwt = JWTManager(self.app)
        self.client = self.app.test_client()
        
        # Create test routes
        @self.app.route('/super-admin-only')
        @super_admin_required
        def super_admin_endpoint():
            return jsonify({'message': 'Super admin access granted'})
            
        @self.app.route('/owner-or-admin')
        @gym_owner_or_admin_required
        def owner_or_admin_endpoint():
            return jsonify({'message': 'Owner or admin access granted'})
    
    def create_test_token(self, user_id=1, role='gym_owner', gym_id=1, **kwargs):
        """Helper to create test JWT tokens with specified claims."""
        with self.app.app_context():
            claims = {
                'role': role,
                'gym_id': gym_id,
                'email': 'test@example.com',
                'name': 'Test User',
                **kwargs
            }
            return create_access_token(
                identity=str(user_id),
                additional_claims=claims
            )
    
    @patch('app.auth_utils.get_jwt')
    def test_get_current_gym_id(self, mock_get_jwt):
        """Test gym_id extraction from JWT claims."""
        # Test with gym owner
        mock_get_jwt.return_value = {'gym_id': 123, 'role': 'gym_owner'}
        self.assertEqual(get_current_gym_id(), 123)
        
        # Test with super admin (no gym_id)
        mock_get_jwt.return_value = {'gym_id': None, 'role': 'super_admin'}
        self.assertIsNone(get_current_gym_id())
        
        # Test with missing gym_id
        mock_get_jwt.return_value = {'role': 'gym_owner'}
        self.assertIsNone(get_current_gym_id())
    
    @patch('app.auth_utils.get_jwt')
    def test_get_current_user_role(self, mock_get_jwt):
        """Test user role extraction from JWT claims."""
        mock_get_jwt.return_value = {'role': 'super_admin', 'gym_id': None}
        self.assertEqual(get_current_user_role(), 'super_admin')
        
        mock_get_jwt.return_value = {'role': 'gym_owner', 'gym_id': 1}
        self.assertEqual(get_current_user_role(), 'gym_owner')
        
        # Test with missing role
        mock_get_jwt.return_value = {'gym_id': 1}
        self.assertIsNone(get_current_user_role())
    
    @patch('app.auth_utils.get_jwt')
    def test_get_current_user_id(self, mock_get_jwt):
        """Test user ID extraction from JWT claims."""
        mock_get_jwt.return_value = {'sub': '123', 'role': 'gym_owner'}
        self.assertEqual(get_current_user_id(), '123')
        
        # Test with missing sub claim
        mock_get_jwt.return_value = {'role': 'gym_owner'}
        self.assertIsNone(get_current_user_id())
    
    @patch('app.auth_utils.get_jwt')
    def test_get_current_user_claims(self, mock_get_jwt):
        """Test complete claims extraction from JWT."""
        test_claims = {'role': 'super_admin', 'gym_id': None, 'user_id': 1}
        mock_get_jwt.return_value = test_claims
        self.assertEqual(get_current_user_claims(), test_claims)
    
    def test_super_admin_required_success(self):
        """Test super_admin_required decorator with valid Super Admin token."""
        token = self.create_test_token(role='super_admin', gym_id=None)
        
        response = self.client.get(
            '/super-admin-only',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['message'], 'Super admin access granted')
    
    def test_super_admin_required_failure_gym_owner(self):
        """Test super_admin_required decorator rejection of gym owner."""
        token = self.create_test_token(role='gym_owner', gym_id=1)
        
        response = self.client.get(
            '/super-admin-only',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        self.assertEqual(response.status_code, 403)
        data = response.get_json()
        self.assertEqual(data['code'], 'SUPER_ADMIN_REQUIRED')
    
    def test_super_admin_required_failure_no_token(self):
        """Test super_admin_required decorator rejection without token."""
        response = self.client.get('/super-admin-only')
        
        self.assertEqual(response.status_code, 401)
        data = response.get_json()
        self.assertEqual(data['code'], 'AUTH_ERROR')
    
    def test_gym_owner_or_admin_required_gym_owner(self):
        """Test gym_owner_or_admin_required decorator with gym owner."""
        token = self.create_test_token(role='gym_owner', gym_id=1)
        
        response = self.client.get(
            '/owner-or-admin',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['message'], 'Owner or admin access granted')
    
    def test_gym_owner_or_admin_required_super_admin(self):
        """Test gym_owner_or_admin_required decorator with super admin."""
        token = self.create_test_token(role='super_admin', gym_id=None)
        
        response = self.client.get(
            '/owner-or-admin',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['message'], 'Owner or admin access granted')
    
    def test_gym_owner_or_admin_required_failure_member(self):
        """Test gym_owner_or_admin_required decorator rejection of member."""
        token = self.create_test_token(role='member', gym_id=1)
        
        response = self.client.get(
            '/owner-or-admin',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        self.assertEqual(response.status_code, 403)
        data = response.get_json()
        self.assertEqual(data['code'], 'INSUFFICIENT_PRIVILEGES')
    
    @patch('app.auth_utils.get_current_user_role')
    @patch('app.auth_utils.get_current_gym_id')
    def test_validate_gym_access_super_admin(self, mock_gym_id, mock_role):
        """Test gym access validation for Super Admin."""
        mock_role.return_value = 'super_admin'
        mock_gym_id.return_value = None
        
        # Super admin should have access to any gym
        self.assertTrue(validate_gym_access(1))
        self.assertTrue(validate_gym_access(999))
    
    @patch('app.auth_utils.get_current_user_role')
    @patch('app.auth_utils.get_current_gym_id')
    def test_validate_gym_access_gym_owner_success(self, mock_gym_id, mock_role):
        """Test gym access validation for gym owner with correct gym."""
        mock_role.return_value = 'gym_owner'
        mock_gym_id.return_value = 5
        
        # Gym owner should have access to their own gym
        self.assertTrue(validate_gym_access(5))
    
    @patch('app.auth_utils.get_current_user_role')
    @patch('app.auth_utils.get_current_gym_id')
    def test_validate_gym_access_gym_owner_failure(self, mock_gym_id, mock_role):
        """Test gym access validation for gym owner with wrong gym."""
        mock_role.return_value = 'gym_owner'
        mock_gym_id.return_value = 5
        
        # Gym owner should not have access to other gyms
        self.assertFalse(validate_gym_access(10))
    
    @patch('app.auth_utils.validate_gym_access')
    def test_require_gym_access_success(self, mock_validate):
        """Test require_gym_access with valid access."""
        mock_validate.return_value = True
        
        error_response, status_code = require_gym_access(1)
        
        self.assertIsNone(error_response)
        self.assertIsNone(status_code)
    
    @patch('app.auth_utils.validate_gym_access')
    def test_require_gym_access_failure(self, mock_validate):
        """Test require_gym_access with denied access."""
        mock_validate.return_value = False
        
        with self.app.app_context():
            error_response, status_code = require_gym_access(1)
        
        self.assertIsNotNone(error_response)
        self.assertEqual(status_code, 403)
        
        # Check error response content
        data = error_response.get_json()
        self.assertEqual(data['code'], 'GYM_ACCESS_DENIED')


if __name__ == '__main__':
    unittest.main()