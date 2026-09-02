import os
import tempfile
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

def get_database_engine():
    # 1. Custom DATABASE_URL if provided
    custom_url = os.getenv("DATABASE_URL")
    if custom_url:
        return create_engine(custom_url, connect_args={"check_same_thread": False} if custom_url.startswith("sqlite") else {})

    # 2. Vercel Serverless environment -> write to OS temp directory or in-memory
    if os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME"):
        try:
            tmp_db_path = os.path.join(tempfile.gettempdir(), "moneylens.db")
            tmp_url = f"sqlite:///{tmp_db_path}"
            eng = create_engine(tmp_url, connect_args={"check_same_thread": False})
            with eng.connect() as conn:
                pass
            return eng
        except Exception:
            return create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})

    # 3. Local environment -> sqlite:///./moneylens.db
    try:
        eng = create_engine("sqlite:///./moneylens.db", connect_args={"check_same_thread": False})
        with eng.connect() as conn:
            pass
        return eng
    except Exception:
        return create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})

engine = get_database_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
