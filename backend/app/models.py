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
    
    # Super Admin fields for gym management
    status = db.Column(db.String(20), nullable=False, default='Pending')  # Pending, Active, Suspended, Deleted
    subscription_id = db.Column(db.Integer, db.ForeignKey('gym_subscriptions.id'), nullable=True)
    approved_at = db.Column(db.DateTime, nullable=True)
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Additional gym metadata
    business_license = db.Column(db.String(100), nullable=True)  # Business license number
    owner_name = db.Column(db.String(100), nullable=True)  # Primary contact name
    website = db.Column(db.String(255), nullable=True)  # Gym website
    description = db.Column(db.Text, nullable=True)  # Gym description
    
    # Timestamps for audit
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to users
    users = db.relationship('User', foreign_keys='User.gym_id', backref='gym', lazy=True)
    
    # Super Admin relationships
    approver = db.relationship('User', foreign_keys=[approved_by], backref='approved_gyms')
    
    # Indexes for Super Admin queries
    __table_args__ = (
        db.Index('idx_gym_status', 'status'),
        db.Index('idx_gym_created_at', 'created_at'),
        db.Index('idx_gym_approved_at', 'approved_at'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'phone': self.phone,
            'status': self.status,
            'business_license': self.business_license,
            'owner_name': self.owner_name,
            'website': self.website,
            'description': self.description,
            'subscription_id': self.subscription_id,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'approved_by': self.approved_by,
            'approved_by_name': self.approver.name if self.approver else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def can_operate(self):
        """Check if gym can operate (is active and not suspended)"""
        return self.status == 'Active'

    def is_pending_approval(self):
        """Check if gym is waiting for Super Admin approval"""
        return self.status == 'Pending'

    def get_member_count(self):
        """Get current number of members in the gym"""
        from app.models import Member  # Import here to avoid circular imports
        return Member.query.filter_by(gym_id=self.id, status='Active').count()

    def get_subscription_info(self):
        """Get subscription information for the gym"""
        if self.subscription_id:
            from app.super_admin_models import GymSubscription
            return GymSubscription.query.get(self.subscription_id)
        return None

    def approve_gym(self, admin_user_id):
        """Approve gym for operation"""
        if self.status == 'Pending':
            self.status = 'Active'
            self.approved_by = admin_user_id
            self.approved_at = datetime.utcnow()
            return True
        return False

    def suspend_gym(self, reason=None):
        """Suspend gym operations"""
        if self.status == 'Active':
            self.status = 'Suspended'
            # Could add reason field and logging here
            return True
        return False

    def reactivate_gym(self):
        """Reactivate suspended gym"""
        if self.status == 'Suspended':
            self.status = 'Active'
            return True
        return False

    def soft_delete_gym(self):
        """Soft delete gym (mark as deleted but keep data)"""
        if self.status in ['Active', 'Suspended', 'Pending']:
            self.status = 'Deleted'
            return True
        return False

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

# =============================================================================
# SUPER ADMIN MODELS - Platform Management and Audit
# =============================================================================

class SystemSettings(db.Model):
    """
    System-wide settings for the SaaS platform.
    Allows Super Admins to configure platform behavior, limits, and features.
    "
#
 =============================================================================
# SUPER ADMIN MODELS - Platform Management and Audit
# =============================================================================

class SystemSettings(db.Model):
    """
    System-wide settings for the SaaS platform.
    Allows Super Admins to configure platform behavior, limits, and features.
    """
    __tablename__ = 'system_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    setting_key = db.Column(db.String(100), unique=True, nullable=False)
    setting_value = db.Column(db.Text, nullable=False)
    setting_type = db.Column(db.String(20), nullable=False)  # string, number, boolean, json
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(50), nullable=False, default='general')  # security, features, limits, notifications
    
    # Audit fields
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    updated_by_user = db.relationship('User', backref='system_settings_updates')
    
    # Indexes for performance
    __table_args__ = (
        db.Index('idx_setting_category', 'category'),
        db.Index('idx_setting_key', 'setting_key'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'setting_key': self.setting_key,
            'setting_value': self.setting_value,
            'setting_type': self.setting_type,
            'description': self.description,
            'category': self.category,
            'updated_by': self.updated_by,
            'updated_by_name': self.updated_by_user.name if self.updated_by_user else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def get_typed_value(self):
        """Convert setting_value based on setting_type"""
        if self.setting_type == 'boolean':
            return self.setting_value.lower() in ('true', '1', 'yes', 'on')
        elif self.setting_type == 'number':
            try:
                return float(self.setting_value) if '.' in self.setting_value else int(self.setting_value)
            except (ValueError, TypeError):
                return 0
        elif self.setting_type == 'json':
            try:
                import json
                return json.loads(self.setting_value)
            except (ValueError, TypeError):
                return {}
        else:  # string
            return self.setting_value


class ActivityLog(db.Model):
    """
    Platform-wide activity logs for audit trail and monitoring.
    Tracks all user actions across the SaaS platform for security and compliance.
    """
    __tablename__ = 'activity_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # User and Gym context (nullable for system-generated events)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    gym_id = db.Column(db.Integer, db.ForeignKey('gyms.id'), nullable=True)
    
    # Action details
    action_type = db.Column(db.String(50), nullable=False)  # login, create, update, delete, view, export
    entity_type = db.Column(db.String(50), nullable=True)   # member, payment, gym, user, system_setting
    entity_id = db.Column(db.Integer, nullable=True)
    description = db.Column(db.Text, nullable=False)
    
    # Request context
    ip_address = db.Column(db.String(45), nullable=True)  # IPv6 compatible
    user_agent = db.Column(db.Text, nullable=True)
    request_method = db.Column(db.String(10), nullable=True)  # GET, POST, PUT, DELETE
    request_path = db.Column(db.String(255), nullable=True)
    
    # Additional metadata (JSON for flexibility)
    metadata = db.Column(db.JSON, nullable=True)
    
    # Severity level for filtering critical events
    severity = db.Column(db.String(20), nullable=False, default='info')  # info, warning, error, critical
    
    # Timestamp
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = db.relationship('User', backref='activity_logs')
    gym = db.relationship('Gym', backref='activity_logs')
    
    # Indexes for performance and searching
    __table_args__ = (
        db.Index('idx_timestamp', 'timestamp'),
        db.Index('idx_user_id_timestamp', 'user_id', 'timestamp'),
        db.Index('idx_gym_id_timestamp', 'gym_id', 'timestamp'),
        db.Index('idx_action_type_timestamp', 'action_type', 'timestamp'),
        db.Index('idx_entity_type_timestamp', 'entity_type', 'timestamp'),
        db.Index('idx_severity_timestamp', 'severity', 'timestamp'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'gym_id': self.gym_id,
            'user_name': self.user.name if self.user else None,
            'user_email': self.user.email if self.user else None,
            'gym_name': self.gym.name if self.gym else None,
            'action_type': self.action_type,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'description': self.description,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'request_method': self.request_method,
            'request_path': self.request_path,
            'metadata': self.metadata,
            'severity': self.severity,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }


class GymSubscription(db.Model):
    """
    Gym subscription management for the SaaS platform.
    Tracks subscription plans, billing cycles, and payment status for each gym.
    """
    __tablename__ = 'gym_subscriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    gym_id = db.Column(db.Integer, db.ForeignKey('gyms.id'), nullable=False, unique=True)
    
    # Subscription Plan Details
    plan_name = db.Column(db.String(100), nullable=False)
    monthly_price = db.Column(Numeric(10, 2), nullable=False)
    max_members = db.Column(db.Integer, nullable=False, default=100)
    max_trainers = db.Column(db.Integer, nullable=False, default=5)
    
    # Feature flags (JSON for flexibility)
    features = db.Column(db.JSON, nullable=True)
    
    # Billing Information
    billing_cycle_start = db.Column(db.Date, nullable=False)
    billing_cycle_end = db.Column(db.Date, nullable=False)
    next_billing_date = db.Column(db.Date, nullable=False)
    
    # Status and Configuration
    status = db.Column(db.String(20), nullable=False, default='Active')  # Active, Suspended, Cancelled, Expired
    auto_renew = db.Column(db.Boolean, default=True)
    
    # Payment Information
    last_payment_date = db.Column(db.Date, nullable=True)
    last_payment_amount = db.Column(Numeric(10, 2), nullable=True)
    payment_method = db.Column(db.String(50), nullable=True)  # Card, Bank Transfer, etc.
    
    # Audit fields
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    gym = db.relationship('Gym', backref=db.backref('subscription', uselist=False))
    created_by_user = db.relationship('User', backref='created_subscriptions')
    
    # Indexes
    __table_args__ = (
        db.Index('idx_status', 'status'),
        db.Index('idx_next_billing_date', 'next_billing_date'),
        db.Index('idx_billing_cycle', 'billing_cycle_start', 'billing_cycle_end'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'gym_id': self.gym_id,
            'gym_name': self.gym.name if self.gym else None,
            'plan_name': self.plan_name,
            'monthly_price': float(self.monthly_price),
            'max_members': self.max_members,
            'max_trainers': self.max_trainers,
            'features': self.features,
            'billing_cycle_start': self.billing_cycle_start.isoformat() if self.billing_cycle_start else None,
            'billing_cycle_end': self.billing_cycle_end.isoformat() if self.billing_cycle_end else None,
            'next_billing_date': self.next_billing_date.isoformat() if self.next_billing_date else None,
            'status': self.status,
            'auto_renew': self.auto_renew,
            'last_payment_date': self.last_payment_date.isoformat() if self.last_payment_date else None,
            'last_payment_amount': float(self.last_payment_amount) if self.last_payment_amount else None,
            'payment_method': self.payment_method,
            'created_by': self.created_by,
            'created_by_name': self.created_by_user.name if self.created_by_user else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def is_active(self):
        """Check if subscription is currently active"""
        return self.status == 'Active' and datetime.utcnow().date() <= self.billing_cycle_end

    def days_until_expiry(self):
        """Calculate days until subscription expires"""
        if self.billing_cycle_end:
            delta = self.billing_cycle_end - datetime.utcnow().date()
            return delta.days
        return 0

    def get_usage_limits(self):
        """Get current usage limits for the subscription"""
        return {
            'max_members': self.max_members,
            'max_trainers': self.max_trainers,
            'features': self.features or {}
        }
# ===
==========================================================================
# SUPER ADMIN MODELS - Platform Management and Audit
# =============================================================================

class SystemSettings(db.Model):
    """
    System-wide settings for the SaaS platform.
    Allows Super Admins to configure platform behavior, limits, and features.
    """
    __tablename__ = 'system_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    setting_key = db.Column(db.String(100), unique=True, nullable=False)
    setting_value = db.Column(db.Text, nullable=False)
    setting_type = db.Column(db.String(20), nullable=False)  # string, number, boolean, json
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(50), nullable=False, default='general')  # security, features, limits, notifications
    
    # Audit fields
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    updated_by_user = db.relationship('User', backref='system_settings_updates')
    
    # Indexes for performance
    __table_args__ = (
        db.Index('idx_setting_category', 'category'),
        db.Index('idx_setting_key', 'setting_key'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'setting_key': self.setting_key,
            'setting_value': self.setting_value,
            'setting_type': self.setting_type,
            'description': self.description,
            'category': self.category,
            'updated_by': self.updated_by,
            'updated_by_name': self.updated_by_user.name if self.updated_by_user else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def get_typed_value(self):
        """Convert setting_value based on setting_type"""
        if self.setting_type == 'boolean':
            return self.setting_value.lower() in ('true', '1', 'yes', 'on')
        elif self.setting_type == 'number':
            try:
                return float(self.setting_value) if '.' in self.setting_value else int(self.setting_value)
            except (ValueError, TypeError):
                return 0
        elif self.setting_type == 'json':
            try:
                import json
                return json.loads(self.setting_value)
            except (ValueError, TypeError):
                return {}
        else:  # string
            return self.setting_value


class ActivityLog(db.Model):
    """
    Platform-wide activity logs for audit trail and monitoring.
    Tracks all user actions across the SaaS platform for security and compliance.
    """
    __tablename__ = 'activity_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # User and Gym context (nullable for system-generated events)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    gym_id = db.Column(db.Integer, db.ForeignKey('gyms.id'), nullable=True)
    
    # Action details
    action_type = db.Column(db.String(50), nullable=False)  # login, create, update, delete, view, export
    entity_type = db.Column(db.String(50), nullable=True)   # member, payment, gym, user, system_setting
    entity_id = db.Column(db.Integer, nullable=True)
    description = db.Column(db.Text, nullable=False)
    
    # Request context
    ip_address = db.Column(db.String(45), nullable=True)  # IPv6 compatible
    user_agent = db.Column(db.Text, nullable=True)
    request_method = db.Column(db.String(10), nullable=True)  # GET, POST, PUT, DELETE
    request_path = db.Column(db.String(255), nullable=True)
    
    # Additional metadata (JSON for flexibility)
    metadata = db.Column(db.JSON, nullable=True)
    
    # Severity level for filtering critical events
    severity = db.Column(db.String(20), nullable=False, default='info')  # info, warning, error, critical
    
    # Timestamp
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = db.relationship('User', backref='activity_logs')
    gym = db.relationship('Gym', backref='activity_logs')
    
    # Indexes for performance and searching
    __table_args__ = (
        db.Index('idx_timestamp', 'timestamp'),
        db.Index('idx_user_id_timestamp', 'user_id', 'timestamp'),
        db.Index('idx_gym_id_timestamp', 'gym_id', 'timestamp'),
        db.Index('idx_action_type_timestamp', 'action_type', 'timestamp'),
        db.Index('idx_entity_type_timestamp', 'entity_type', 'timestamp'),
        db.Index('idx_severity_timestamp', 'severity', 'timestamp'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'gym_id': self.gym_id,
            'user_name': self.user.name if self.user else None,
            'user_email': self.user.email if self.user else None,
            'gym_name': self.gym.name if self.gym else None,
            'action_type': self.action_type,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'description': self.description,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'request_method': self.request_method,
            'request_path': self.request_path,
            'metadata': self.metadata,
            'severity': self.severity,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }


class GymSubscription(db.Model):
    """
    Gym subscription management for the SaaS platform.
    Tracks subscription plans, billing cycles, and payment status for each gym.
    """
    __tablename__ = 'gym_subscriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    gym_id = db.Column(db.Integer, db.ForeignKey('gyms.id'), nullable=False, unique=True)
    
    # Subscription Plan Details
    plan_name = db.Column(db.String(100), nullable=False)
    monthly_price = db.Column(Numeric(10, 2), nullable=False)
    max_members = db.Column(db.Integer, nullable=False, default=100)
    max_trainers = db.Column(db.Integer, nullable=False, default=5)
    
    # Feature flags (JSON for flexibility)
    features = db.Column(db.JSON, nullable=True)
    
    # Billing Information
    billing_cycle_start = db.Column(db.Date, nullable=False)
    billing_cycle_end = db.Column(db.Date, nullable=False)
    next_billing_date = db.Column(db.Date, nullable=False)
    
    # Status and Configuration
    status = db.Column(db.String(20), nullable=False, default='Active')  # Active, Suspended, Cancelled, Expired
    auto_renew = db.Column(db.Boolean, default=True)
    
    # Payment Information
    last_payment_date = db.Column(db.Date, nullable=True)
    last_payment_amount = db.Column(Numeric(10, 2), nullable=True)
    payment_method = db.Column(db.String(50), nullable=True)  # Card, Bank Transfer, etc.
    
    # Audit fields
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    gym = db.relationship('Gym', backref=db.backref('subscription', uselist=False))
    created_by_user = db.relationship('User', backref='created_subscriptions')
    
    # Indexes
    __table_args__ = (
        db.Index('idx_status', 'status'),
        db.Index('idx_next_billing_date', 'next_billing_date'),
        db.Index('idx_billing_cycle', 'billing_cycle_start', 'billing_cycle_end'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'gym_id': self.gym_id,
            'gym_name': self.gym.name if self.gym else None,
            'plan_name': self.plan_name,
            'monthly_price': float(self.monthly_price),
            'max_members': self.max_members,
            'max_trainers': self.max_trainers,
            'features': self.features,
            'billing_cycle_start': self.billing_cycle_start.isoformat() if self.billing_cycle_start else None,
            'billing_cycle_end': self.billing_cycle_end.isoformat() if self.billing_cycle_end else None,
            'next_billing_date': self.next_billing_date.isoformat() if self.next_billing_date else None,
            'status': self.status,
            'auto_renew': self.auto_renew,
            'last_payment_date': self.last_payment_date.isoformat() if self.last_payment_date else None,
            'last_payment_amount': float(self.last_payment_amount) if self.last_payment_amount else None,
            'payment_method': self.payment_method,
            'created_by': self.created_by,
            'created_by_name': self.created_by_user.name if self.created_by_user else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def is_active(self):
        """Check if subscription is currently active"""
        return self.status == 'Active' and datetime.utcnow().date() <= self.billing_cycle_end

    def days_until_expiry(self):
        """Calculate days until subscription expires"""
        if self.billing_cycle_end:
            delta = self.billing_cycle_end - datetime.utcnow().date()
            return delta.days
        return 0

    def get_usage_limits(self):
        """Get current usage limits for the subscription"""
        return {
            'max_members': self.max_members,
            'max_trainers': self.max_trainers,
            'features': self.features or {}
        }