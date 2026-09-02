import pandas as pd
from typing import List, Dict, Any, Optional

def db_txs_to_df(transactions: List[Any]) -> pd.DataFrame:
    """
    Converts list of DBTransaction objects or dicts into a clean Pandas DataFrame.
    """
    if not transactions:
        return pd.DataFrame(columns=[
            "id", "date", "description", "amount", "transaction_type", "category", "is_unusual", "created_at"
        ])

    records = []
    for tx in transactions:
        if isinstance(tx, dict):
            records.append(tx)
        else:
            records.append({
                "id": getattr(tx, "id", None),
                "date": getattr(tx, "date", None),
                "description": getattr(tx, "description", None),
                "amount": float(getattr(tx, "amount", 0.0)),
                "transaction_type": getattr(tx, "transaction_type", "expense"),
                "category": getattr(tx, "category", "Other"),
                "is_unusual": getattr(tx, "is_unusual", False),
                "created_at": getattr(tx, "created_at", None),
            })

    df = pd.DataFrame(records)
    if not df.empty and "amount" in df.columns:
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0.0)
    return df

def get_total_income(df: pd.DataFrame) -> float:
    if df.empty:
        return 0.0
    inc_df = df[df["transaction_type"] == "income"]
    return float(inc_df["amount"].sum()) if not inc_df.empty else 0.0

def get_total_expenses(df: pd.DataFrame) -> float:
    if df.empty:
        return 0.0
    exp_df = df[df["transaction_type"] == "expense"]
    return float(exp_df["amount"].sum()) if not exp_df.empty else 0.0

def get_remaining_balance(df: pd.DataFrame) -> float:
    return get_total_income(df) - get_total_expenses(df)

def get_average_expense(df: pd.DataFrame) -> float:
    if df.empty:
        return 0.0
    exp_df = df[df["transaction_type"] == "expense"]
    return float(exp_df["amount"].mean()) if not exp_df.empty else 0.0

def get_highest_expense(df: pd.DataFrame) -> Optional[Dict[str, Any]]:
    if df.empty:
        return None
    exp_df = df[df["transaction_type"] == "expense"]
    if exp_df.empty:
        return None
    highest_row = exp_df.loc[exp_df["amount"].idxmax()]
    return {
        "id": str(highest_row["id"]),
        "date": str(highest_row["date"]),
        "description": str(highest_row["description"]),
        "amount": float(highest_row["amount"]),
        "category": str(highest_row["category"]),
    }

def get_category_spending(df: pd.DataFrame) -> Dict[str, Any]:
    if df.empty:
        return {"categories": [], "total": 0.0}

    exp_df = df[df["transaction_type"] == "expense"]
    if exp_df.empty:
        return {"categories": [], "total": 0.0}

    total = float(exp_df["amount"].sum())
    grouped = exp_df.groupby("category").agg(
        total_amount=("amount", "sum"),
        count=("amount", "count")
    ).reset_index()

    grouped = grouped.sort_values(by="total_amount", ascending=False)

    categories = []
    for _, row in grouped.iterrows():
        amt = float(row["total_amount"])
        pct = round((amt / total) * 100.0, 2) if total > 0 else 0.0
        categories.append({
            "category": str(row["category"]),
            "total_amount": amt,
            "percentage": pct,
            "count": int(row["count"])
        })

    return {"categories": categories, "total": total}

def get_top_spending_category(df: pd.DataFrame) -> Optional[str]:
    cats = get_category_spending(df).get("categories", [])
    return cats[0]["category"] if cats else None

def get_monthly_spending(df: pd.DataFrame) -> List[Dict[str, Any]]:
    if df.empty:
        return []

    df_copy = df.copy()
    df_copy["month"] = df_copy["date"].apply(lambda x: str(x)[:7] if x else "Unknown")

    grouped = df_copy.groupby(["month", "transaction_type"])["amount"].sum().unstack(fill_value=0.0).reset_index()

    if "income" not in grouped.columns:
        grouped["income"] = 0.0
    if "expense" not in grouped.columns:
        grouped["expense"] = 0.0

    grouped = grouped.sort_values(by="month")

    results = []
    for _, row in grouped.iterrows():
        inc = float(row["income"])
        exp = float(row["expense"])
        results.append({
            "month": str(row["month"]),
            "income": inc,
            "expenses": exp,
            "net": inc - exp
        })

    return results
