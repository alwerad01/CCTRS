"""
Officer routes for viewing and updating complaints
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Complaint
from app.utils.decorators import role_required

bp = Blueprint('officer', __name__, url_prefix='/officer')

@bp.route('/dashboard')
@login_required
@role_required('officer')
def dashboard():
    """Officer dashboard with department complaints"""
    if not current_user.department_id:
        flash('You are not assigned to any department. Please contact admin.', 'warning')
        return render_template('officer/dashboard.html', complaints=[])
    
    # Get complaints for officer's department
    complaints = Complaint.query.filter_by(department_id=current_user.department_id)\
                                .order_by(Complaint.created_at.desc()).all()
    
    # Statistics
    total = len(complaints)
    pending = sum(1 for c in complaints if c.current_status == 'Received')
    in_progress = sum(1 for c in complaints if c.current_status == 'In Progress')
    resolved = sum(1 for c in complaints if c.current_status == 'Resolved')
    
    return render_template('officer/dashboard.html',
                         complaints=complaints,
                         total=total,
                         pending=pending,
                         in_progress=in_progress,
                         resolved=resolved)

@bp.route('/complaint/<int:complaint_id>')
@login_required
@role_required('officer')
def complaint_detail(complaint_id):
    """View complaint details"""
    complaint = Complaint.query.get_or_404(complaint_id)
    
    # Ensure officer can only view complaints from their department
    if complaint.department_id != current_user.department_id:
        flash('You do not have permission to view this complaint.', 'danger')
        return redirect(url_for('officer.dashboard'))
    
    history = complaint.status_history.all()
    
    return render_template('officer/complaint_detail.html',
                         complaint=complaint,
                         history=history)

@bp.route('/update_status/<int:complaint_id>', methods=['POST'])
@login_required
@role_required('officer')
def update_status(complaint_id):
    """Update complaint status"""
    complaint = Complaint.query.get_or_404(complaint_id)
    
    # Verify officer has permission
    if complaint.department_id != current_user.department_id:
        flash('You do not have permission to update this complaint.', 'danger')
        return redirect(url_for('officer.dashboard'))
    
    new_status = request.form.get('new_status', '').strip()
    notes = request.form.get('notes', '').strip()
    
    if not new_status:
        flash('Please select a status.', 'danger')
        return redirect(url_for('officer.complaint_detail', complaint_id=complaint_id))
    
    try:
        # Assign officer to complaint if not already assigned
        if not complaint.assigned_officer_id:
            complaint.assigned_officer_id = current_user.id
        
        # Update status with validation
        complaint.update_status(new_status, current_user, notes)
        db.session.commit()
        
        flash(f'Status updated to {new_status} successfully!', 'success')
    except ValueError as e:
        flash(str(e), 'danger')
        db.session.rollback()
    
    return redirect(url_for('officer.complaint_detail', complaint_id=complaint_id))
