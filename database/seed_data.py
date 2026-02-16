"""
Database seed script with sample data for testing
Run this script to initialize the database with test data
"""
import sys
import os

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import User, Department, Complaint

def seed_database():
    """Populate database with sample data"""
    app = create_app('default')
    
    with app.app_context():
        # Drop all tables and recreate (CAUTION: This deletes all data!)
        print("Creating database tables...")
        db.drop_all()
        db.create_all()
        
        # Create Departments
        print("Creating departments...")
        departments = [
            Department(name='Public Works', description='Roads, bridges, and infrastructure'),
            Department(name='Health & Sanitation', description='Public health and waste management'),
            Department(name='Water Supply', description='Water distribution and quality'),
            Department(name='Electricity', description='Power supply and street lights'),
            Department(name='Traffic Management', description='Traffic signals and enforcement')
        ]
        
        for dept in departments:
            db.session.add(dept)
        
        db.session.commit()
        print(f"Created {len(departments)} departments")
        
        # Create Admin Users
        print("Creating admin users...")
        admin1 = User(username='admin1', email='admin1@civic.gov', role='admin')
        admin1.set_password('password123')
        db.session.add(admin1)
        
        admin2 = User(username='admin2', email='admin2@civic.gov', role='admin')
        admin2.set_password('password123')
        db.session.add(admin2)
        
        db.session.commit()
        print("Created 2 admin users")
        
        # Create Officer Users (one per department)
        print("Creating officer users...")
        officers = []
        for i, dept in enumerate(departments, 1):
            officer = User(
                username=f'officer{i}',
                email=f'officer{i}@civic.gov',
                role='officer',
                department_id=dept.id
            )
            officer.set_password('password123')
            db.session.add(officer)
            officers.append(officer)
        
        db.session.commit()
        print(f"Created {len(officers)} officers")
        
        # Create Citizen Users
        print("Creating citizen users...")
        citizens = []
        for i in range(1, 6):
            citizen = User(
                username=f'citizen{i}',
                email=f'citizen{i}@example.com',
                role='citizen'
            )
            citizen.set_password('password123')
            db.session.add(citizen)
            citizens.append(citizen)
        
        db.session.commit()
        print(f"Created {len(citizens)} citizens")
        
        # Create Sample Complaints
        print("Creating sample complaints...")
        complaints_data = [
            {
                'title': 'Potholes on Main Street',
                'description': 'Large potholes have formed on Main Street near the library. This poses a safety hazard to vehicles and pedestrians.',
                'dept_index': 0,  # Public Works
                'citizen_index': 0,
                'status': 'Resolved'
            },
            {
                'title': 'Street light not working',
                'description': 'The street light at the corner of Oak Avenue and 5th Street has not been working for two weeks.',
                'dept_index': 3,  # Electricity
                'citizen_index': 0,
                'status': 'In Progress'
            },
            {
                'title': 'Garbage not collected',
                'description': 'Garbage collection was skipped in our neighborhood last week. Waste is accumulating.',
                'dept_index': 1,  # Health & Sanitation
                'citizen_index': 1,
                'status': 'Received'
            },
            {
                'title': 'Water supply disruption',
                'description': 'No water supply in our area for the past 24 hours. Please send a team to investigate.',
                'dept_index': 2,  # Water Supply
                'citizen_index': 1,
                'status': 'In Progress'
            },
            {
                'title': 'Traffic signal malfunction',
                'description': 'Traffic signal at City Center junction is not working properly, causing traffic jams.',
                'dept_index': 4,  # Traffic
                'citizen_index': 2,
                'status': 'Received'
            },
            {
                'title': 'Broken sidewalk',
                'description': 'The sidewalk on Park Lane is broken and damaged, making it difficult for pedestrians.',
                'dept_index': 0,  # Public Works
                'citizen_index': 2,
                'status': 'Resolved'
            },
            {
                'title': 'Illegal dumping site',
                'description': 'Construction waste is being dumped illegally near the riverside park.',
                'dept_index': 1,  # Health & Sanitation
                'citizen_index': 3,
                'status': 'In Progress'
            },
            {
                'title': 'Leaking water pipe',
                'description': 'Public water pipe is leaking on Elm Street, wasting water continuously.',
                'dept_index': 2,  # Water Supply
                'citizen_index': 3,
                'status': 'Received'
            },
            {
                'title': 'Streetlight timing issue',
                'description': 'Streetlights turn on too late in the evening, creating safety concerns.',
                'dept_index': 3,  # Electricity
                'citizen_index': 4,
                'status': 'Received'
            },
            {
                'title': 'Parking zone markings faded',
                'description': 'Parking zone markings on Commercial Street have completely faded and need repainting.',
                'dept_index': 4,  # Traffic
                'citizen_index': 4,
                'status': 'Resolved'
            },
            {
                'title': 'Bridge repair needed',
                'description': 'The pedestrian bridge over the canal shows signs of structural damage and needs urgent repair.',
                'dept_index': 0,  # Public Works
                'citizen_index': 0,
                'status': 'In Progress'
            },
            {
                'title': 'Stray dogs in residential area',
                'description': 'Large number of stray dogs in Green Valley Colony causing safety issues.',
                'dept_index': 1,  # Health & Sanitation
                'citizen_index': 1,
                'status': 'Received'
            },
            {
                'title': 'Low water pressure',
                'description': 'Very low water pressure in Highland Area, especially during morning hours.',
                'dept_index': 2,  # Water Supply
                'citizen_index': 2,
                'status': 'Resolved'
            },
            {
                'title': 'Power outage frequency',
                'description': 'Frequent power outages in Sector 12, happening almost daily for the past week.',
                'dept_index': 3,  # Electricity
                'citizen_index': 3,
                'status': 'In Progress'
            },
            {
                'title': 'Need speed breaker',
                'description': 'Vehicles speed excessively on School Road. Need speed breakers for child safety.',
                'dept_index': 4,  # Traffic
                'citizen_index': 4,
                'status': 'Received'
            }
        ]
        
        for data in complaints_data:
            complaint = Complaint(
                title=data['title'],
                description=data['description'],
                citizen_id=citizens[data['citizen_index']].id,
                department_id=departments[data['dept_index']].id,
                assigned_officer_id=officers[data['dept_index']].id,
                current_status=data['status']
            )
            db.session.add(complaint)
        
        db.session.commit()
        print(f"Created {len(complaints_data)} sample complaints")
        
        # Create some status history entries for complaints that have progressed
        print("Creating status history...")
        from app.models import StatusHistory
        from datetime import datetime, timedelta
        
        for complaint in Complaint.query.all():
            if complaint.current_status in ['In Progress', 'Resolved']:
                # Add initial status change to In Progress
                history1 = StatusHistory(
                    complaint_id=complaint.id,
                    previous_status='Received',
                    new_status='In Progress',
                    changed_by_user_id=complaint.assigned_officer_id,
                    notes='Complaint acknowledged. Team assigned to investigate.',
                    changed_at=complaint.created_at + timedelta(hours=2)
                )
                db.session.add(history1)
                
                if complaint.current_status == 'Resolved':
                    # Add resolution
                    history2 = StatusHistory(
                        complaint_id=complaint.id,
                        previous_status='In Progress',
                        new_status='Resolved',
                        changed_by_user_id=complaint.assigned_officer_id,
                        notes='Issue has been fixed. Work completed successfully.',
                        changed_at=complaint.created_at + timedelta(days=2)
                    )
                    db.session.add(history2)
        
        db.session.commit()
        print("Created status history entries")
        
        print("\n" + "="*50)
        print("DATABASE SEEDED SUCCESSFULLY!")
        print("="*50)
        print("\nTest Credentials:")
        print("\nAdmin Login:")
        print("  Username: admin1  |  Password: password123")
        print("\nOfficer Login:")
        print("  Username: officer1  |  Password: password123")
        print("  (officer1 = Public Works, officer2 = Health & Sanitation, etc.)")
        print("\nCitizen Login:")
        print("  Username: citizen1  |  Password: password123")
        print("\nTotal Data Created:")
        print(f"  - Departments: {Department.query.count()}")
        print(f"  - Users: {User.query.count()}")
        print(f"  - Complaints: {Complaint.query.count()}")
        print(f"  - Status History: {StatusHistory.query.count()}")
        print("="*50)

if __name__ == '__main__':
    print("Initializing database with sample data...")
    print("WARNING: This will delete all existing data!\n")
    
    confirm = input("Continue? (yes/no): ")
    if confirm.lower() == 'yes':
        seed_database()
    else:
        print("Aborted.")
