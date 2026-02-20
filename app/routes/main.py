"""
Main routes — home redirect and public guest stats page
"""
from flask import Blueprint, render_template, redirect
from flask_login import current_user
from sqlalchemy import func
from app import db
from app.models import Complaint, Department

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

    return render_template('public/stats.html',
                           total=total,
                           resolved=resolved,
                           active=active,
                           flagged=flagged,
                           by_dept=by_dept,
                           resolution_rate=resolution_rate)


@bp.route('/about')
def about():
    return render_template('about.html')
