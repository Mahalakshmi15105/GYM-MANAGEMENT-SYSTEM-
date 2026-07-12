from datetime import datetime
from app.extensions import db
from sqlalchemy import Numeric
import uuid


class Gym(db.Model):
    __tablename__ = 'gyms'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(255), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    status = db.Column(db.String(20), nullable=False, default='Active')
    logo = db.Column(db.String(255), nullable=True)
    currency = db.Column(db.String(3), nullable=True, default='INR')
    language = db.Column(db.String(5), nullable=True, default='en')
    attendance_qr = db.Column(db.String(255), nullable=True, unique=True)  # Unique QR code for gym attendance
    subscription_end_date = db.Column(db.Date, nullable=True)  # Gym subscription expiry date
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    members = db.relationship('Member', backref='gym', lazy=True, cascade='all, delete-orphan')
    users = db.relationship('User', backref='gym', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'phone': self.phone,
            'status': self.status,
            'logo': self.logo,
            'currency': self.currency or 'INR',
            'language': self.language or 'en',
            'attendance_qr': self.attendance_qr,
            'subscription_end_date': self.subscription_end_date.isoformat() if self.subscription_end_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def approve_gym(self, admin_user_id):
        if self.status == 'Pending':
            self.status = 'Active'
            return True
        return False

    def suspend_gym(self, reason=None):
        if self.status == 'Active':
            self.status = 'Suspended'
            return True
        return False

    def reactivate_gym(self):
        if self.status == 'Suspended':
            self.status = 'Active'
            return True
        return False

    def soft_delete_gym(self):
        if self.status not in ['Cancelled', 'Deleted']:
            self.status = 'Deleted'
            return True
        return False

    def get_member_count(self):
        return Member.query.filter_by(gym_id=self.id).count()

    def get_subscription_info(self):
        # Return dummy or check super_admin_models if needed, but for now return None to avoid errors
        try:
            from app.super_admin_models import GymSubscription
            return GymSubscription.query.filter_by(gym_id=self.id, status='Active').first()
        except ImportError:
            return None


class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # Changed from username to name to match DB
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)  # Increased length to match DB
    role = db.Column(db.String(20), nullable=False, default='user')
    gym_id = db.Column(db.Integer, db.ForeignKey('gyms.id'), nullable=True)
    created_at = db.Column(db.DateTime, nullable=True)  # Match DB schema
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,  # Changed from username to name
            'email': self.email,
            'role': self.role,
            'gym_id': self.gym_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Member(db.Model):
    __tablename__ = 'members'
    
    id = db.Column(db.Integer, primary_key=True)
    gym_id = db.Column(db.Integer, db.ForeignKey('gyms.id'), nullable=False)
    member_id = db.Column(db.String(20), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    gender = db.Column(db.String(10), nullable=True)
    date_of_birth = db.Column(db.Date, nullable=True)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    password_hash = db.Column(db.String(255), nullable=True)  # Added for member account creation
    address = db.Column(db.Text, nullable=True)
    emergency_contact_name = db.Column(db.String(100), nullable=True)
    emergency_contact_phone = db.Column(db.String(20), nullable=True)
    medical_notes = db.Column(db.Text, nullable=True)
    membership_plan_name = db.Column(db.String(100), nullable=True)
    membership_start_date = db.Column(db.Date, nullable=False)
    membership_end_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False)
    workout_duration_minutes = db.Column(db.Integer, nullable=True, default=120)  # Default 2 hours (120 minutes)
    photo = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, nullable=True)
    updated_at = db.Column(db.DateTime, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'gym_id': self.gym_id,
            'member_id': self.member_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'gender': self.gender,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'phone': self.phone,
            'email': self.email,
            # password_hash is intentionally excluded for security
            'address': self.address,
            'emergency_contact_name': self.emergency_contact_name,
            'emergency_contact_phone': self.emergency_contact_phone,
            'medical_notes': self.medical_notes,
            'membership_plan_name': self.membership_plan_name,
            'membership_start_date': self.membership_start_date.isoformat() if self.membership_start_date else None,
            'membership_end_date': self.membership_end_date.isoformat() if self.membership_end_date else None,
            'status': self.status,
            'workout_duration_minutes': self.workout_duration_minutes,
            'photo': self.photo,
            'has_account': bool(self.password_hash and self.password_hash.strip()),  # Indicates if member has login account
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    gym_id = db.Column(db.Integer, db.ForeignKey('gyms.id'), nullable=False)
    member_id = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=False)
    membership_plan_id = db.Column(db.Integer, nullable=True)
    payment_amount = db.Column(Numeric(10, 2), nullable=False)
    payment_date = db.Column(db.Date, nullable=False)
    payment_method = db.Column(db.String(20), nullable=False)
    payment_status = db.Column(db.String(20), nullable=False)
    transaction_id = db.Column(db.String(100), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=True)
    updated_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    member = db.relationship('Member', backref='payments')
    gym = db.relationship('Gym', backref='payments')
    
    def to_dict(self):
        return {
            'id': self.id,
            'gym_id': self.gym_id,
            'member_id': self.member_id,
            'membership_plan_id': self.membership_plan_id,
            'payment_amount': float(self.payment_amount),
            'payment_date': self.payment_date.isoformat() if self.payment_date else None,
            'payment_method': self.payment_method,
            'payment_status': self.payment_status,
            'transaction_id': self.transaction_id,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'member_name': f"{self.member.first_name} {self.member.last_name}".strip() if self.member else None,
            'member_phone': self.member.phone if self.member else None,
            'gym_name': self.gym.name if self.gym else None
        }


class Attendance(db.Model):
    __tablename__ = 'attendance'
    
    id = db.Column(db.Integer, primary_key=True)
    gym_id = db.Column(db.Integer, db.ForeignKey('gyms.id'), nullable=False)
    member_id = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=False)
    check_in_time = db.Column(db.DateTime, nullable=False)
    check_out_time = db.Column(db.DateTime, nullable=True)
    expected_finish_time = db.Column(db.DateTime, nullable=True)  # Expected finish time based on workout duration
    timeout_notification_sent = db.Column(db.Boolean, default=False)  # Track if timeout notification was sent
    attendance_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=True)
    updated_at = db.Column(db.DateTime, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'gym_id': self.gym_id,
            'member_id': self.member_id,
            'check_in_time': self.check_in_time.isoformat() if self.check_in_time else None,
            'check_out_time': self.check_out_time.isoformat() if self.check_out_time else None,
            'expected_finish_time': self.expected_finish_time.isoformat() if self.expected_finish_time else None,
            'attendance_date': self.attendance_date.isoformat() if self.attendance_date else None,
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class MembershipPlan(db.Model):
    __tablename__ = 'membership_plans'
    
    id = db.Column(db.Integer, primary_key=True)
    gym_id = db.Column(db.Integer, db.ForeignKey('gyms.id'), nullable=False)
    plan_name = db.Column(db.String(100), nullable=False)
    duration = db.Column(db.Integer, nullable=False)  # Match DB: duration not duration_months
    price = db.Column(Numeric(10, 2), nullable=False)  # Match DB: price not monthly_fee
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False)  # Match DB: has status field
    created_at = db.Column(db.DateTime, nullable=True)  # Match DB: nullable
    updated_at = db.Column(db.DateTime, nullable=True)  # Match DB: has updated_at
    
    def to_dict(self):
        return {
            'id': self.id,
            'gym_id': self.gym_id,
            'plan_name': self.plan_name,
            'duration': self.duration,
            'price': float(self.price),
            'description': self.description,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    gym_id = db.Column(db.Integer, db.ForeignKey('gyms.id'), nullable=True, index=True)  # Nullable for Super Admin notifications
    recipient_role = db.Column(db.String(20), nullable=False, index=True)  # 'super_admin', 'gym_owner', 'member'
    recipient_id = db.Column(db.Integer, nullable=True, index=True)  # User or Member ID
    notification_type = db.Column(db.String(50), nullable=False, index=True)  # 'gym_subscription_expiry', 'member_membership_expiry'
    title = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    reference_id = db.Column(db.Integer, nullable=True)  # Gym ID or Member ID
    is_read = db.Column(db.Boolean, default=False, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    scheduled_for = db.Column(db.DateTime, nullable=True, index=True)  # When the notification should be delivered
    delivered_at = db.Column(db.DateTime, nullable=True)  # When the notification was actually delivered
    
    def to_dict(self):
        return {
            'id': self.id,
            'gym_id': self.gym_id,
            'recipient_role': self.recipient_role,
            'recipient_id': self.recipient_id,
            'notification_type': self.notification_type,
            'title': self.title,
            'message': self.message,
            'reference_id': self.reference_id,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'scheduled_for': self.scheduled_for.isoformat() if self.scheduled_for else None,
            'delivered_at': self.delivered_at.isoformat() if self.delivered_at else None
        }


class BroadcastMessage(db.Model):
    __tablename__ = 'broadcast_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    gym_id = db.Column(db.Integer, db.ForeignKey('gyms.id'), nullable=False, index=True)
    subject = db.Column(db.String(255), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    attachment_url = db.Column(db.String(500), nullable=True)
    banner_url = db.Column(db.String(500), nullable=True)
    recipient_type = db.Column(db.String(50), nullable=False, default='all')  # 'all', 'active', 'expiring', 'selected'
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    gym = db.relationship('Gym', backref='broadcast_messages')
    creator = db.relationship('User', backref='broadcast_messages')
    recipients = db.relationship('BroadcastRecipient', backref='broadcast', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'gym_id': self.gym_id,
            'subject': self.subject,
            'title': self.title,
            'message': self.message,
            'attachment_url': self.attachment_url,
            'banner_url': self.banner_url,
            'recipient_type': self.recipient_type,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'total_recipients': len(self.recipients),
            'read_count': sum(1 for r in self.recipients if r.is_read)
        }


class BroadcastRecipient(db.Model):
    __tablename__ = 'broadcast_recipients'
    
    id = db.Column(db.Integer, primary_key=True)
    broadcast_id = db.Column(db.Integer, db.ForeignKey('broadcast_messages.id'), nullable=False, index=True)
    member_id = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=False, index=True)
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    read_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    member = db.relationship('Member', backref='broadcast_recipients')
    
    def to_dict(self):
        return {
            'id': self.id,
            'broadcast_id': self.broadcast_id,
            'member_id': self.member_id,
            'is_read': self.is_read,
            'read_at': self.read_at.isoformat() if self.read_at else None
        }