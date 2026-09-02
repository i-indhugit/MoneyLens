from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database.session import get_db
from app.models.schemas import TransactionResponse, TransactionCreate, TransactionUpdate, GeneralMessageResponse
from app.services.transaction_service import (
    get_all_transactions, create_transaction, update_transaction, delete_transaction
)

router = APIRouter(prefix="/api/transactions", tags=["transactions"])

@router.get("", response_model=List[TransactionResponse])
def list_transactions(
    search: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    transaction_type: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    txs = get_all_transactions(db)

    if search:
        s = search.lower()
        txs = [t for t in txs if s in t.description.lower() or s in t.category.lower()]

    if category and category != "all":
        txs = [t for t in txs if t.category.lower() == category.lower()]

    if transaction_type and transaction_type != "all":
        txs = [t for t in txs if t.transaction_type.lower() == transaction_type.lower()]

    return txs

@router.post("", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def add_new_transaction(tx_in: TransactionCreate, db: Session = Depends(get_db)):
    return create_transaction(db, tx_in)

@router.put("/{tx_id}", response_model=TransactionResponse)
def edit_transaction(tx_id: str, tx_update: TransactionUpdate, db: Session = Depends(get_db)):
    updated = update_transaction(db, tx_id, tx_update)
    if not updated:
        raise HTTPException(status_code=404, detail="Transaction not found.")
    return updated

@router.delete("/{tx_id}", response_model=GeneralMessageResponse)
def remove_transaction(tx_id: str, db: Session = Depends(get_db)):
    success = delete_transaction(db, tx_id)
    if not success:
        raise HTTPException(status_code=404, detail="Transaction not found.")
    return GeneralMessageResponse(message="Transaction successfully deleted.", success=True)
