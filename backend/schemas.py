from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class TransactionBase(BaseModel):
    description: str
    amount: float
    date: Optional[str] = None
    transaction_type: Optional[str] = Field(default="expense", description="expense or income")
    category: Optional[str] = Field(default=None, description="Optional category. Auto-assigned if empty.")

class TransactionCreate(TransactionBase):
    pass

class TransactionResponse(TransactionBase):
    id: str
    date: str
    category: str
    transaction_type: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class SummaryResponse(BaseModel):
    total_income: float
    total_expenses: float
    remaining_balance: float
    average_expense: float
    highest_expense: Optional[Dict[str, Any]] = None
    transaction_count: int

class CategorySpending(BaseModel):
    category: str
    total_amount: float
    percentage: float
    count: int

class MonthlySpending(BaseModel):
    month: str
    income: float
    expenses: float
    net: float

class AnomalyItem(BaseModel):
    id: str
    date: str
    description: str
    amount: float
    category: str
    reason: str

class AnomalyResponse(BaseModel):
    total_anomalies: int
    anomalies: List[AnomalyItem]
    message: Optional[str] = None

class MoneyMoodSchema(BaseModel):
    mood: str
    description: str

class InsightItem(BaseModel):
    type: str
    title: str
    description: str

class InsightsResponse(BaseModel):
    money_mood: MoneyMoodSchema
    insights: List[InsightItem]

class AskRequest(BaseModel):
    question: str

class AskResponse(BaseModel):
    question: str
    answer: str
    intent: str
    result_data: Optional[Dict[str, Any]] = None

class GeneralMessage(BaseModel):
    message: str
    success: bool
