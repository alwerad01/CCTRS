"""
Admin routes for user management, department management, and reports
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from sqlalchemy import func, case
from datetime import datetime
from app import db
from app.models import User, Department, Complaint, StatusHistory, STATUS_TRANSITIONS, VALID_ROLES
from app.utils.decorators import role_required

bp = Blueprint('admin', __name__, url_prefix='/admin')

# Statuses that count as "needs attention"
ACTIVE_STATUSES = ['Submitted', 'Under Review', 'Assigned', 'In Progress', 'On Hold', 'Escalated']
STAFF_ROLES = ['supervisor', 'moderator', 'officer', 'auditor', 'admin']


@bp.route('/dashboard')
@login_required
@role_required('admin')
def dashboard():
    """Admin dashboard with statistics and charts"""
    total_complaints = Complaint.query.filter(Complaint.current_status != 'Draft').count()
    total_users = User.query.count()
    total_departments = Department.query.count()

    # Count by each lifecycle stage (11 stages)
    all_statuses = ['draft', 'submitted', 'flagged', 'under_review', 'assigned',
                    'in_progress', 'on_hold', 'escalated', 'resolved', 'rejected', 'closed']
    status_map = {k: k.replace('_', ' ').title() for k in all_statuses}
    status_map['under_review'] = 'Under Review'
    status_map['in_progress']  = 'In Progress'
    status_map['on_hold']      = 'On Hold'

    status_counts = {k: Complaint.query.filter_by(current_status=v).count()
                     for k, v in status_map.items()}
    active = sum(Complaint.query.filter_by(current_status=s).count() for s in ACTIVE_STATUSES)

    dept_stats = db.session.query(
        Department.name, func.count(Complaint.id).label('count')
    ).join(Complaint).group_by(Department.name).all()

    dept_labels = [s[0] for s in dept_stats]
    dept_counts = [s[1] for s in dept_stats]

    chart_labels = ['Submitted', 'Flagged', 'Under Review', 'Assigned',
                    'In Progress', 'On Hold', 'Escalated', 'Resolved', 'Rejected', 'Closed']
    chart_keys   = ['submitted', 'flagged', 'under_review', 'assigned',
                    'in_progress', 'on_hold', 'escalated', 'resolved', 'rejected', 'closed']
    status_chart_data = [status_counts.get(k, 0) for k in chart_keys]

    complaints = Complaint.query.filter(
        Complaint.current_status != 'Draft'
    ).order_by(Complaint.created_at.desc()).all()

    # Role distribution
    role_counts = {r: User.query.filter_by(role=r).count() for r in VALID_ROLES}

    return render_template('admin/dashboard.html',
                           total_complaints=total_complaints,
                           total_users=total_users,
                           total_departments=total_departments,
                           active=active,
                           status_counts=status_counts,
                           dept_labels=dept_labels,
                           dept_counts=dept_counts,
                           status_chart_labels=chart_labels,
                           status_chart_data=status_chart_data,
                           complaints=complaints,
                           role_counts=role_counts)


# ========== User Management ==========

@bp.route('/users')
@login_required
@role_required('admin')
def manage_users():
    """List all users"""
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/manage_users.html', users=users)


@bp.route('/user/add', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def add_user():
    """Add a new user (officer or admin)"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        role = request.form.get('role', '').strip()
        department_id = request.form.get('department_id')

        errors = []
        if not username or len(username) < 3:
            errors.append('Username must be at least 3 characters.')
        if User.query.filter_by(username=username).first():
            errors.append('Username already exists.')
        if not email or '@' not in email:
            errors.append('Invalid email.')
        if User.query.filter_by(email=email).first():
            errors.append('Email already registered.')
        if not password or len(password) < 6:
            errors.append('Password must be at least 6 characters.')
        if role not in VALID_ROLES:
            errors.append('Invalid role.')
        if role in ['officer', 'supervisor'] and not department_id:
            errors.append('Officers and Supervisors must be assigned to a department.')

        if errors:
            for error in errors:
                flash(error, 'danger')
            departments = Department.query.all()
            return render_template('admin/add_user.html', departments=departments)

        new_user = User(
            username=username,
            email=email,
            role=role,
            department_id=int(department_id) if department_id else None
        )
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        flash(f'User {username} created successfully!', 'success')
        return redirect(url_for('admin.manage_users'))

    departments = Department.query.all()
    return render_template('admin/add_user.html', departments=departments)


@bp.route('/user/delete/<int:user_id>', methods=['POST'])
@login_required
@role_required('admin')
def delete_user(user_id):
    """Delete a user"""
    user = User.query.get_or_404(user_id)

    if user.id == current_user.id:
        flash('You cannot delete your own account.', 'danger')
        return redirect(url_for('admin.manage_users'))

    username = user.username
    db.session.delete(user)
    db.session.commit()

    flash(f'User {username} deleted successfully.', 'success')
    return redirect(url_for('admin.manage_users'))


# ========== Department Management ==========

@bp.route('/departments')
@login_required
@role_required('admin')
def manage_departments():
    """List all departments"""
    departments = Department.query.all()
    return render_template('admin/manage_departments.html', departments=departments)


@bp.route('/department/add', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def add_department():
    """Add a new department"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()

        if not name:
            flash('Department name is required.', 'danger')
            return render_template('admin/add_department.html')

        if Department.query.filter_by(name=name).first():
            flash('Department already exists.', 'danger')
            return render_template('admin/add_department.html')

        new_dept = Department(name=name, description=description)
        db.session.add(new_dept)
        db.session.commit()

        flash(f'Department {name} created successfully!', 'success')
        return redirect(url_for('admin.manage_departments'))

    return render_template('admin/add_department.html')


@bp.route('/department/delete/<int:dept_id>', methods=['POST'])
@login_required
@role_required('admin')
def delete_department(dept_id):
    """Delete a department"""
    dept = Department.query.get_or_404(dept_id)

    if dept.complaints.count() > 0:
        flash('Cannot delete department with existing complaints.', 'danger')
        return redirect(url_for('admin.manage_departments'))

    name = dept.name
    db.session.delete(dept)
    db.session.commit()

    flash(f'Department {name} deleted successfully.', 'success')
    return redirect(url_for('admin.manage_departments'))


@bp.route('/department/<int:dept_id>')
@login_required
@role_required('admin')
def department_view(dept_id):
    """View department details with all complaints and staff"""
    dept = Department.query.get_or_404(dept_id)

    # Staff
    supervisors = User.query.filter_by(department_id=dept.id, role='supervisor').all()
    officers = User.query.filter_by(department_id=dept.id, role='officer').all()

    # Complaints — optional status filter (always exclude drafts)
    status_filter = request.args.get('status', '')
    complaints_q = Complaint.query.filter_by(department_id=dept.id).filter(
        Complaint.current_status != 'Draft'
    )
    if status_filter:
        complaints_q = complaints_q.filter_by(current_status=status_filter)
    complaints = complaints_q.order_by(Complaint.created_at.desc()).all()

    # Quick counts (exclude drafts)
    total = Complaint.query.filter_by(department_id=dept.id).filter(
        Complaint.current_status != 'Draft'
    ).count()
    active = Complaint.query.filter_by(department_id=dept.id).filter(
        Complaint.current_status.in_(ACTIVE_STATUSES)
    ).count()
    resolved = Complaint.query.filter_by(department_id=dept.id).filter(
        Complaint.current_status.in_(['Resolved', 'Closed'])
    ).count()

    return render_template('admin/department_view.html',
                           dept=dept,
                           supervisors=supervisors,
                           officers=officers,
                           complaints=complaints,
                           total=total,
                           active=active,
                           resolved=resolved,
                           status_filter=status_filter)


# ========== Reports ==========

@bp.route('/reports')
@login_required
@role_required('admin')
def reports():
    """Generate reports with full lifecycle stage breakdown"""
    # Active (non-closed/rejected) complaints
    active_complaints = Complaint.query.filter(
        Complaint.current_status.in_(ACTIVE_STATUSES)
    ).order_by(Complaint.created_at.asc()).all()

    # Resolved/Closed for avg resolution time
    done_complaints = Complaint.query.filter(
        Complaint.current_status.in_(['Resolved', 'Closed'])
    ).all()

    if done_complaints:
        times = [c.get_resolution_time() for c in done_complaints if c.get_resolution_time() is not None]
        avg_resolution_time = sum(times) / len(times) if times else 0
    else:
        avg_resolution_time = 0

    # Per-department stats with all lifecycle stages
    complaints_by_dept = db.session.query(
        Department.name,
        func.count(Complaint.id).label('total'),
        func.sum(case((Complaint.current_status == 'Submitted', 1), else_=0)).label('submitted'),
        func.sum(case((Complaint.current_status == 'Under Review', 1), else_=0)).label('under_review'),
        func.sum(case((Complaint.current_status == 'Assigned', 1), else_=0)).label('assigned'),
        func.sum(case((Complaint.current_status == 'In Progress', 1), else_=0)).label('in_progress'),
        func.sum(case((Complaint.current_status == 'On Hold', 1), else_=0)).label('on_hold'),
        func.sum(case((Complaint.current_status == 'Resolved', 1), else_=0)).label('resolved'),
        func.sum(case((Complaint.current_status == 'Rejected', 1), else_=0)).label('rejected'),
        func.sum(case((Complaint.current_status == 'Closed', 1), else_=0)).label('closed'),
    ).join(Complaint).group_by(Department.name).all()

    return render_template('admin/reports.html',
                           active_complaints=active_complaints,
                           avg_resolution_time=avg_resolution_time,
                           complaints_by_dept=complaints_by_dept,
                           now=datetime.now)


@bp.route('/complaint/<int:complaint_id>')
@login_required
@role_required('admin')
def view_complaint(complaint_id):
    """View any complaint (read-only for admin)"""
    complaint = Complaint.query.get_or_404(complaint_id)
    history = complaint.status_history.all()
    allowed_transitions = complaint.get_allowed_next_statuses()

    return render_template('admin/complaint_detail.html',
                           complaint=complaint,
                           history=history,
                           allowed_transitions=allowed_transitions)


@bp.route('/complaint/<int:complaint_id>/update_status', methods=['POST'])
@login_required
@role_required('admin')
def admin_update_status(complaint_id):
    """Admin can force-advance a complaint to its next valid state"""
    complaint = Complaint.query.get_or_404(complaint_id)
    new_status = request.form.get('new_status', '').strip()
    notes = request.form.get('notes', '').strip()

    if not new_status:
        flash('Please select a status.', 'danger')
        return redirect(url_for('admin.view_complaint', complaint_id=complaint_id))

    try:
        complaint.update_status(new_status, current_user, notes)
        db.session.commit()
        flash(f'Complaint #{complaint_id} status updated to "{new_status}".', 'success')
    except ValueError as e:
        flash(str(e), 'danger')
        db.session.rollback()

    return redirect(url_for('admin.view_complaint', complaint_id=complaint_id))
