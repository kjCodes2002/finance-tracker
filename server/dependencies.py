# dependencies.py
from database import session
from typing import Generator
from sqlalchemy.orm import Session

def get_db() -> Generator[Session, None, None]:
    db = session()
    try:
        yield db
    finally:
        db.close()

def get_current_user_id():
    # TEMP mock
    return "test-user-123"
