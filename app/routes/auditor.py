"""
Auditor routes — read-only access to all complaints and audit trails
"""
from flask import Blueprint, render_template, request
from flask_login import login_required
from app.models import Complaint, StatusHistory, VALID_STATUSES
from app.utils.decorators import role_required

bp = Blueprint('auditor', __name__, url_prefix='/auditor')


@bp.route('/dashboard')
@login_required
@role_required('auditor', 'admin')
def dashboard():
    """Read-only view of all complaints across all departments"""
    status_filter = request.args.get('status', 'all')

    query = Complaint.query
    if status_filter != 'all' and status_filter in VALID_STATUSES:
        query = query.filter_by(current_status=status_filter)

    complaints = query.order_by(Complaint.created_at.desc()).all()

    status_counts = {s: Complaint.query.filter_by(current_status=s).count()
                     for s in VALID_STATUSES}

    return render_template('auditor/dashboard.html',
                           complaints=complaints,
                           valid_statuses=VALID_STATUSES,
                           status_filter=status_filter,
                           status_counts=status_counts)


@bp.route('/complaint/<int:complaint_id>')
@login_required
@role_required('auditor', 'admin')
def complaint_detail(complaint_id):
    """Read-only complaint detail with full status history"""
    complaint = Complaint.query.get_or_404(complaint_id)
    history = complaint.status_history.all()
    return render_template('auditor/complaint_detail.html',
                           complaint=complaint,
                           history=history)
