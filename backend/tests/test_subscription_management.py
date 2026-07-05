"""
Unit tests for subscription management endpoints.
Tests all subscription-related functionality including CRUD operations, analytics, and status management.
"""

import unittest
from unittest.mock import patch, MagicMock
import json
from datetime import datetime, date, timedelta
from decimal import Decimal

from flask import Flask
from flask_jwt_extended import JWTManager, create_access_token


class TestSubscriptionManagement(unittest.TestCase):
    
    def setUp(self):
        """Set up test Flask app for subscription management testing."""
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
    
    @patch('app.routes.admin.GymSubscription')
    @patch('app.routes.admin.Gym')
    def test_list_subscriptions_success(self, mock_gym, mock_subscription):
        """Test successful subscription listing with pagination."""
        token = self.create_super_admin_token()
        
        # Mock pagination
        mock_pagination = MagicMock()
        mock_pagination.items = []
        mock_pagination.total = 0
        mock_pagination.pages = 0
        mock_pagination.has_next = False
        mock_pagination.has_prev = False
        
        mock_subscription.query.join.return_value.order_by.return_value.paginate.return_value = mock_pagination
        
        response = self.client.get(
            '/admin/subscriptions?status=Active&page=1&per_page=20',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        
        self.assertIn('subscriptions', data)
        self.assertIn('pagination', data)
        self.assertIn('filters', data)
        self.assertEqual(data['filters']['status'], 'Active')
    
    @patch('app.routes.admin.GymSubscription')
    def test_list_subscriptions_expiring_soon(self, mock_subscription):
        """Test listing subscriptions expiring soon."""
        token = self.create_super_admin_token()
        
        # Mock pagination for expiring subscriptions
        mock_pagination = MagicMock()
        mock_pagination.items = []
        mock_pagination.total = 5
        mock_pagination.pages = 1
        mock_pagination.has_next = False
        mock_pagination.has_prev = False
        
        mock_subscription.query.join.return_value.filter.return_value.order_by.return_value.paginate.return_value = mock_pagination
        
        response = self.client.get(
            '/admin/subscriptions?expiring_soon=true',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        
        self.assertTrue(data['filters']['expiring_soon'])
        self.assertEqual(data['pagination']['total'], 5)
    
    @patch('app.routes.admin.GymSubscription')
    @patch('app.routes.admin.Payment')
    def test_get_subscription_details(self, mock_payment, mock_subscription):
        """Test getting detailed subscription information."""
        token = self.create_super_admin_token()
        
        # Mock subscription instance
        mock_sub_instance = MagicMock()
        mock_sub_instance.gym_id = 1
        mock_sub_instance.to_dict.return_value = {
            'id': 1, 'plan_name': 'Professional', 'monthly_price': 59.99
        }
        mock_sub_instance.days_until_expiry.return_value = 15
        mock_sub_instance.is_active.return_value = True
        mock_sub_instance.get_usage_limits.return_value = {
            'max_members': 200, 'max_trainers': 5
        }
        
        mock_subscription.query.get_or_404.return_value = mock_sub_instance
        
        # Mock payment history
        mock_payment.query.filter_by.return_value.order_by.return_value.limit.return_value.all.return_value = []
        
        response = self.client.get(
            '/admin/subscriptions/1',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        
        self.assertEqual(data['id'], 1)
        self.assertEqual(data['days_until_expiry'], 15)
        self.assertTrue(data['is_active'])
        self.assertIn('payment_history', data)
        self.assertIn('usage_limits', data)
    
    @patch('app.routes.admin.GymSubscription')
    @patch('app.routes.admin.Gym')
    @patch('app.routes.admin.db.session.add')
    @patch('app.routes.admin.db.session.commit')
    @patch('app.routes.admin.log_activity')
    def test_create_subscription_success(self, mock_log, mock_commit, mock_add, mock_gym, mock_subscription):
        """Test successful subscription creation."""
        token = self.create_super_admin_token()
        
        # Mock gym instance
        mock_gym_instance = MagicMock()
        mock_gym_instance.name = 'Test Gym'
        mock_gym.query.get.return_value = mock_gym_instance
        
        # Mock no existing subscription
        mock_subscription.query.filter_by.return_value.first.return_value = None
        
        subscription_data = {
            'gym_id': 1,
            'plan_name': 'Professional',
            'monthly_price': 59.99,
            'max_members': 200,
            'max_trainers': 5,
            'billing_cycle_start': '2026-07-01',
            'billing_cycle_end': '2026-07-31',
            'next_billing_date': '2026-07-31',
            'features': {'api_access': True, 'advanced_reports': True}
        }
        
        response = self.client.post(
            '/admin/subscriptions',
            headers={'Authorization': f'Bearer {token}'},
            data=json.dumps(subscription_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        
        self.assertEqual(data['message'], 'Subscription created successfully')
        self.assertIn('subscription', data)
        mock_add.assert_called_once()
        mock_commit.assert_called_once()
        mock_log.assert_called_once()
    
    @patch('app.routes.admin.GymSubscription')
    @patch('app.routes.admin.Gym')
    def test_create_subscription_gym_not_found(self, mock_gym, mock_subscription):
        """Test subscription creation with non-existent gym."""
        token = self.create_super_admin_token()
        
        # Mock gym not found
        mock_gym.query.get.return_value = None
        
        subscription_data = {
            'gym_id': 999,
            'plan_name': 'Professional',
            'monthly_price': 59.99,
            'billing_cycle_start': '2026-07-01',
            'billing_cycle_end': '2026-07-31'
        }
        
        response = self.client.post(
            '/admin/subscriptions',
            headers={'Authorization': f'Bearer {token}'},
            data=json.dumps(subscription_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 404)
        data = response.get_json()
        self.assertEqual(data['error'], 'Gym not found')
    
    @patch('app.routes.admin.GymSubscription')
    def test_create_subscription_existing_active(self, mock_subscription):
        """Test subscription creation when gym already has active subscription."""
        token = self.create_super_admin_token()
        
        with patch('app.routes.admin.Gym') as mock_gym:
            # Mock gym exists
            mock_gym.query.get.return_value = MagicMock()
            
            # Mock existing active subscription
            mock_subscription.query.filter_by.return_value.first.return_value = MagicMock()
            
            subscription_data = {
                'gym_id': 1,
                'plan_name': 'Professional',
                'monthly_price': 59.99,
                'billing_cycle_start': '2026-07-01',
                'billing_cycle_end': '2026-07-31'
            }
            
            response = self.client.post(
                '/admin/subscriptions',
                headers={'Authorization': f'Bearer {token}'},
                data=json.dumps(subscription_data),
                content_type='application/json'
            )
            
            self.assertEqual(response.status_code, 400)
            data = response.get_json()
            self.assertEqual(data['error'], 'Gym already has an active subscription')
    
    @patch('app.routes.admin.GymSubscription')
    @patch('app.routes.admin.db.session.commit')
    @patch('app.routes.admin.log_activity')
    def test_update_subscription(self, mock_log, mock_commit, mock_subscription):
        """Test subscription update functionality."""
        token = self.create_super_admin_token()
        
        # Mock subscription instance
        mock_sub_instance = MagicMock()
        mock_sub_instance.plan_name = 'Basic'
        mock_sub_instance.monthly_price = Decimal('29.99')
        mock_sub_instance.to_dict.return_value = {'id': 1, 'plan_name': 'Professional'}
        
        mock_subscription.query.get_or_404.return_value = mock_sub_instance
        
        update_data = {
            'plan_name': 'Professional',
            'monthly_price': 59.99,
            'max_members': 200
        }
        
        response = self.client.put(
            '/admin/subscriptions/1',
            headers={'Authorization': f'Bearer {token}'},
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        
        self.assertEqual(data['message'], 'Subscription updated successfully')
        self.assertIn('changes', data)
        mock_commit.assert_called_once()
    
    @patch('app.routes.admin.GymSubscription')
    @patch('app.routes.admin.db.session.commit')
    @patch('app.routes.admin.log_activity')
    def test_suspend_subscription(self, mock_log, mock_commit, mock_subscription):
        """Test subscription suspension."""
        token = self.create_super_admin_token()
        
        # Mock active subscription
        mock_sub_instance = MagicMock()
        mock_sub_instance.status = 'Active'
        mock_sub_instance.gym.name = 'Test Gym'
        mock_sub_instance.to_dict.return_value = {'id': 1, 'status': 'Suspended'}
        
        mock_subscription.query.get_or_404.return_value = mock_sub_instance
        
        response = self.client.put(
            '/admin/subscriptions/1/suspend',
            headers={'Authorization': f'Bearer {token}'},
            data=json.dumps({'reason': 'Payment failure'}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        
        self.assertEqual(data['message'], 'Subscription suspended successfully')
        self.assertEqual(mock_sub_instance.status, 'Suspended')
        self.assertFalse(mock_sub_instance.auto_renew)
        mock_commit.assert_called_once()
        mock_log.assert_called_once()
    
    @patch('app.routes.admin.GymSubscription')
    def test_suspend_subscription_invalid_status(self, mock_subscription):
        """Test suspension of non-active subscription (should fail)."""
        token = self.create_super_admin_token()
        
        # Mock suspended subscription
        mock_sub_instance = MagicMock()
        mock_sub_instance.status = 'Cancelled'
        
        mock_subscription.query.get_or_404.return_value = mock_sub_instance
        
        response = self.client.put(
            '/admin/subscriptions/1/suspend',
            headers={'Authorization': f'Bearer {token}'},
            data=json.dumps({'reason': 'Test'}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertEqual(data['error'], 'Only active subscriptions can be suspended')
    
    @patch('app.routes.admin.GymSubscription')
    @patch('app.routes.admin.db.session.commit')
    @patch('app.routes.admin.log_activity')
    def test_reactivate_subscription(self, mock_log, mock_commit, mock_subscription):
        """Test subscription reactivation."""
        token = self.create_super_admin_token()
        
        # Mock suspended subscription
        mock_sub_instance = MagicMock()
        mock_sub_instance.status = 'Suspended'
        mock_sub_instance.billing_cycle_end = date.today() + timedelta(days=20)
        mock_sub_instance.next_billing_date = date.today() + timedelta(days=20)
        mock_sub_instance.gym.name = 'Test Gym'
        mock_sub_instance.to_dict.return_value = {'id': 1, 'status': 'Active'}
        
        mock_subscription.query.get_or_404.return_value = mock_sub_instance
        
        response = self.client.put(
            '/admin/subscriptions/1/reactivate',
            headers={'Authorization': f'Bearer {token}'},
            data=json.dumps({'extend_billing_cycle_days': 7, 'auto_renew': True}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        
        self.assertEqual(data['message'], 'Subscription reactivated successfully')
        self.assertEqual(mock_sub_instance.status, 'Active')
        self.assertTrue(mock_sub_instance.auto_renew)
        mock_commit.assert_called_once()
        mock_log.assert_called_once()
    
    @patch('app.routes.admin.GymSubscription')
    @patch('app.routes.admin.db.session.commit')
    @patch('app.routes.admin.log_activity')
    def test_cancel_subscription_immediate(self, mock_log, mock_commit, mock_subscription):
        """Test immediate subscription cancellation."""
        token = self.create_super_admin_token()
        
        # Mock active subscription
        mock_sub_instance = MagicMock()
        mock_sub_instance.status = 'Active'
        mock_sub_instance.gym.name = 'Test Gym'
        mock_sub_instance.to_dict.return_value = {'id': 1, 'status': 'Cancelled'}
        
        mock_subscription.query.get_or_404.return_value = mock_sub_instance
        
        response = self.client.put(
            '/admin/subscriptions/1/cancel',
            headers={'Authorization': f'Bearer {token}'},
            data=json.dumps({'reason': 'Requested by customer', 'immediate': True}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        
        self.assertEqual(data['message'], 'Subscription cancelled successfully')
        self.assertEqual(mock_sub_instance.status, 'Cancelled')
        self.assertFalse(mock_sub_instance.auto_renew)
        self.assertEqual(mock_sub_instance.billing_cycle_end, date.today())
        mock_commit.assert_called_once()
        mock_log.assert_called_once()
    
    @patch('app.routes.admin.db.session.query')
    def test_get_subscription_analytics(self, mock_query):
        """Test subscription analytics endpoint."""
        token = self.create_super_admin_token()
        
        # Mock status breakdown query
        mock_status_result = [
            MagicMock(status='Active', count=25, total_revenue=Decimal('1500.00')),
            MagicMock(status='Suspended', count=3, total_revenue=Decimal('180.00')),
            MagicMock(status='Cancelled', count=2, total_revenue=Decimal('120.00'))
        ]
        
        # Mock plan popularity query
        mock_plan_result = [
            MagicMock(plan_name='Professional', count=15, avg_price=Decimal('59.99')),
            MagicMock(plan_name='Basic', count=8, avg_price=Decimal('29.99')),
            MagicMock(plan_name='Enterprise', count=2, avg_price=Decimal('99.99'))
        ]
        
        # Setup query return values
        mock_query.return_value.group_by.return_value.all.side_effect = [
            mock_status_result,  # First call for status breakdown
            mock_plan_result     # Second call for plan popularity
        ]
        
        # Mock scalar queries
        mock_query.return_value.filter.return_value.scalar.return_value = 1800.00
        
        with patch('app.routes.admin.GymSubscription') as mock_subscription:
            # Mock expiring subscriptions count
            mock_subscription.query.filter.return_value.count.side_effect = [5, 20, 5]
            
            response = self.client.get(
                '/admin/subscriptions/analytics',
                headers={'Authorization': f'Bearer {token}'}
            )
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        
        self.assertIn('status_breakdown', data)
        self.assertIn('plan_popularity', data)
        self.assertIn('metrics', data)
        self.assertIn('generated_at', data)
        
        # Verify status breakdown structure
        self.assertEqual(len(data['status_breakdown']), 3)
        self.assertEqual(data['status_breakdown'][0]['status'], 'Active')
        self.assertEqual(data['status_breakdown'][0]['count'], 25)
        
        # Verify metrics
        self.assertIn('total_monthly_revenue', data['metrics'])
        self.assertIn('expiring_next_30_days', data['metrics'])
    
    def test_get_subscription_plans(self):
        """Test getting available subscription plans."""
        token = self.create_super_admin_token()
        
        response = self.client.get(
            '/admin/subscriptions/plans',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        
        self.assertIn('plans', data)
        plans = data['plans']
        
        # Should have at least 3 predefined plans
        self.assertGreaterEqual(len(plans), 3)
        
        # Check plan structure
        for plan in plans:
            self.assertIn('name', plan)
            self.assertIn('monthly_price', plan)
            self.assertIn('max_members', plan)
            self.assertIn('max_trainers', plan)
            self.assertIn('features', plan)
        
        # Verify specific plans exist
        plan_names = [plan['name'] for plan in plans]
        self.assertIn('Basic', plan_names)
        self.assertIn('Professional', plan_names)
        self.assertIn('Enterprise', plan_names)
    
    def test_subscription_management_requires_super_admin(self):
        """Test that all subscription endpoints require Super Admin role."""
        # Create gym owner token
        with self.app.app_context():
            gym_owner_token = create_access_token(
                identity='2',
                additional_claims={
                    'role': 'gym_owner',
                    'gym_id': 1,
                    'email': 'owner@testgym.com'
                }
            )
        
        endpoints = [
            ('GET', '/admin/subscriptions'),
            ('GET', '/admin/subscriptions/1'),
            ('POST', '/admin/subscriptions'),
            ('PUT', '/admin/subscriptions/1'),
            ('PUT', '/admin/subscriptions/1/suspend'),
            ('PUT', '/admin/subscriptions/1/reactivate'),
            ('PUT', '/admin/subscriptions/1/cancel'),
            ('GET', '/admin/subscriptions/analytics'),
            ('GET', '/admin/subscriptions/plans')
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


if __name__ == '__main__':
    unittest.main()