"""
Super Admin models for the Gym Management SaaS platform.
Contains SystemSettings, ActivityLog, and GymSubscription models.
"""

from datetime import datetime
from app.extensions import db
from sqlalchemy import Numeric


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
    updated_by_user = db.relationship('User', foreign_keys=[updated_by], backref='system_settings_updates')
    
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
    extra_data = db.Column(db.JSON, nullable=True)
    
    # Severity level for filtering critical events
    severity = db.Column(db.String(20), nullable=False, default='info')  # info, warning, error, critical
    
    # Timestamp
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], backref='activity_logs')
    gym = db.relationship('Gym', foreign_keys=[gym_id], backref='activity_logs')
    
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
            'metadata': self.extra_data,
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
    gym = db.relationship('Gym', foreign_keys=[gym_id], backref=db.backref('subscription', uselist=False))
    created_by_user = db.relationship('User', foreign_keys=[created_by], backref='created_subscriptions')
    
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