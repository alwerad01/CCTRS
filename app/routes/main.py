"""
Main routes — home redirect and public guest stats page
"""
from flask import Blueprint, render_template, redirect, flash, url_for, request
from flask_login import current_user, login_required
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
    supervisors = User.query.filter_by(department_id=dept.id, role='supervisor').all()
    officers = User.query.filter_by(department_id=dept.id, role='officer').all()

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

@bp.route('/public/complaints')
def public_complaints():
    """Feed of all public complaints"""
    # Exclude drafts and fetch public
    complaints = Complaint.query.filter_by(is_public=True).filter(Complaint.current_status != 'Draft').order_by(Complaint.created_at.desc()).all()
    return render_template('public/feed.html', complaints=complaints)

@bp.route('/public/complaint/<int:complaint_id>/upvote', methods=['POST'])
@login_required
def upvote_complaint(complaint_id):
    """Upvote a public complaint"""
    complaint = Complaint.query.get_or_404(complaint_id)
    
    if not complaint.is_public:
        flash('Cannot upvote a private complaint.', 'danger')
        return redirect(url_for('main.public_complaints'))
        
    from app.models import Upvote
    existing = Upvote.query.filter_by(user_id=current_user.id, complaint_id=complaint_id).first()
    
    if existing:
        flash('You have already upvoted this complaint.', 'info')
    else:
        upvote = Upvote(user_id=current_user.id, complaint_id=complaint_id)
        db.session.add(upvote)
        db.session.commit()
        flash('Complaint upvoted!', 'success')
        
    return redirect(request.referrer or url_for('main.public_complaints'))


@bp.route('/about')
def about():
    return render_template('about.html')


@bp.route('/presentation')
def presentation():
    """Standalone presentation page for system architecture and features"""
    return render_template('public/presentation.html')


@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """Universal user profile settings page"""
    if request.method == 'POST':
        phone = request.form.get('phone_number', '').strip()
        address = request.form.get('address', '').strip()
        
        current_user.phone_number = phone if phone else None
        current_user.address = address if address else None
        
        db.session.commit()
        flash('Your profile has been updated.', 'success')
        return redirect(url_for('main.profile'))
        
    return render_template('public/profile.html', user=current_user)

