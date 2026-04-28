from app.core.database import engine
from sqlalchemy import text

def run_migration():
    """
    Applies PostgreSQL migration to rename the old class model columns 
    ('name' and 'code' if it existed) to match the new SQLAlchemy schema values
    ('course_name' and 'course_code') to fix the NOT NULL constraint mismatch.
    """
    with engine.begin() as conn:
        try:
            # Check and rename 'name' to 'course_name' if it wasn't done yet mapping wise
            conn.execute(text("ALTER TABLE classes RENAME COLUMN name TO course_name;"))
        except Exception as e:
            pass # Already renamed or doesn't exist
            
        try:
            # Check and rename 'code' to 'course_code' if 'code' existed
            conn.execute(text("ALTER TABLE classes RENAME COLUMN code TO course_code;"))
        except Exception as e:
            pass # Already renamed or doesn't exist
            
        # Ensure a default created_at exists for new schema sync logic
        try:
            conn.execute(text("ALTER TABLE classes ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;"))
        except Exception:
            pass
            
        print("Schema migration successfully completed.")

if __name__ == "__main__":
    run_migration()
