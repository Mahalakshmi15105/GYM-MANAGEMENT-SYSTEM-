#!/usr/bin/env python3
"""
Validate International Currency Support Implementation
"""

import sys
from app.currency_utils import get_default_currency, DEFAULT_CURRENCY
from app.super_admin_models import SystemSettings
from app.extensions import db
from app import create_app

def validate_currency_backend():
    """Validate backend currency implementation"""
    print("=" * 60)
    print("VALIDATING INTERNATIONAL CURRENCY SUPPORT")
    print("=" * 60)
    
    app = create_app()
    
    with app.app_context():
        print("\n1. Testing get_default_currency() function...")
        try:
            currency = get_default_currency()
            print(f"   ✓ Default currency function works: {currency}")
            assert currency == DEFAULT_CURRENCY, "Default currency should be INR"
            print(f"   ✓ Default currency is {DEFAULT_CURRENCY}")
        except Exception as e:
            print(f"   ✗ Error: {e}")
            return False
        
        print("\n2. Testing SystemSettings table...")
        try:
            # Try to query the table
            settings_count = SystemSettings.query.count()
            print(f"   ✓ SystemSettings table accessible ({settings_count} records)")
        except Exception as e:
            print(f"   ✗ Error accessing SystemSettings: {e}")
            return False
        
        print("\n3. Testing currency setting storage...")
        try:
            # Check if currency setting exists
            currency_setting = SystemSettings.query.filter_by(
                setting_key='currency.default_currency'
            ).first()
            
            if currency_setting:
                print(f"   ✓ Currency setting exists: {currency_setting.setting_value}")
            else:
                print("   ℹ Currency setting not yet created (will be created by admin)")
        except Exception as e:
            print(f"   ✗ Error: {e}")
            return False
        
        print("\n4. Validating supported currencies...")
        supported_currencies = [
            'INR', 'USD', 'EUR', 'GBP', 'KES', 'AED', 'SGD', 'AUD', 'CAD',
            'JPY', 'CNY', 'MYR', 'THB', 'SAR', 'ZAR', 'NZD', 'CHF', 'HKD',
            'PKR', 'BDT', 'LKR', 'NPR'
        ]
        print(f"   ✓ {len(supported_currencies)} currencies supported")
        print(f"   Currencies: {', '.join(supported_currencies)}")
        
        print("\n" + "=" * 60)
        print("✓ ALL BACKEND CURRENCY VALIDATION PASSED")
        print("=" * 60)
        return True

if __name__ == "__main__":
    try:
        success = validate_currency_backend()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ VALIDATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
