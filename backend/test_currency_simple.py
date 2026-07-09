#!/usr/bin/env python3
"""
Simple test to verify currency functionality works correctly
"""
import os
import sys

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db
from app.models import Gym
from app.currency_utils import get_gym_currency, DEFAULT_CURRENCY

def test_currency_functionality():
    """Test that currency functionality works"""
    print("Testing Currency Functionality...")
    
    app = create_app()
    with app.app_context():
        try:
            # Test 1: Default currency
            print(f"✓ DEFAULT_CURRENCY = {DEFAULT_CURRENCY}")
            
            # Test 2: get_gym_currency with None
            currency = get_gym_currency(None)
            print(f"✓ get_gym_currency(None) = {currency}")
            assert currency == DEFAULT_CURRENCY, f"Expected {DEFAULT_CURRENCY}, got {currency}"
            
            # Test 3: get_gym_currency with non-existent gym
            currency = get_gym_currency(99999)
            print(f"✓ get_gym_currency(99999) = {currency}")
            assert currency == DEFAULT_CURRENCY, f"Expected {DEFAULT_CURRENCY}, got {currency}"
            
            # Test 4: Check if any gyms exist with currency
            gyms_with_currency = Gym.query.filter(Gym.currency.isnot(None)).count()
            print(f"✓ Gyms with currency set: {gyms_with_currency}")
            
            # Test 5: Check first gym if exists
            first_gym = Gym.query.first()
            if first_gym:
                print(f"✓ First gym ID: {first_gym.id}, Currency: {first_gym.currency or 'None'}")
                currency = get_gym_currency(first_gym.id)
                expected = first_gym.currency or DEFAULT_CURRENCY
                print(f"✓ get_gym_currency({first_gym.id}) = {currency}")
                assert currency == expected, f"Expected {expected}, got {currency}"
            else:
                print("✓ No gyms found in database")
            
            print("\n✅ ALL CURRENCY TESTS PASSED!")
            return True
            
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    success = test_currency_functionality()
    sys.exit(0 if success else 1)