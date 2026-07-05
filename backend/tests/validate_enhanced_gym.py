"""
Validation script for enhanced Gym model.
Tests that all new fields and methods are properly added.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from app.models import Gym
    print("✅ Successfully imported enhanced Gym model")
    
    # Test new fields exist
    new_fields = [
        'status', 'subscription_id', 'approved_at', 'approved_by',
        'business_license', 'owner_name', 'website', 'description', 'updated_at'
    ]
    
    for field in new_fields:
        if hasattr(Gym, field):
            print(f"✅ Gym.{field} field exists")
        else:
            print(f"❌ Gym.{field} field missing")
    
    # Test new methods exist
    new_methods = [
        'can_operate', 'is_pending_approval', 'get_member_count',
        'get_subscription_info', 'approve_gym', 'suspend_gym',
        'reactivate_gym', 'soft_delete_gym'
    ]
    
    for method in new_methods:
        if hasattr(Gym, method):
            print(f"✅ Gym.{method} method exists")
        else:
            print(f"❌ Gym.{method} method missing")
    
    # Test that original fields still exist
    original_fields = ['id', 'name', 'address', 'phone', 'created_at']
    for field in original_fields:
        if hasattr(Gym, field):
            print(f"✅ Original Gym.{field} field preserved")
        else:
            print(f"❌ Original Gym.{field} field missing!")
    
    # Test that to_dict method still exists
    if hasattr(Gym, 'to_dict'):
        print("✅ Gym.to_dict method exists")
    else:
        print("❌ Gym.to_dict method missing!")
    
    print("\n🎉 Enhanced Gym model validation completed!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Validation error: {e}")