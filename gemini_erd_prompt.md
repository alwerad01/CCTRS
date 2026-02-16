# Prompt for Gemini AI to Generate ERD

Use this detailed prompt with Gemini AI (or any AI image generator) to create a professional Entity-Relationship Diagram for your Civic Complaint Tracking System:

---

## PROMPT FOR GEMINI AI

```
Create a professional, highly detailed Entity-Relationship Diagram (ERD) for a Civic Complaint Tracking System database. The diagram should follow standard ERD notation and be suitable for an academic/professional presentation.

REQUIREMENTS:
- Use standard Chen notation or Crow's Foot notation
- Clean, professional appearance with white or light background
- Each entity should be in a distinct colored box (pastel colors preferred)
- Show all attributes, primary keys (PK), and foreign keys (FK)
- Clearly indicate cardinality (1:1, 1:N, M:N) on relationship lines
- Use proper database symbols and conventions
- High resolution, suitable for printing

ENTITIES AND ATTRIBUTES:

1. USER Entity (suggest light blue box)
   - id [PK] (Integer, Auto-increment)
   - username (VARCHAR(80), UNIQUE, NOT NULL, INDEXED)
   - email (VARCHAR(120), UNIQUE, NOT NULL)
   - password_hash (VARCHAR(255), NOT NULL)
   - role (VARCHAR(20), NOT NULL, DEFAULT='citizen')
   - department_id [FK] (Integer, NULLABLE)
   - created_at (DATETIME, DEFAULT=NOW)

2. DEPARTMENT Entity (suggest light green box)
   - id [PK] (Integer, Auto-increment)
   - name (VARCHAR(100), UNIQUE, NOT NULL)
   - description (TEXT, NULLABLE)
   - created_at (DATETIME, DEFAULT=NOW)

3. COMPLAINT Entity (suggest light orange box)
   - id [PK] (Integer, Auto-increment)
   - title (VARCHAR(200), NOT NULL)
   - description (TEXT, NOT NULL)
   - citizen_id [FK] (Integer, NOT NULL)
   - department_id [FK] (Integer, NOT NULL)
   - assigned_officer_id [FK] (Integer, NULLABLE)
   - current_status (VARCHAR(50), NOT NULL, DEFAULT='Received')
   - created_at (DATETIME, DEFAULT=NOW, INDEXED)
   - updated_at (DATETIME, AUTO-UPDATE)

4. STATUS_HISTORY Entity (suggest light purple box)
   - id [PK] (Integer, Auto-increment)
   - complaint_id [FK] (Integer, NOT NULL)
   - previous_status (VARCHAR(50), NOT NULL)
   - new_status (VARCHAR(50), NOT NULL)
   - changed_by_user_id [FK] (Integer, NOT NULL)
   - notes (TEXT, NULLABLE)
   - changed_at (DATETIME, DEFAULT=NOW, INDEXED)

RELATIONSHIPS (with cardinality):

1. USER —submits→ COMPLAINT
   - Cardinality: 1:N (One-to-Many)
   - A citizen user can submit many complaints
   - Foreign Key: COMPLAINT.citizen_id → USER.id

2. USER —handles→ COMPLAINT
   - Cardinality: 1:N (One-to-Many)
   - An officer user can handle many complaints
   - Foreign Key: COMPLAINT.assigned_officer_id → USER.id

3. DEPARTMENT —receives→ COMPLAINT
   - Cardinality: 1:N (One-to-Many)
   - A department receives many complaints
   - Foreign Key: COMPLAINT.department_id → DEPARTMENT.id

4. DEPARTMENT —employs→ USER
   - Cardinality: 1:N (One-to-Many)
   - A department has many officer users
   - Foreign Key: USER.department_id → DEPARTMENT.id

5. COMPLAINT —tracks→ STATUS_HISTORY
   - Cardinality: 1:N (One-to-Many)
   - A complaint has many status history records
   - Foreign Key: STATUS_HISTORY.complaint_id → COMPLAINT.id
   - CASCADE DELETE (deleting complaint deletes its history)

6. USER —changes→ STATUS_HISTORY
   - Cardinality: 1:N (One-to-Many)
   - A user makes many status changes
   - Foreign Key: STATUS_HISTORY.changed_by_user_id → USER.id

BUSINESS RULES TO ANNOTATE:
- User.role can be: 'citizen', 'officer', or 'admin'
- Complaint.current_status can be: 'Received', 'In Progress', or 'Resolved'
- Status transitions: Received → In Progress → Resolved (one-way only)
- Officers must have a department_id; citizens and admins have NULL
- Username and email are globally unique across all users
- Indexed fields: USER.username, COMPLAINT.created_at, STATUS_HISTORY.changed_at

LAYOUT SUGGESTIONS:
- Place USER and DEPARTMENT at the top level
- COMPLAINT in the middle (connects to both USER and DEPARTMENT)
- STATUS_HISTORY at the bottom (connects to COMPLAINT and USER)
- Minimize crossing relationship lines for clarity
- Use clear, readable fonts (Arial or similar)
- Make entity boxes large enough to clearly show all attributes

STYLE PREFERENCES:
- Professional, technical appearance
- Suitable for academic presentation or thesis documentation
- Clear labeling of all relationships
- Legend showing PK = Primary Key, FK = Foreign Key
- Color coding: primary keys in bold or different color
- High contrast for readability when projected

Create the diagram with these specifications in mind, ensuring it's visually clear, technically accurate, and presentation-ready.
```

---

## How to Use This Prompt

### Option 1: Gemini AI (Google AI Studio)
1. Go to https://aistudio.google.com/
2. Click "Create new prompt"
3. Paste the entire prompt above
4. Generate the image
5. Download and save to your project

### Option 2: Other AI Image Generators
- **ChatGPT (DALL-E)**: Paste the prompt
- **Microsoft Copilot**: Paste the prompt (uses DALL-E)
- **Midjourney**: May need to simplify the prompt
- **Stable Diffusion**: Works well with technical diagrams

### Option 3: Diagramming Tools
You can also use the information to manually create the ERD in:
- **Draw.io** (diagrams.net) - Free
- **Lucidchart** - Professional
- **dbdiagram.io** - Specialized for database ERDs
- **MySQL Workbench** - Auto-generates from schema
- **Microsoft Visio** - Enterprise standard

---

## Tips for Best Results

1. **If the AI doesn't understand ERD notation**:
   - Add: "Use standard database ERD notation like in academic textbooks"
   - Reference: "Similar to ERDs in Database Systems by Elmasri & Navathe"

2. **If the diagram is too cluttered**:
   - Ask to "create a simplified version showing only primary and foreign keys"
   - Request: "split into two diagrams: entities and relationships separately"

3. **If colors don't work well**:
   - Specify: "use pastel colors with good contrast for projection"
   - Or request: "professional black and white diagram with clear borders"

4. **For academic presentation**:
   - Add: "include a title: 'Civic Complaint Tracking System - Database Schema'"
   - Request: "add your name and project details in a footer"

---

## Alternative: Simple Text-Based Prompt

If you want a quicker, simpler prompt:

```
Create an Entity-Relationship Diagram for a civic complaint database with 4 tables:
- USER (stores citizens, officers, admins)
- DEPARTMENT (civic departments like Public Works, Water Supply)
- COMPLAINT (issues reported by citizens)
- STATUS_HISTORY (tracks complaint status changes)

Show relationships: Users submit complaints, departments receive complaints, officers handle complaints, complaints have status history. Use professional ERD notation with crow's foot symbols.
```

---

Now you have both a generated visual ERD and multiple prompts for creating variations!
