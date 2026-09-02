from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.schemas import AskQuestionRequest, AskQuestionResponse
from app.models.db import DBUserSettings
from app.services.transaction_service import get_all_transactions
from app.ai.query_engine import process_user_question

router = APIRouter(prefix="/api", tags=["assistant"])

@router.post("/ask", response_model=AskQuestionResponse)
def ask_moneylens_assistant(payload: AskQuestionRequest, db: Session = Depends(get_db)):
    if not payload.question or not payload.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    txs = get_all_transactions(db)

    settings = db.query(DBUserSettings).filter(DBUserSettings.id == 1).first()
    currency = settings.currency if settings else "₹"

    res = process_user_question(payload.question, txs, currency_symbol=currency, db=db)
    return AskQuestionResponse(**res)
