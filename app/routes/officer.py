"""
Officer routes for viewing and updating complaints through the 9-stage lifecycle
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
    """Officer dashboard with department complaints and lifecycle stats"""
    if not current_user.department_id:
        flash('You are not assigned to any department. Please contact admin.', 'warning')
        return render_template('officer/dashboard.html', complaints=[],
                               total=0, submitted=0, under_review=0,
                               assigned=0, in_progress=0, on_hold=0,
                               resolved=0, rejected=0, closed=0)

    complaints = Complaint.query.filter_by(department_id=current_user.department_id)\
                                .filter(Complaint.current_status != 'Draft')\
                                .order_by(Complaint.created_at.desc()).all()

    def count(status):
        return sum(1 for c in complaints if c.current_status == status)

    return render_template('officer/dashboard.html',
                           complaints=complaints,
                           total=len(complaints),
                           submitted=count('Submitted'),
                           under_review=count('Under Review'),
                           assigned=count('Assigned'),
                           in_progress=count('In Progress'),
                           on_hold=count('On Hold'),
                           resolved=count('Resolved'),
                           rejected=count('Rejected'),
                           closed=count('Closed'))


@bp.route('/complaint/<int:complaint_id>')
@login_required
@role_required('officer')
def complaint_detail(complaint_id):
    """View complaint details with dynamic status transition options"""
    complaint = Complaint.query.get_or_404(complaint_id)

    if complaint.department_id != current_user.department_id:
        flash('You do not have permission to view this complaint.', 'danger')
        return redirect(url_for('officer.dashboard'))

    history = complaint.status_history.all()
    allowed_transitions = complaint.get_allowed_next_statuses()

    return render_template('officer/complaint_detail.html',
                           complaint=complaint,
                           history=history,
                           allowed_transitions=allowed_transitions)


@bp.route('/update_status/<int:complaint_id>', methods=['POST'])
@login_required
@role_required('officer')
def update_status(complaint_id):
    """Update complaint status — validated against the lifecycle transition map"""
    complaint = Complaint.query.get_or_404(complaint_id)

    if complaint.department_id != current_user.department_id:
        flash('You do not have permission to update this complaint.', 'danger')
        return redirect(url_for('officer.dashboard'))

    new_status = request.form.get('new_status', '').strip()
    notes = request.form.get('notes', '').strip()

    if not new_status:
        flash('Please select a status.', 'danger')
        return redirect(url_for('officer.complaint_detail', complaint_id=complaint_id))

    try:
        # Auto-assign officer if not already set
        if not complaint.assigned_officer_id:
            complaint.assigned_officer_id = current_user.id

        complaint.update_status(new_status, current_user, notes)
        db.session.commit()
        flash(f'Status updated to "{new_status}" successfully!', 'success')
    except ValueError as e:
        flash(str(e), 'danger')
        db.session.rollback()

    return redirect(url_for('officer.complaint_detail', complaint_id=complaint_id))
