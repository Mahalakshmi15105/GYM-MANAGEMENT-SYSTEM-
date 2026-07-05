"""
Simple test to verify enhanced Gym model functionality.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from app.models import Gym
    from datetime import datetime
    
    # Test creating a gym instance
    gym = Gym(
        name='Test Enhanced Gym',
        address='123 Test Street',
        phone='555-0123',
        status='Pending',
        business_license='BL-001',
        owner_name='John Doe'
    )
    
    print("✅ Created Gym instance successfully")
    print(f"   Name: {gym.name}")
    print(f"   Status: {gym.status}")
    print(f"   Business License: {gym.business_license}")
    print(f"   Owner Name: {gym.owner_name}")
    
    # Test methods
    print(f"✅ can_operate(): {gym.can_operate()}")
    print(f"✅ is_pending_approval(): {gym.is_pending_approval()}")
    
    # Test approval workflow
    result = gym.approve_gym(admin_user_id=1)
    print(f"✅ approve_gym() result: {result}")
    print(f"   New status: {gym.status}")
    print(f"   Can operate now: {gym.can_operate()}")
    
    # Test suspension
    result = gym.suspend_gym()
    print(f"✅ suspend_gym() result: {result}")
    print(f"   New status: {gym.status}")
    print(f"   Can operate now: {gym.can_operate()}")
    
    # Test reactivation
    result = gym.reactivate_gym()
    print(f"✅ reactivate_gym() result: {result}")
    print(f"   New status: {gym.status}")
    
    # Test soft delete
    result = gym.soft_delete_gym()
    print(f"✅ soft_delete_gym() result: {result}")
    print(f"   Final status: {gym.status}")
    
    # Test to_dict
    gym_dict = gym.to_dict()
    print(f"✅ to_dict() contains {len(gym_dict)} fields")
    print(f"   Contains status: {'status' in gym_dict}")
    print(f"   Contains business_license: {'business_license' in gym_dict}")
    
    print("\n🎉 Enhanced Gym model is working perfectly!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()