import sqlite3
import os
import sys

# Ensure we are in the project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'instance', 'civic_complaints.db')

def migrate():
    print(f"Connecting to database at {db_path}...")
    if not os.path.exists(db_path):
        print("Database does not exist! Run app.py or seed_data.py first.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("Migrating users table...")
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN phone_number VARCHAR(20)")
        cursor.execute("ALTER TABLE users ADD COLUMN address TEXT")
        print(" -> Added phone_number and address to users")
    except sqlite3.OperationalError as e:
        print(f" -> Skipping users columns (already exist?): {e}")

    print("Migrating complaints table...")
    try:
        cursor.execute("ALTER TABLE complaints ADD COLUMN evidence_filename VARCHAR(255)")
        cursor.execute("ALTER TABLE complaints ADD COLUMN latitude FLOAT")
        cursor.execute("ALTER TABLE complaints ADD COLUMN longitude FLOAT")
        cursor.execute("ALTER TABLE complaints ADD COLUMN is_public BOOLEAN DEFAULT 0 NOT NULL")
        cursor.execute("ALTER TABLE complaints ADD COLUMN rating INTEGER")
        cursor.execute("ALTER TABLE complaints ADD COLUMN feedback_text TEXT")
        print(" -> Added evidence_filename, latitude, longitude, is_public, rating, feedback_text to complaints")
    except sqlite3.OperationalError as e:
        print(f" -> Skipping complaints columns (already exist?): {e}")

    print("Creating notifications table...")
    try:
        cursor.execute("""
        CREATE TABLE notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            message VARCHAR(255) NOT NULL,
            link VARCHAR(255),
            is_read BOOLEAN DEFAULT 0 NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
        """)
        cursor.execute("CREATE INDEX ix_notifications_created_at ON notifications(created_at)")
        print(" -> Created notifications table")
    except sqlite3.OperationalError as e:
        print(f" -> Skipping notifications table (already exists?): {e}")

    print("Creating upvotes table...")
    try:
        cursor.execute("""
        CREATE TABLE upvotes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            complaint_id INTEGER NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(complaint_id) REFERENCES complaints(id)
        )
        """)
        print(" -> Created upvotes table")
    except sqlite3.OperationalError as e:
        print(f" -> Skipping upvotes table (already exists?): {e}")

    conn.commit()
    conn.close()
    print("Migration complete!")

if __name__ == "__main__":
    migrate()
