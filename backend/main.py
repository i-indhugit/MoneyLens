from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, status, Query, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import io

from database import engine, get_db
from models import Base, DBTransaction
from schemas import (
    TransactionCreate, TransactionResponse, SummaryResponse,
    CategorySpending, MonthlySpending, AnomalyResponse,
    InsightsResponse, AskRequest, AskResponse, GeneralMessage
)
from services.csv_parser import parse_csv_file
from services.categorizer import categorize_transaction
from services.analytics import (
    db_txs_to_df, get_total_income, get_total_expenses, get_remaining_balance,
    get_average_expense, get_highest_expense, get_category_spending,
    get_top_spending_category, get_monthly_spending
)
from services.anomaly_detector import detect_unusual_transactions
from services.insights import generate_financial_insights
from services.question_engine import answer_user_question

# Initialize SQLite database tables safely
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Database initialization notice: {e}")

app = FastAPI(
    title="MoneyLens AI API",
    description="Mobile-First Personal Expense & Financial Insights API",
    version="2.5.0"
)

# CORS middleware for local frontend dev server & PWA
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Router for all backend API endpoints (/api/...)
api_router = APIRouter(prefix="/api")

@api_router.get("")
@api_router.get("/")
def api_root():
    return {
        "status": "online",
        "app": "MoneyLens AI",
        "tagline": "Understand your money. Make better decisions.",
        "privacy": "MoneyLens AI is 100% local and API-free. Zero external AI services or bank keys required."
    }

# 1. Transactions API

@api_router.post("/transactions/upload", response_model=List[TransactionResponse])
async def upload_csv_transactions(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a .csv file format.")

    content = await file.read()
    try:
        parsed_records = parse_csv_file(content)
    except ValueError as ve:
        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to process CSV file: {str(e)}")

    db_objs = []
    for item in parsed_records:
        db_objs.append(DBTransaction(
            date=item["date"],
            description=item["description"],
            amount=item["amount"],
            transaction_type=item["transaction_type"],
            category=item["category"]
        ))

    db.bulk_save_objects(db_objs)
    db.commit()

    return db.query(DBTransaction).order_by(DBTransaction.date.desc()).all()

@api_router.post("/transactions", response_model=TransactionResponse)
def add_transaction(payload: TransactionCreate, db: Session = Depends(get_db)):
    if payload.amount <= 0:
        raise HTTPException(status_code=422, detail="Transaction amount must be greater than 0.")

    category = payload.category
    if not category or category.strip() == "" or category.lower() == "auto detect":
        category = categorize_transaction(payload.description, payload.transaction_type or "expense")

    new_tx = DBTransaction(
        description=payload.description.strip(),
        amount=float(payload.amount),
        date=payload.date,
        transaction_type=payload.transaction_type or "expense",
        category=category
    )

    db.add(new_tx)
    db.commit()
    db.refresh(new_tx)
    return new_tx

@api_router.get("/transactions", response_model=List[TransactionResponse])
def list_transactions(
    search: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(DBTransaction)
    if search:
        query = query.filter(DBTransaction.description.ilike(f"%{search}%"))
    if category and category.lower() != "all":
        query = query.filter(DBTransaction.category.ilike(category))

    return query.order_by(DBTransaction.date.desc()).all()

@api_router.delete("/transactions/{transaction_id}", response_model=GeneralMessage)
def delete_transaction(transaction_id: str, db: Session = Depends(get_db)):
    tx = db.query(DBTransaction).filter(DBTransaction.id == transaction_id).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction record not found.")

    db.delete(tx)
    db.commit()
    return GeneralMessage(message="Transaction record deleted successfully.", success=True)

@api_router.delete("/transactions", response_model=GeneralMessage)
def delete_all_transactions(db: Session = Depends(get_db)):
    db.query(DBTransaction).delete()
    db.commit()
    return GeneralMessage(message="All transactions have been permanently deleted.", success=True)

@api_router.post("/transactions/sample-data", response_model=List[TransactionResponse])
def load_sample_data(db: Session = Depends(get_db)):
    possible_paths = [
        os.path.join(os.getcwd(), "sample_data", "sample_expenses.csv"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "sample_data", "sample_expenses.csv"),
        "sample_data/sample_expenses.csv"
    ]
    sample_path = next((p for p in possible_paths if os.path.exists(p)), None)

    if not sample_path:
        raise HTTPException(status_code=404, detail="Sample expenses dataset file not found.")

    with open(sample_path, "rb") as f:
        content = f.read()

    parsed = parse_csv_file(content)

    db.query(DBTransaction).delete()
    db.commit()

    db_objs = [
        DBTransaction(
            date=item["date"],
            description=item["description"],
            amount=item["amount"],
            transaction_type=item["transaction_type"],
            category=item["category"]
        ) for item in parsed
    ]

    db.bulk_save_objects(db_objs)
    db.commit()

    return db.query(DBTransaction).order_by(DBTransaction.date.desc()).all()

# 2. Financial Analytics API

@api_router.get("/analytics/summary", response_model=SummaryResponse)
def get_analytics_summary(db: Session = Depends(get_db)):
    txs = db.query(DBTransaction).all()
    df = db_txs_to_df(txs)

    return SummaryResponse(
        total_income=get_total_income(df),
        total_expenses=get_total_expenses(df),
        remaining_balance=get_remaining_balance(df),
        average_expense=get_average_expense(df),
        highest_expense=get_highest_expense(df),
        top_spending_category=get_top_spending_category(df),
        transaction_count=len(df)
    )

@api_router.get("/analytics/categories")
def get_category_analytics(db: Session = Depends(get_db)):
    txs = db.query(DBTransaction).all()
    df = db_txs_to_df(txs)
    return get_category_spending(df)

@api_router.get("/analytics/monthly", response_model=List[MonthlySpending])
def get_monthly_analytics(db: Session = Depends(get_db)):
    txs = db.query(DBTransaction).all()
    df = db_txs_to_df(txs)
    return get_monthly_spending(df)

@api_router.get("/analytics/anomalies", response_model=AnomalyResponse)
def get_anomaly_analytics(db: Session = Depends(get_db)):
    txs = db.query(DBTransaction).all()
    res = detect_unusual_transactions(txs)
    return AnomalyResponse(**res)

@api_router.get("/insights", response_model=InsightsResponse)
def get_financial_insights(db: Session = Depends(get_db)):
    txs = db.query(DBTransaction).all()
    res = generate_financial_insights(txs)
    return InsightsResponse(**res)

@api_router.post("/ask", response_model=AskResponse)
def ask_question(payload: AskRequest, db: Session = Depends(get_db)):
    txs = db.query(DBTransaction).all()
    tx_dicts = [
        {
            "id": t.id,
            "date": t.date,
            "description": t.description,
            "amount": t.amount,
            "transaction_type": t.transaction_type,
            "category": t.category,
            "is_unusual": t.is_unusual
        }
        for t in txs
    ]

    res = answer_user_question(payload.question, tx_dicts)
    return AskResponse(**res)

# Register /api router
app.include_router(api_router)

# Only mount StaticFiles when running locally (not on Vercel serverless CDN)
if not os.getenv("VERCEL"):
    frontend_dist = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "frontend", "dist")
    if os.path.exists(frontend_dist):
        app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="static")
