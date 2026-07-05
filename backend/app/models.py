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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to users
    users = db.relationship('User', backref='gym', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'phone': self.phone,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Roles: 'super_admin', 'gym_owner', 'member'
    role = db.Column(db.String(20), nullable=False, default='gym_owner')
    
    # Multi-tenant isolation: Every user (Gym Owner, Member) belongs to a specific Gym.
    # Nullable ONLY for super_admins (who manage the entire SaaS platform) or during registration setup.
    gym_id = db.Column(db.Integer, db.ForeignKey('gyms.id', ondelete='CASCADE'), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'gym_id': self.gym_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Attendance(db.Model):
    __tablename__ = 'attendance'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Multi-tenant isolation - CRITICAL for SaaS
    gym_id = db.Column(db.Integer, db.ForeignKey('gyms.id', ondelete='CASCADE'), nullable=False)
    
    # Member reference
    member_id = db.Column(db.Integer, db.ForeignKey('members.id', ondelete='CASCADE'), nullable=False)
    
    # Attendance Information
    check_in_time = db.Column(db.DateTime, nullable=False)
    check_out_time = db.Column(db.DateTime, nullable=True)
    attendance_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Checked In')  # Checked In, Checked Out
    notes = db.Column(db.Text, nullable=True)  # Additional notes
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    gym = db.relationship('Gym', backref='attendance_records')
    member = db.relationship('Member', backref='attendance_records')
    
    # Composite index for tenant isolation and search performance
    __table_args__ = (
        db.Index('idx_gym_id_date', 'gym_id', 'attendance_date'),
        db.Index('idx_gym_id_member_id', 'gym_id', 'member_id'),
        db.Index('idx_gym_id_status', 'gym_id', 'status'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'gym_id': self.gym_id,
            'member_id': self.member_id,
            'member_name': f"{self.member.first_name} {self.member.last_name}" if self.member else None,
            'member_phone': self.member.phone if self.member else None,
            'check_in_time': self.check_in_time.isoformat() if self.check_in_time else None,
            'check_out_time': self.check_out_time.isoformat() if self.check_out_time else None,
            'attendance_date': self.attendance_date.isoformat() if self.attendance_date else None,
            'status': self.status,
            'notes': self.notes,
            'duration_minutes': self.get_duration_minutes(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def get_duration_minutes(self):
        """Calculate workout duration in minutes"""
        if self.check_out_time and self.check_in_time:
            delta = self.check_out_time - self.check_in_time
            return int(delta.total_seconds() / 60)
        return None


class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Multi-tenant isolation - CRITICAL for SaaS
    gym_id = db.Column(db.Integer, db.ForeignKey('gyms.id', ondelete='CASCADE'), nullable=False)
    
    # Member and Plan references
    member_id = db.Column(db.Integer, db.ForeignKey('members.id', ondelete='CASCADE'), nullable=False)
    membership_plan_id = db.Column(db.Integer, db.ForeignKey('membership_plans.id', ondelete='SET NULL'), nullable=True)
    
    # Payment Information
    payment_amount = db.Column(Numeric(10, 2), nullable=False)
    payment_date = db.Column(db.Date, nullable=False)
    payment_method = db.Column(db.String(20), nullable=False)  # Cash, UPI, Card, Bank Transfer
    payment_status = db.Column(db.String(20), nullable=False, default='Paid')  # Paid, Pending, Failed
    transaction_id = db.Column(db.String(100), nullable=True)  # Receipt/Transaction number
    notes = db.Column(db.Text, nullable=True)  # Additional notes
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    gym = db.relationship('Gym', backref='payments')
    member = db.relationship('Member', backref='payments')
    membership_plan = db.relationship('MembershipPlan', backref='payments')
    
    # Composite index for tenant isolation and search performance
    __table_args__ = (
        db.Index('idx_gym_id_payment_date', 'gym_id', 'payment_date'),
        db.Index('idx_gym_id_member_id', 'gym_id', 'member_id'),
        db.Index('idx_gym_id_status', 'gym_id', 'payment_status'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'gym_id': self.gym_id,
            'member_id': self.member_id,
            'member_name': f"{self.member.first_name} {self.member.last_name}" if self.member else None,
            'member_phone': self.member.phone if self.member else None,
            'membership_plan_id': self.membership_plan_id,
            'membership_plan_name': self.membership_plan.plan_name if self.membership_plan else None,
            'payment_amount': float(self.payment_amount),
            'payment_date': self.payment_date.isoformat() if self.payment_date else None,
            'payment_method': self.payment_method,
            'payment_status': self.payment_status,
            'transaction_id': self.transaction_id,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class MembershipPlan(db.Model):
    __tablename__ = 'membership_plans'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Multi-tenant isolation - CRITICAL for SaaS
    gym_id = db.Column(db.Integer, db.ForeignKey('gyms.id', ondelete='CASCADE'), nullable=False)
    
    # Plan Information
    plan_name = db.Column(db.String(100), nullable=False)
    duration = db.Column(db.Integer, nullable=False)  # Duration in days
    price = db.Column(Numeric(10, 2), nullable=False)  # Price with 2 decimal places
    description = db.Column(db.Text, nullable=True)
    
    # Status: Active, Inactive
    status = db.Column(db.String(20), nullable=False, default='Active')
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    gym = db.relationship('Gym', backref='membership_plans')
    
    # Composite index for tenant isolation and search performance
    __table_args__ = (
        db.Index('idx_gym_id_status_plans', 'gym_id', 'status'),
        db.UniqueConstraint('gym_id', 'plan_name', name='unique_plan_name_per_gym'),
    )

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


class Member(db.Model):
    __tablename__ = 'members'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Multi-tenant isolation - CRITICAL for SaaS
    gym_id = db.Column(db.Integer, db.ForeignKey('gyms.id', ondelete='CASCADE'), nullable=False)
    
    # Auto-generated unique member ID (unique within gym, not globally)
    member_id = db.Column(db.String(20), nullable=False, default=lambda: f"MEM{str(uuid.uuid4())[:8].upper()}")
    
    # Personal Information
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=True)
    gender = db.Column(db.String(10), nullable=True)  # Male, Female, Other
    date_of_birth = db.Column(db.Date, nullable=True)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    address = db.Column(db.Text, nullable=True)
    
    # Emergency Contact
    emergency_contact_name = db.Column(db.String(100), nullable=True)
    emergency_contact_phone = db.Column(db.String(20), nullable=True)
    
    # Medical Information
    medical_notes = db.Column(db.Text, nullable=True)
    
    # Membership Information
    membership_plan_name = db.Column(db.String(100), nullable=True)  # Text field since plans module doesn't exist
    membership_start_date = db.Column(db.Date, nullable=True)
    membership_end_date = db.Column(db.Date, nullable=True)
    
    # Status: Active, Expired, Inactive
    status = db.Column(db.String(20), nullable=False, default='Active')
    
    # Profile Photo
    photo = db.Column(db.String(255), nullable=True)  # File path
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    gym = db.relationship('Gym', backref='members')
    
    # Composite index for tenant isolation and search performance
    __table_args__ = (
        db.Index('idx_gym_id_status', 'gym_id', 'status'),
        db.Index('idx_gym_id_email', 'gym_id', 'email'),
        db.Index('idx_gym_id_phone', 'gym_id', 'phone'),
        db.UniqueConstraint('gym_id', 'email', name='unique_email_per_gym'),
        db.UniqueConstraint('gym_id', 'phone', name='unique_phone_per_gym'),
        db.UniqueConstraint('gym_id', 'member_id', name='unique_member_id_per_gym'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'gym_id': self.gym_id,
            'member_id': self.member_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': f"{self.first_name} {self.last_name}",
            'gender': self.gender,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'phone': self.phone,
            'email': self.email,
            'address': self.address,
            'emergency_contact_name': self.emergency_contact_name,
            'emergency_contact_phone': self.emergency_contact_phone,
            'medical_notes': self.medical_notes,
            'membership_plan_name': self.membership_plan_name,
            'membership_start_date': self.membership_start_date.isoformat() if self.membership_start_date else None,
            'membership_end_date': self.membership_end_date.isoformat() if self.membership_end_date else None,
            'status': self.status,
            'photo': self.photo,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
