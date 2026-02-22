# Software Requirement Engineering (SRE) - Civic Complaint Tracking System

## 1. Introduction
The Civic Complaint Tracking System (CCTS) is a comprehensive web platform designed to streamline the reporting, tracking, and resolution of civic issues. From an SRE perspective, the system bridges the gap between citizens and municipal authorities by providing a structured, 11-stage workflow for complaint management.

## 2. User Roles and Access Control (RBAC)
The system employs a 7-Role Role-Based Access Control (RBAC) mechanism to ensure proper separation of duties:
1. **Admin**: Full system access, user management, and department control.
2. **Supervisor**: Department oversight, evaluating officer workload, and handling escalated complaints.
3. **Moderator**: Verification queue management (verifying or flagging incoming submissions).
4. **Officer**: Active resolution of complaints (In Progress, On Hold, Resolved).
5. **Auditor**: Read-only oversight across all departments for transparency.
6. **Citizen**: Ability to draft, submit, track, and provide feedback on complaints.
7. **Guest**: Access to public statistics and anonymized data without logging in.

## 3. Functional Requirements
- **Authentication:** Secure login and registration for all user types.
- **Complaint Management:** Citizens must be able to draft, save, submit, and attach evidence (Files/Images/Location) to complaints.
- **Moderation Queue:** System must route new complaints to a moderation stage before officer assignment.
- **Lifecycle Tracking:** Complaints must follow a strict 11-stage lifecycle (Draft → Submitted → Under Review → Assigned → In Progress → Resolved/Rejected → Closed, etc.).
- **Dashboard & Analytics:** System must provide role-specific dashboards with filtering, search (DataTables), and visual analytics (Chart.js).
- **Notifications & Audit:** System must alert users of status changes and maintain a rigid, timestamped audit trail of all transitions.

## 4. Non-Functional Requirements
- **Security:** Password hashing (Werkzeug), session security (Flask-Login), and route-level role verification.
- **Usability:** Intuitive interfaces providing clear feedback to users.
- **Reliability:** Data integrity ensured by transactional database updates.
- **Scalability:** Modular MVC architecture via Flask Blueprints allows the system to expand to incorporate new departments or roles.

## 5. System Architecture
The application is built on the Model-View-Controller (MVC) architectural pattern:
- **Model:** SQLAlchemy ORM managing entities like Users, Departments, and Complaints.
- **View:** Jinja2 templates returning dynamic HTML with Bootstrap 5.
- **Controller:** Flask routing logic handling HTTP requests, authentication, and business rules (e.g., validating allowed status transitions).
