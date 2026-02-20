"""
Supervisor routes — monitor department complaints, escalate stalled issues
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Complaint, User
from app.utils.decorators import role_required

bp = Blueprint('supervisor', __name__, url_prefix='/supervisor')

# Statuses a supervisor considers "active" (not terminal)
UNRESOLVED = ['Submitted', 'Under Review', 'Assigned', 'In Progress', 'On Hold', 'Escalated']


@bp.route('/dashboard')
@login_required
@role_required('supervisor', 'admin')
def dashboard():
    """Supervisor dashboard — unresolved complaints + officer workload"""
    dept_id = current_user.department_id

    if not dept_id:
        flash('You are not assigned to any department.', 'warning')
        return render_template('supervisor/dashboard.html',
                               unresolved=[], escalated=[],
                               officer_stats=[], total=0)

    dept_complaints = Complaint.query.filter_by(department_id=dept_id).all()
    unresolved = [c for c in dept_complaints if c.current_status in UNRESOLVED]
    escalated  = [c for c in dept_complaints if c.current_status == 'Escalated']

    # Officer workload: how many open complaints each officer has
    officers = User.query.filter_by(department_id=dept_id, role='officer').all()
    officer_stats = []
    for officer in officers:
        open_count = Complaint.query.filter_by(
            assigned_officer_id=officer.id
        ).filter(Complaint.current_status.in_(UNRESOLVED)).count()
        officer_stats.append({'officer': officer, 'open': open_count})

    return render_template('supervisor/dashboard.html',
                           unresolved=unresolved,
                           escalated=escalated,
                           officer_stats=officer_stats,
                           total=len(dept_complaints))


@bp.route('/complaint/<int:complaint_id>')
@login_required
@role_required('supervisor', 'admin')
def complaint_detail(complaint_id):
    """View complaint details + escalation option"""
    complaint = Complaint.query.get_or_404(complaint_id)

    if complaint.department_id != current_user.department_id and current_user.role != 'admin':
        flash('You can only view complaints in your department.', 'danger')
        return redirect(url_for('supervisor.dashboard'))

    history = complaint.status_history.all()
    allowed_transitions = complaint.get_allowed_next_statuses()
    return render_template('supervisor/complaint_detail.html',
                           complaint=complaint,
                           history=history,
                           allowed_transitions=allowed_transitions)


@bp.route('/escalate/<int:complaint_id>', methods=['POST'])
@login_required
@role_required('supervisor', 'admin')
def escalate(complaint_id):
    """Escalate a stalled complaint to Escalated status"""
    complaint = Complaint.query.get_or_404(complaint_id)

    if complaint.department_id != current_user.department_id and current_user.role != 'admin':
        flash('You can only escalate complaints in your department.', 'danger')
        return redirect(url_for('supervisor.dashboard'))

    notes = request.form.get('notes', '').strip()
    if not notes:
        flash('Please provide escalation notes.', 'danger')
        return redirect(url_for('supervisor.complaint_detail', complaint_id=complaint_id))

    try:
        complaint.escalation_notes = notes
        complaint.update_status('Escalated', current_user, f'Escalated by supervisor: {notes}')
        db.session.commit()
        flash(f'Complaint #{complaint_id} has been escalated to admin attention.', 'warning')
    except ValueError as e:
        flash(str(e), 'danger')
        db.session.rollback()

    return redirect(url_for('supervisor.dashboard'))
