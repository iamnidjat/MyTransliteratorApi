from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.models import User


def seed_users(db: Session):
    db.execute(text("TRUNCATE TABLE users RESTART IDENTITY CASCADE;"))

    default_user = User(
        name="Default User",
        email="user@example.com",
        password="user123",
    )

    db.merge(default_user)
    print("✅ Default user was added.")

def run_all_seeds():
    db: Session = SessionLocal()
    try:
        seed_users(db)
        db.commit()
        print("✅ Seed data was added.")
    except Exception as e:
        db.rollback()
        print("❌ Seed data was not added:", e)
    finally:
        db.close()
if __name__ == "__main__":
    run_all_seeds()