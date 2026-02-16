# Database Queries Documentation
## Civic Complaint Tracking System

---

## Table of Contents
1. [Overview](#overview)
2. [Citizen Queries](#citizen-queries)
3. [Officer Queries](#officer-queries)
4. [Admin Queries](#admin-queries)
5. [Query Performance Notes](#query-performance-notes)

---

## Overview

This document explains all database queries used in the Civic Complaint Tracking System. Each query is presented with:
- **Purpose**: What the query does
- **ORM Query**: Python SQLAlchemy code used in the application
- **SQL Equivalent**: Equivalent SQL statement
- **Explanation**: How it works step-by-step
- **Example Result**: Sample output

> [!NOTE]
> This system uses **SQLAlchemy ORM** (Object-Relational Mapping) which translates Python code into SQL queries automatically. This makes the code more maintainable and secure.

---

## Citizen Queries

### 1. Get Citizen's Complaint Statistics

**Purpose**: Display dashboard statistics (total, pending, in-progress, resolved complaints)

**File**: [`citizen.py:18-21`](file:///C:/Users/ALWERAD%20KHAN/OneDrive/Desktop/Civic%20Complaint/app/routes/citizen.py#L18-L21)

**ORM Query**:
```python
total_complaints = current_user.complaints.count()
pending = current_user.complaints.filter_by(current_status='Received').count()
in_progress = current_user.complaints.filter_by(current_status='In Progress').count()
resolved = current_user.complaints.filter_by(current_status='Resolved').count()
```

**SQL Equivalent**:
```sql
-- Total complaints
SELECT COUNT(*) 
FROM complaints 
WHERE citizen_id = ?;

-- Pending complaints
SELECT COUNT(*) 
FROM complaints 
WHERE citizen_id = ? AND current_status = 'Received';

-- In Progress complaints
SELECT COUNT(*) 
FROM complaints 
WHERE citizen_id = ? AND current_status = 'In Progress';

-- Resolved complaints
SELECT COUNT(*) 
FROM complaints 
WHERE citizen_id = ? AND current_status = 'Resolved';
```

**Explanation**:
1. Uses the relationship `User.complaints` to access the citizen's complaints
2. `.count()` performs a COUNT(*) aggregation to get the total
3. `.filter_by(current_status='...')` adds a WHERE clause to filter by status
4. Each query runs independently to get counts for different statuses

**Example Result**:
- `total_complaints = 5`
- `pending = 2`
- `in_progress = 1`
- `resolved = 2`

---

### 2. Get Recent Complaints for Citizen

**Purpose**: Show the 5 most recent complaints on the citizen dashboard

**File**: [`citizen.py:24`](file:///C:/Users/ALWERAD%20KHAN/OneDrive/Desktop/Civic%20Complaint/app/routes/citizen.py#L24)

**ORM Query**:
```python
recent_complaints = current_user.complaints.order_by(Complaint.created_at.desc()).limit(5).all()
```

**SQL Equivalent**:
```sql
SELECT * 
FROM complaints 
WHERE citizen_id = ? 
ORDER BY created_at DESC 
LIMIT 5;
```

**Explanation**:
1. Access citizen's complaints through the relationship
2. `.order_by(Complaint.created_at.desc())` sorts by creation date (newest first)
3. `.limit(5)` restricts results to 5 records
4. `.all()` executes the query and returns a list of Complaint objects

**Example Result**:
```
[Complaint #15, Complaint #12, Complaint #10, Complaint #8, Complaint #5]
```

---

### 3. Submit New Complaint

**Purpose**: Insert a new complaint into the database

**File**: [`citizen.py:62-71`](file:///C:/Users/ALWERAD%20KHAN/OneDrive/Desktop/Civic%20Complaint/app/routes/citizen.py#L62-L71)

**ORM Query**:
```python
complaint = Complaint(
    title=title,
    description=description,
    citizen_id=current_user.id,
    department_id=int(department_id),
    current_status='Received'
)
db.session.add(complaint)
db.session.commit()
```

**SQL Equivalent**:
```sql
INSERT INTO complaints (title, description, citizen_id, department_id, current_status, created_at, updated_at)
VALUES (?, ?, ?, ?, 'Received', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);
```

**Explanation**:
1. Create a new `Complaint` object with the form data
2. Set `current_status` to 'Received' by default
3. `db.session.add()` stages the object for insertion
4. `db.session.commit()` executes the INSERT statement
5. The database auto-generates `id`, `created_at`, and `updated_at`

**Example Result**:
```
New complaint created with ID: 16
```

---

### 4. View All Citizen Complaints

**Purpose**: Display all complaints submitted by the logged-in citizen

**File**: [`citizen.py:85`](file:///C:/Users/ALWERAD%20KHAN/OneDrive/Desktop/Civic%20Complaint/app/routes/citizen.py#L85)

**ORM Query**:
```python
complaints = current_user.complaints.order_by(Complaint.created_at.desc()).all()
```

**SQL Equivalent**:
```sql
SELECT * 
FROM complaints 
WHERE citizen_id = ? 
ORDER BY created_at DESC;
```

**Explanation**:
1. Uses the `User.complaints` relationship (defined in models)
2. Orders by newest complaints first
3. Returns all matching records (no limit)

---

### 5. Get Complaint Details with Status History

**Purpose**: Show full complaint details including all status changes

**File**: [`citizen.py:93-101`](file:///C:/Users/ALWERAD%20KHAN/OneDrive/Desktop/Civic%20Complaint/app/routes/citizen.py#L93-L101)

**ORM Query**:
```python
complaint = Complaint.query.get_or_404(complaint_id)
history = complaint.status_history.all()
```

**SQL Equivalent**:
```sql
-- Get complaint
SELECT * 
FROM complaints 
WHERE id = ?;

-- Get status history
SELECT * 
FROM status_history 
WHERE complaint_id = ? 
ORDER BY changed_at DESC;
```

**Explanation**:
1. `.get_or_404()` retrieves the complaint by ID or returns 404 error if not found
2. `complaint.status_history` uses the relationship to get related history records
3. The relationship is automatically ordered by `changed_at DESC` (defined in models)
4. `.all()` executes and returns a list of StatusHistory objects

---

## Officer Queries

### 6. Get Department Complaints

**Purpose**: Show all complaints assigned to the officer's department

**File**: [`officer.py:22-23`](file:///C:/Users/ALWERAD%20KHAN/OneDrive/Desktop/Civic%20Complaint/app/routes/officer.py#L22-L23)

**ORM Query**:
```python
complaints = Complaint.query.filter_by(department_id=current_user.department_id)\
                            .order_by(Complaint.created_at.desc()).all()
```

**SQL Equivalent**:
```sql
SELECT * 
FROM complaints 
WHERE department_id = ? 
ORDER BY created_at DESC;
```

**Explanation**:
1. `.filter_by(department_id=...)` filters complaints for the officer's department
2. Orders by creation date (newest first)
3. Returns all complaints (for dashboard display)

**Example Result**:
```
Officer in "Public Works" department sees:
- Complaint #15: Bridge repair needed
- Complaint #12: Potholes on Main Street
- Complaint #8: Broken sidewalk
```

---

### 7. Update Complaint Status with History

**Purpose**: Change complaint status and record the change in status history

**File**: [`officer.py:76-82`](file:///C:/Users/ALWERAD%20KHAN/OneDrive/Desktop/Civic%20Complaint/app/routes/officer.py#L76-L82) and [`models.py:76-105`](file:///C:/Users/ALWERAD%20KHAN/OneDrive/Desktop/Civic%20Complaint/app/models.py#L76-L105)

**ORM Query**:
```python
# Assign officer if not assigned
if not complaint.assigned_officer_id:
    complaint.assigned_officer_id = current_user.id

# Update status (calls method in models.py)
complaint.update_status(new_status, current_user, notes)
db.session.commit()
```

**Inside `update_status()` method**:
```python
# Create history record
history = StatusHistory(
    complaint_id=self.id,
    previous_status=self.current_status,
    new_status=new_status,
    changed_by_user_id=changed_by_user.id,
    notes=notes
)
db.session.add(history)

# Update complaint status
self.current_status = new_status
self.updated_at = datetime.utcnow()
```

**SQL Equivalent**:
```sql
-- Update officer assignment
UPDATE complaints 
SET assigned_officer_id = ? 
WHERE id = ? AND assigned_officer_id IS NULL;

-- Insert status history
INSERT INTO status_history (complaint_id, previous_status, new_status, changed_by_user_id, notes, changed_at)
VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP);

-- Update complaint status
UPDATE complaints 
SET current_status = ?, updated_at = CURRENT_TIMESTAMP 
WHERE id = ?;
```

**Explanation**:
1. First checks if officer is assigned, assigns current officer if not
2. Creates a StatusHistory record to log the change
3. Updates the complaint's current_status
4. Updates the updated_at timestamp
5. All operations are wrapped in a transaction (committed together)

**Example**:
```
Officer changes status from "Received" to "In Progress":
- Creates StatusHistory: Received → In Progress (with notes)
- Updates Complaint.current_status = "In Progress"
- Updates Complaint.updated_at = now
- Updates Complaint.assigned_officer_id = officer's ID
```

---

## Admin Queries

### 8. Dashboard Statistics

**Purpose**: Show high-level statistics for the entire system

**File**: [`admin.py:20-23`](file:///C:/Users/ALWERAD%20KHAN/OneDrive/Desktop/Civic%20Complaint/app/routes/admin.py#L20-L23)

**ORM Query**:
```python
total_complaints = Complaint.query.count()
total_users = User.query.count()
total_departments = Department.query.count()
unresolved = Complaint.query.filter(Complaint.current_status != 'Resolved').count()
```

**SQL Equivalent**:
```sql
SELECT COUNT(*) FROM complaints;
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM departments;
SELECT COUNT(*) FROM complaints WHERE current_status != 'Resolved';
```

**Explanation**:
Simple COUNT queries on each table to get totals. The unresolved count uses a WHERE clause to exclude resolved complaints.

---

### 9. Complaints by Department (Chart Data)

**Purpose**: Generate data for pie/bar charts showing complaint distribution across departments

**File**: [`admin.py:26-32`](file:///C:/Users/ALWERAD%20KHAN/OneDrive/Desktop/Civic%20Complaint/app/routes/admin.py#L26-L32)

**ORM Query**:
```python
dept_stats = db.session.query(
    Department.name,
    func.count(Complaint.id).label('count')
).join(Complaint).group_by(Department.name).all()

dept_labels = [stat[0] for stat in dept_stats]
dept_counts = [stat[1] for stat in dept_stats]
```

**SQL Equivalent**:
```sql
SELECT departments.name, COUNT(complaints.id) AS count
FROM departments
JOIN complaints ON departments.id = complaints.department_id
GROUP BY departments.name;
```

**Explanation**:
1. `db.session.query()` creates a custom query (not using ORM models)
2. Selects department name and count of complaints
3. `.join(Complaint)` joins with complaints table
4. `.group_by(Department.name)` groups results by department
5. Returns tuples like `[('Public Works', 25), ('Water Supply', 18), ...]`

**Example Result**:
```python
dept_labels = ['Public Works', 'Water Supply', 'Electricity', 'Health & Sanitation', 'Traffic']
dept_counts = [25, 18, 15, 22, 10]
```

---

### 10. Recent Complaints (Admin View)

**Purpose**: Show the 10 most recent complaints across all departments

**File**: [`admin.py:35`](file:///C:/Users/ALWERAD%20KHAN/OneDrive/Desktop/Civic%20Complaint/app/routes/admin.py#L35)

**ORM Query**:
```python
recent_complaints = Complaint.query.order_by(Complaint.created_at.desc()).limit(10).all()
```

**SQL Equivalent**:
```sql
SELECT * 
FROM complaints 
ORDER BY created_at DESC 
LIMIT 10;
```

**Explanation**:
Simple query to get the 10 newest complaints system-wide (no filtering by department or citizen).

---

### 11. User Management Queries

**Purpose**: List, add, and delete users

**File**: [`admin.py:53, 92-101, 122-123`](file:///C:/Users/ALWERAD%20KHAN/OneDrive/Desktop/Civic%20Complaint/app/routes/admin.py#L53)

**ORM Queries**:
```python
# List all users
users = User.query.order_by(User.created_at.desc()).all()

# Add new user
new_user = User(username=username, email=email, role=role, department_id=department_id)
new_user.set_password(password)
db.session.add(new_user)
db.session.commit()

# Delete user
user = User.query.get_or_404(user_id)
db.session.delete(user)
db.session.commit()
```

**SQL Equivalent**:
```sql
-- List users
SELECT * FROM users ORDER BY created_at DESC;

-- Add user
INSERT INTO users (username, email, password_hash, role, department_id, created_at)
VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP);

-- Delete user
DELETE FROM users WHERE id = ?;
```

**Explanation**:
Standard CRUD (Create, Read, Update, Delete) operations on the users table.

---

### 12. Department Management Queries

**Purpose**: List, add, and delete departments

**File**: [`admin.py:135, 155-157, 177-178`](file:///C:/Users/ALWERAD%20KHAN/OneDrive/Desktop/Civic%20Complaint/app/routes/admin.py#L135)

**ORM Queries**:
```python
# List departments
departments = Department.query.all()

# Add department
new_dept = Department(name=name, description=description)
db.session.add(new_dept)
db.session.commit()

# Delete department (with validation)
dept = Department.query.get_or_404(dept_id)
if dept.complaints.count() > 0:
    # Error: cannot delete
db.session.delete(dept)
db.session.commit()
```

**SQL Equivalent**:
```sql
-- List departments
SELECT * FROM departments;

-- Add department
INSERT INTO departments (name, description, created_at)
VALUES (?, ?, CURRENT_TIMESTAMP);

-- Check if department has complaints
SELECT COUNT(*) FROM complaints WHERE department_id = ?;

-- Delete department
DELETE FROM departments WHERE id = ?;
```

**Explanation**:
1. List query retrieves all departments
2. Add creates a new department with name and description
3. Delete first checks if department has complaints (business rule: cannot delete if complaints exist)
4. If safe, deletes the department

---

### 13. Reports - Unresolved Complaints

**Purpose**: Generate report of all unresolved complaints (for admin action)

**File**: [`admin.py:191-192`](file:///C:/Users/ALWERAD%20KHAN/OneDrive/Desktop/Civic%20Complaint/app/routes/admin.py#L191-L192)

**ORM Query**:
```python
unresolved_complaints = Complaint.query.filter(Complaint.current_status != 'Resolved')\
                                      .order_by(Complaint.created_at.asc()).all()
```

**SQL Equivalent**:
```sql
SELECT * 
FROM complaints 
WHERE current_status != 'Resolved' 
ORDER BY created_at ASC;
```

**Explanation**:
1. Filters out resolved complaints (keeps Received and In Progress)
2. Orders by oldest first (ascending) to prioritize old complaints
3. Returns all unresolved complaints for admin review

---

### 14. Reports - Average Resolution Time

**Purpose**: Calculate average time (in days) to resolve complaints

**File**: [`admin.py:195-201`](file:///C:/Users/ALWERAD%20KHAN/OneDrive/Desktop/Civic%20Complaint/app/routes/admin.py#L195-L201)

**ORM Query**:
```python
resolved_complaints = Complaint.query.filter_by(current_status='Resolved').all()

if resolved_complaints:
    resolution_times = [c.get_resolution_time() for c in resolved_complaints]
    avg_resolution_time = sum(resolution_times) / len(resolution_times)
```

**Method in `models.py`**:
```python
def get_resolution_time(self):
    if self.current_status == 'Resolved':
        return (self.updated_at - self.created_at).days
    return None
```

**SQL Equivalent**:
```sql
-- Get all resolved complaints
SELECT id, created_at, updated_at 
FROM complaints 
WHERE current_status = 'Resolved';

-- Calculate average in Python (could be done in SQL with AVG and date functions)
```

**Explanation**:
1. Retrieves all resolved complaints
2. For each complaint, calculates `(updated_at - created_at)` in days
3. Computes the average of all resolution times
4. Used for performance metrics

**Example**:
```
Complaint #1: 2 days
Complaint #2: 5 days
Complaint #3: 3 days
Average: (2 + 5 + 3) / 3 = 3.33 days
```

---

### 15. Reports - Complaints by Department with Status Breakdown

**Purpose**: Generate detailed report showing total, resolved, and unresolved complaints per department

**File**: [`admin.py:204-210`](file:///C:/Users/ALWERAD%20KHAN/OneDrive/Desktop/Civic%20Complaint/app/routes/admin.py#L204-L210)

**ORM Query**:
```python
from sqlalchemy import case

complaints_by_dept = db.session.query(
    Department.name,
    func.count(Complaint.id).label('total'),
    func.sum(case((Complaint.current_status == 'Resolved', 1), else_=0)).label('resolved'),
    func.sum(case((Complaint.current_status != 'Resolved', 1), else_=0)).label('unresolved')
).join(Complaint).group_by(Department.name).all()
```

**SQL Equivalent**:
```sql
SELECT 
    departments.name,
    COUNT(complaints.id) AS total,
    SUM(CASE WHEN complaints.current_status = 'Resolved' THEN 1 ELSE 0 END) AS resolved,
    SUM(CASE WHEN complaints.current_status != 'Resolved' THEN 1 ELSE 0 END) AS unresolved
FROM departments
JOIN complaints ON departments.id = complaints.department_id
GROUP BY departments.name;
```

**Explanation**:
1. Joins departments with complaints
2. Groups by department name
3. Counts total complaints per department
4. Uses `CASE` statements to count resolved vs unresolved separately
5. Returns aggregated data for each department

**Example Result**:
```python
[
    ('Public Works', 25, 18, 7),         # 25 total, 18 resolved, 7 unresolved
    ('Water Supply', 18, 12, 6),
    ('Electricity', 15, 10, 5),
    ('Health & Sanitation', 22, 15, 7),
    ('Traffic', 10, 8, 2)
]
```

---

## Query Performance Notes

### Indexed Fields

The following fields are indexed for faster query performance:

| Table | Indexed Column | Purpose |
|-------|---------------|---------|
| `users` | `username` | Fast login authentication |
| `complaints` | `created_at` | Efficient date-based sorting |
| `status_history` | `changed_at` | Quick history retrieval |

### Relationship Loading Strategies

The application uses **lazy loading** for most relationships:
```python
complaints = db.relationship('Complaint', backref='citizen', lazy='dynamic')
```

- **`lazy='dynamic'`**: Returns a query object instead of loading all data immediately
- Allows filtering/sorting before execution (e.g., `.filter_by()`, `.order_by()`)
- More memory efficient for large datasets

### Query Optimization Tips

1. **Use `.filter_by()` for simple equality checks**:
   ```python
   User.query.filter_by(role='admin')  # Simpler syntax
   ```

2. **Use `.filter()` for complex conditions**:
   ```python
   Complaint.query.filter(Complaint.current_status != 'Resolved')  # More flexible
   ```

3. **Limit result sets** when possible:
   ```python
   .limit(10)  # Only fetch what you need
   ```

4. **Use `.count()` instead of `.all()` for totals**:
   ```python
   User.query.count()  # Executes COUNT(*), doesn't load data
   ```

---

## Security Features

### Password Hashing

Uses Werkzeug's `generate_password_hash()` function:
```python
from werkzeug.security import generate_password_hash, check_password_hash

# Store password
user.password_hash = generate_password_hash(password)

# Verify password
check_password_hash(user.password_hash, password)
```

- Passwords are never stored in plain text
- Uses PBKDF2 algorithm with salt
- Computationally expensive to crack

### SQL Injection Protection

SQLAlchemy ORM automatically escapes all parameters:
```python
# Safe - ORM handles escaping
User.query.filter_by(username=user_input).first()

# Equivalent to prepared statement:
# SELECT * FROM users WHERE username = ? [user_input]
```

> [!IMPORTANT]
> Never use raw SQL with user input unless properly parameterized!

---

## Summary of Key Query Patterns

| Pattern | ORM Syntax | SQL Equivalent |
|---------|-----------|----------------|
| **Select all** | `Model.query.all()` | `SELECT * FROM table` |
| **Filter** | `Model.query.filter_by(col=val)` | `SELECT * FROM table WHERE col = val` |
| **Order by** | `.order_by(Model.col.desc())` | `ORDER BY col DESC` |
| **Limit** | `.limit(n)` | `LIMIT n` |
| **Count** | `.count()` | `SELECT COUNT(*)` |
| **Join** | `.join(OtherModel)` | `JOIN other_table` |
| **Group by** | `.group_by(Model.col)` | `GROUP BY col` |
| **Aggregate** | `func.count()`, `func.sum()` | `COUNT()`, `SUM()` |
| **Insert** | `db.session.add(obj)` then `commit()` | `INSERT INTO` |
| **Update** | Modify object then `commit()` | `UPDATE` |
| **Delete** | `db.session.delete(obj)` then `commit()` | `DELETE FROM` |

---

## Conclusion

This documentation covers all database queries used in the Civic Complaint Tracking System. The queries are organized by user role (Citizen, Officer, Admin) and demonstrate:

✓ **CRUD operations** (Create, Read, Update, Delete)  
✓ **Aggregation queries** (COUNT, SUM, AVG)  
✓ **Complex joins** (multi-table queries)  
✓ **Business logic** (status validation, cascade operations)  
✓ **Security** (password hashing, SQL injection prevention)  
✓ **Performance** (indexing, lazy loading, query optimization)

The system uses SQLAlchemy ORM for type safety, maintainability, and automatic SQL generation.
