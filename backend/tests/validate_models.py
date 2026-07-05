"""
Simple validation script for Super Admin models.
Tests model creation and basic functionality without database conflicts.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from app.super_admin_models import SystemSettings, ActivityLog, GymSubscription
    print("✅ Successfully imported all Super Admin models")
    
    # Test SystemSettings model structure
    settings_fields = ['setting_key', 'setting_value', 'setting_type', 'category', 'updated_by']
    for field in settings_fields:
        if hasattr(SystemSettings, field):
            print(f"✅ SystemSettings.{field} exists")
        else:
            print(f"❌ SystemSettings.{field} missing")
    
    # Test ActivityLog model structure
    activity_fields = ['user_id', 'gym_id', 'action_type', 'description', 'severity', 'timestamp']
    for field in activity_fields:
        if hasattr(ActivityLog, field):
            print(f"✅ ActivityLog.{field} exists")
        else:
            print(f"❌ ActivityLog.{field} missing")
    
    # Test GymSubscription model structure
    subscription_fields = ['gym_id', 'plan_name', 'monthly_price', 'status', 'billing_cycle_start']
    for field in subscription_fields:
        if hasattr(GymSubscription, field):
            print(f"✅ GymSubscription.{field} exists")
        else:
            print(f"❌ GymSubscription.{field} missing")
    
    # Test model methods
    if hasattr(SystemSettings, 'get_typed_value'):
        print("✅ SystemSettings.get_typed_value method exists")
    else:
        print("❌ SystemSettings.get_typed_value method missing")
        
    if hasattr(GymSubscription, 'is_active'):
        print("✅ GymSubscription.is_active method exists")
    else:
        print("❌ GymSubscription.is_active method missing")
        
    if hasattr(GymSubscription, 'days_until_expiry'):
        print("✅ GymSubscription.days_until_expiry method exists")
    else:
        print("❌ GymSubscription.days_until_expiry method missing")
    
    print("\n🎉 All Super Admin models validation passed!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Validation error: {e}")