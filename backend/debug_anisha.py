from app import create_app
from app.models import Member, BroadcastMessage, BroadcastRecipient, Notification
from app.extensions import db

app = create_app()
with app.app_context():
    member = Member.query.filter_by(email='anisha@gmail.com').first()
    if not member:
        print("Member Anisha not found")
    else:
        print(f"Member: {member.first_name} {member.last_name}, ID: {member.id}, Gym ID: {member.gym_id}")
        
        recipients = BroadcastRecipient.query.filter_by(member_id=member.id).all()
        print(f"BroadcastRecipient count for Anisha: {len(recipients)}")
        for r in recipients:
            broadcast = BroadcastMessage.query.get(r.broadcast_id)
            print(f"  - Broadcast ID: {r.broadcast_id}, Title: {broadcast.title}, Gym ID: {broadcast.gym_id}, Is Read: {r.is_read}")
            
        notifications = Notification.query.filter_by(recipient_id=member.id, recipient_role='member').all()
        print(f"Notification count for Anisha: {len(notifications)}")
        for n in notifications:
            print(f"  - Notification ID: {n.id}, Title: {n.title}, Type: {n.notification_type}, Is Read: {n.is_read}")
