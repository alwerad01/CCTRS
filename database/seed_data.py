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
    # Accept --yes / -y flag for non-interactive environments (e.g. Render CI)
    auto_confirm = '--yes' in sys.argv or '-y' in sys.argv

    print("\nInitializing database with sample data (7-Role RBAC + 11 Stages)..\n")
    print("WARNING: This will delete all existing data!\n")

    if auto_confirm:
        print("Auto-confirmed via --yes flag.\n")
    else:
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
            'Public Health': Department(
                name='Public Health',
                description='Ensures hospitals and clinics are functional, manages disease outbreaks, and monitors water contamination.'),
            'Parks & Recreation': Department(
                name='Parks & Recreation',
                description='Maintains public parks, playgrounds, and recreational facilities; manages greenery and public events.'),
            'Public Works': Department(
                name='Public Works',
                description='Handles roads, street lights, drainage systems, and public building maintenance.'),
            'Sanitation': Department(
                name='Sanitation',
                description='Manages garbage collection, street cleaning, and sewer maintenance.'),
            'Traffic': Department(
                name='Traffic',
                description='Oversees traffic signals, road signage, accident response, and public transport issues.'),
            'Water & Sewerage': Department(
                name='Water & Sewerage',
                description='Provides clean water supply, fixes leakages, and maintains sewerage systems.'),
            'Electricity': Department(
                name='Electricity',
                description='Handles power outages, street lighting, and transformer issues.'),
            'Local Police': Department(
                name='Local Police',
                description='Ensures neighbourhood safety, addresses non-emergency complaints, and promotes public security.'),
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

        # ── Supervisors (one per key dept) ───────────────────────────────────
        print("Creating supervisors...")
        sup1 = User(username='supervisor1', email='sup1@cctrs.local',
                    role='supervisor', department_id=depts['Public Works'].id)
        sup1.set_password('password123')
        sup2 = User(username='supervisor2', email='sup2@cctrs.local',
                    role='supervisor', department_id=depts['Sanitation'].id)
        sup2.set_password('password123')
        sup3 = User(username='supervisor3', email='sup3@cctrs.local',
                    role='supervisor', department_id=depts['Public Health'].id)
        sup3.set_password('password123')
        sup4 = User(username='supervisor4', email='sup4@cctrs.local',
                    role='supervisor', department_id=depts['Traffic'].id)
        sup4.set_password('password123')
        db.session.add_all([sup1, sup2, sup3, sup4])
        db.session.flush()

        # ── Moderator ────────────────────────────────────────────────────────
        print("Creating moderators...")
        mod1 = User(username='moderator1', email='mod1@cctrs.local', role='moderator')
        mod1.set_password('password123')
        db.session.add(mod1)
        db.session.flush()

        # ── Officers (one per dept) ───────────────────────────────────────────
        print("Creating officers...")
        officers = []
        officer_data = [
            ('officer1', 'Public Works'),
            ('officer2', 'Sanitation'),
            ('officer3', 'Public Health'),
            ('officer4', 'Traffic'),
            ('officer5', 'Parks & Recreation'),
            ('officer6', 'Water & Sewerage'),
            ('officer7', 'Electricity'),
            ('officer8', 'Local Police'),
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

            # Draft
            ("Pothole on Main St", "Large pothole causing vehicle damage and accidents.",
             citizens[0], depts['Public Works'], []),

            # Submitted
            ("Broken Street Light", "Street light at Junction Rd has been out for 5 days.",
             citizens[1], depts['Traffic'], [('Submitted', 'Citizen submitted')]),

            # Flagged
            ("Overflowing Bins", "Garbage bins near market not emptied for 2 weeks.",
             citizens[2], depts['Sanitation'],
             [('Submitted', 'Citizen submitted'), ('Flagged', 'Duplicate complaint — already logged')]),

            # Under Review
            ("Contaminated Water Supply", "Tap water has unusual smell and brown colour.",
             citizens[3], depts['Water & Sewerage'],
             [('Submitted', 'Citizen submitted'), ('Under Review', 'Verified by moderator')]),

            # Assigned
            ("Fallen Tree on Road", "Large tree blocking main road after storm.",
             citizens[4], depts['Public Works'],
             [('Submitted', ''), ('Under Review', 'Verified'), ('Assigned', 'Handed to officer1')]),

            # In Progress
            ("Park Vandalism", "Benches and play equipment in Central Park damaged.",
             citizens[5], depts['Parks & Recreation'],
             [('Submitted', ''), ('Under Review', ''), ('Assigned', ''),
              ('In Progress', 'Officer investigating and scheduling repairs')]),

            # On Hold
            ("Road Flooding", "Water accumulates on Junction Rd after every rain.",
             citizens[6], depts['Public Works'],
             [('Submitted', ''), ('Under Review', ''), ('Assigned', ''),
              ('In Progress', ''), ('On Hold', 'Waiting for drainage materials')]),

            # Escalated
            ("Mosquito Infestation", "Standing water near Block 5 breeding mosquitoes.",
             citizens[0], depts['Public Health'],
             [('Submitted', ''), ('Under Review', ''), ('Assigned', ''),
              ('In Progress', ''), ('Escalated', 'No action for 3 weeks — escalated by supervisor')]),

            # Resolved
            ("Traffic Signal Fault", "Signal stuck on red at Main Chowk for over 30 mins.",
             citizens[1], depts['Traffic'],
             [('Submitted', ''), ('Under Review', ''), ('Assigned', ''),
              ('In Progress', ''), ('Resolved', 'Signal repaired by technical team')]),

            # Flagged → Closed
            ("Illegal Dumping", "Large quantities of waste dumped near the river bank.",
             citizens[2], depts['Sanitation'],
             [('Submitted', ''), ('Flagged', 'No specific location provided — marked invalid'),
              ('Closed', 'Closed after flag')]),

            # Fully Closed (Resolved → Closed)
            ("Burst Water Pipe", "Water pipe burst on Oak Avenue flooding the street.",
             citizens[3], depts['Water & Sewerage'],
             [('Submitted', ''), ('Under Review', ''), ('Assigned', ''), ('In Progress', ''),
              ('Resolved', 'Pipe repaired and road restored'), ('Closed', 'Citizen confirmed resolution')]),

            # Rejected
            ("Power Outage Block 9", "Electricity has been cut in Block 9 for 8 hours.",
             citizens[4], depts['Electricity'],
             [('Submitted', ''), ('Under Review', ''), ('Rejected', 'Outage already reported and scheduled for repair')]),

            # Rejected → Closed
            ("Suspicious Persons", "Unidentified individuals loitering near school.",
             citizens[5], depts['Local Police'],
             [('Submitted', ''), ('Under Review', ''), ('Rejected', 'Referred to emergency services'),
              ('Closed', 'Closed')]),
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
        print("  Admin       : admin1, admin2")
        print("  Supervisors : supervisor1 (Public Works), supervisor2 (Sanitation)")
        print("                supervisor3 (Public Health), supervisor4 (Traffic)")
        print("  Moderator   : moderator1")
        print("  Officers    : officer1-officer8 (one per department)")
        print("  Auditor     : auditor1")
        print("  Citizens    : citizen1-citizen7")
        print("\nDepartments (8):")
        for d in depts.values():
            print(f"  • {d.name}")
        print("\nComplaint Stages Covered:")
        for status in ['Draft', 'Submitted', 'Flagged', 'Under Review', 'Assigned',
                       'In Progress', 'On Hold', 'Escalated', 'Resolved', 'Rejected', 'Closed']:
            print(f"  {status:<16}: {status_counts.get(status, 0)}")
        print("\nPublic Stats: http://localhost:5000/public  (no login needed)")
        print("="*60)

if __name__ == '__main__':
    seed()
