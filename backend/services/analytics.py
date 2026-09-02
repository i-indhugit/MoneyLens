import pandas as pd
from typing import List, Dict, Any, Optional

def db_txs_to_df(transactions: List[Any]) -> pd.DataFrame:
    if not transactions:
        return pd.DataFrame(columns=["id", "date", "description", "amount", "transaction_type", "category"])

    data = []
    for tx in transactions:
        d = {
            "id": getattr(tx, "id", None) or tx.get("id") if isinstance(tx, dict) else getattr(tx, "id", None),
            "date": getattr(tx, "date", "") if not isinstance(tx, dict) else tx.get("date", ""),
            "description": getattr(tx, "description", "") if not isinstance(tx, dict) else tx.get("description", ""),
            "amount": float(getattr(tx, "amount", 0.0) if not isinstance(tx, dict) else tx.get("amount", 0.0)),
            "transaction_type": getattr(tx, "transaction_type", "expense") if not isinstance(tx, dict) else tx.get("transaction_type", "expense"),
            "category": getattr(tx, "category", "Other") if not isinstance(tx, dict) else tx.get("category", "Other"),
        }
        data.append(d)

    df = pd.DataFrame(data)
    df["datetime"] = pd.to_datetime(df["date"], errors='coerce')
    return df

def get_total_income(df: pd.DataFrame) -> float:
    if df.empty:
        return 0.0
    inc = df[df["transaction_type"] == "income"]
    return round(float(inc["amount"].sum()), 2)

def get_total_expenses(df: pd.DataFrame) -> float:
    if df.empty:
        return 0.0
    exp = df[df["transaction_type"] == "expense"]
    return round(float(exp["amount"].sum()), 2)

def get_remaining_balance(df: pd.DataFrame) -> float:
    return round(get_total_income(df) - get_total_expenses(df), 2)

def get_average_expense(df: pd.DataFrame) -> float:
    exp = df[df["transaction_type"] == "expense"]
    if exp.empty:
        return 0.0
    return round(float(exp["amount"].mean()), 2)

def get_highest_expense(df: pd.DataFrame) -> Optional[Dict[str, Any]]:
    exp = df[df["transaction_type"] == "expense"]
    if exp.empty:
        return None
    idx = exp["amount"].idxmax()
    row = exp.loc[idx]
    return {
        "id": str(row["id"]),
        "date": str(row["date"]),
        "description": str(row["description"]),
        "amount": round(float(row["amount"]), 2),
        "category": str(row["category"])
    }

def get_category_spending(df: pd.DataFrame) -> Dict[str, Any]:
    exp = df[df["transaction_type"] == "expense"]
    if exp.empty:
        return {"categories": [], "total": 0.0}

    total_expense = exp["amount"].sum()

    grouped = exp.groupby("category").agg(
        total_amount=("amount", "sum"),
        count=("amount", "count")
    ).reset_index()

    grouped["percentage"] = (grouped["total_amount"] / total_expense * 100).round(2) if total_expense > 0 else 0.0
    grouped = grouped.sort_values(by="total_amount", ascending=False)

    categories_list = []
    for _, row in grouped.iterrows():
        categories_list.append({
            "category": str(row["category"]),
            "total_amount": round(float(row["total_amount"]), 2),
            "percentage": float(row["percentage"]),
            "count": int(row["count"])
        })

    return {"categories": categories_list, "total": round(float(total_expense), 2)}

def get_monthly_spending(df: pd.DataFrame) -> List[Dict[str, Any]]:
    if df.empty:
        return []

    df["month"] = df["datetime"].dt.to_period("M").astype(str)

    grouped = df.groupby(["month", "transaction_type"])["amount"].sum().unstack(fill_value=0).reset_index()

    if "expense" not in grouped.columns:
        grouped["expense"] = 0.0
    if "income" not in grouped.columns:
        grouped["income"] = 0.0

    grouped = grouped.sort_values(by="month")

    res = []
    for _, row in grouped.iterrows():
        e = round(float(row["expense"]), 2)
        i = round(float(row["income"]), 2)
        res.append({
            "month": str(row["month"]),
            "expenses": e,
            "income": i,
            "net": round(i - e, 2)
        })
    return res
