from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import os

from app.models.db import Base, DBUserSettings

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./moneylens.db")

# SQLite specific connect_args
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
    # Ensure default user settings row exists
    db = SessionLocal()
    try:
        settings = db.query(DBUserSettings).filter(DBUserSettings.id == 1).first()
        if not settings:
            default_settings = DBUserSettings(id=1, currency="₹", llm_provider="auto", llm_api_key="")
            db.add(default_settings)
            db.commit()
    except Exception as e:
        db.rollback()
    finally:
        db.close()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
