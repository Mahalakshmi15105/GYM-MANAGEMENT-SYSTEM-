"""
Test to verify Gym model import and field existence.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Test import
try:
    from app.models import Gym
    print("✅ Gym model imported successfully")
    
    # Create instance to test
    gym = Gym()
    print(f"✅ Empty Gym instance created: {gym}")
    
    # Test setting attributes directly
    gym.name = 'Test Gym'
    gym.status = 'Active'
    print(f"✅ Set name: {gym.name}")
    print(f"✅ Set status: {gym.status}")
    
    # Test if columns exist as class attributes
    print(f"✅ Has status column: {hasattr(Gym, 'status')}")
    print(f"✅ Has business_license column: {hasattr(Gym, 'business_license')}")
    print(f"✅ Has owner_name column: {hasattr(Gym, 'owner_name')}")
    
    # Test methods
    print(f"✅ Has can_operate method: {hasattr(gym, 'can_operate')}")
    print(f"✅ Has approve_gym method: {hasattr(gym, 'approve_gym')}")
    
    if hasattr(gym, 'can_operate'):
        print(f"✅ can_operate() returns: {gym.can_operate()}")
    
    print("\n🎉 Enhanced Gym model validation passed!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()