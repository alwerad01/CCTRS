"""
Seed data script for CCTRS — 7-Role RBAC + 11-Stage Lifecycle
Run: python database/seed_data.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import User, Department, Complaint, StatusHistory
from datetime import datetime, timedelta
import random

app = create_app('default')

def create_status_chain(complaint, transitions, users):
    """Helper to walk a complaint through a series of status transitions"""
    for i, (new_status, notes) in enumerate(transitions):
        actor = random.choice(users)
        history = StatusHistory(
            complaint_id=complaint.id,
            previous_status=complaint.current_status,
            new_status=new_status,
            changed_by_user_id=actor.id,
            notes=notes
        )
        db.session.add(history)
        complaint.current_status = new_status
        complaint.updated_at = datetime.utcnow() - timedelta(days=len(transitions)-i)
    db.session.flush()

def seed():
    print("\nInitializing database with sample data (7-Role RBAC + 11 Stages)..\n")
    print("WARNING: This will delete all existing data!\n")

    confirm = input("Continue? (yes/no): ").strip().lower()
    if confirm != 'yes':
        print("Aborted.")
        return

    with app.app_context():
        print("Creating database tables...")
        db.drop_all()
        db.create_all()

        # ── Departments ──────────────────────────────────────────────────────
        print("Creating departments...")
        depts = {
            'Public Works':  Department(name='Public Works',  description='Roads, bridges, and infrastructure'),
            'Sanitation':    Department(name='Sanitation',    description='Waste management and cleanliness'),
            'Health':        Department(name='Health',         description='Public health services'),
            'Traffic':       Department(name='Traffic',        description='Traffic management and signals'),
            'Parks & Rec':   Department(name='Parks & Rec',    description='Public parks and recreational spaces'),
        }
        for d in depts.values():
            db.session.add(d)
        db.session.flush()
        print(f"  → {len(depts)} departments created")

        # ── Admin Users ──────────────────────────────────────────────────────
        print("Creating admin users...")
        admin1 = User(username='admin1', email='admin1@cctrs.local', role='admin')
        admin1.set_password('password123')
        admin2 = User(username='admin2', email='admin2@cctrs.local', role='admin')
        admin2.set_password('password123')
        db.session.add_all([admin1, admin2])
        db.session.flush()

        # ── Supervisor ───────────────────────────────────────────────────────
        print("Creating supervisors...")
        sup1 = User(username='supervisor1', email='sup1@cctrs.local',
                    role='supervisor', department_id=depts['Public Works'].id)
        sup1.set_password('password123')
        sup2 = User(username='supervisor2', email='sup2@cctrs.local',
                    role='supervisor', department_id=depts['Sanitation'].id)
        sup2.set_password('password123')
        db.session.add_all([sup1, sup2])
        db.session.flush()

        # ── Moderator ────────────────────────────────────────────────────────
        print("Creating moderators...")
        mod1 = User(username='moderator1', email='mod1@cctrs.local', role='moderator')
        mod1.set_password('password123')
        db.session.add(mod1)
        db.session.flush()

        # ── Officers ─────────────────────────────────────────────────────────
        print("Creating officers...")
        officers = []
        officer_data = [
            ('officer1', 'Public Works'), ('officer2', 'Sanitation'),
            ('officer3', 'Health'), ('officer4', 'Traffic'), ('officer5', 'Parks & Rec'),
        ]
        for uname, dept_name in officer_data:
            o = User(username=uname, email=f'{uname}@cctrs.local',
                     role='officer', department_id=depts[dept_name].id)
            o.set_password('password123')
            db.session.add(o)
            officers.append(o)
        db.session.flush()

        # ── Auditor ──────────────────────────────────────────────────────────
        print("Creating auditors...")
        aud1 = User(username='auditor1', email='aud1@cctrs.local', role='auditor')
        aud1.set_password('password123')
        db.session.add(aud1)
        db.session.flush()

        # ── Citizens ─────────────────────────────────────────────────────────
        print("Creating citizens...")
        citizens = []
        for i in range(1, 8):
            c = User(username=f'citizen{i}', email=f'citizen{i}@cctrs.local', role='citizen')
            c.set_password('password123')
            db.session.add(c)
            citizens.append(c)
        db.session.flush()
        print(f"  → 7 citizens created")

        # ── Complaints (one per lifecycle stage) ─────────────────────────────
        print("Creating sample complaints...")
        staff = [admin1, mod1, sup1, sup2] + officers

        complaint_data = [
            # (title, description, citizen, dept, status_chain)
            ("Pothole on Main St",  "Large pothole causing accidents.",        citizens[0], depts['Public Works'],
             []),  # stays Draft

            ("Broken Street Light", "No light at the intersection.",           citizens[1], depts['Traffic'],
             [('Submitted', 'Citizen submitted')]),

            ("Overflowing Bins",    "Garbage bins not emptied for 2 weeks.",   citizens[2], depts['Sanitation'],
             [('Submitted', 'Citizen submitted'), ('Flagged', 'Duplicate complaint')]),

            ("Contaminated Water",  "Water has unusual smell from tap.",       citizens[3], depts['Health'],
             [('Submitted', 'Citizen submitted'), ('Under Review', 'Verified by moderator')]),

            ("Fallen Tree",         "Tree blocks road after storm.",           citizens[4], depts['Public Works'],
             [('Submitted', ''), ('Under Review', 'Verified'), ('Assigned', 'Handed to officer1')]),

            ("Park Vandalism",      "Benches in Central Park damaged.",        citizens[5], depts['Parks & Rec'],
             [('Submitted', ''), ('Under Review', ''), ('Assigned', ''),
              ('In Progress', 'Officer investigating')]),

            ("Road Flooding",       "Water accumulates on Junction Rd.",       citizens[6], depts['Public Works'],
             [('Submitted', ''), ('Under Review', ''), ('Assigned', ''),
              ('In Progress', ''), ('On Hold', 'Waiting for materials')]),

            ("Mosquito Infestation","Standing water breeding mosquitoes.",     citizens[0], depts['Health'],
             [('Submitted', ''), ('Under Review', ''), ('Assigned', ''),
              ('In Progress', ''), ('Escalated', 'No action for 3 weeks — escalated by supervisor')]),

            ("Traffic Signal Fault","Signal stuck on red for 30 mins.",       citizens[1], depts['Traffic'],
             [('Submitted', ''), ('Under Review', ''), ('Assigned', ''),
              ('In Progress', ''), ('Resolved', 'Signal repaired by tech team')]),

            ("Illegal Dumping",     "Dumping near river bank.",               citizens[2], depts['Sanitation'],
             [('Submitted', ''), ('Flagged', 'Spam — no location provided'), ('Closed', 'Closed after flag')]),

            ("Burst Water Pipe",    "Water pipe burst on Oak Ave.",           citizens[3], depts['Public Works'],
             [('Submitted', ''), ('Under Review', ''), ('Assigned', ''), ('In Progress', ''),
              ('Resolved', 'Pipe repaired'), ('Closed', 'Citizen confirmed resolution')]),

            ("Unlicensed Vendor",   "Vendor operating without permit.",       citizens[4], depts['Health'],
             [('Submitted', ''), ('Under Review', ''), ('Rejected', 'Out of department scope')]),

            ("Graffiti on Wall",    "Offensive graffiti near school.",        citizens[5], depts['Parks & Rec'],
             [('Submitted', ''), ('Under Review', ''), ('Rejected', ''), ('Closed', 'Closed')]),
        ]

        created_complaints = []
        for title, desc, citizen, dept, chain in complaint_data:
            c_obj = Complaint(
                title=title,
                description=desc,
                citizen_id=citizen.id,
                department_id=dept.id,
                current_status='Draft',
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 30)),
                updated_at=datetime.utcnow() - timedelta(days=random.randint(0, 5))
            )
            db.session.add(c_obj)
            db.session.flush()

            if chain:
                # First transition from Draft to Submitted
                hist = StatusHistory(
                    complaint_id=c_obj.id,
                    previous_status='Draft',
                    new_status=chain[0][0],
                    changed_by_user_id=citizen.id,
                    notes=chain[0][1] or 'Complaint submitted.'
                )
                db.session.add(hist)
                c_obj.current_status = chain[0][0]

                for prev_s, (new_s, notes) in zip(chain, chain[1:]):
                    actor = mod1 if new_s in ('Flagged', 'Under Review') else \
                            (sup1 if new_s == 'Escalated' else random.choice(officers + [admin1]))
                    h = StatusHistory(
                        complaint_id=c_obj.id,
                        previous_status=prev_s[0],
                        new_status=new_s,
                        changed_by_user_id=actor.id,
                        notes=notes or f'Moved to {new_s}.'
                    )
                    db.session.add(h)
                    c_obj.current_status = new_s

            created_complaints.append(c_obj)

        db.session.flush()

        # Assign officers to mid-late stage complaints
        for comp in created_complaints:
            if comp.current_status in ('Assigned', 'In Progress', 'On Hold', 'Escalated', 'Resolved'):
                dept_officer = next(
                    (o for o in officers if o.department_id == comp.department_id), None
                )
                if dept_officer:
                    comp.assigned_officer_id = dept_officer.id

        db.session.commit()

        # Count per status
        from collections import Counter
        status_counts = Counter(c.current_status for c in created_complaints)

        print(f"  → {len(created_complaints)} complaints created (covering all 11 stages)")
        print("\n" + "="*60)
        print("  DATABASE SEEDED SUCCESSFULLY (7-Role RBAC + 11 Stages)")
        print("="*60)
        print("\nTest Credentials (password: password123)")
        print("-"*44)
        print("  Admin      : admin1, admin2")
        print("  Supervisors: supervisor1 (Public Works), supervisor2 (Sanitation)")
        print("  Moderator  : moderator1")
        print("  Officers   : officer1–officer5 (one per department)")
        print("  Auditor    : auditor1")
        print("  Citizens   : citizen1–citizen7")
        print("\nComplaint Stages Covered:")
        for status in ['Draft', 'Submitted', 'Flagged', 'Under Review', 'Assigned',
                       'In Progress', 'On Hold', 'Escalated', 'Resolved', 'Rejected', 'Closed']:
            print(f"  {status:<16}: {status_counts.get(status, 0)}")
        print("\nPublic Stats: http://localhost:5000/public  (no login needed)")
        print("="*60)

if __name__ == '__main__':
    seed()
