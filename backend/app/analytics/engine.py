import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional

def transactions_to_df(transactions: List[Any]) -> pd.DataFrame:
    """Converts a list of ORM or Pydantic transactions to a Pandas DataFrame."""
    if not transactions:
        return pd.DataFrame(columns=["id", "date", "description", "amount", "transaction_type", "category", "source"])

    data = []
    for idx, tx in enumerate(transactions):
        tx_id = getattr(tx, "id", None)
        if not tx_id and isinstance(tx, dict):
            tx_id = tx.get("id")
        if not tx_id:
            tx_id = f"tx-{idx}"

        d = {
            "id": str(tx_id),
            "date": getattr(tx, "date", "") if not isinstance(tx, dict) else tx.get("date", ""),
            "description": getattr(tx, "description", "") if not isinstance(tx, dict) else tx.get("description", ""),
            "amount": float(getattr(tx, "amount", 0.0) if not isinstance(tx, dict) else tx.get("amount", 0.0)),
            "transaction_type": getattr(tx, "transaction_type", "expense") if not isinstance(tx, dict) else tx.get("transaction_type", "expense"),
            "category": getattr(tx, "category", "Other") if not isinstance(tx, dict) else tx.get("category", "Other"),
            "source": getattr(tx, "source", "manual") if not isinstance(tx, dict) else tx.get("source", "manual")
        }
        data.append(d)

    df = pd.DataFrame(data)
    # Ensure date column is datetime for datetime math
    df["datetime"] = pd.to_datetime(df["date"], errors='coerce')
    return df

def get_total_expenses(df: pd.DataFrame) -> float:
    if df.empty:
        return 0.0
    expenses = df[df["transaction_type"] == "expense"]
    return round(float(expenses["amount"].sum()), 2)

def get_total_income(df: pd.DataFrame) -> float:
    if df.empty:
        return 0.0
    income = df[df["transaction_type"] == "income"]
    return round(float(income["amount"].sum()), 2)

def get_net_cash_flow(df: pd.DataFrame) -> float:
    return round(get_total_income(df) - get_total_expenses(df), 2)

def get_average_transaction(df: pd.DataFrame) -> float:
    expenses = df[df["transaction_type"] == "expense"]
    if expenses.empty:
        return 0.0
    return round(float(expenses["amount"].mean()), 2)

def get_average_daily_spending(df: pd.DataFrame) -> float:
    expenses = df[df["transaction_type"] == "expense"]
    if expenses.empty:
        return 0.0
    unique_days = expenses["date"].nunique()
    if unique_days == 0:
        return 0.0
    return round(float(expenses["amount"].sum() / unique_days), 2)

def get_largest_transaction(df: pd.DataFrame) -> Optional[Dict[str, Any]]:
    expenses = df[df["transaction_type"] == "expense"]
    if expenses.empty:
        return None
    idx = expenses["amount"].idxmax()
    row = expenses.loc[idx]
    return {
        "id": row["id"],
        "date": row["date"],
        "description": row["description"],
        "amount": round(float(row["amount"]), 2),
        "category": row["category"]
    }

def get_smallest_transaction(df: pd.DataFrame) -> Optional[Dict[str, Any]]:
    expenses = df[df["transaction_type"] == "expense"]
    if expenses.empty:
        return None
    idx = expenses["amount"].idxmin()
    row = expenses.loc[idx]
    return {
        "id": row["id"],
        "date": row["date"],
        "description": row["description"],
        "amount": round(float(row["amount"]), 2),
        "category": row["category"]
    }

def get_category_spending(df: pd.DataFrame, category: Optional[str] = None) -> Dict[str, Any]:
    expenses = df[df["transaction_type"] == "expense"]
    if expenses.empty:
        return {"categories": [], "total": 0.0}

    total_expense = expenses["amount"].sum()

    if category:
        cat_df = expenses[expenses["category"].str.lower() == category.lower()]
        cat_total = float(cat_df["amount"].sum())
        cat_pct = round((cat_total / total_expense * 100), 2) if total_expense > 0 else 0.0
        return {
            "category": category,
            "total_amount": round(cat_total, 2),
            "percentage": cat_pct,
            "count": int(len(cat_df))
        }

    grouped = expenses.groupby("category").agg(
        total_amount=("amount", "sum"),
        count=("amount", "count")
    ).reset_index()

    grouped["percentage"] = (grouped["total_amount"] / total_expense * 100).round(2) if total_expense > 0 else 0.0
    grouped = grouped.sort_values(by="total_amount", ascending=False)

    categories_list = []
    for _, row in grouped.iterrows():
        categories_list.append({
            "category": row["category"],
            "total_amount": round(float(row["total_amount"]), 2),
            "percentage": float(row["percentage"]),
            "count": int(row["count"])
        })

    return {"categories": categories_list, "total": round(float(total_expense), 2)}

def get_monthly_spending(df: pd.DataFrame) -> List[Dict[str, Any]]:
    if df.empty:
        return []

    # Extract YYYY-MM
    df["month"] = df["datetime"].dt.to_period("M").astype(str)

    grouped = df.groupby(["month", "transaction_type"])["amount"].sum().unstack(fill_value=0).reset_index()

    if "expense" not in grouped.columns:
        grouped["expense"] = 0.0
    if "income" not in grouped.columns:
        grouped["income"] = 0.0

    grouped = grouped.sort_values(by="month")

    result = []
    for _, row in grouped.iterrows():
        exp = round(float(row["expense"]), 2)
        inc = round(float(row["income"]), 2)
        result.append({
            "month": str(row["month"]),
            "expenses": exp,
            "income": inc,
            "net": round(inc - exp, 2)
        })

    return result

def get_top_expenses(df: pd.DataFrame, limit: int = 5) -> List[Dict[str, Any]]:
    expenses = df[df["transaction_type"] == "expense"]
    if expenses.empty:
        return []

    top_df = expenses.sort_values(by="amount", ascending=False).head(limit)
    res = []
    for _, row in top_df.iterrows():
        res.append({
            "id": row["id"],
            "date": row["date"],
            "description": row["description"],
            "amount": round(float(row["amount"]), 2),
            "category": row["category"]
        })
    return res

def get_month_comparison(df: pd.DataFrame) -> Dict[str, Any]:
    if df.empty:
        return {
            "current_month": "",
            "previous_month": "",
            "current_month_spending": 0.0,
            "previous_month_spending": 0.0,
            "change_pct": 0.0
        }

    expenses = df[df["transaction_type"] == "expense"].copy()
    if expenses.empty:
        return {
            "current_month": "",
            "previous_month": "",
            "current_month_spending": 0.0,
            "previous_month_spending": 0.0,
            "change_pct": 0.0
        }

    expenses["month"] = expenses["datetime"].dt.to_period("M").astype(str)
    months = sorted(expenses["month"].unique())

    if len(months) == 0:
        return {"current_month": "", "previous_month": "", "current_month_spending": 0.0, "previous_month_spending": 0.0, "change_pct": 0.0}

    curr_month = months[-1]
    prev_month = months[-2] if len(months) > 1 else ""

    curr_amt = float(expenses[expenses["month"] == curr_month]["amount"].sum())
    prev_amt = float(expenses[expenses["month"] == prev_month]["amount"].sum()) if prev_month else 0.0

    change_pct = 0.0
    if prev_amt > 0:
        change_pct = round(((curr_amt - prev_amt) / prev_amt) * 100, 2)

    return {
        "current_month": curr_month,
        "previous_month": prev_month,
        "current_month_spending": round(curr_amt, 2),
        "previous_month_spending": round(prev_amt, 2),
        "change_pct": change_pct
    }

def get_weekend_spending(df: pd.DataFrame) -> Dict[str, Any]:
    expenses = df[df["transaction_type"] == "expense"].copy()
    if expenses.empty:
        return {"weekend_total": 0.0, "weekday_total": 0.0, "weekend_pct": 0.0}

    # Day of week: 5=Saturday, 6=Sunday
    expenses["is_weekend"] = expenses["datetime"].dt.dayofweek.isin([5, 6])

    weekend_total = float(expenses[expenses["is_weekend"]]["amount"].sum())
    weekday_total = float(expenses[~expenses["is_weekend"]]["amount"].sum())
    total = weekend_total + weekday_total

    weekend_pct = round((weekend_total / total * 100), 2) if total > 0 else 0.0

    return {
        "weekend_total": round(weekend_total, 2),
        "weekday_total": round(weekday_total, 2),
        "weekend_pct": weekend_pct
    }

def get_subscription_spending(df: pd.DataFrame) -> Dict[str, Any]:
    expenses = df[df["transaction_type"] == "expense"]
    sub_df = expenses[expenses["category"].str.lower() == "subscriptions"]

    total = float(sub_df["amount"].sum()) if not sub_df.empty else 0.0
    items = []
    if not sub_df.empty:
        for _, row in sub_df.iterrows():
            items.append({
                "description": row["description"],
                "amount": round(float(row["amount"]), 2),
                "date": row["date"]
            })

    return {
        "total_subscriptions": round(total, 2),
        "count": len(sub_df),
        "items": items
    }
