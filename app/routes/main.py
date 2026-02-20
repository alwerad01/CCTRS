"""
Main routes — home redirect and public guest stats page
"""
from flask import Blueprint, render_template, redirect
from flask_login import current_user
from sqlalchemy import func
from app import db
from app.models import Complaint, Department, User

bp = Blueprint('main', __name__)


@bp.route('/')
def index():
    """Redirect authenticated users to their dashboard, others to login"""
    if current_user.is_authenticated:
        return redirect(current_user.get_dashboard_url())
    from flask import url_for
    return redirect(url_for('auth.login'))


@bp.route('/public')
def public_stats():
    """Public guest page — anonymized complaint statistics (no login required)"""
    total = Complaint.query.filter(Complaint.current_status != 'Draft').count()
    resolved = Complaint.query.filter(
        Complaint.current_status.in_(['Resolved', 'Closed'])
    ).count()
    active = Complaint.query.filter(
        Complaint.current_status.in_(['Submitted', 'Under Review', 'Assigned', 'In Progress', 'On Hold', 'Escalated'])
    ).count()
    flagged = Complaint.query.filter_by(current_status='Flagged').count()

    by_dept = db.session.query(
        Department.name,
        func.count(Complaint.id).label('count')
    ).join(Complaint).filter(
        Complaint.current_status != 'Draft'
    ).group_by(Department.name).all()

    resolution_rate = round((resolved / total * 100) if total else 0)

    # All departments for the directory section
    departments = Department.query.order_by(Department.name).all()

    return render_template('public/stats.html',
                           total=total,
                           resolved=resolved,
                           active=active,
                           flagged=flagged,
                           by_dept=by_dept,
                           resolution_rate=resolution_rate,
                           departments=departments)


@bp.route('/public/department/<int:dept_id>')
def department_detail(dept_id):
    """Public department detail — shows description, supervisor, and officers"""
    dept = Department.query.get_or_404(dept_id)

    # Get supervisor(s) and officers for this department
    supervisors = User.query.filter_by(department_id=dept.id, role='supervisor', is_active=True).all()
    officers = User.query.filter_by(department_id=dept.id, role='officer', is_active=True).all()

    # Complaint stats for this department (exclude drafts)
    dept_complaints = Complaint.query.filter_by(department_id=dept.id).filter(
        Complaint.current_status != 'Draft'
    )
    total_complaints = dept_complaints.count()
    resolved_complaints = dept_complaints.filter(
        Complaint.current_status.in_(['Resolved', 'Closed'])
    ).count()
    active_complaints = dept_complaints.filter(
        Complaint.current_status.in_(['Submitted', 'Under Review', 'Assigned', 'In Progress', 'On Hold', 'Escalated'])
    ).count()

    return render_template('public/department_detail.html',
                           dept=dept,
                           supervisors=supervisors,
                           officers=officers,
                           total_complaints=total_complaints,
                           resolved_complaints=resolved_complaints,
                           active_complaints=active_complaints)


@bp.route('/about')
def about():
    return render_template('about.html')

