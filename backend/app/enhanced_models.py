"""
Enhanced models with Super Admin functionality.
This file contains the updated Gym model and imports from super_admin_models.
"""

from datetime import datetime
from app.extensions import db
from sqlalchemy import Numeric
import uuid

# Import Super Admin models
from app.super_admin_models import SystemSettings, ActivityLog, GymSubscription


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
    
    # Relationships (defined later to avoid circular imports)
    
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
            'approved_by_name': self.get_approver_name(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def get_approver_name(self):
        """Get the name of the admin who approved this gym"""
        if self.approved_by:
            from app.models import User
            approver = User.query.get(self.approved_by)
            return approver.name if approver else None
        return None

    def can_operate(self):
        """Check if gym can operate (is active and not suspended)"""
        return self.status == 'Active'

    def is_pending_approval(self):
        """Check if gym is waiting for Super Admin approval"""
        return self.status == 'Pending'

    def get_member_count(self):
        """Get current number of members in the gym"""
        try:
            from app.models import Member
            return Member.query.filter_by(gym_id=self.id, status='Active').count()
        except ImportError:
            return 0  # If Member model not available

    def get_subscription_info(self):
        """Get subscription information for the gym"""
        if self.subscription_id:
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