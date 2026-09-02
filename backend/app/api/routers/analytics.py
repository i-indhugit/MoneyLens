from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.database.session import get_db
from app.models.schemas import FinancialSummary, AnomalyResponse, InsightsResponse
from app.services.transaction_service import (
    get_all_transactions, get_financial_summary, get_automated_insights
)
from app.analytics.engine import (
    transactions_to_df, get_category_spending, get_monthly_spending
)
from app.anomaly.detector import detect_anomalies

router = APIRouter(prefix="/api", tags=["analytics"])

@router.get("/summary", response_model=FinancialSummary)
def get_summary_metrics(db: Session = Depends(get_db)):
    return get_financial_summary(db)

@router.get("/categories")
def get_categories_breakdown(db: Session = Depends(get_db)):
    txs = get_all_transactions(db)
    df = transactions_to_df(txs)
    return get_category_spending(df)

@router.get("/monthly")
def get_monthly_trends(db: Session = Depends(get_db)):
    txs = get_all_transactions(db)
    df = transactions_to_df(txs)
    return get_monthly_spending(df)

@router.get("/anomalies", response_model=AnomalyResponse)
def get_unusual_spending_anomalies(db: Session = Depends(get_db)):
    txs = get_all_transactions(db)
    anoms = detect_anomalies(txs)
    return AnomalyResponse(
        total_anomalies=len(anoms),
        anomalies=anoms
    )

@router.get("/insights", response_model=InsightsResponse)
def get_ai_spending_insights(db: Session = Depends(get_db)):
    return get_automated_insights(db)
