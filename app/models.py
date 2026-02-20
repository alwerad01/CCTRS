"""
Database models for Civic Complaint Tracking System — 7-Role RBAC
"""
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login_manager

# All valid roles
VALID_ROLES = ['admin', 'supervisor', 'moderator', 'officer', 'auditor', 'citizen']

# All valid status values in the lifecycle (11 stages)
VALID_STATUSES = [
    'Draft', 'Submitted', 'Flagged',
    'Under Review', 'Assigned', 'In Progress',
    'On Hold', 'Escalated', 'Resolved',
    'Rejected', 'Closed'
]

# Allowed status transitions (enforced by update_status)
STATUS_TRANSITIONS = {
    'Draft':        ['Submitted'],
    'Submitted':    ['Under Review', 'Flagged'],       # Moderator action
    'Flagged':      ['Closed'],                        # Terminal via Moderator/Admin
    'Under Review': ['Assigned', 'Rejected'],
    'Assigned':     ['In Progress', 'On Hold', 'Rejected'],
    'In Progress':  ['Resolved', 'On Hold', 'Rejected', 'Escalated'],
    'On Hold':      ['In Progress', 'Rejected', 'Escalated'],
    'Escalated':    ['In Progress', 'Assigned'],       # Supervisor/Admin resolves escalation
    'Resolved':     ['Closed'],
    'Rejected':     ['Closed', 'Submitted'],            # Citizen can edit & resubmit
    'Closed':       []   # Terminal
}

# Badge colour CSS class per status
STATUS_BADGE_COLORS = {
    'Draft':        'status-draft',
    'Submitted':    'status-submitted',
    'Flagged':      'status-flagged',
    'Under Review': 'status-under-review',
    'Assigned':     'status-assigned',
    'In Progress':  'status-in-progress',
    'On Hold':      'status-on-hold',
    'Escalated':    'status-escalated',
    'Resolved':     'status-resolved',
    'Rejected':     'status-rejected',
    'Closed':       'status-closed',
}

# Roles that count as "staff" (can access internal views)
STAFF_ROLES = ['admin', 'supervisor', 'moderator', 'officer', 'auditor']


class User(UserMixin, db.Model):
    """User model — supports 6 internal roles + citizen"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='citizen')
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    department = db.relationship('Department', backref='users')
    complaints = db.relationship('Complaint', foreign_keys='Complaint.citizen_id',
                                  backref='citizen', lazy='dynamic')
    assigned_complaints = db.relationship('Complaint', foreign_keys='Complaint.assigned_officer_id',
                                           backref='assigned_officer', lazy='dynamic')
    status_changes = db.relationship('StatusHistory', backref='changed_by', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_staff(self):
        return self.role in STAFF_ROLES

    def get_dashboard_url(self):
        """Return the correct dashboard URL for this user's role"""
        from flask import url_for
        routes = {
            'admin':      'admin.dashboard',
            'supervisor': 'supervisor.dashboard',
            'moderator':  'moderator.dashboard',
            'officer':    'officer.dashboard',
            'auditor':    'auditor.dashboard',
            'citizen':    'citizen.dashboard',
        }
        return url_for(routes.get(self.role, 'citizen.dashboard'))

    def __repr__(self):
        return f'<User {self.username} ({self.role})>'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Department(db.Model):
    """Department model"""
    __tablename__ = 'departments'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    complaints = db.relationship('Complaint', backref='department', lazy='dynamic')

    def __repr__(self):
        return f'<Department {self.name}>'


class Complaint(db.Model):
    """Complaint model — 11-stage lifecycle"""
    __tablename__ = 'complaints'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    citizen_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    assigned_officer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    current_status = db.Column(db.String(50), nullable=False, default='Draft')
    flag_reason = db.Column(db.Text, nullable=True)       # Set by Moderator when flagging
    escalation_notes = db.Column(db.Text, nullable=True)  # Set by Supervisor when escalating
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    status_history = db.relationship(
        'StatusHistory', backref='complaint', lazy='dynamic',
        order_by='StatusHistory.changed_at.desc()', cascade='all, delete-orphan'
    )

    def get_allowed_next_statuses(self):
        return STATUS_TRANSITIONS.get(self.current_status, [])

    def is_terminal(self):
        return self.current_status == 'Closed'

    def update_status(self, new_status, changed_by_user, notes=''):
        """
        Update complaint status with validation.
        Raises ValueError if transition is invalid.
        """
        allowed = STATUS_TRANSITIONS.get(self.current_status, [])
        if new_status not in allowed:
            raise ValueError(
                f'Invalid transition: {self.current_status} → {new_status}. '
                f'Allowed: {", ".join(allowed) if allowed else "None (terminal)"}'
            )

        history = StatusHistory(
            complaint_id=self.id,
            previous_status=self.current_status,
            new_status=new_status,
            changed_by_user_id=changed_by_user.id,
            notes=notes
        )
        db.session.add(history)
        self.current_status = new_status
        self.updated_at = datetime.utcnow()

    def get_resolution_time(self):
        if self.current_status in ('Resolved', 'Closed'):
            return (self.updated_at - self.created_at).days
        return None

    def get_badge_class(self):
        return STATUS_BADGE_COLORS.get(self.current_status, 'bg-secondary')

    def __repr__(self):
        return f'<Complaint #{self.id}: {self.title} ({self.current_status})>'


class StatusHistory(db.Model):
    """Full audit trail of all status transitions"""
    __tablename__ = 'status_history'

    id = db.Column(db.Integer, primary_key=True)
    complaint_id = db.Column(db.Integer, db.ForeignKey('complaints.id'), nullable=False)
    previous_status = db.Column(db.String(50), nullable=False)
    new_status = db.Column(db.String(50), nullable=False)
    changed_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    changed_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f'<StatusHistory: {self.previous_status} → {self.new_status}>'
