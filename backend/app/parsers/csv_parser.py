import pandas as pd
import io
import re
from datetime import datetime
from typing import List, Dict, Any, Tuple
from app.models.schemas import ParsedTransaction
from app.categorization.engine import categorize_description

DATE_COLUMNS = ["date", "transaction date", "txn date", "value date", "post date"]
DESC_COLUMNS = ["description", "transaction description", "details", "particulars", "narration", "remark", "payee", "merchant"]
AMOUNT_COLUMNS = ["amount", "txn amount", "net amount"]
DEBIT_COLUMNS = ["debit", "dr", "withdrawal", "spent", "debit amount"]
CREDIT_COLUMNS = ["credit", "cr", "deposit", "income", "credit amount"]
TYPE_COLUMNS = ["type", "transaction type", "dr/cr", "mode"]

def parse_date(date_str: Any) -> str:
    """Standardizes various date formats to YYYY-MM-DD."""
    if pd.isna(date_str) or not date_str:
        return datetime.utcnow().strftime("%Y-%m-%d")

    s = str(date_str).strip()

    # Check ISO format YYYY-MM-DD or YYYY/MM/DD first
    if re.match(r'^\d{4}[-/.]\d{2}[-/.]\d{2}', s):
        try:
            dt = pd.to_datetime(s, errors='coerce')
            if not pd.isna(dt):
                return dt.strftime("%Y-%m-%d")
        except Exception:
            pass

    # Try dayfirst=True for DD/MM/YYYY or DD-MM-YYYY
    try:
        dt = pd.to_datetime(s, dayfirst=True, errors='coerce')
        if not pd.isna(dt):
            return dt.strftime("%Y-%m-%d")
    except Exception:
        pass

    # Standard fallback
    try:
        dt = pd.to_datetime(s, errors='coerce')
        if not pd.isna(dt):
            return dt.strftime("%Y-%m-%d")
    except Exception:
        pass

    return datetime.utcnow().strftime("%Y-%m-%d")

def clean_amount(val: Any) -> float:
    """Extracts floating point number from string amounts like ₹1,200.50 or (450)."""
    if pd.isna(val) or val is None:
        return 0.0
    if isinstance(val, (int, float)):
        return abs(float(val))

    s = str(val).strip().replace(",", "")
    # Check if enclosed in parentheses (negative amount)
    is_neg = False
    if s.startswith("(") and s.endswith(")"):
        is_neg = True
        s = s[1:-1]

    # Find float pattern
    match = re.search(r'[-+]?\d*\.?\d+', s)
    if match:
        amt = abs(float(match.group()))
        return amt
    return 0.0

def parse_csv_content(content_bytes: bytes, filename: str = "upload.csv", db = None) -> Tuple[List[ParsedTransaction], List[str]]:
    """
    Parses CSV content into normalized ParsedTransaction objects.
    """
    warnings: List[str] = []

    try:
        # Try reading with pandas
        df = pd.read_csv(io.BytesIO(content_bytes))
    except Exception as e:
        warnings.append(f"Failed to read CSV format: {str(e)}")
        return [], warnings

    if df.empty:
        warnings.append("CSV file is empty.")
        return [], warnings

    # Normalize column names to lowercase for matching
    orig_cols = list(df.columns)
    cols_lower = [str(c).strip().lower() for c in orig_cols]
    col_map = {orig_cols[i]: cols_lower[i] for i in range(len(orig_cols))}

    # Identify column matches
    date_col = next((c for c in orig_cols if col_map[c] in DATE_COLUMNS), None)
    desc_col = next((c for c in orig_cols if col_map[c] in DESC_COLUMNS), None)
    amount_col = next((c for c in orig_cols if col_map[c] in AMOUNT_COLUMNS), None)
    debit_col = next((c for c in orig_cols if col_map[c] in DEBIT_COLUMNS), None)
    credit_col = next((c for c in orig_cols if col_map[c] in CREDIT_COLUMNS), None)
    type_col = next((c for c in orig_cols if col_map[c] in TYPE_COLUMNS), None)
    cat_col = next((c for c in orig_cols if col_map[c] == "category"), None)

    # Fallbacks if strict column matching fails
    if not date_col:
        for c in orig_cols:
            if "date" in col_map[c]:
                date_col = c
                break

    if not desc_col:
        for c in orig_cols:
            if any(k in col_map[c] for k in ["desc", "detail", "payee", "name", "particular"]):
                desc_col = c
                break

    if not date_col or not desc_col:
        warnings.append("Could not confidently auto-detect Date or Description columns. Used best fallback matching.")

    parsed_list: List[ParsedTransaction] = []

    for idx, row in df.iterrows():
        # Parse Date
        d_val = row[date_col] if date_col and date_col in row else None
        date_str = parse_date(d_val)

        # Parse Description
        desc_val = str(row[desc_col]).strip() if desc_col and desc_col in row and not pd.isna(row[desc_col]) else "Unknown Transaction"

        # Determine Amount and Type (Debit vs Credit)
        amt = 0.0
        t_type = "expense"

        if debit_col and credit_col:
            d_amt = clean_amount(row[debit_col])
            c_amt = clean_amount(row[credit_col])
            if c_amt > 0:
                amt = c_amt
                t_type = "income"
            else:
                amt = d_amt
                t_type = "expense"
        elif amount_col:
            raw_amt = row[amount_col]
            amt = clean_amount(raw_amt)
            if type_col and type_col in row and not pd.isna(row[type_col]):
                t_str = str(row[type_col]).lower().strip()
                if "cr" in t_str or "income" in t_str or "deposit" in t_str:
                    t_type = "income"
                else:
                    t_type = "expense"
            else:
                # Check sign or fallback
                if isinstance(raw_amt, (int, float)) and raw_amt < 0:
                    t_type = "expense"
                elif str(raw_amt).startswith("-"):
                    t_type = "expense"
                else:
                    # Heuristic check on description
                    t_type = "income" if any(k in desc_val.lower() for k in ["salary", "deposit", "credit", "freelance", "refund"]) else "expense"
        else:
            # Fallback scan all columns for numeric
            for c in orig_cols:
                v = clean_amount(row[c])
                if v > 0:
                    amt = v
                    break

        # Categorize
        if cat_col and not pd.isna(row[cat_col]) and str(row[cat_col]).strip():
            category = str(row[cat_col]).strip()
            confidence = 0.95
        else:
            category, confidence = categorize_description(desc_val, db=db)

        # Ignore invalid zero amounts if description is empty
        if amt <= 0 and desc_val == "Unknown Transaction":
            continue

        item = ParsedTransaction(
            temp_id=f"csv-{idx}",
            date=date_str,
            description=desc_val,
            amount=round(amt, 2),
            transaction_type=t_type,
            category=category,
            confidence=round(confidence, 2),
            source="csv",
            warnings=[]
        )
        parsed_list.append(item)

    return parsed_list, warnings
