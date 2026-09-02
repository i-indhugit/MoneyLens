from sqlalchemy import Column, String, Float, DateTime, Boolean
from database import Base
import uuid
from datetime import datetime

class DBTransaction(Base):
    __tablename__ = "transactions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    date = Column(String, nullable=False)
    description = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    transaction_type = Column(String, nullable=False, default="expense") # expense or income
    category = Column(String, nullable=False, default="Other")
    is_unusual = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
