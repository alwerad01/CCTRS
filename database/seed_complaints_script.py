import sys
import os
import random
from datetime import datetime, timedelta

# Add parent directory to path so we can import app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import User, Department, Complaint, StatusHistory

app = create_app()

def generate_random_date():
    now = datetime.utcnow()
    days_ago = random.randint(1, 30)
    return now - timedelta(days=days_ago, hours=random.randint(1, 23))

seed_data = [
    {
        "title": "Massive pothole on Main Avenue",
        "description": "There is a very deep pothole right in the middle lane of Main Avenue near the intersection. It's causing severe traffic backups and is a hazard to vehicles, especially at night when visibility is low.",
        "status": "In Progress",
        "is_public": True,
        "keywords": ["Road", "Transport", "Infrastructure", "Public Works", "Highway"]
    },
    {
        "title": "Water supply contaminated",
        "description": "The tap water in our block has been coming out brownish for the last two days. It smells foul and is completely unsafe for drinking or washing. We need immediate checking of the local water line.",
        "status": "Submitted",
        "is_public": True,
        "keywords": ["Water", "Sanitation", "Health"]
    },
    {
        "title": "Street lights out for a week",
        "description": "Entire street is dark because the halogen street lamps have burnt out. It feels very unsafe walking home from the bus stop. Please replace the bulbs.",
        "status": "Under Review",
        "is_public": True,
        "keywords": ["Electricity", "Power", "Lighting", "Energy"]
    },
    {
        "title": "Uncollected garbage overflowing",
        "description": "The community dumpsters haven't been cleared for over a week. Trash is spilling onto the pavement and attracting stray animals. The stench is unbearable.",
        "status": "Assigned",
        "is_public": True,
        "keywords": ["Waste", "Sanitation", "Health", "Environment"]
    },
    {
        "title": "Broken swings in neighborhood park",
        "description": "The playground equipment in the community park is severely damaged. Two swings are broken and the slide has a sharp edge. It is dangerous for children.",
        "status": "Resolved",
        "is_public": True,
        "rating": 5,
        "feedback_text": "Thank you for fixing it promptly before the weekend!",
        "keywords": ["Parks", "Recreation", "Community"]
    },
    {
        "title": "Illegal parking blocking sidewalk",
        "description": "Vehicles from the newly opened commercial plaza are consistently parking on the pedestrian sidewalk and blocking the way for wheelchairs and strollers.",
        "status": "Closed",
        "is_public": False,
        "rating": 4,
        "feedback_text": "Good response but still happens occasionally.",
        "keywords": ["Traffic", "Transport", "Police", "Enforcement", "Security"]
    },
    {
        "title": "Manhole cover missing",
        "description": "There is an open manhole on 5th Street. I almost fell into it yesterday. Urgent action is needed as it is a major safety hazard.",
        "status": "Escalated",
        "is_public": True,
        "keywords": ["Road", "Infrastructure", "Sanitation", "Public Works"]
    },
    {
        "title": "Stray dog menace",
        "description": "A pack of aggressive stray dogs has been roaming near the local school, making it dangerous for kids to walk alone.",
        "status": "Submitted",
        "is_public": True,
        "keywords": ["Animal", "Health", "Community"]
    },
    {
        "title": "Noise pollution from construction site at night",
        "description": "The construction site on 12th Avenue is operating heavy machinery well past midnight, violating noise ordinances and disturbing the neighborhood's sleep.",
        "status": "Under Review",
        "is_public": True,
        "keywords": ["Environment", "Police", "Community"]
    },
    {
        "title": "Blocked drainage causing waterlogging",
        "description": "The storm drains are completely clogged with plastic waste. After the light rain yesterday, the entire street is flooded.",
        "status": "Assigned",
        "is_public": True,
        "keywords": ["Water", "Sanitation", "Infrastructure"]
    }
]

with app.app_context():
    # Find a citizen user
    citizen = User.query.filter_by(role='citizen').first()
    if not citizen:
        print("Error: No user with role 'citizen' found. Please register a citizen first.")
        sys.exit(1)
        
    officer = User.query.filter_by(role='officer').first()
        
    departments = Department.query.all()
    if not departments:
        print("Error: No departments found.")
        sys.exit(1)
        
    print(f"Using citizen: {citizen.username} (ID: {citizen.id})")
    
    added_count = 0
    for item in seed_data:
        # Find a suitable department or just pick a random one
        chosen_dept = random.choice(departments)
        for dept in departments:
            if any(k.lower() in dept.name.lower() for k in item["keywords"]):
                chosen_dept = dept
                break
                
        # Base location (example: Islamabad)
        base_lat = 33.6844 + random.uniform(-0.05, 0.05)
        base_lng = 73.0479 + random.uniform(-0.05, 0.05)
        
        complaint = Complaint(
            title=item["title"],
            description=item["description"],
            citizen_id=citizen.id,
            department_id=chosen_dept.id,
            current_status=item["status"],
            latitude=base_lat,
            longitude=base_lng,
            is_public=item.get("is_public", True),
            created_at=generate_random_date()
        )
        
        if complaint.current_status in ['Resolved', 'Closed']:
            complaint.rating = item.get("rating")
            complaint.feedback_text = item.get("feedback_text")
            
        if complaint.current_status not in ['Submitted', 'Draft'] and officer:
            complaint.assigned_officer_id = officer.id
            
        db.session.add(complaint)
        db.session.flush() # get ID
        
        # Add a status history entry
        history1 = StatusHistory(
            complaint_id=complaint.id,
            changed_by_user_id=citizen.id,
            previous_status='Draft',
            new_status='Submitted',
            changed_at=complaint.created_at
        )
        db.session.add(history1)
        
        if complaint.current_status != 'Submitted':
            history2 = StatusHistory(
                complaint_id=complaint.id,
                changed_by_user_id=officer.id if officer else citizen.id,
                previous_status='Submitted',
                new_status=item["status"],
                notes="Status updated after initial review.",
                changed_at=complaint.created_at + timedelta(days=1)
            )
            db.session.add(history2)
        added_count += 1
            
    db.session.commit()
    print(f"Successfully seeded {added_count} realistic complaints into various departments!")
