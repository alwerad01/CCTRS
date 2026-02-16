"""
Database models for Civic Complaint Tracking System
"""
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login_manager

class User(UserMixin, db.Model):
    """User model for citizens, officers, and admins"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='citizen')  # citizen, officer, admin
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    department = db.relationship('Department', backref='users')
    complaints = db.relationship('Complaint', foreign_keys='Complaint.citizen_id', backref='citizen', lazy='dynamic')
    assigned_complaints = db.relationship('Complaint', foreign_keys='Complaint.assigned_officer_id', backref='assigned_officer', lazy='dynamic')
    status_changes = db.relationship('StatusHistory', backref='changed_by', lazy='dynamic')
    
    def set_password(self, password):
        """Hash and set user password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username} ({self.role})>'

@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login"""
    return User.query.get(int(user_id))

class Department(db.Model):
    """Department model for organizing complaints"""
    __tablename__ = 'departments'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    complaints = db.relationship('Complaint', backref='department', lazy='dynamic')
    
    def __repr__(self):
        return f'<Department {self.name}>'

class Complaint(db.Model):
    """Complaint model for tracking civic issues"""
    __tablename__ = 'complaints'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    citizen_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    assigned_officer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    current_status = db.Column(db.String(50), nullable=False, default='Received')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    status_history = db.relationship('StatusHistory', backref='complaint', lazy='dynamic', 
                                     order_by='StatusHistory.changed_at.desc()', cascade='all, delete-orphan')
    
    def update_status(self, new_status, changed_by_user, notes=''):
        """
        Update complaint status with validation and history tracking
        
        Valid transitions:
        - Received -> In Progress
        - In Progress -> Resolved
        """
        valid_transitions = {
            'Received': ['In Progress'],
            'In Progress': ['Resolved'],
            'Resolved': []  # Cannot change from resolved
        }
        
        if new_status not in valid_transitions.get(self.current_status, []):
            raise ValueError(f'Invalid status transition from {self.current_status} to {new_status}')
        
        # Create status history entry
        history = StatusHistory(
            complaint_id=self.id,
            previous_status=self.current_status,
            new_status=new_status,
            changed_by_user_id=changed_by_user.id,
            notes=notes
        )
        db.session.add(history)
        
        # Update current status
        self.current_status = new_status
        self.updated_at = datetime.utcnow()
    
    def get_resolution_time(self):
        """Calculate resolution time in days (if resolved)"""
        if self.current_status == 'Resolved':
            return (self.updated_at - self.created_at).days
        return None
    
    def __repr__(self):
        return f'<Complaint #{self.id}: {self.title} ({self.current_status})>'

class StatusHistory(db.Model):
    """Status history model for tracking complaint status changes"""
    __tablename__ = 'status_history'
    
    id = db.Column(db.Integer, primary_key=True)
    complaint_id = db.Column(db.Integer, db.ForeignKey('complaints.id'), nullable=False)
    previous_status = db.Column(db.String(50), nullable=False)
    new_status = db.Column(db.String(50), nullable=False)
    changed_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    changed_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f'<StatusHistory: {self.previous_status} -> {self.new_status}>'
