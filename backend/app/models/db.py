from sqlalchemy import Column, String, Float, DateTime, Integer, Boolean
from sqlalchemy.orm import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

class DBTransaction(Base):
    __tablename__ = "transactions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    date = Column(String, nullable=False, index=True)  # YYYY-MM-DD
    description = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    transaction_type = Column(String, nullable=False, default="expense")  # "expense" or "income"
    category = Column(String, nullable=False, default="Other")
    source = Column(String, nullable=False, default="manual")  # csv, excel, pdf, manual, demo
    confidence = Column(Float, nullable=False, default=1.0)
    created_at = Column(DateTime, default=datetime.utcnow)

class DBCategoryRule(Base):
    __tablename__ = "category_rules"

    id = Column(Integer, primary_key=True, autoincrement=True)
    keyword = Column(String, unique=True, nullable=False, index=True)
    category = Column(String, nullable=False)
    is_user_override = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class DBUserSettings(Base):
    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True, default=1)
    currency = Column(String, default="₹")
    llm_provider = Column(String, default="auto")  # gemini, auto
    llm_api_key = Column(String, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
