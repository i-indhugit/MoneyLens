from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import io

from database import engine, get_db
from models import Base, DBTransaction
from schemas import (
    TransactionCreate, TransactionResponse, SummaryResponse,
    AnomalyResponse, InsightsResponse, AskRequest, AskResponse, GeneralMessage
)
from services.csv_parser import parse_csv_file
from services.categorizer import categorize_transaction
from services.analytics import (
    db_txs_to_df, get_total_income, get_total_expenses, get_remaining_balance,
    get_average_expense, get_highest_expense, get_category_spending, get_monthly_spending
)
from services.anomaly_detector import detect_unusual_transactions
from services.insights import generate_financial_insights
from services.question_engine import answer_user_question

# Initialize database tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="MoneyLens AI MVP API",
    description="100% API-Free, Privacy-First Personal Expense Analysis API",
    version="2.0.0"
)

# Configure CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "status": "online",
        "app": "MoneyLens AI MVP",
        "privacy": "MoneyLens AI is 100% local and API-free. No external AI APIs or credentials required."
    }

# 1. Transactions API

@app.post("/transactions/upload", response_model=List[TransactionResponse])
async def upload_csv_transactions(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a .csv file format.")

    content = await file.read()
    try:
        parsed_records = parse_csv_file(content)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=400, detail="Failed to parse CSV file. Please check file format.")

    db_objs = []
    for item in parsed_records:
        obj = DBTransaction(
            date=item["date"],
            description=item["description"],
            amount=item["amount"],
            transaction_type=item["transaction_type"],
            category=item["category"]
        )
        db_objs.append(obj)

    db.bulk_save_objects(db_objs)
    db.commit()

    return db.query(DBTransaction).order_by(DBTransaction.date.desc()).all()

@app.post("/transactions", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def add_single_transaction(tx_in: TransactionCreate, db: Session = Depends(get_db)):
    if tx_in.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be greater than zero.")

    # Assign category automatically if omitted
    final_cat = tx_in.category if tx_in.category and tx_in.category.strip() else categorize_transaction(tx_in.description, tx_in.transaction_type or "expense")
    date_str = tx_in.date if tx_in.date else pd.Timestamp.now().strftime("%Y-%m-%d")

    db_tx = DBTransaction(
        date=date_str,
        description=tx_in.description,
        amount=tx_in.amount,
        transaction_type=tx_in.transaction_type or "expense",
        category=final_cat
    )
    db.add(db_tx)
    db.commit()
    db.refresh(db_tx)
    return db_tx

@app.get("/transactions", response_model=List[TransactionResponse])
def list_transactions(
    search: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    txs = db.query(DBTransaction).order_by(DBTransaction.date.desc()).all()

    if search:
        s = search.lower()
        txs = [t for t in txs if s in t.description.lower() or s in t.category.lower()]

    if category and category != "All":
        txs = [t for t in txs if t.category.lower() == category.lower()]

    return txs

@app.delete("/transactions/{tx_id}", response_model=GeneralMessage)
def delete_single_transaction(tx_id: str, db: Session = Depends(get_db)):
    tx = db.query(DBTransaction).filter(DBTransaction.id == tx_id).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction record not found.")
    db.delete(tx)
    db.commit()
    return GeneralMessage(message="Transaction successfully deleted.", success=True)

@app.delete("/transactions", response_model=GeneralMessage)
def delete_all_transactions(db: Session = Depends(get_db)):
    db.query(DBTransaction).delete()
    db.commit()
    return GeneralMessage(message="All transaction records have been permanently deleted.", success=True)

@app.post("/transactions/sample-data", response_model=List[TransactionResponse])
def import_sample_data(db: Session = Depends(get_db)):
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

    db_objs = []
    for item in parsed:
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

# 2. Financial Analytics API

@app.get("/analytics/summary", response_model=SummaryResponse)
def get_analytics_summary(db: Session = Depends(get_db)):
    txs = db.query(DBTransaction).all()
    df = db_txs_to_df(txs)
    return SummaryResponse(
        total_income=get_total_income(df),
        total_expenses=get_total_expenses(df),
        remaining_balance=get_remaining_balance(df),
        average_expense=get_average_expense(df),
        highest_expense=get_highest_expense(df),
        transaction_count=len(txs)
    )

@app.get("/analytics/categories")
def get_categories_breakdown(db: Session = Depends(get_db)):
    txs = db.query(DBTransaction).all()
    df = db_txs_to_df(txs)
    return get_category_spending(df)

@app.get("/analytics/monthly")
def get_monthly_breakdown(db: Session = Depends(get_db)):
    txs = db.query(DBTransaction).all()
    df = db_txs_to_df(txs)
    return get_monthly_spending(df)

@app.get("/analytics/anomalies", response_model=AnomalyResponse)
def get_unusual_spending(db: Session = Depends(get_db)):
    txs = db.query(DBTransaction).all()
    res = detect_unusual_transactions(txs)
    return AnomalyResponse(**res)

@app.get("/insights", response_model=InsightsResponse)
def get_financial_insights(db: Session = Depends(get_db)):
    txs = db.query(DBTransaction).all()
    res = generate_financial_insights(txs)
    return InsightsResponse(**res)

@app.post("/ask", response_model=AskResponse)
def ask_question(payload: AskRequest, db: Session = Depends(get_db)):
    txs = db.query(DBTransaction).all()
    res = answer_user_question(payload.question, txs)
    return AskResponse(**res)
