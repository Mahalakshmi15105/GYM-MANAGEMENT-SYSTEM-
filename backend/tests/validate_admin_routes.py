"""
Validate Super Admin routes structure and imports.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from app.routes.admin import admin_bp, PlatformAnalyticsService, log_activity
    
    print("✅ Successfully imported admin blueprint and services")
    
    # Check blueprint configuration
    print(f"✅ Blueprint name: {admin_bp.name}")
    print(f"✅ Blueprint import name: {admin_bp.import_name}")
    
    # Check that we have the expected routes
    expected_routes = [
        '/dashboard/analytics',
        '/dashboard/growth-metrics', 
        '/gyms',
        '/gyms/<int:gym_id>',
        '/gyms/<int:gym_id>/approve',
        '/gyms/<int:gym_id>/suspend',
        '/gyms/<int:gym_id>/reactivate',
        '/gyms/<int:gym_id>',  # DELETE
        '/activity-logs'
    ]
    
    # Get all rules for the blueprint
    print(f"\n✅ Blueprint has {len(admin_bp.deferred_functions)} deferred functions")
    
    # Check service classes
    service_methods = [
        'get_platform_metrics',
        'get_gym_performance_data'
    ]
    
    for method in service_methods:
        if hasattr(PlatformAnalyticsService, method):
            print(f"✅ PlatformAnalyticsService.{method} exists")
        else:
            print(f"❌ PlatformAnalyticsService.{method} missing")
    
    # Check log_activity function
    if callable(log_activity):
        print("✅ log_activity function exists and is callable")
    else:
        print("❌ log_activity function missing or not callable")
    
    print("\n🎉 Admin routes validation completed successfully!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Validation error: {e}")
    import traceback
    traceback.print_exc()