"""
Citizen routes for complaint submission and tracking
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Complaint, Department
from app.utils.decorators import role_required

bp = Blueprint('citizen', __name__, url_prefix='/citizen')

@bp.route('/dashboard')
@login_required
@role_required('citizen')
def dashboard():
    """Citizen dashboard with complaint summary"""
    # Get complaint statistics
    total_complaints = current_user.complaints.count()
    pending = current_user.complaints.filter_by(current_status='Received').count()
    in_progress = current_user.complaints.filter_by(current_status='In Progress').count()
    resolved = current_user.complaints.filter_by(current_status='Resolved').count()
    
    # Get recent complaints
    recent_complaints = current_user.complaints.order_by(Complaint.created_at.desc()).limit(5).all()
    
    return render_template('citizen/dashboard.html',
                         total=total_complaints,
                         pending=pending,
                         in_progress=in_progress,
                         resolved=resolved,
                         recent_complaints=recent_complaints)

@bp.route('/submit', methods=['GET', 'POST'])
@login_required
@role_required('citizen')
def submit_complaint():
    """Complaint submission form"""
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        department_id = request.form.get('department_id')
        
        # Validate input
        errors = []
        
        if not title or len(title) < 5:
            errors.append('Title must be at least 5 characters long.')
        
        if not description or len(description) < 20:
            errors.append('Description must be at least 20 characters long.')
        
        if not department_id:
            errors.append('Please select a department.')
        
        if errors:
            for error in errors:
                flash(error, 'danger')
            departments = Department.query.all()
            return render_template('citizen/submit_complaint.html', departments=departments)
        
        # Create new complaint
        complaint = Complaint(
            title=title,
            description=description,
            citizen_id=current_user.id,
            department_id=int(department_id),
            current_status='Received'
        )
        
        db.session.add(complaint)
        db.session.commit()
        
        flash('Complaint submitted successfully! Complaint ID: #' + str(complaint.id), 'success')
        return redirect(url_for('citizen.view_complaints'))
    
    # GET request - show form
    departments = Department.query.all()
    return render_template('citizen/submit_complaint.html', departments=departments)

@bp.route('/complaints')
@login_required
@role_required('citizen')
def view_complaints():
    """View all complaints submitted by the current citizen"""
    complaints = current_user.complaints.order_by(Complaint.created_at.desc()).all()
    return render_template('citizen/complaints.html', complaints=complaints)

@bp.route('/complaint/<int:complaint_id>')
@login_required
@role_required('citizen')
def complaint_detail(complaint_id):
    """View detailed information about a specific complaint"""
    complaint = Complaint.query.get_or_404(complaint_id)
    
    # Ensure citizen can only view their own complaints
    if complaint.citizen_id != current_user.id:
        flash('You do not have permission to view this complaint.', 'danger')
        return redirect(url_for('citizen.view_complaints'))
    
    # Get status history
    history = complaint.status_history.all()
    
    return render_template('citizen/complaint_detail.html', 
                         complaint=complaint, 
                         history=history)
