"""
Moderator routes — verify or flag submitted complaints before they reach officers
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Complaint
from app.utils.decorators import role_required

bp = Blueprint('moderator', __name__, url_prefix='/moderator')


@bp.route('/dashboard')
@login_required
@role_required('moderator', 'admin')
def dashboard():
    """Queue of complaints awaiting moderation"""
    pending = Complaint.query.filter(
        Complaint.current_status.in_(['Submitted', 'Flagged'])
    ).order_by(Complaint.created_at.asc()).all()

    flagged = [c for c in pending if c.current_status == 'Flagged']
    submitted = [c for c in pending if c.current_status == 'Submitted']

    return render_template('moderator/dashboard.html',
                           submitted_complaints=submitted,
                           flagged_complaints=flagged,
                           total_pending=len(submitted),
                           total_flagged=len(flagged))


@bp.route('/complaint/<int:complaint_id>')
@login_required
@role_required('moderator', 'admin')
def complaint_detail(complaint_id):
    """Review a complaint before verifying or flagging"""
    complaint = Complaint.query.get_or_404(complaint_id)
    history = complaint.status_history.all()
    return render_template('moderator/complaint_detail.html',
                           complaint=complaint,
                           history=history)


@bp.route('/verify/<int:complaint_id>', methods=['POST'])
@login_required
@role_required('moderator', 'admin')
def verify(complaint_id):
    """Verify a Submitted complaint → Under Review"""
    complaint = Complaint.query.get_or_404(complaint_id)

    if complaint.current_status != 'Submitted':
        flash('Only Submitted complaints can be verified.', 'warning')
        return redirect(url_for('moderator.complaint_detail', complaint_id=complaint_id))

    notes = request.form.get('notes', 'Complaint verified — forwarded to department.').strip()
    try:
        complaint.update_status('Under Review', current_user, notes)
        db.session.commit()
        flash(f'Complaint #{complaint_id} verified and forwarded to the department.', 'success')
    except ValueError as e:
        flash(str(e), 'danger')
        db.session.rollback()

    return redirect(url_for('moderator.dashboard'))


@bp.route('/flag/<int:complaint_id>', methods=['POST'])
@login_required
@role_required('moderator', 'admin')
def flag(complaint_id):
    """Flag a Submitted complaint as spam/invalid"""
    complaint = Complaint.query.get_or_404(complaint_id)

    if complaint.current_status != 'Submitted':
        flash('Only Submitted complaints can be flagged.', 'warning')
        return redirect(url_for('moderator.complaint_detail', complaint_id=complaint_id))

    reason = request.form.get('flag_reason', '').strip()
    if not reason:
        flash('Please provide a reason for flagging this complaint.', 'danger')
        return redirect(url_for('moderator.complaint_detail', complaint_id=complaint_id))

    try:
        complaint.flag_reason = reason
        complaint.update_status('Flagged', current_user, f'Flagged: {reason}')
        db.session.commit()
        flash(f'Complaint #{complaint_id} has been flagged.', 'warning')
    except ValueError as e:
        flash(str(e), 'danger')
        db.session.rollback()

    return redirect(url_for('moderator.dashboard'))
