"""
Admin routes for user management, department management, and reports
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from sqlalchemy import func
from datetime import datetime, timedelta
from app import db
from app.models import User, Department, Complaint, StatusHistory
from app.utils.decorators import role_required

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route('/dashboard')
@login_required
@role_required('admin')
def dashboard():
    """Admin dashboard with statistics and charts"""
    # Overall statistics
    total_complaints = Complaint.query.count()
    total_users = User.query.count()
    total_departments = Department.query.count()
    unresolved = Complaint.query.filter(Complaint.current_status != 'Resolved').count()
    
    # Complaints by department (for chart)
    dept_stats = db.session.query(
        Department.name,
        func.count(Complaint.id).label('count')
    ).join(Complaint).group_by(Department.name).all()
    
    dept_labels = [stat[0] for stat in dept_stats]
    dept_counts = [stat[1] for stat in dept_stats]
    
    # Recent complaints
    recent_complaints = Complaint.query.order_by(Complaint.created_at.desc()).limit(10).all()
    
    return render_template('admin/dashboard.html',
                         total_complaints=total_complaints,
                         total_users=total_users,
                         total_departments=total_departments,
                         unresolved=unresolved,
                         dept_labels=dept_labels,
                         dept_counts=dept_counts,
                         recent_complaints=recent_complaints)

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
        
        # Validate
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
        if role not in ['citizen', 'officer', 'admin']:
            errors.append('Invalid role.')
        if role == 'officer' and not department_id:
            errors.append('Officers must be assigned to a department.')
        
        if errors:
            for error in errors:
                flash(error, 'danger')
            departments = Department.query.all()
            return render_template('admin/add_user.html', departments=departments)
        
        # Create user
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
    
    # Prevent deleting self
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
    
    # Check if department has complaints
    if dept.complaints.count() > 0:
        flash('Cannot delete department with existing complaints.', 'danger')
        return redirect(url_for('admin.manage_departments'))
    
    name = dept.name
    db.session.delete(dept)
    db.session.commit()
    
    flash(f'Department {name} deleted successfully.', 'success')
    return redirect(url_for('admin.manage_departments'))

# ========== Reports ==========

@bp.route('/reports')
@login_required
@role_required('admin')
def reports():
    """Generate various reports"""
    # Unresolved complaints
    unresolved_complaints = Complaint.query.filter(Complaint.current_status != 'Resolved')\
                                          .order_by(Complaint.created_at.asc()).all()
    
    # Resolved complaints for average resolution time
    resolved_complaints = Complaint.query.filter_by(current_status='Resolved').all()
    
    if resolved_complaints:
        resolution_times = [c.get_resolution_time() for c in resolved_complaints]
        avg_resolution_time = sum(resolution_times) / len(resolution_times)
    else:
        avg_resolution_time = 0
    
    # Complaints by department
    from sqlalchemy import case
    complaints_by_dept = db.session.query(
        Department.name,
        func.count(Complaint.id).label('total'),
        func.sum(case((Complaint.current_status == 'Resolved', 1), else_=0)).label('resolved'),
        func.sum(case((Complaint.current_status != 'Resolved', 1), else_=0)).label('unresolved')
    ).join(Complaint).group_by(Department.name).all()
    
    return render_template('admin/reports.html',
                         unresolved_complaints=unresolved_complaints,
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
    
    return render_template('admin/complaint_detail.html',
                         complaint=complaint,
                         history=history)
