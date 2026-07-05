"""
Unit tests for Super Admin models.
Tests SystemSettings, ActivityLog, and GymSubscription model functionality.
"""

import unittest
from datetime import datetime, date, timedelta
from decimal import Decimal
from unittest.mock import patch

from app.super_admin_models import SystemSettings, ActivityLog, GymSubscription
from app.models import Gym, User
from app.extensions import db
from flask import Flask


class TestSuperAdminModels(unittest.TestCase):
    
    def setUp(self):
        """Set up test Flask app and database."""
        self.app = Flask(__name__)
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        self.app.config['TESTING'] = True
        
        db.init_app(self.app)
        
        with self.app.app_context():
            db.create_all()
            
            # Create test gym and user
            self.test_gym = Gym(name='Test Gym', address='123 Test St', phone='1234567890')
            db.session.add(self.test_gym)
            db.session.flush()
            
            self.test_user = User(
                name='Test User',
                email='test@example.com',
                password_hash='hashed_password',
                role='super_admin',
                gym_id=None
            )
            db.session.add(self.test_user)
            db.session.commit()
    
    def tearDown(self):
        """Clean up after each test."""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_system_settings_creation(self):
        """Test SystemSettings model creation and validation."""
        with self.app.app_context():
            setting = SystemSettings(
                setting_key='test_setting',
                setting_value='test_value',
                setting_type='string',
                description='Test setting description',
                category='test',
                updated_by=self.test_user.id
            )
            
            db.session.add(setting)
            db.session.commit()
            
            # Test retrieval
            retrieved = SystemSettings.query.filter_by(setting_key='test_setting').first()
            self.assertIsNotNone(retrieved)
            self.assertEqual(retrieved.setting_value, 'test_value')
            self.assertEqual(retrieved.setting_type, 'string')
            self.assertEqual(retrieved.category, 'test')
            self.assertEqual(retrieved.updated_by, self.test_user.id)
    
    def test_system_settings_to_dict(self):
        """Test SystemSettings to_dict method."""
        with self.app.app_context():
            setting = SystemSettings(
                setting_key='test_dict',
                setting_value='dict_value',
                setting_type='string',
                description='Test dict conversion',
                category='general',
                updated_by=self.test_user.id
            )
            
            db.session.add(setting)
            db.session.commit()
            
            setting_dict = setting.to_dict()
            
            self.assertEqual(setting_dict['setting_key'], 'test_dict')
            self.assertEqual(setting_dict['setting_value'], 'dict_value')
            self.assertEqual(setting_dict['setting_type'], 'string')
            self.assertEqual(setting_dict['category'], 'general')
            self.assertEqual(setting_dict['updated_by'], self.test_user.id)
            self.assertIn('created_at', setting_dict)
            self.assertIn('updated_at', setting_dict)
    
    def test_system_settings_get_typed_value(self):
        """Test SystemSettings type conversion functionality."""
        with self.app.app_context():
            # Test boolean conversion
            bool_setting = SystemSettings(
                setting_key='bool_test',
                setting_value='true',
                setting_type='boolean',
                updated_by=self.test_user.id
            )
            self.assertTrue(bool_setting.get_typed_value())
            
            bool_setting.setting_value = 'false'
            self.assertFalse(bool_setting.get_typed_value())
            
            # Test number conversion
            num_setting = SystemSettings(
                setting_key='num_test',
                setting_value='42',
                setting_type='number',
                updated_by=self.test_user.id
            )
            self.assertEqual(num_setting.get_typed_value(), 42)
            
            num_setting.setting_value = '3.14'
            self.assertEqual(num_setting.get_typed_value(), 3.14)
            
            # Test string (default)
            str_setting = SystemSettings(
                setting_key='str_test',
                setting_value='hello world',
                setting_type='string',
                updated_by=self.test_user.id
            )
            self.assertEqual(str_setting.get_typed_value(), 'hello world')
    
    def test_activity_log_creation(self):
        """Test ActivityLog model creation and validation."""
        with self.app.app_context():
            log = ActivityLog(
                user_id=self.test_user.id,
                gym_id=self.test_gym.id,
                action_type='create',
                entity_type='member',
                entity_id=123,
                description='Created new member',
                ip_address='192.168.1.1',
                user_agent='Test Browser',
                request_method='POST',
                request_path='/api/members',
                extra_data={'test': 'data'},
                severity='info'
            )
            
            db.session.add(log)
            db.session.commit()
            
            # Test retrieval
            retrieved = ActivityLog.query.filter_by(action_type='create').first()
            self.assertIsNotNone(retrieved)
            self.assertEqual(retrieved.entity_type, 'member')
            self.assertEqual(retrieved.entity_id, 123)
            self.assertEqual(retrieved.description, 'Created new member')
            self.assertEqual(retrieved.severity, 'info')
            self.assertEqual(retrieved.extra_data, {'test': 'data'})
    
    def test_activity_log_to_dict(self):
        """Test ActivityLog to_dict method."""
        with self.app.app_context():
            log = ActivityLog(
                user_id=self.test_user.id,
                gym_id=self.test_gym.id,
                action_type='update',
                entity_type='payment',
                entity_id=456,
                description='Updated payment status',
                severity='warning'
            )
            
            db.session.add(log)
            db.session.commit()
            
            log_dict = log.to_dict()
            
            self.assertEqual(log_dict['action_type'], 'update')
            self.assertEqual(log_dict['entity_type'], 'payment')
            self.assertEqual(log_dict['entity_id'], 456)
            self.assertEqual(log_dict['user_name'], self.test_user.name)
            self.assertEqual(log_dict['gym_name'], self.test_gym.name)
            self.assertIn('timestamp', log_dict)
    
    def test_gym_subscription_creation(self):
        """Test GymSubscription model creation and validation."""
        with self.app.app_context():
            subscription = GymSubscription(
                gym_id=self.test_gym.id,
                plan_name='Premium Plan',
                monthly_price=Decimal('99.99'),
                max_members=500,
                max_trainers=10,
                features={'analytics': True, 'api_access': True},
                billing_cycle_start=date.today(),
                billing_cycle_end=date.today() + timedelta(days=30),
                next_billing_date=date.today() + timedelta(days=30),
                status='Active',
                created_by=self.test_user.id
            )
            
            db.session.add(subscription)
            db.session.commit()
            
            # Test retrieval
            retrieved = GymSubscription.query.filter_by(gym_id=self.test_gym.id).first()
            self.assertIsNotNone(retrieved)
            self.assertEqual(retrieved.plan_name, 'Premium Plan')
            self.assertEqual(retrieved.monthly_price, Decimal('99.99'))
            self.assertEqual(retrieved.max_members, 500)
            self.assertEqual(retrieved.features, {'analytics': True, 'api_access': True})
            self.assertEqual(retrieved.status, 'Active')
    
    def test_gym_subscription_to_dict(self):
        """Test GymSubscription to_dict method."""
        with self.app.app_context():
            subscription = GymSubscription(
                gym_id=self.test_gym.id,
                plan_name='Basic Plan',
                monthly_price=Decimal('49.99'),
                max_members=100,
                max_trainers=5,
                billing_cycle_start=date.today(),
                billing_cycle_end=date.today() + timedelta(days=30),
                next_billing_date=date.today() + timedelta(days=30),
                created_by=self.test_user.id
            )
            
            db.session.add(subscription)
            db.session.commit()
            
            sub_dict = subscription.to_dict()
            
            self.assertEqual(sub_dict['plan_name'], 'Basic Plan')
            self.assertEqual(sub_dict['monthly_price'], 49.99)
            self.assertEqual(sub_dict['max_members'], 100)
            self.assertEqual(sub_dict['gym_name'], self.test_gym.name)
            self.assertEqual(sub_dict['created_by_name'], self.test_user.name)
            self.assertIn('created_at', sub_dict)
    
    def test_gym_subscription_is_active(self):
        """Test GymSubscription is_active method."""
        with self.app.app_context():
            # Active subscription
            active_sub = GymSubscription(
                gym_id=self.test_gym.id,
                plan_name='Active Plan',
                monthly_price=Decimal('99.99'),
                billing_cycle_start=date.today() - timedelta(days=15),
                billing_cycle_end=date.today() + timedelta(days=15),
                next_billing_date=date.today() + timedelta(days=15),
                status='Active',
                created_by=self.test_user.id
            )
            
            self.assertTrue(active_sub.is_active())
            
            # Expired subscription
            expired_sub = GymSubscription(
                gym_id=self.test_gym.id,
                plan_name='Expired Plan',
                monthly_price=Decimal('99.99'),
                billing_cycle_start=date.today() - timedelta(days=60),
                billing_cycle_end=date.today() - timedelta(days=30),
                next_billing_date=date.today() - timedelta(days=30),
                status='Active',
                created_by=self.test_user.id
            )
            
            self.assertFalse(expired_sub.is_active())
            
            # Suspended subscription
            suspended_sub = GymSubscription(
                gym_id=self.test_gym.id,
                plan_name='Suspended Plan',
                monthly_price=Decimal('99.99'),
                billing_cycle_start=date.today() - timedelta(days=15),
                billing_cycle_end=date.today() + timedelta(days=15),
                next_billing_date=date.today() + timedelta(days=15),
                status='Suspended',
                created_by=self.test_user.id
            )
            
            self.assertFalse(suspended_sub.is_active())
    
    def test_gym_subscription_days_until_expiry(self):
        """Test GymSubscription days_until_expiry method."""
        with self.app.app_context():
            subscription = GymSubscription(
                gym_id=self.test_gym.id,
                plan_name='Test Plan',
                monthly_price=Decimal('99.99'),
                billing_cycle_start=date.today(),
                billing_cycle_end=date.today() + timedelta(days=30),
                next_billing_date=date.today() + timedelta(days=30),
                created_by=self.test_user.id
            )
            
            days_left = subscription.days_until_expiry()
            self.assertEqual(days_left, 30)
    
    def test_gym_subscription_get_usage_limits(self):
        """Test GymSubscription get_usage_limits method."""
        with self.app.app_context():
            subscription = GymSubscription(
                gym_id=self.test_gym.id,
                plan_name='Feature Plan',
                monthly_price=Decimal('99.99'),
                max_members=200,
                max_trainers=8,
                features={'analytics': True, 'custom_branding': False},
                billing_cycle_start=date.today(),
                billing_cycle_end=date.today() + timedelta(days=30),
                next_billing_date=date.today() + timedelta(days=30),
                created_by=self.test_user.id
            )
            
            limits = subscription.get_usage_limits()
            
            self.assertEqual(limits['max_members'], 200)
            self.assertEqual(limits['max_trainers'], 8)
            self.assertEqual(limits['features']['analytics'], True)
            self.assertEqual(limits['features']['custom_branding'], False)


if __name__ == '__main__':
    unittest.main()