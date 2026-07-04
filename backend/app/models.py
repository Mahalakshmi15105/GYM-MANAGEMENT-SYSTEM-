from datetime import datetime
from app.extensions import db
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


class Member(db.Model):
    __tablename__ = 'members'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Multi-tenant isolation - CRITICAL for SaaS
    gym_id = db.Column(db.Integer, db.ForeignKey('gyms.id', ondelete='CASCADE'), nullable=False)
    
    # Auto-generated unique member ID
    member_id = db.Column(db.String(20), nullable=False, unique=True, default=lambda: f"MEM{str(uuid.uuid4())[:8].upper()}")
    
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
