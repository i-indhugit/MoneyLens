from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class TransactionBase(BaseModel):
    date: str
    description: str
    amount: float
    transaction_type: str = Field(default="expense", description="expense or income")
    category: str = Field(default="Other")
    source: str = Field(default="manual")
    confidence: float = Field(default=1.0)

class TransactionCreate(TransactionBase):
    pass

class TransactionUpdate(BaseModel):
    date: Optional[str] = None
    description: Optional[str] = None
    amount: Optional[float] = None
    transaction_type: Optional[str] = None
    category: Optional[str] = None

class TransactionResponse(TransactionBase):
    id: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ParsedTransaction(BaseModel):
    temp_id: str
    date: str
    description: str
    amount: float
    transaction_type: str
    category: str
    confidence: float
    source: str
    warnings: List[str] = []

class ImportPreviewResponse(BaseModel):
    source: str
    total_detected: int
    confidence_average: float
    has_warnings: bool
    sheet_names: Optional[List[str]] = None
    warnings: List[str] = []
    transactions: List[ParsedTransaction]

class ImportCommitRequest(BaseModel):
    transactions: List[TransactionCreate]

class CategorySummary(BaseModel):
    category: str
    total_amount: float
    percentage: float
    count: int

class MonthlySummary(BaseModel):
    month: str  # YYYY-MM
    income: float
    expenses: float
    net: float

class FinancialSummary(BaseModel):
    total_expenses: float
    total_income: float
    net_cash_flow: float
    average_transaction: float
    average_daily_spending: float
    largest_transaction: Optional[Dict[str, Any]] = None
    smallest_transaction: Optional[Dict[str, Any]] = None
    transaction_count: int
    category_count: int
    current_month_spending: float
    previous_month_spending: float
    month_over_month_change_pct: float

class AnomalyItem(BaseModel):
    id: str
    date: str
    description: str
    amount: float
    category: str
    anomaly_score: float
    explanation: str

class AnomalyResponse(BaseModel):
    total_anomalies: int
    anomalies: List[AnomalyItem]

class InsightItem(BaseModel):
    type: str  # breakdown, trend, savings, alert
    title: str
    description: str
    impact_amount: Optional[float] = None
    category: Optional[str] = None

class InsightsResponse(BaseModel):
    insights: List[InsightItem]
    savings_suggestions: List[Dict[str, Any]]
    disclaimer: str

class AskQuestionRequest(BaseModel):
    question: str

class AskQuestionResponse(BaseModel):
    question: str
    intent_detected: str
    calculation_results: Dict[str, Any]
    answer: str

class UserSettingsSchema(BaseModel):
    currency: str = "₹"
    llm_provider: str = "auto"
    llm_api_key: str = ""

class GeneralMessageResponse(BaseModel):
    message: str
    success: bool
