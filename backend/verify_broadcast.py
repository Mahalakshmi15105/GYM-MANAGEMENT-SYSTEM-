import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import db, Member, BroadcastMessage, BroadcastRecipient, Notification, Gym, User

app = create_app()

with app.app_context():
    print("=" * 80)
    print("STEP 1: Verify Members in Database")
    print("=" * 80)
    
    # Get all gyms
    gyms = Gym.query.all()
    print(f"\nTotal gyms in database: {len(gyms)}")
    for gym in gyms:
        print(f"\nGym ID: {gym.id}, Name: {gym.name}")
        members = Member.query.filter_by(gym_id=gym.id).all()
        print(f"  Members in this gym: {len(members)}")
        for member in members:
            print(f"    - ID: {member.id}, Name: {member.first_name} {member.last_name}, Email: {member.email}, Status: {member.status}")
    
    print("\n" + "=" * 80)
    print("STEP 2: Verify Broadcast Messages")
    print("=" * 80)
    
    broadcasts = BroadcastMessage.query.all()
    print(f"\nTotal broadcasts in database: {len(broadcasts)}")
    for broadcast in broadcasts:
        print(f"\nBroadcast ID: {broadcast.id}")
        print(f"  Gym ID: {broadcast.gym_id}")
        print(f"  Subject: {broadcast.subject}")
        print(f"  Title: {broadcast.title}")
        print(f"  Recipient Type: {broadcast.recipient_type}")
        print(f"  Created At: {broadcast.created_at}")
    
    print("\n" + "=" * 80)
    print("STEP 3: Verify BroadcastRecipients Table")
    print("=" * 80)
    
    if broadcasts:
        for broadcast in broadcasts:
            recipients = BroadcastRecipient.query.filter_by(broadcast_id=broadcast.id).all()
            print(f"\nBroadcast ID: {broadcast.id}")
            print(f"  Recipients in broadcast_recipients table: {len(recipients)}")
            for recipient in recipients:
                member = Member.query.get(recipient.member_id)
                if member:
                    print(f"    - Member ID: {recipient.member_id}, Name: {member.first_name} {member.last_name}, Is Read: {recipient.is_read}")
                else:
                    print(f"    - Member ID: {recipient.member_id} (NOT FOUND)")
    else:
        print("No broadcasts found")
    
    print("\n" + "=" * 80)
    print("STEP 4: Verify Notifications")
    print("=" * 80)
    
    broadcast_notifications = Notification.query.filter_by(notification_type='broadcast_message').all()
    print(f"\nTotal broadcast notifications: {len(broadcast_notifications)}")
    for notification in broadcast_notifications:
        print(f"\nNotification ID: {notification.id}")
        print(f"  Gym ID: {notification.gym_id}")
        print(f"  Recipient Role: {notification.recipient_role}")
        print(f"  Recipient ID: {notification.recipient_id}")
        print(f"  Title: {notification.title}")
        print(f"  Message: {notification.message}")
        print(f"  Reference ID: {notification.reference_id}")
        member = Member.query.get(notification.recipient_id)
        if member:
            print(f"  Recipient Name: {member.first_name} {member.last_name}")
    
    print("\n" + "=" * 80)
    print("STEP 5: Verify All Notifications for Members")
    print("=" * 80)
    
    for gym in gyms:
        members = Member.query.filter_by(gym_id=gym.id).all()
        print(f"\nGym: {gym.name} (ID: {gym.id})")
        for member in members:
            notifications = Notification.query.filter_by(
                gym_id=gym.id,
                recipient_role='member',
                recipient_id=member.id
            ).all()
            print(f"  Member: {member.first_name} {member.last_name} (ID: {member.id})")
            print(f"    Total notifications: {len(notifications)}")
            for notif in notifications:
                print(f"      - Type: {notif.notification_type}, Title: {notif.title}")
    
    print("\n" + "=" * 80)
    print("VERIFICATION COMPLETE")
    print("=" * 80)
