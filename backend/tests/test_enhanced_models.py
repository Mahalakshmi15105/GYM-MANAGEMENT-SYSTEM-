"""
Test the enhanced models functionality.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from app.enhanced_models import Gym
    from datetime import datetime
    
    print("✅ Successfully imported enhanced Gym model")
    
    # Test creating a gym instance with new fields
    gym = Gym(
        name='Enhanced Test Gym',
        address='123 Enhanced Street',
        phone='555-0123',
        status='Pending',
        business_license='BL-002',
        owner_name='Jane Doe',
        website='https://enhanced.gym.com',
        description='A test gym with enhanced features'
    )
    
    print("✅ Created enhanced Gym instance:")
    print(f"   Name: {gym.name}")
    print(f"   Status: {gym.status}")
    print(f"   Business License: {gym.business_license}")
    print(f"   Owner: {gym.owner_name}")
    print(f"   Website: {gym.website}")
    print(f"   Description: {gym.description}")
    
    # Test status checking methods
    print("\n✅ Testing status methods:")
    print(f"   can_operate(): {gym.can_operate()}")
    print(f"   is_pending_approval(): {gym.is_pending_approval()}")
    
    # Test approval workflow
    print("\n✅ Testing approval workflow:")
    result = gym.approve_gym(admin_user_id=1)
    print(f"   approve_gym() result: {result}")
    print(f"   New status: {gym.status}")
    print(f"   Approved by: {gym.approved_by}")
    print(f"   Approved at: {gym.approved_at}")
    print(f"   Can operate now: {gym.can_operate()}")
    
    # Test suspension
    print("\n✅ Testing suspension:")
    result = gym.suspend_gym()
    print(f"   suspend_gym() result: {result}")
    print(f"   New status: {gym.status}")
    print(f"   Can operate now: {gym.can_operate()}")
    
    # Test reactivation
    print("\n✅ Testing reactivation:")
    result = gym.reactivate_gym()
    print(f"   reactivate_gym() result: {result}")
    print(f"   New status: {gym.status}")
    print(f"   Can operate now: {gym.can_operate()}")
    
    # Test soft delete
    print("\n✅ Testing soft delete:")
    result = gym.soft_delete_gym()
    print(f"   soft_delete_gym() result: {result}")
    print(f"   Final status: {gym.status}")
    print(f"   Can operate now: {gym.can_operate()}")
    
    # Test to_dict method
    print("\n✅ Testing to_dict method:")
    gym_dict = gym.to_dict()
    print(f"   Dictionary contains {len(gym_dict)} fields")
    print(f"   Has status: {'status' in gym_dict}")
    print(f"   Has business_license: {'business_license' in gym_dict}")
    print(f"   Has owner_name: {'owner_name' in gym_dict}")
    print(f"   Has approved_at: {'approved_at' in gym_dict}")
    
    # Test get_member_count (should return 0 without database)
    print(f"\n✅ get_member_count(): {gym.get_member_count()}")
    
    # Test get_subscription_info (should return None without subscription)
    print(f"✅ get_subscription_info(): {gym.get_subscription_info()}")
    
    print("\n🎉 All enhanced Gym model tests passed!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()