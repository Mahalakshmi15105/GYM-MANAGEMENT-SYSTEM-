"""
Unit tests for Super Admin routes.
Tests all admin endpoints including gym management, analytics, and activity logging.
"""

import unittest
from unittest.mock import patch, MagicMock
import json
from datetime import datetime, date, timedelta

from flask import Flask
from flask_jwt_extended import JWTManager, create_access_token

from app.routes.admin import admin_bp, PlatformAnalyticsService, log_activity
from app.extensions import db


class TestAdminRoutes(unittest.TestCase):
    
    def setUp(self):
        """Set up test Flask app with admin routes."""
        self.app = Flask(__name__)
        self.app.config['JWT_SECRET_KEY'] = 'test-secret-key'
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        self.jwt = JWTManager(self.app)
        db.init_app(self.app)
        
        # Register admin blueprint
        self.app.register_blueprint(admin_bp, url_prefix='/admin')
        
        self.client = self.app.test_client()
        
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
    
    def test_platform_analytics_requires_super_admin(self):
        """Test that platform analytics endpoint requires Super Admin role."""
        gym_owner_token = self.create_gym_owner_token()
        
        response = self.client.get(
            '/admin/dashboard/analytics',
            headers={'Authorization': f'Bearer {gym_owner_token}'}
        )
        
        self.assertEqual(response.status_code, 403)
        data = response.get_json()
        self.assertEqual(data['code'], 'SUPER_ADMIN_REQUIRED')
    
    def test_platform_analytics_without_token(self):
        """Test that platform analytics endpoint requires authentication."""
        response = self.client.get('/admin/dashboard/analytics')
        self.assertEqual(response.status_code, 401)
    
    @patch('app.routes.admin.Gym')
    @patch('app.routes.admin.Member')
    @patch('app.routes.admin.Payment')
    @patch('app.routes.admin.GymSubscription')
    def test_get_platform_analytics_success(self, mock_subscription, mock_payment, mock_member, mock_gym):
        """Test successful platform analytics retrieval."""
        token = self.create_super_admin_token()
        
        # Mock query results
        mock_gym.query.count.return_value = 50
        mock_gym.query.filter_by.return_value.count.return_value = 40
        mock_member.query.join.return_value.filter.return_value.count.return_value = 1000
        mock_subscription.query.filter_by.return_value.count.return_value = 35
        
        # Mock database session query
        with patch('app.routes.admin.db.session.query') as mock_query:
            mock_query.return_value.join.return_value.filter.return_value.scalar.return_value = 50000.0
            
            response = self.client.get(
                '/admin/dashboard/analytics',
                headers={'Authorization': f'Bearer {token}'}
            )
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        
        self.assertIn('platform_metrics', data)
        self.assertIn('generated_at', data)
        
        metrics = data['platform_metrics']
        self.assertEqual(metrics['total_gyms'], 50)
        self.assertEqual(metrics['active_subscriptions'], 35)
    
    @patch('app.routes.admin.Gym')
    def test_list_gyms_with_filters(self, mock_gym):
        """Test gym listing with status filter."""
        token = self.create_super_admin_token()
        
        # Mock pagination
        mock_pagination = MagicMock()
        mock_pagination.items = []
        mock_pagination.total = 0
        mock_pagination.pages = 0
        mock_pagination.has_next = False
        mock_pagination.has_prev = False
        
        mock_gym.query.filter.return_value.order_by.return_value.paginate.return_value = mock_pagination
        
        response = self.client.get(
            '/admin/gyms?status=Active&page=1&per_page=20',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        
        self.assertIn('gyms', data)
        self.assertIn('pagination', data)
        self.assertIn('filters', data)
        self.assertEqual(data['filters']['status'], 'Active')
    
    @patch('app.routes.admin.Gym')
    @patch('app.routes.admin.log_activity')
    def test_approve_gym_success(self, mock_log, mock_gym):
        """Test successful gym approval."""
        token = self.create_super_admin_token()
        
        # Mock gym instance
        mock_gym_instance = MagicMock()
        mock_gym_instance.approve_gym.return_value = True
        mock_gym_instance.to_dict.return_value = {'id': 1, 'name': 'Test Gym', 'status': 'Active'}
        mock_gym.query.get_or_404.return_value = mock_gym_instance
        
        with patch('app.routes.admin.db.session.commit'):
            response = self.client.put(
                '/admin/gyms/1/approve',
                headers={'Authorization': f'Bearer {token}'}
            )
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        
        self.assertEqual(data['message'], 'Gym approved successfully')
        self.assertIn('gym', data)
        mock_gym_instance.approve_gym.assert_called_once()
        mock_log.assert_called_once()
    
    @patch('app.routes.admin.Gym')
    def test_approve_gym_failure(self, mock_gym):
        """Test gym approval failure when gym cannot be approved."""
        token = self.create_super_admin_token()
        
        # Mock gym instance that cannot be approved
        mock_gym_instance = MagicMock()
        mock_gym_instance.approve_gym.return_value = False
        mock_gym.query.get_or_404.return_value = mock_gym_instance
        
        response = self.client.put(
            '/admin/gyms/1/approve',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertEqual(data['error'], 'Gym cannot be approved in current status')
    
    @patch('app.routes.admin.Gym')
    @patch('app.routes.admin.log_activity')
    def test_suspend_gym_with_reason(self, mock_log, mock_gym):
        """Test gym suspension with reason."""
        token = self.create_super_admin_token()
        
        # Mock gym instance
        mock_gym_instance = MagicMock()
        mock_gym_instance.suspend_gym.return_value = True
        mock_gym_instance.name = 'Test Gym'
        mock_gym_instance.to_dict.return_value = {'id': 1, 'name': 'Test Gym', 'status': 'Suspended'}
        mock_gym.query.get_or_404.return_value = mock_gym_instance
        
        with patch('app.routes.admin.db.session.commit'):
            response = self.client.put(
                '/admin/gyms/1/suspend',
                headers={'Authorization': f'Bearer {token}'},
                data=json.dumps({'reason': 'Policy violation'}),
                content_type='application/json'
            )
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        
        self.assertEqual(data['message'], 'Gym suspended successfully')
        mock_gym_instance.suspend_gym.assert_called_once_with('Policy violation')
        mock_log.assert_called_once()
    
    @patch('app.routes.admin.ActivityLog')
    def test_get_activity_logs_with_filters(self, mock_activity_log):
        """Test activity logs retrieval with filters."""
        token = self.create_super_admin_token()
        
        # Mock pagination
        mock_pagination = MagicMock()
        mock_pagination.items = []
        mock_pagination.total = 0
        mock_pagination.pages = 0
        mock_pagination.has_next = False
        mock_pagination.has_prev = False
        
        mock_activity_log.query.filter.return_value.order_by.return_value.paginate.return_value = mock_pagination
        
        response = self.client.get(
            '/admin/activity-logs?action_type=approve&severity=info&page=1',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        
        self.assertIn('logs', data)
        self.assertIn('pagination', data)
        self.assertIn('filters', data)
        self.assertEqual(data['filters']['action_type'], 'approve')
        self.assertEqual(data['filters']['severity'], 'info')
    
    def test_platform_analytics_service_get_metrics(self):
        """Test PlatformAnalyticsService get_platform_metrics method."""
        with patch('app.routes.admin.Gym') as mock_gym, \
             patch('app.routes.admin.Member') as mock_member, \
             patch('app.routes.admin.GymSubscription') as mock_subscription:
            
            # Mock query results
            mock_gym.query.count.return_value = 25
            mock_gym.query.filter_by.return_value.count.return_value = 20
            mock_member.query.join.return_value.filter.return_value.count.return_value = 500
            mock_subscription.query.filter_by.return_value.count.return_value = 18
            
            with patch('app.routes.admin.date') as mock_date:
                mock_date.today.return_value = date(2026, 7, 5)
                mock_subscription.query.filter.return_value.count.return_value = 3
                
                metrics = PlatformAnalyticsService.get_platform_metrics()
            
            self.assertEqual(metrics['gyms']['total'], 25)
            self.assertEqual(metrics['gyms']['active'], 20)
            self.assertEqual(metrics['members']['total'], 500)
            self.assertEqual(metrics['subscriptions']['active'], 18)
            self.assertEqual(metrics['subscriptions']['expiring_soon'], 3)
    
    @patch('app.routes.admin.ActivityLog')
    @patch('app.routes.admin.db.session.add')
    @patch('app.routes.admin.db.session.commit')
    def test_log_activity_function(self, mock_commit, mock_add, mock_activity_log):
        """Test activity logging function."""
        with self.app.app_context():
            with self.app.test_request_context('/test', method='POST'):
                log_activity(
                    user_id=1,
                    action_type='test',
                    description='Test activity',
                    gym_id=5,
                    entity_type='gym',
                    entity_id=5,
                    severity='info'
                )
                
                mock_add.assert_called_once()
                mock_commit.assert_called_once()
    
    def test_invalid_pagination_parameters(self):
        """Test that invalid pagination parameters are handled correctly."""
        token = self.create_super_admin_token()
        
        with patch('app.routes.admin.Gym') as mock_gym:
            mock_pagination = MagicMock()
            mock_pagination.items = []
            mock_pagination.total = 0
            mock_pagination.pages = 0
            mock_pagination.has_next = False
            mock_pagination.has_prev = False
            
            mock_gym.query.order_by.return_value.paginate.return_value = mock_pagination
            
            # Test with per_page > 100 (should be capped at 100)
            response = self.client.get(
                '/admin/gyms?per_page=150',
                headers={'Authorization': f'Bearer {token}'}
            )
            
            self.assertEqual(response.status_code, 200)
    
    def test_gym_not_found(self):
        """Test handling of non-existent gym ID."""
        token = self.create_super_admin_token()
        
        with patch('app.routes.admin.Gym') as mock_gym:
            from werkzeug.exceptions import NotFound
            mock_gym.query.get_or_404.side_effect = NotFound()
            
            response = self.client.put(
                '/admin/gyms/999/approve',
                headers={'Authorization': f'Bearer {token}'}
            )
            
            self.assertEqual(response.status_code, 404)


if __name__ == '__main__':
    unittest.main()