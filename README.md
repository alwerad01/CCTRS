# Civic Complaint Tracking & Resolution System

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/alwerad01/CCTRS)

## 🚀 Quick Deploy Options

### Option 1: Render.com (Permanent Free Link)
1. Create account at [Render.com](https://render.com)
2. Click **New** → **Web Service**
3. Connect your GitHub repository
4. Configure:
   - **Build Command**: `pip install -r requirements.txt && python database/seed_data.py`
   - **Start Command**: `gunicorn app:app`
5. Add Environment Variables from `.env.example`
6. Click **Create** → Your app will be live at `https://your-app.onrender.com`

### Option 2: GitHub Codespaces (Quick Testing)
1. Click the badge above
2. Wait for setup → Run: `python app.py`
3. Go to **PORTS** tab → Make port 5000 **Public**
4. Share the forwarded URL for mobile testing

---

## 🌟 Features

### For Citizens
- ✅ User registration and authentication
- ✅ Submit complaints with title, description, and department selection
- ✅ Track complaint status in real-time
- ✅ View complete status history and timeline
- ✅ Dashboard with complaint statistics

### For Officers
- ✅ View complaints assigned to their department
- ✅ Update complaint status: Received → In Progress → Resolved
- ✅ Add notes for each status change
- ✅ Department-specific dashboard

### For Administrators
- ✅ User management (Create, Read, Delete)
- ✅ Department management (Create, Read, Delete)
- ✅ Comprehensive reports and analytics
- ✅ Visual charts using Chart.js
- ✅ View all complaints across departments
- ✅ Average resolution time calculation

## 🛠️ Tech Stack

- **Backend:** Python 3.8+ with Flask
- **Database:** SQLite (easily switchable to MySQL/PostgreSQL)
- **Frontend:** HTML5, Bootstrap 5, Vanilla JavaScript
- **Charts:** Chart.js
- **Authentication:** Flask-Login with password hashing
- **ORM:** SQLAlchemy

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git (for version control)

## 🚀 Installation & Setup

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd "Civic Complaint"
```

### 2. Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Copy the example environment file:
```bash
copy .env.example .env    # Windows
cp .env.example .env      # macOS/Linux
```

Edit `.env` and update if needed (defaults work for SQLite):
```
SECRET_KEY=your-secret-key-change-in-production
DATABASE_URL=sqlite:///civic_complaints.db
```

### 5. Initialize Database

Run the seed script to create tables and add sample data:

```bash
python database/seed_data.py
```

When prompted, type `yes` to confirm.

### 6. Run the Application

```bash
python app.py
```

The server will start on `http://localhost:5000`

## 🔐 Default Login Credentials

After seeding the database, use these credentials to log in:

| Role    | Username | Password    |
|---------|----------|-------------|
| Admin   | admin1   | password123 |
| Officer | officer1 | password123 |
| Citizen | citizen1 | password123 |

**Note:** Change these passwords after first login in production!

## 📁 Project Structure

```
Civic Complaint/
│
├── app/
│   ├── __init__.py           # Flask app factory
│   ├── models.py             # Database models
│   │
│   ├── routes/
│   │   ├── auth.py           # Authentication routes
│   │   ├── citizen.py        # Citizen routes
│   │   ├── officer.py        # Officer routes
│   │   └── admin.py          # Admin routes
│   │
│   ├── templates/
│   │   ├── base.html         # Base template
│   │   ├── auth/             # Login & registration
│   │   ├── citizen/          # Citizen templates
│   │   ├── officer/          # Officer templates
│   │   ├── admin/            # Admin templates
│   │   └── errors/           # Error pages (403, 404, 500)
│   │
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css     # Custom styles
│   │   └── js/
│   │       └── main.js       # Custom JavaScript
│   │
│   └── utils/
│       └── decorators.py     # Authorization decorators
│
├── database/
│   ├── schema.sql            # MySQL schema (optional)
│   └── seed_data.py          # Database seeding script
│
├── app.py                    # Application entry point
├── config.py                 # Configuration settings
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variables template
├── .gitignore                # Git ignore file
└── README.md                 # This file
```

## 🗄️ Database Schema

### Tables

1. **users**: User accounts (citizens, officers, admins)
2. **departments**: Government departments
3. **complaints**: Citizen complaints
4. **status_history**: Audit trail of status changes

### Relationships

- User → Complaints (one-to-many)
- User → Assigned Complaints as Officer (one-to-many)
- Department → Complaints (one-to-many)
- Department → Officers (one-to-many)
- Complaint → Status History (one-to-many)

## 🔧 Using MySQL Instead of SQLite

### 1. Install MySQL Connector

```bash
pip install pymysql
```

### 2. Create MySQL Database

```bash
mysql -u root -p
CREATE DATABASE civic_complaints CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Or run the schema file:
```bash
mysql -u root -p < database/schema.sql
```

### 3. Update .env File

```
DATABASE_URL=mysql+pymysql://username:password@localhost/civic_complaints
```

### 4. Run Seed Script

```bash
python database/seed_data.py
```

## 🌐 Deployment

### Deploy to Render

1. Create account on [Render.com](https://render.com)
2. Create new Web Service
3. Connect your GitHub repository
4. Set environment variables in Render dashboard
5. Deploy!

### Deploy to PythonAnywhere

1. Upload files to PythonAnywhere
2. Create virtual environment on server
3. Install dependencies: `pip install -r requirements.txt`
4. Configure WSGI file to point to `app`
5. Reload web app

### Environment Variables for Production

```
SECRET_KEY=<generate-strong-random-key>
FLASK_ENV=production
DATABASE_URL=<your-production-database-url>
```

## 📊 Features Walkthrough

### Citizen Workflow

1. Register account → Login
2. Submit complaint with title, description, department
3. View dashboard showing complaint statistics
4. Track complaint status and view history

### Officer Workflow

1. Login with officer credentials
2. View all complaints for assigned department
3. Click on complaint to view details
4. Update status: Received → In Progress → Resolved
5. Add notes explaining actions taken

### Admin Workflow

1. Login with admin credentials
2. View dashboard with charts and statistics
3. Manage users: Add officers, delete users
4. Manage departments: Add/remove departments
5. Generate reports:
   - Unresolved complaints
   - Resolution time analysis
   - Department-wise breakdown

## 🛡️ Security Features

- ✅ Password hashing with werkzeug.security
- ✅ Session-based authentication via Flask-Login
- ✅ Role-based access control with decorators
- ✅ CSRF protection (Flask default)
- ✅ SQL injection prevention (SQLAlchemy ORM)
- ✅ Form validation (client & server-side)

## 🧪 Testing

To test the application:

1. **Registration:** Create new citizen account
2. **Login:** Test all three role types
3. **Complaint Submission:** Submit test complaint
4. **Status Updates:** Log in as officer and update status
5. **Admin Functions:** Manage users and departments
6. **Reports:** Verify statistics are accurate

## 📝 Notes for University PBL

### Project Highlights for Presentation

- **Full-Stack:** Complete backend + frontend
- **Database Design:** Proper normalization and relationships
- **Security:** Authentication, authorization, password hashing
- **Audit Trail:** Complete status history logging
- **Responsive Design:** Mobile-friendly Bootstrap UI
- **Clean Code:** Well-commented, MVC architecture
- **Scalable:** Easy to add features or switch databases

### Viva Questions You Might Face

1. **Why Flask over Django?** Lightweight, easier to learn, perfect for medium-sized projects
2. **Why SQLite?** Easy setup for development, production can use MySQL/PostgreSQL
3. **How is status validated?** Server-side validation prevents invalid transitions
4. **Security measures?** Password hashing, role-based access, CSRF protection
5. **Database normalization?** Third normal form (3NF) followed

## 🤝 Contributing

This is a university project, but suggestions are welcome!

## 📄 License

Educational project for university PBL.

## 👨‍💻 Author

Created for University PBL Project - 2026

---

## 💡 Future Enhancements (Optional)

- Email notifications for status updates
- File upload for complaint photos
- Mobile app using Flutter/React Native
- SMS alerts via Twilio
- Advanced analytics dashboard
- Multi-language support
- Export reports to PDF/Excel

---

**Need Help?** Check the code comments or create an issue!

**Good luck with your PBL presentation! 🎓**
