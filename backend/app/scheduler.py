"""
Background scheduler for generating expiry notifications
"""

from datetime import datetime, timedelta
from app.extensions import db
from app.models import Notification, Gym, Member, User
from sqlalchemy import and_
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def check_gym_subscription_expiry():
    """Check gym subscriptions and generate expiry notifications"""
    try:
        today = datetime.utcnow().date()
        
        # Check for gyms expiring in 5, 3, 1 days and today
        days_to_check = [5, 3, 1, 0]
        
        for days in days_to_check:
            target_date = today + timedelta(days=days)
            
            # Find gyms with subscription ending on target_date
            # Note: Assuming Gym model has subscription_end_date field
            # If not, this needs to be adjusted based on actual schema
            gyms = Gym.query.filter(
                Gym.status == 'Active'
            ).all()
            
            for gym in gyms:
                # Check if gym has subscription_end_date (this field may need to be added to Gym model)
                # For now, we'll skip if the field doesn't exist
                if not hasattr(gym, 'subscription_end_date'):
                    continue
                
                if gym.subscription_end_date and gym.subscription_end_date.date() == target_date:
                    # Check if notification already exists for this gym and days
                    existing_notification = Notification.query.filter(
                        Notification.gym_id == gym.id,
                        Notification.notification_type == 'gym_subscription_expiry',
                        Notification.reference_id == gym.id,
                        Notification.scheduled_for == target_date
                    ).first()
                    
                    if existing_notification:
                        continue  # Skip if notification already exists
                    
                    # Generate notification for Super Admin
                    super_admin_notification = Notification(
                        gym_id=None,  # Global notification for Super Admin
                        recipient_role='super_admin',
                        recipient_id=None,
                        notification_type='gym_subscription_expiry',
                        title=f'Gym "{gym.name}" subscription will expire in {days} days' if days > 0 else f'Gym "{gym.name}" subscription expires today',
                        message=f'Gym "{gym.name}" subscription will expire in {days} days. Please take appropriate action.' if days > 0 else f'Gym "{gym.name}" subscription expires today.',
                        reference_id=gym.id,
                        is_read=False,
                        created_at=datetime.utcnow(),
                        scheduled_for=target_date
                    )
                    db.session.add(super_admin_notification)
                    
                    # Generate notification for Gym Owner
                    gym_owner = User.query.filter(
                        User.gym_id == gym.id,
                        User.role == 'gym_owner'
                    ).first()
                    
                    if gym_owner:
                        owner_notification = Notification(
                            gym_id=gym.id,
                            recipient_role='gym_owner',
                            recipient_id=gym_owner.id,
                            notification_type='gym_subscription_expiry',
                            title='Your gym subscription will expire in {} days'.format(days) if days > 0 else 'Your gym subscription expires today',
                            message='Your gym subscription will expire in {} days. Please renew your subscription to avoid interruption of services.'.format(days) if days > 0 else 'Your gym subscription expires today. Please renew your subscription immediately.',
                            reference_id=gym.id,
                            is_read=False,
                            created_at=datetime.utcnow(),
                            scheduled_for=target_date
                        )
                        db.session.add(owner_notification)
        
        db.session.commit()
        logger.info('Gym subscription expiry notifications generated successfully')
        
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error generating gym subscription expiry notifications: {str(e)}')


def check_member_membership_expiry():
    """Check member memberships and generate expiry notifications"""
    try:
        today = datetime.utcnow().date()
        
        # Check for memberships expiring in 5, 3, 1 days and today
        days_to_check = [5, 3, 1, 0]
        
        for days in days_to_check:
            target_date = today + timedelta(days=days)
            
            # Find members with membership ending on target_date
            members = Member.query.filter(
                Member.membership_end_date == target_date,
                Member.status == 'Active'
            ).all()
            
            for member in members:
                # Check if notification already exists for this member and days
                existing_notification = Notification.query.filter(
                    Notification.gym_id == member.gym_id,
                    Notification.notification_type == 'member_membership_expiry',
                    Notification.reference_id == member.id,
                    Notification.scheduled_for == target_date
                ).first()
                
                if existing_notification:
                    continue  # Skip if notification already exists
                
                # Generate notification for Gym Owner
                gym_owner = User.query.filter(
                    User.gym_id == member.gym_id,
                    User.role == 'gym_owner'
                ).first()
                
                if gym_owner:
                    owner_notification = Notification(
                        gym_id=member.gym_id,
                        recipient_role='gym_owner',
                        recipient_id=gym_owner.id,
                        notification_type='member_membership_expiry',
                        title=f'Member {member.first_name} {member.last_name}\'s {member.membership_plan_name or "Membership"} expires in {days} days' if days > 0 else f'Member {member.first_name} {member.last_name}\'s {member.membership_plan_name or "Membership"} expires today',
                        message=f'Member {member.first_name} {member.last_name}\'s {member.membership_plan_name or "Membership"} expires in {days} days.' if days > 0 else f'Member {member.first_name} {member.last_name}\'s {member.membership_plan_name or "Membership"} expires today.',
                        reference_id=member.id,
                        is_read=False,
                        created_at=datetime.utcnow(),
                        scheduled_for=target_date
                    )
                    db.session.add(owner_notification)
                
                # Generate notification for Member (if they have an account)
                if member.password_hash:  # Member has login account
                    member_notification = Notification(
                        gym_id=member.gym_id,
                        recipient_role='member',
                        recipient_id=member.id,
                        notification_type='member_membership_expiry',
                        title='Your {} expires in {} days'.format(member.membership_plan_name or 'Membership', days) if days > 0 else 'Your {} expires today'.format(member.membership_plan_name or 'Membership'),
                        message='Your {} expires in {} days. Please renew your membership.'.format(member.membership_plan_name or 'Membership', days) if days > 0 else 'Your {} expires today. Please renew your membership immediately.'.format(member.membership_plan_name or 'Membership'),
                        reference_id=member.id,
                        is_read=False,
                        created_at=datetime.utcnow(),
                        scheduled_for=target_date
                    )
                    db.session.add(member_notification)
        
        db.session.commit()
        logger.info('Member membership expiry notifications generated successfully')
        
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error generating member membership expiry notifications: {str(e)}')


def generate_all_notifications():
    """Generate all expiry notifications (called by scheduler)"""
    logger.info('Starting notification generation job...')
    check_gym_subscription_expiry()
    check_member_membership_expiry()
    logger.info('Notification generation job completed')
