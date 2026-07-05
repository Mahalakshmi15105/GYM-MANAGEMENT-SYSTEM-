"""
Unit tests for user management endpoints.
Tests cross-platform user administration functionality.
"""

import unittest
from unittest.mock import patch, MagicMock
import json
from datetime import datetime, timedelta

from flask import Flask
from flask_jwt_extended import JWTManager, create_access_token


class TestUserManagement(unittest.TestCase):
    
    def setUp(self):
        """Set up test Flask app for user management testing."""
        self.app = Flask(__name__)
        self.app.config['JWT_SECRET_KEY'] = 'test-secret-key'
        self.app.config['TESTING'] = True
        
        self.jwt = JWTManager(self.app)
        self.client = self.app.test_client()
        
        # Import and register admin blueprint
        from app.routes.admin import admin_bp
        self.app.register_blueprint(admin_bp, url_prefix='/admin')
        
    def create_super_admin_token(self):
        """Create a Super Admin JWT token for testing."""
        with self.app.app_context():
            return create_access_token(
                identity='1',
                additional_claims={
                    'role': 'super_admin',
                    'gym_id': None,
                    'email': 'admin@flexigym.com',
                    'name': 'Super Admin'
                }
            )
    
    def create_gym_owner_token(self):
        """Create a Gym Owner JWT token for testing."""
        with self.app.app_context():
            return create_access_token(
                identity='2',
                additional_claims={
                    'role': 'gym_owner',
                    'gym_id': 1,
                    'email': 'owner@testgym.com',
                    'name': 'Gym Owner'
                }
            )
    
    @patch('app.routes.admin.User')
    @patch('app.routes.admin.Gym')
    def test_list_users_success(self, mock_gym, mock_user):
        """Test successful user listing with pagination and filtering."""
        token = self.create_super_admin_token()
        
        # Mock pagination
        mock_pagination = MagicMock()
        mock_pagination.items = []
        mock_pagination.total = 0
        mock_pagination.pages = 0
        mock_pagination.has_next = False
        mock_pagination.has_prev = False
        
        mock_user.query.outerjoin.return_value.order_by.return_value.paginate.return_value = mock_pagination
        
        with patch('app.routes.admin.get_user_last_login') as mock_last_login, \
             patch('app.routes.admin.get_user_activity_stats') as mock_activity_stats:
            
            mock_last_login.return_value = '2026-07-05T10:00:00Z'
            mock_activity_stats.return_value = {'total_actions': 25, 'actions_last_30_days': 5}
            
            response = self.client.get(
                '/admin/users?role=gym_owner&page=1&per_page=20',
                headers={'Authorization': f'Bearer {token}'}
            )
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        
        self.assertIn('users', data)
        self.assertIn('pagination', data)
        self.assertIn('filters', data)
        self.assertEqual(data['filters']['role'], 'gym_owner')
    
    @patch('app.routes.admin.User')
    @patch('app.routes.admin.ActivityLog')
    def test_get_user_details(self, mock_activity_log, mock_user):
        """Test getting detailed user information."""
        token = self.create_super_admin_token()
        
        # Mock user instance with gym
        mock_user_instance = MagicMock()
        mock_user_instance.id = 1
        mock_user_instance.created_at = datetime(2026, 1, 1)
        mock_user_instance.to_dict.return_value = {
            'id': 1, 'name': 'Test User', 'email': 'test@example.com', 'role': 'gym_owner'
        }
        
        # Mock gym
        mock_gym_instance = MagicMock()
        mock_gym_instance.id = 1
        mock_gym_instance.name = 'Test Gym'
        mock_gym_instance.status = 'Active'
        mock_gym_instance.created_at = datetime(2026, 1, 1)
        mock_gym_instance.get_member_count.return_value = 50
        
        mock_user_instance.gym = mock_gym_instance
        mock_user.query.get_or_404.return_value = mock_user_instance
        
        # Mock activity logs
        mock_activity_log.query.filter_by.return_value.order_by.return_value.limit.return_value.all.return_value = []
        
        with patch('app.routes.admin.get_user_login_count') as mock_login_count, \
             patch('app.routes.admin.get_user_last_login') as mock_last_login, \
             patch('app.routes.admin.get_user_activity_count') as mock_activity_count, \
             patch('app.routes.admin.get_user_permissions') as mock_permissions:
            
            mock_login_count.return_value = 15
            mock_last_login.return_value = '2026-07-05T10:00:00Z'
            mock_activity_count.return_value = 8
            mock_permissions.return_value = {'can_manage_own_gym': True}
            
            response = self.client.get(
                '/admin/users/1',
                headers={'Authorization': f'Bearer {token}'}
            )
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        
        self.assertEqual(data['id'], 1)
        self.assertIn('gym_details', data)
        self.assertIn('recent_activity', data)
        self.assertIn('activity_summary', data)
        self.assertIn('permissions', data)
        self.assertEqual(data['gym_details']['name'], 'Test Gym')
    
    @patch('app.routes.admin.User')
    @patch('app.routes.admin.log_activity')
    def test_disable_user_success(self, mock_log, mock_user):
        """Test successful user account disable."""
        token = self.create_super_admin_token()
        
        # Mock non-super admin user
        mock_user_instance = MagicMock()
        mock_user_instance.id = 2
        mock_user_instance.role = 'gym_owner'
        mock_user_instance.email = 'test@example.com'
        mock_user_instance.name = 'Test User'
        mock_user_instance.gym_id = 1
        mock_user_instance.to_dict.return_value = {'id': 2, 'name': 'Test User'}
        
        mock_user.query.get_or_404.return_value = mock_user_instance
        
        response = self.client.put(
            '/admin/users/2/disable',
            headers={'Authorization': f'Bearer {token}'},
            data=json.dumps({'reason': 'Policy violation'}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        
        self.assertEqual(data['message'], 'User account disabled successfully')
        self.assertEqual(data['reason'], 'Policy violation')
        mock_log.assert_called_once()
    
    @patch('app.routes.admin.User')
    def test_disable_user_super_admin_forbidden(self, mock_user):
        """Test that disabling Super Admin is forbidden."""
        token = self.create_super_admin_token()
        
        # Mock super admin user
        mock_user_instance = MagicMock()
        mock_user_instance.role = 'super_admin'
        
        mock_user.query.get_or_404.return_value = mock_user_instance
        
        response = self.client.put(
            '/admin/users/1/disable',
            headers={'Authorization': f'Bearer {token}'},
            data=json.dumps({'reason': 'Test'}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 403)
        data = response.get_json()
        self.assertEqual(data['error'], 'Cannot disable Super Admin accounts')
    
    @patch('app.routes.admin.User')
    @patch('app.routes.admin.log_activity')
    def test_enable_user_success(self, mock_log, mock_user):
        """Test successful user account enable."""
        token = self.create_super_admin_token()
        
        mock_user_instance = MagicMock()
        mock_user_instance.id = 2
        mock_user_instance.email = 'test@example.com'
        mock_user_instance.name = 'Test User'
        mock_user_instance.gym_id = 1
        mock_user_instance.to_dict.return_value = {'id': 2, 'name': 'Test User'}
        
        mock_user.query.get_or_404.return_value = mock_user_instance
        
        response = self.client.put(
            '/admin/users/2/enable',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        
        self.assertEqual(data['message'], 'User account enabled successfully')
        mock_log.assert_called_once()
    
    @patch('app.routes.admin.User')
    @patch('app.routes.admin.db.session.commit')
    @patch('app.routes.admin.log_activity')
    def test_change_user_role_success(self, mock_log, mock_commit, mock_user):
        """Test successful user role change."""
        token = self.create_super_admin_token()
        
        # Mock gym owner user
        mock_user_instance = MagicMock()
        mock_user_instance.id = 2
        mock_user_instance.role = 'member'
        mock_user_instance.email = 'test@example.com'
        mock_user_instance.gym_id = 1
        mock_user_instance.to_dict.return_value = {'id': 2, 'role': 'gym_owner'}
        
        mock_user.query.get_or_404.return_value = mock_user_instance
        
        response = self.client.put(
            '/admin/users/2/change-role',
            headers={'Authorization': f'Bearer {token}'},
            data=json.dumps({
                'new_role': 'gym_owner',
                'reason': 'Promoted to gym owner'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        
        self.assertEqual(data['message'], 'User role changed successfully')
        self.assertEqual(data['old_role'], 'member')
        self.assertEqual(data['new_role'], 'gym_owner')
        self.assertEqual(mock_user_instance.role, 'gym_owner')
        mock_commit.assert_called_once()
        mock_log.assert_called_once()
    
    @patch('app.routes.admin.User')
    def test_change_role_invalid_role(self, mock_user):
        """Test role change with invalid role."""
        token = self.create_super_admin_token()
        
        mock_user_instance = MagicMock()
        mock_user_instance.role = 'gym_owner'
        mock_user.query.get_or_404.return_value = mock_user_instance
        
        response = self.client.put(
            '/admin/users/2/change-role',
            headers={'Authorization': f'Bearer {token}'},
            data=json.dumps({'new_role': 'invalid_role'}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn('Invalid role', data['error'])
    
    @patch('app.routes.admin.User')
    def test_change_role_super_admin_forbidden(self, mock_user):
        """Test that changing Super Admin role is forbidden."""
        token = self.create_super_admin_token()
        
        mock_user_instance = MagicMock()
        mock_user_instance.role = 'super_admin'
        mock_user.query.get_or_404.return_value = mock_user_instance
        
        response = self.client.put(
            '/admin/users/1/change-role',
            headers={'Authorization': f'Bearer {token}'},
            data=json.dumps({'new_role': 'gym_owner'}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 403)
        data = response.get_json()
        self.assertEqual(data['error'], 'Cannot change Super Admin roles')
    
    @patch('app.routes.admin.User')
    @patch('app.routes.admin.log_activity')
    def test_reset_user_password(self, mock_log, mock_user):
        """Test admin-initiated password reset."""
        token = self.create_super_admin_token()
        
        mock_user_instance = MagicMock()
        mock_user_instance.id = 2
        mock_user_instance.email = 'test@example.com'
        mock_user_instance.gym_id = 1
        
        mock_user.query.get_or_404.return_value = mock_user_instance
        
        response = self.client.post(
            '/admin/users/2/reset-password',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        
        self.assertEqual(data['message'], 'Password reset initiated successfully')
        self.assertEqual(data['user_email'], 'test@example.com')
        self.assertIn('temporary_password', data)
        self.assertIn('instructions', data)
        mock_log.assert_called_once()
    
    @patch('app.routes.admin.db.session.query')
    def test_get_user_analytics(self, mock_query):
        """Test user analytics endpoint."""
        token = self.create_super_admin_token()
        
        # Mock role distribution query
        mock_role_result = [
            MagicMock(role='gym_owner', count=15),
            MagicMock(role='member', count=150),
            MagicMock(role='super_admin', count=2)
        ]
        
        # Mock registration trend query
        mock_registration_result = [
            MagicMock(date='2026-07-01', count=5),
            MagicMock(date='2026-07-02', count=3),
            MagicMock(date='2026-07-03', count=7)
        ]
        
        # Mock gym user stats query
        mock_gym_stats_result = [
            MagicMock(id=1, name='Gym A', status='Active', user_count=25),
            MagicMock(id=2, name='Gym B', status='Active', user_count=30),
            MagicMock(id=3, name='Gym C', status='Pending', user_count=5)
        ]
        
        # Mock users by gym status query
        mock_gym_status_result = [
            MagicMock(status='Active', user_count=55),
            MagicMock(status='Pending', user_count=5)
        ]
        
        # Setup query return values
        mock_query.return_value.group_by.return_value.all.side_effect = [
            mock_role_result,          # Role distribution
            mock_registration_result,  # Registration trend
            mock_gym_stats_result,     # Gym user stats
            mock_gym_status_result     # Users by gym status
        ]
        
        # Mock scalar query for active users
        mock_query.return_value.filter.return_value.scalar.return_value = 45
        
        with patch('app.routes.admin.User') as mock_user:
            # Mock total user count
            mock_user.query.count.return_value = 167
            mock_user.query.filter_by.return_value.count.side_effect = [2, 15, 150]  # super_admin, gym_owner, member
            
            response = self.client.get(
                '/admin/users/analytics',
                headers={'Authorization': f'Bearer {token}'}
            )
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        
        self.assertIn('role_distribution', data)
        self.assertIn('registration_trend', data)
        self.assertIn('gym_user_stats', data)
        self.assertIn('users_by_gym_status', data)
        self.assertIn('activity_metrics', data)
        self.assertIn('generated_at', data)
        
        # Verify role distribution structure
        self.assertEqual(len(data['role_distribution']), 3)
        self.assertEqual(data['role_distribution'][0]['role'], 'gym_owner')
        self.assertEqual(data['role_distribution'][0]['count'], 15)
        
        # Verify activity metrics
        self.assertEqual(data['activity_metrics']['total_users'], 167)
        self.assertEqual(data['activity_metrics']['super_admins'], 2)
    
    @patch('app.routes.admin.User')
    @patch('app.routes.admin.Gym')
    def test_search_users(self, mock_gym, mock_user):
        """Test advanced user search functionality."""
        token = self.create_super_admin_token()
        
        # Mock search results
        mock_user_results = []
        mock_user.query.outerjoin.return_value.order_by.return_value.limit.return_value.all.return_value = mock_user_results
        
        response = self.client.get(
            '/admin/users/search?email=test@example.com&role=gym_owner&gym_name=Fitness',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        
        self.assertIn('users', data)
        self.assertIn('total_results', data)
        self.assertIn('search_criteria', data)
        
        # Verify search criteria
        criteria = data['search_criteria']
        self.assertEqual(criteria['email'], 'test@example.com')
        self.assertEqual(criteria['role'], 'gym_owner')
        self.assertEqual(criteria['gym_name'], 'Fitness')
    
    def test_user_management_requires_super_admin(self):
        """Test that all user management endpoints require Super Admin role."""
        gym_owner_token = self.create_gym_owner_token()
        
        endpoints = [
            ('GET', '/admin/users'),
            ('GET', '/admin/users/1'),
            ('PUT', '/admin/users/1/disable'),
            ('PUT', '/admin/users/1/enable'),
            ('PUT', '/admin/users/1/change-role'),
            ('POST', '/admin/users/1/reset-password'),
            ('GET', '/admin/users/analytics'),
            ('GET', '/admin/users/search')
        ]
        
        for method, endpoint in endpoints:
            response = self.client.open(
                method=method,
                path=endpoint,
                headers={'Authorization': f'Bearer {gym_owner_token}'},
                data=json.dumps({}),
                content_type='application/json'
            )
            
            self.assertEqual(response.status_code, 403, f"Endpoint {method} {endpoint} should require Super Admin")
            data = response.get_json()
            self.assertEqual(data['code'], 'SUPER_ADMIN_REQUIRED')
    
    def test_get_user_permissions(self):
        """Test user permission mapping function."""
        from app.routes.admin import get_user_permissions
        
        # Test super admin permissions
        super_admin_perms = get_user_permissions('super_admin')
        self.assertTrue(super_admin_perms['can_manage_all_gyms'])
        self.assertTrue(super_admin_perms['can_manage_all_users'])
        self.assertTrue(super_admin_perms['can_view_all_data'])
        
        # Test gym owner permissions
        gym_owner_perms = get_user_permissions('gym_owner')
        self.assertFalse(gym_owner_perms['can_manage_all_gyms'])
        self.assertFalse(gym_owner_perms['can_manage_all_users'])
        self.assertTrue(gym_owner_perms['can_manage_own_gym'])
        
        # Test member permissions
        member_perms = get_user_permissions('member')
        self.assertFalse(member_perms['can_manage_all_gyms'])
        self.assertFalse(member_perms['can_manage_own_gym'])
        self.assertTrue(member_perms['can_view_own_data'])
        
        # Test unknown role (should default to member)
        unknown_perms = get_user_permissions('unknown_role')
        self.assertEqual(unknown_perms, member_perms)


if __name__ == '__main__':
    unittest.main()