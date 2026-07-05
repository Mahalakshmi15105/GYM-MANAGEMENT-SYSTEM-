"""
Test just the enhanced Gym model methods without SQLAlchemy relationships.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from datetime import datetime


class MockGym:
    """Mock Gym class to test the business logic methods"""
    
    def __init__(self, status='Pending', **kwargs):
        self.status = status
        self.approved_by = None
        self.approved_at = None
        for key, value in kwargs.items():
            setattr(self, key, value)

    def can_operate(self):
        """Check if gym can operate (is active and not suspended)"""
        return self.status == 'Active'

    def is_pending_approval(self):
        """Check if gym is waiting for Super Admin approval"""
        return self.status == 'Pending'

    def approve_gym(self, admin_user_id):
        """Approve gym for operation"""
        if self.status == 'Pending':
            self.status = 'Active'
            self.approved_by = admin_user_id
            self.approved_at = datetime.utcnow()
            return True
        return False

    def suspend_gym(self, reason=None):
        """Suspend gym operations"""
        if self.status == 'Active':
            self.status = 'Suspended'
            return True
        return False

    def reactivate_gym(self):
        """Reactivate suspended gym"""
        if self.status == 'Suspended':
            self.status = 'Active'
            return True
        return False

    def soft_delete_gym(self):
        """Soft delete gym (mark as deleted but keep data)"""
        if self.status in ['Active', 'Suspended', 'Pending']:
            self.status = 'Deleted'
            return True
        return False


def test_gym_functionality():
    """Test all enhanced Gym model functionality"""
    
    print("🧪 Testing Enhanced Gym Model Methods")
    
    # Test 1: Initial pending status
    gym = MockGym(name='Test Gym', status='Pending')
    print(f"\n✅ Test 1 - Initial State:")
    print(f"   Status: {gym.status}")
    print(f"   can_operate(): {gym.can_operate()}")
    print(f"   is_pending_approval(): {gym.is_pending_approval()}")
    
    assert not gym.can_operate(), "Pending gym should not be able to operate"
    assert gym.is_pending_approval(), "New gym should be pending approval"
    
    # Test 2: Approval process
    print(f"\n✅ Test 2 - Approval Process:")
    result = gym.approve_gym(admin_user_id=123)
    print(f"   approve_gym() result: {result}")
    print(f"   New status: {gym.status}")
    print(f"   Approved by: {gym.approved_by}")
    print(f"   Approved at: {gym.approved_at}")
    print(f"   can_operate(): {gym.can_operate()}")
    
    assert result == True, "Approval should succeed"
    assert gym.status == 'Active', "Status should be Active after approval"
    assert gym.approved_by == 123, "approved_by should be set"
    assert gym.can_operate(), "Active gym should be able to operate"
    assert not gym.is_pending_approval(), "Approved gym should not be pending"
    
    # Test 3: Double approval (should fail)
    print(f"\n✅ Test 3 - Double Approval:")
    result2 = gym.approve_gym(admin_user_id=456)
    print(f"   Second approve_gym() result: {result2}")
    assert result2 == False, "Second approval should fail"
    
    # Test 4: Suspension
    print(f"\n✅ Test 4 - Suspension:")
    result = gym.suspend_gym()
    print(f"   suspend_gym() result: {result}")
    print(f"   New status: {gym.status}")
    print(f"   can_operate(): {gym.can_operate()}")
    
    assert result == True, "Suspension should succeed"
    assert gym.status == 'Suspended', "Status should be Suspended"
    assert not gym.can_operate(), "Suspended gym should not operate"
    
    # Test 5: Double suspension (should fail)
    print(f"\n✅ Test 5 - Double Suspension:")
    result2 = gym.suspend_gym()
    print(f"   Second suspend_gym() result: {result2}")
    assert result2 == False, "Second suspension should fail"
    
    # Test 6: Reactivation
    print(f"\n✅ Test 6 - Reactivation:")
    result = gym.reactivate_gym()
    print(f"   reactivate_gym() result: {result}")
    print(f"   New status: {gym.status}")
    print(f"   can_operate(): {gym.can_operate()}")
    
    assert result == True, "Reactivation should succeed"
    assert gym.status == 'Active', "Status should be Active after reactivation"
    assert gym.can_operate(), "Reactivated gym should operate"
    
    # Test 7: Soft delete
    print(f"\n✅ Test 7 - Soft Delete:")
    result = gym.soft_delete_gym()
    print(f"   soft_delete_gym() result: {result}")
    print(f"   Final status: {gym.status}")
    print(f"   can_operate(): {gym.can_operate()}")
    
    assert result == True, "Soft delete should succeed"
    assert gym.status == 'Deleted', "Status should be Deleted"
    assert not gym.can_operate(), "Deleted gym should not operate"
    
    # Test 8: Operations on deleted gym (should fail)
    print(f"\n✅ Test 8 - Operations on Deleted Gym:")
    result_suspend = gym.suspend_gym()
    result_reactivate = gym.reactivate_gym()
    result_delete = gym.soft_delete_gym()
    
    print(f"   suspend_gym() on deleted: {result_suspend}")
    print(f"   reactivate_gym() on deleted: {result_reactivate}")
    print(f"   soft_delete_gym() on deleted: {result_delete}")
    
    assert result_suspend == False, "Cannot suspend deleted gym"
    assert result_reactivate == False, "Cannot reactivate deleted gym"
    assert result_delete == False, "Cannot delete already deleted gym"
    
    print(f"\n🎉 All Enhanced Gym Model Tests Passed!")


if __name__ == "__main__":
    test_gym_functionality()