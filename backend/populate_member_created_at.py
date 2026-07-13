"""
Migration script to populate created_at for existing members with NULL values.
For members with NULL created_at, we'll use their membership_start_date as a fallback,
or use the current timestamp if that's also not available.
"""

from app import create_app
from app.extensions import db
from app.models import Member
from datetime import datetime

def populate_created_at():
    app = create_app()
    
    with app.app_context():
        # Find all members with NULL created_at
        members_without_created_at = Member.query.filter(Member.created_at.is_(None)).all()
        
        print(f"Found {len(members_without_created_at)} members without created_at")
        
        for member in members_without_created_at:
            # Use membership_start_date as fallback if available
            if member.membership_start_date:
                member.created_at = datetime.combine(member.membership_start_date, datetime.min.time())
                print(f"Setting created_at for member {member.member_id} to membership_start_date: {member.created_at}")
            else:
                # Use current timestamp as last resort
                member.created_at = datetime.utcnow()
                print(f"Setting created_at for member {member.member_id} to current timestamp: {member.created_at}")
        
        # Commit the changes
        db.session.commit()
        print("Successfully populated created_at for all members")

if __name__ == '__main__':
    populate_created_at()
