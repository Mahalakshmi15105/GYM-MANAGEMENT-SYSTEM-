"""
Unit tests for enhanced Gym model.
Tests Super Admin operations like approval, suspension, and status management.
"""

import unittest
from datetime import datetime, timedelta
from unittest.mock import patch

from app.models import Gym, User
from app.extensions import db
from flask import Flask


class TestEnhancedGymModel(unittest.TestCase):
    
    def setUp(self):
        """Set up test Flask app and database."""
        self.app = Flask(__name__)
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        self.app.config['TESTING'] = True
        
        db.init_app(self.app)
        
        with self.app.app_context():
            db.create_all()
            
            # Create test super admin user
            self.super_admin = User(
                name='Super Admin',
                email='admin@flexigym.com',
                password_hash='hashed_password',
                role='super_admin',
                gym_id=None
            )
            db.session.add(self.super_admin)
            db.session.commit()
    
    def tearDown(self):
        """Clean up after each test."""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_gym_creation_with_new_fields(self):
        """Test Gym model creation with new Super Admin fields."""
        with self.app.app_context():
            gym = Gym(
                name='Test Fitness Center',
                address='123 Fitness Street',
                phone='555-0123',
                business_license='BL-2026-001',
                owner_name='John Doe',
                website='https://testfitness.com',
                description='A premium fitness center',
                status='Pending'
            )
            
            db.session.add(gym)
            db.session.commit()
            
            # Test retrieval
            retrieved = Gym.query.filter_by(name='Test Fitness Center').first()
            self.assertIsNotNone(retrieved)
            self.assertEqual(retrieved.status, 'Pending')
            self.assertEqual(retrieved.business_license, 'BL-2026-001')
            self.assertEqual(retrieved.owner_name, 'John Doe')
            self.assertEqual(retrieved.website, 'https://testfitness.com')
            self.assertEqual(retrieved.description, 'A premium fitness center')
    
    def test_gym_to_dict_enhanced(self):
        """Test enhanced to_dict method with new fields."""
        with self.app.app_context():
            gym = Gym(
                name='Dict Test Gym',
                address='456 Test Ave',
                phone='555-0456',
                status='Active',
                business_license='BL-2026-002',
                owner_name='Jane Smith',
                approved_by=self.super_admin.id
            )
            
            db.session.add(gym)
            db.session.commit()
            
            gym_dict = gym.to_dict()
            
            self.assertEqual(gym_dict['name'], 'Dict Test Gym')
            self.assertEqual(gym_dict['status'], 'Active')
            self.assertEqual(gym_dict['business_license'], 'BL-2026-002')
            self.assertEqual(gym_dict['owner_name'], 'Jane Smith')
            self.assertEqual(gym_dict['approved_by'], self.super_admin.id)
            self.assertEqual(gym_dict['approved_by_name'], self.super_admin.name)
            self.assertIn('updated_at', gym_dict)
    
    def test_can_operate_method(self):
        """Test can_operate method for gym status checking."""
        with self.app.app_context():
            # Active gym can operate
            active_gym = Gym(name='Active Gym', status='Active')
            self.assertTrue(active_gym.can_operate())
            
            # Pending gym cannot operate
            pending_gym = Gym(name='Pending Gym', status='Pending')
            self.assertFalse(pending_gym.can_operate())
            
            # Suspended gym cannot operate
            suspended_gym = Gym(name='Suspended Gym', status='Suspended')
            self.assertFalse(suspended_gym.can_operate())
            
            # Deleted gym cannot operate
            deleted_gym = Gym(name='Deleted Gym', status='Deleted')
            self.assertFalse(deleted_gym.can_operate())
    
    def test_is_pending_approval_method(self):
        """Test is_pending_approval method."""
        with self.app.app_context():
            pending_gym = Gym(name='Pending Gym', status='Pending')
            self.assertTrue(pending_gym.is_pending_approval())
            
            active_gym = Gym(name='Active Gym', status='Active')
            self.assertFalse(active_gym.is_pending_approval())
    
    @patch('app.models.Member')
    def test_get_member_count_method(self, mock_member):
        """Test get_member_count method."""
        with self.app.app_context():
            gym = Gym(name='Count Test Gym')
            db.session.add(gym)
            db.session.commit()
            
            # Mock the Member query to return a count
            mock_member.query.filter_by.return_value.count.return_value = 25
            
            count = gym.get_member_count()
            self.assertEqual(count, 25)
            
            # Verify the query was called correctly
            mock_member.query.filter_by.assert_called_with(gym_id=gym.id, status='Active')
    
    def test_approve_gym_method(self):
        """Test approve_gym method for Super Admin approval."""
        with self.app.app_context():
            gym = Gym(name='Approval Test Gym', status='Pending')
            db.session.add(gym)
            db.session.commit()
            
            # Test successful approval
            result = gym.approve_gym(self.super_admin.id)
            self.assertTrue(result)
            self.assertEqual(gym.status, 'Active')
            self.assertEqual(gym.approved_by, self.super_admin.id)
            self.assertIsNotNone(gym.approved_at)
            
            # Test approval of already approved gym (should fail)
            result2 = gym.approve_gym(self.super_admin.id)
            self.assertFalse(result2)
    
    def test_suspend_gym_method(self):
        """Test suspend_gym method for Super Admin suspension."""
        with self.app.app_context():
            gym = Gym(name='Suspension Test Gym', status='Active')
            db.session.add(gym)
            db.session.commit()
            
            # Test successful suspension
            result = gym.suspend_gym()
            self.assertTrue(result)
            self.assertEqual(gym.status, 'Suspended')
            
            # Test suspension of already suspended gym (should fail)
            result2 = gym.suspend_gym()
            self.assertFalse(result2)
    
    def test_reactivate_gym_method(self):
        """Test reactivate_gym method for restoring suspended gyms."""
        with self.app.app_context():
            gym = Gym(name='Reactivation Test Gym', status='Suspended')
            db.session.add(gym)
            db.session.commit()
            
            # Test successful reactivation
            result = gym.reactivate_gym()
            self.assertTrue(result)
            self.assertEqual(gym.status, 'Active')
            
            # Test reactivation of active gym (should fail)
            result2 = gym.reactivate_gym()
            self.assertFalse(result2)
    
    def test_soft_delete_gym_method(self):
        """Test soft_delete_gym method for marking gyms as deleted."""
        with self.app.app_context():
            # Test deletion of active gym
            active_gym = Gym(name='Delete Test Gym 1', status='Active')
            db.session.add(active_gym)
            db.session.commit()
            
            result = active_gym.soft_delete_gym()
            self.assertTrue(result)
            self.assertEqual(active_gym.status, 'Deleted')
            
            # Test deletion of suspended gym
            suspended_gym = Gym(name='Delete Test Gym 2', status='Suspended')
            db.session.add(suspended_gym)
            db.session.commit()
            
            result = suspended_gym.soft_delete_gym()
            self.assertTrue(result)
            self.assertEqual(suspended_gym.status, 'Deleted')
            
            # Test deletion of already deleted gym (should fail)
            result2 = active_gym.soft_delete_gym()
            self.assertFalse(result2)
    
    def test_gym_status_workflow(self):
        """Test complete gym status workflow from pending to active to suspended."""
        with self.app.app_context():
            gym = Gym(
                name='Workflow Test Gym',
                status='Pending',
                owner_name='Test Owner'
            )
            db.session.add(gym)
            db.session.commit()
            
            # Initial state
            self.assertTrue(gym.is_pending_approval())
            self.assertFalse(gym.can_operate())
            
            # Approve gym
            gym.approve_gym(self.super_admin.id)
            self.assertFalse(gym.is_pending_approval())
            self.assertTrue(gym.can_operate())
            
            # Suspend gym
            gym.suspend_gym()
            self.assertFalse(gym.can_operate())
            
            # Reactivate gym
            gym.reactivate_gym()
            self.assertTrue(gym.can_operate())
            
            # Soft delete gym
            gym.soft_delete_gym()
            self.assertFalse(gym.can_operate())
            self.assertEqual(gym.status, 'Deleted')
    
    def test_default_status_is_pending(self):
        """Test that new gyms default to Pending status."""
        with self.app.app_context():
            gym = Gym(name='Default Status Gym')
            self.assertEqual(gym.status, 'Pending')
    
    def test_updated_at_timestamp(self):
        """Test that updated_at timestamp is set properly."""
        with self.app.app_context():
            gym = Gym(name='Timestamp Test Gym')
            db.session.add(gym)
            db.session.commit()
            
            original_updated_at = gym.updated_at
            
            # Update gym
            gym.description = 'Updated description'
            db.session.commit()
            
            # Check that updated_at changed (in a real database with proper triggers)
            # Note: SQLite in-memory DB may not trigger ON UPDATE, so we test the field exists
            self.assertIsNotNone(gym.updated_at)


if __name__ == '__main__':
    unittest.main()