#!/usr/bin/env python3
"""Seed initial platform subscription plans"""

import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app import create_app
from app.extensions import db
from app.super_admin_models import PlatformSubscriptionPlan

def seed_plans():
    app = create_app()
    
    with app.app_context():
        # Check if plans already exist
        existing_plans = PlatformSubscriptionPlan.query.all()
        if existing_plans:
            print("Plans already exist, skipping seed.")
            return

        # Create initial plans
        plans = [
            PlatformSubscriptionPlan(
                plan_name="Basic",
                price=499.00,
                currency="INR",
                billing_cycle="monthly",
                description="Perfect for small gyms",
                features=[
                    "Basic Member Management",
                    "Attendance Tracking",
                    "Payment Processing",
                    "Basic Reports"
                ],
                recommended=False,
                is_active=True
            ),
            PlatformSubscriptionPlan(
                plan_name="Pro",
                price=999.00,
                currency="INR",
                billing_cycle="monthly",
                description="Ideal for medium gyms",
                features=[
                    "Everything in Basic",
                    "Advanced Reports",
                    "Trainer Management",
                    "Notifications",
                    "Analytics Dashboard"
                ],
                recommended=True,
                is_active=True
            ),
            PlatformSubscriptionPlan(
                plan_name="Enterprise",
                price=2499.00,
                currency="INR",
                billing_cycle="monthly",
                description="Built for large gym chains",
                features=[
                    "Everything in Pro",
                    "Multi-Branch Support",
                    "Priority Support",
                    "Custom Branding",
                    "Advanced Analytics",
                    "API Access"
                ],
                recommended=False,
                is_active=True
            )
        ]

        for plan in plans:
            db.session.add(plan)
        
        db.session.commit()
        print("Successfully seeded initial plans!")

if __name__ == "__main__":
    seed_plans()
