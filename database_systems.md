# Database Systems - Civic Complaint Tracking System

## 1. Relational Database Design & Architecture
The Civic Complaint Tracking System (CCTS) utilizes a relational database management system (RDBMS). It is abstracted behind the SQLAlchemy Object-Relational Mapping (ORM) layer, ensuring data reliability and reducing direct SQL vulnerabilities (like SQL injection). Dev staging uses SQLite, while production environments deploy MySQL/PostgreSQL.

## 2. Entity-Relationship Model (ERD) Structure
The schema is normalized to the 3rd Normal Form (3NF) to eliminate data redundancy and anomalies:
- **USER (1) to COMPLAINT (M)**: A single citizen can submit multiple complaints.
- **DEPARTMENT (1) to OFFICER (M)**: Departments employ multiple officers and supervisors.
- **DEPARTMENT (1) to COMPLAINT (M)**: A department handles multiple complaints.
- **OFFICER (1) to COMPLAINT (M)**: An officer is assigned multiple complaints for resolution.
- **COMPLAINT (1) to STATUS_HISTORY (M)**: Every complaint maintains an aggressive audit log of its status transitions.

## 3. Core Database Entities
### 3.1. Users Table
Handles authentication and RBAC for 7 different roles. 
- **Attributes:** `id` (PK), `username`, `email`, `password_hash`, `role` (Admin, Supervisor, etc.), `department_id` (FK to Departments), and metadata.
- **Indexes:** Indexed heavily on `username` and `role` to optimize frequent login queries.

### 3.2. Departments Table
Stores logical separation of municipal responsibilities.
- **Attributes:** `id` (PK), `name` (e.g., Public Health, Sanitation), `description`, `created_at`.

### 3.3. Complaints Table
The heart of the application with detailed spatial and descriptive attributes.
- **Attributes:** `id` (PK), `title`, `description`, `citizen_id` (FK), `department_id` (FK), `assigned_officer_id` (FK), `current_status` (Enum of 11 stages), `evidence_filename`, `latitude/longitude`, `rating/feedback`.

### 3.4. StatusHistory Table
An append-only table logging all complaint lifecycle transitions for auditing.
- **Attributes:** `id` (PK), `complaint_id` (FK), `previous_status`, `new_status`, `changed_by_user_id` (FK), `changed_at` (Timestamp).

## 4. Query Optimization & Indexing
To ensure rapid dashboard load times across large datasets, Database indexing is heavily applied to:
- Time-series data (`created_at`, `changed_at`) for sorting.
- Foreign Keys (`citizen_id`, `department_id`, `assigned_officer_id`) to speed up inner/outer relational JOIN operations during Dashboard data fetches.
- **Lazy Dynamics:** SQLAlchemy `lazy='dynamic'` is employed on User > Complaint relationships to prevent massive N+1 query fetching during initial record load.
