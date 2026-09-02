from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, status
from sqlalchemy.orm import Session
import os
from typing import Optional, List

from app.database.session import get_db
from app.models.schemas import ImportPreviewResponse, ImportCommitRequest, GeneralMessageResponse
from app.parsers.csv_parser import parse_csv_content
from app.parsers.excel_parser import parse_excel_content, get_excel_sheet_names
from app.parsers.pdf_parser import parse_pdf_content
from app.services.transaction_service import bulk_create_transactions

router = APIRouter(prefix="/api/import", tags=["import"])

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB limit

@router.post("/csv", response_model=ImportPreviewResponse)
async def import_csv_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a .csv file format.")

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File size exceeds maximum allowed limit (10MB).")

    transactions, warnings = parse_csv_content(content, filename=file.filename, db=db)

    conf_avg = sum(tx.confidence for tx in transactions) / len(transactions) if transactions else 0.0

    return ImportPreviewResponse(
        source="csv",
        total_detected=len(transactions),
        confidence_average=round(conf_avg, 2),
        has_warnings=len(warnings) > 0,
        warnings=warnings,
        transactions=transactions
    )

@router.post("/excel", response_model=ImportPreviewResponse)
async def import_excel_file(
    file: UploadFile = File(...),
    sheet_name: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    if not any(file.filename.lower().endswith(ext) for ext in [".xlsx", ".xls"]):
        raise HTTPException(status_code=400, detail="File must be an Excel file (.xlsx or .xls).")

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File size exceeds maximum allowed limit (10MB).")

    transactions, warnings, sheets = parse_excel_content(content, sheet_name=sheet_name, filename=file.filename, db=db)

    conf_avg = sum(tx.confidence for tx in transactions) / len(transactions) if transactions else 0.0

    return ImportPreviewResponse(
        source="excel",
        total_detected=len(transactions),
        confidence_average=round(conf_avg, 2),
        has_warnings=len(warnings) > 0,
        sheet_names=sheets,
        warnings=warnings,
        transactions=transactions
    )

@router.post("/pdf", response_model=ImportPreviewResponse)
async def import_pdf_statement(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="File must be a PDF document (.pdf).")

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File size exceeds maximum allowed limit (10MB).")

    transactions, warnings, conf_avg = parse_pdf_content(content, filename=file.filename, db=db)

    return ImportPreviewResponse(
        source="pdf",
        total_detected=len(transactions),
        confidence_average=conf_avg,
        has_warnings=len(warnings) > 0,
        warnings=warnings,
        transactions=transactions
    )

@router.post("/demo", response_model=ImportPreviewResponse)
async def import_demo_data(db: Session = Depends(get_db)):
    # Try finding sample_expenses.csv from root workspace or relative path
    possible_paths = [
        os.path.join(os.getcwd(), "sample_data", "sample_expenses.csv"),
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "sample_data", "sample_expenses.csv"),
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "sample_data", "sample_expenses.csv"),
        "sample_data/sample_expenses.csv"
    ]
    
    sample_path = next((p for p in possible_paths if os.path.exists(p)), None)
    
    if not sample_path:
        raise HTTPException(status_code=404, detail="Sample expenses dataset file not found.")

    with open(sample_path, "rb") as f:
        content = f.read()

    transactions, warnings = parse_csv_content(content, filename="sample_expenses.csv", db=db)

    for tx in transactions:
        tx.source = "demo"

    conf_avg = sum(tx.confidence for tx in transactions) / len(transactions) if transactions else 1.0

    return ImportPreviewResponse(
        source="demo",
        total_detected=len(transactions),
        confidence_average=round(conf_avg, 2),
        has_warnings=False,
        warnings=warnings,
        transactions=transactions
    )

@router.post("/commit", response_model=GeneralMessageResponse)
async def commit_imported_transactions(payload: ImportCommitRequest, db: Session = Depends(get_db)):
    if not payload.transactions:
        raise HTTPException(status_code=400, detail="No transactions provided to commit.")

    count = bulk_create_transactions(db, payload.transactions)
    return GeneralMessageResponse(
        message=f"Successfully saved {count} transaction records into MoneyLens AI database.",
        success=True
    )
