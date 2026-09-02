import pandas as pd
import io
import re
from datetime import datetime
from typing import List, Dict, Any, Tuple
from services.categorizer import categorize_transaction

DATE_COLS = ["date", "transaction date", "txn date", "value date"]
DESC_COLS = ["description", "transaction description", "transaction", "details", "particulars", "narration", "payee", "item"]
AMOUNT_COLS = ["amount", "txn amount", "net amount"]
DEBIT_COLS = ["debit", "dr", "withdrawal", "spent"]
CREDIT_COLS = ["credit", "cr", "deposit", "income"]
TYPE_COLS = ["type", "transaction type", "dr/cr", "mode"]

def clean_amount(val: Any) -> float:
    if pd.isna(val) or val is None:
        return 0.0
    if isinstance(val, (int, float)):
        return abs(float(val))

    s = str(val).strip().replace(",", "")
    match = re.search(r'[-+]?\d*\.?\d+', s)
    if match:
        return abs(float(match.group()))
    return 0.0

def parse_date_str(val: Any) -> str:
    if pd.isna(val) or not val:
        return datetime.utcnow().strftime("%Y-%m-%d")

    s = str(val).strip()

    # Check ISO format YYYY-MM-DD or YYYY/MM/DD
    if re.match(r'^\d{4}[-/.]\d{2}[-/.]\d{2}', s):
        try:
            dt = pd.to_datetime(s, errors='coerce')
            if not pd.isna(dt):
                return dt.strftime("%Y-%m-%d")
        except Exception:
            pass

    # Try dayfirst=True for DD/MM/YYYY
    try:
        dt = pd.to_datetime(s, dayfirst=True, errors='coerce')
        if not pd.isna(dt):
            return dt.strftime("%Y-%m-%d")
    except Exception:
        pass

    try:
        dt = pd.to_datetime(s, errors='coerce')
        if not pd.isna(dt):
            return dt.strftime("%Y-%m-%d")
    except Exception:
        pass

    return datetime.utcnow().strftime("%Y-%m-%d")

def parse_csv_file(content_bytes: bytes) -> List[Dict[str, Any]]:
    """
    Parses CSV content bytes and returns a list of normalized transaction dictionaries.
    Raises ValueError with beginner-friendly explanations if parsing fails.
    """
    if not content_bytes or len(content_bytes.strip()) == 0:
        raise ValueError("The uploaded CSV file is empty. Please upload a CSV containing transactions.")

    try:
        df = pd.read_csv(io.BytesIO(content_bytes))
    except Exception as e:
        raise ValueError(f"Could not read CSV file format. Please check your file formatting.")

    if df.empty:
        raise ValueError("The uploaded CSV file contains no transaction rows.")

    orig_cols = list(df.columns)
    cols_lower = [str(c).strip().lower() for c in orig_cols]
    col_map = {orig_cols[i]: cols_lower[i] for i in range(len(orig_cols))}

    date_col = next((c for c in orig_cols if col_map[c] in DATE_COLS), None)
    desc_col = next((c for c in orig_cols if col_map[c] in DESC_COLS), None)
    amount_col = next((c for c in orig_cols if col_map[c] in AMOUNT_COLS), None)
    debit_col = next((c for c in orig_cols if col_map[c] in DEBIT_COLS), None)
    credit_col = next((c for c in orig_cols if col_map[c] in CREDIT_COLS), None)
    type_col = next((c for c in orig_cols if col_map[c] in TYPE_COLS), None)
    cat_col = next((c for c in orig_cols if col_map[c] == "category"), None)

    # Fallback column search
    if not date_col:
        for c in orig_cols:
            if "date" in col_map[c]:
                date_col = c
                break

    if not desc_col:
        for c in orig_cols:
            if any(k in col_map[c] for k in ["desc", "detail", "item", "narration", "payee", "particular"]):
                desc_col = c
                break

    # Mandatory amount column check with beginner-friendly error
    if not amount_col and not (debit_col or credit_col):
        for c in orig_cols:
            if any(k in col_map[c] for k in ["amount", "price", "cost", "sum", "val"]):
                amount_col = c
                break

    if not amount_col and not (debit_col or credit_col):
        raise ValueError("We couldn't find an Amount column. Please upload a CSV containing transaction amounts.")

    parsed_records = []

    for _, row in df.iterrows():
        d_val = row[date_col] if date_col and date_col in row else None
        date_str = parse_date_str(d_val)

        desc_val = str(row[desc_col]).strip() if desc_col and desc_col in row and not pd.isna(row[desc_col]) else "Expense Transaction"

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
                if any(k in t_str for k in ["cr", "income", "deposit"]):
                    t_type = "income"
                else:
                    t_type = "expense"
            else:
                # Infer from description keyword
                t_type = "income" if any(k in desc_val.lower() for k in ["salary", "deposit", "credit", "freelance", "stipend"]) else "expense"

        # Explicit or rule-based categorization
        user_cat = str(row[cat_col]).strip() if cat_col and cat_col in row and not pd.isna(row[cat_col]) else None
        category = user_cat if user_cat else categorize_transaction(desc_val, t_type)

        if amt > 0:
            parsed_records.append({
                "date": date_str,
                "description": desc_val,
                "amount": round(amt, 2),
                "transaction_type": t_type,
                "category": category
            })

    return parsed_records
