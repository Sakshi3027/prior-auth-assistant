"""
One-off migration: add the human-in-the-loop override columns to the
existing requests table. Safe to run repeatedly (IF NOT EXISTS).
Run: python -m db.add_override_columns
"""
from sqlalchemy import text
from db.database import engine

STATEMENTS = [
    "ALTER TABLE requests ADD COLUMN IF NOT EXISTS overridden BOOLEAN DEFAULT FALSE",
    "ALTER TABLE requests ADD COLUMN IF NOT EXISTS override_decision VARCHAR(20)",
    "ALTER TABLE requests ADD COLUMN IF NOT EXISTS override_reason TEXT",
    "ALTER TABLE requests ADD COLUMN IF NOT EXISTS override_by VARCHAR(120)",
]

def run():
    with engine.connect() as conn:
        for stmt in STATEMENTS:
            conn.execute(text(stmt))
        conn.commit()
    print("override columns added")

if __name__ == "__main__":
    run()