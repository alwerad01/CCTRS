"""
Citizen routes for complaint submission, draft saving, and tracking
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from werkzeug.utils import secure_filename
import os
import uuid
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
        Complaint.current_status.in_(['Under Review', 'Assigned', 'In Progress', 'On Hold', 'Escalated'])
    ).count()
    resolved = all_complaints.filter(
        Complaint.current_status.in_(['Resolved', 'Closed'])
    ).count()
    rejected = all_complaints.filter_by(current_status='Rejected').count()

    complaints = all_complaints.order_by(Complaint.created_at.desc()).all()

    return render_template('citizen/dashboard.html',
                           total=total_complaints,
                           drafts=drafts,
                           submitted=submitted,
                           pending=submitted,
                           in_progress=in_progress,
                           resolved=resolved,
                           rejected=rejected,
                           complaints=complaints)


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
        
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')
        is_public = request.form.get('is_public') == '1'
        
        evidence_filename = None
        if 'evidence' in request.files:
            file = request.files['evidence']
            if file and file.filename != '':
                ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
                if ext in {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'pdf'}:
                    evidence_filename = f"{uuid.uuid4().hex}.{ext}"
                    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], evidence_filename)
                    file.save(filepath)

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
            current_status=initial_status,
            evidence_filename=evidence_filename,
            latitude=float(latitude) if latitude else None,
            longitude=float(longitude) if longitude else None,
            is_public=is_public
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


@bp.route('/complaint/<int:complaint_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('citizen')
def edit_draft(complaint_id):
    """Edit a Draft or Rejected complaint – update title, description, department"""
    complaint = Complaint.query.get_or_404(complaint_id)

    if complaint.citizen_id != current_user.id:
        flash('You do not have permission to modify this complaint.', 'danger')
        return redirect(url_for('citizen.view_complaints'))

    if complaint.current_status not in ('Draft', 'Rejected'):
        flash('Only draft or rejected complaints can be edited.', 'warning')
        return redirect(url_for('citizen.complaint_detail', complaint_id=complaint_id))

    is_rejected = complaint.current_status == 'Rejected'

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        department_id = request.form.get('department_id')
        submit_now = request.form.get('submit_now') == '1'
        
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')
        is_public = request.form.get('is_public') == '1'
        
        if 'evidence' in request.files:
            file = request.files['evidence']
            if file and file.filename != '':
                ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
                if ext in {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'pdf'}:
                    evidence_filename = f"{uuid.uuid4().hex}.{ext}"
                    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], evidence_filename)
                    file.save(filepath)
                    complaint.evidence_filename = evidence_filename

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
            return render_template('citizen/edit_draft.html',
                                   complaint=complaint, departments=departments)

        complaint.title = title
        complaint.description = description
        complaint.department_id = int(department_id)
        if latitude: complaint.latitude = float(latitude)
        if longitude: complaint.longitude = float(longitude)
        complaint.is_public = is_public

        if submit_now:
            try:
                note = 'Citizen revised and resubmitted after rejection.' if is_rejected \
                       else 'Citizen edited and submitted draft.'
                complaint.update_status('Submitted', current_user, notes=note)
                flash(f'Complaint #{complaint.id} updated and submitted!', 'success')
            except ValueError as e:
                flash(str(e), 'danger')
                db.session.rollback()
                departments = Department.query.all()
                return render_template('citizen/edit_draft.html',
                                       complaint=complaint, departments=departments)
        else:
            flash(f'Complaint #{complaint.id} updated successfully.', 'info')

        db.session.commit()
        return redirect(url_for('citizen.view_complaints'))

    departments = Department.query.all()
    return render_template('citizen/edit_draft.html',
                           complaint=complaint, departments=departments)


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

@bp.route('/complaint/<int:complaint_id>/rate', methods=['POST'])
@login_required
@role_required('citizen')
def rate_complaint(complaint_id):
    """Submit a rating and feedback for a resolved/closed complaint"""
    complaint = Complaint.query.get_or_404(complaint_id)

    if complaint.citizen_id != current_user.id:
        flash('You do not have permission to rate this complaint.', 'danger')
        return redirect(url_for('citizen.view_complaints'))

    if complaint.current_status not in ['Resolved', 'Closed']:
        flash('You can only rate complaints that have been resolved or closed.', 'warning')
        return redirect(url_for('citizen.complaint_detail', complaint_id=complaint_id))

    if complaint.rating is not None:
        flash('You have already rated this complaint.', 'info')
        return redirect(url_for('citizen.complaint_detail', complaint_id=complaint_id))

    rating = request.form.get('rating')
    feedback = request.form.get('feedback', '').strip()

    if not rating or not rating.isdigit() or not (1 <= int(rating) <= 5):
        flash('Please provide a valid rating between 1 and 5.', 'danger')
        return redirect(url_for('citizen.complaint_detail', complaint_id=complaint_id))

    complaint.rating = int(rating)
    if feedback:
        complaint.feedback_text = feedback

    db.session.commit()
    flash('Thank you! Your feedback has been submitted.', 'success')
    return redirect(url_for('citizen.complaint_detail', complaint_id=complaint_id))

@bp.route('/notifications/read', methods=['POST'])
@login_required
@role_required('citizen')
def read_notifications():
    """Mark all notifications as read for current user"""
    unread = current_user.notifications.filter_by(is_read=False).all()
    for notif in unread:
        notif.is_read = True
    db.session.commit()
    return redirect(request.referrer or url_for('citizen.dashboard'))
