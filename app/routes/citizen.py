"""
Citizen routes for complaint submission, draft saving, and tracking
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Complaint, Department, STATUS_TRANSITIONS
from app.utils.decorators import role_required

bp = Blueprint('citizen', __name__, url_prefix='/citizen')


@bp.route('/dashboard')
@login_required
@role_required('citizen')
def dashboard():
    """Citizen dashboard with complaint summary"""
    all_complaints = current_user.complaints

    total_complaints = all_complaints.count()
    drafts = all_complaints.filter_by(current_status='Draft').count()
    submitted = all_complaints.filter_by(current_status='Submitted').count()
    in_progress = all_complaints.filter(
        Complaint.current_status.in_(['Under Review', 'Assigned', 'In Progress', 'On Hold'])
    ).count()
    resolved = all_complaints.filter(
        Complaint.current_status.in_(['Resolved', 'Closed'])
    ).count()
    rejected = all_complaints.filter_by(current_status='Rejected').count()

    recent_complaints = all_complaints.order_by(Complaint.created_at.desc()).limit(5).all()

    return render_template('citizen/dashboard.html',
                           total=total_complaints,
                           drafts=drafts,
                           submitted=submitted,
                           in_progress=in_progress,
                           resolved=resolved,
                           rejected=rejected,
                           recent_complaints=recent_complaints)


@bp.route('/submit', methods=['GET', 'POST'])
@login_required
@role_required('citizen')
def submit_complaint():
    """Complaint submission form – supports both Draft and immediate Submit"""
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        department_id = request.form.get('department_id')
        save_as_draft = request.form.get('save_as_draft') == '1'

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

        # Determine initial status
        initial_status = 'Draft' if save_as_draft else 'Submitted'

        complaint = Complaint(
            title=title,
            description=description,
            citizen_id=current_user.id,
            department_id=int(department_id),
            current_status=initial_status
        )

        db.session.add(complaint)
        db.session.commit()

        if save_as_draft:
            flash(f'Complaint saved as Draft. ID: #{complaint.id}. You can submit it later from My Complaints.', 'info')
        else:
            flash(f'Complaint #{complaint.id} submitted successfully! It is now under review.', 'success')

        return redirect(url_for('citizen.view_complaints'))

    departments = Department.query.all()
    return render_template('citizen/submit_complaint.html', departments=departments)


@bp.route('/complaint/<int:complaint_id>/submit_draft', methods=['POST'])
@login_required
@role_required('citizen')
def submit_draft(complaint_id):
    """Convert a Draft complaint to Submitted status"""
    complaint = Complaint.query.get_or_404(complaint_id)

    if complaint.citizen_id != current_user.id:
        flash('You do not have permission to modify this complaint.', 'danger')
        return redirect(url_for('citizen.view_complaints'))

    if complaint.current_status != 'Draft':
        flash('Only draft complaints can be submitted this way.', 'warning')
        return redirect(url_for('citizen.complaint_detail', complaint_id=complaint_id))

    try:
        complaint.update_status('Submitted', current_user, notes='Citizen submitted draft complaint.')
        db.session.commit()
        flash(f'Complaint #{complaint.id} has been submitted successfully!', 'success')
    except ValueError as e:
        flash(str(e), 'danger')
        db.session.rollback()

    return redirect(url_for('citizen.view_complaints'))


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

    if complaint.citizen_id != current_user.id:
        flash('You do not have permission to view this complaint.', 'danger')
        return redirect(url_for('citizen.view_complaints'))

    history = complaint.status_history.all()

    return render_template('citizen/complaint_detail.html',
                           complaint=complaint,
                           history=history)
