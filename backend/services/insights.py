import pandas as pd
from typing import List, Dict, Any
from services.analytics import (
    db_txs_to_df, get_total_income, get_total_expenses, get_remaining_balance,
    get_category_spending, get_monthly_spending, get_highest_expense
)

def calculate_money_health(df: pd.DataFrame) -> Dict[str, str]:
    """
    Generates simple Python rule-based Money Health summary:
    - Excellent: Income > Expenses with healthy balance savings
    - Stable: Balanced spending within income
    - Caution: Expenses taking up over 85% of income or exceeding balance
    """
    if df.empty:
        return {
            "status": "Getting Started",
            "summary": "Your financial analysis will generate automatically when you import expenses."
        }

    total_inc = get_total_income(df)
    total_exp = get_total_expenses(df)
    balance = get_remaining_balance(df)

    if total_inc > 0:
        expense_ratio = total_exp / total_inc
        if balance > 0 and expense_ratio < 0.65:
            return {
                "status": "Healthy & Growing",
                "summary": "Your income comfortably exceeds your spending, leaving a strong cash reserve."
            }
        elif balance >= 0 and expense_ratio <= 0.85:
            return {
                "status": "Balanced",
                "summary": "Your expenses are well controlled within your monthly income level."
            }
        elif expense_ratio > 0.85:
            return {
                "status": "Attention Needed",
                "summary": "Your spending is consuming over 85% of your total income. Consider reviewing top categories."
            }

    if balance < 0:
        return {
            "status": "Deficit Warning",
            "summary": "Expenses exceed total income for this recorded period."
        }

    return {
        "status": "Stable",
        "summary": "Your overall personal expenses are tracked and balanced."
    }

def generate_financial_insights(transactions: List[Any]) -> Dict[str, Any]:
    """
    Rule-based MoneyLens Insights engine.
    100% Local Python logic — No external AI APIs required.
    """
    df = db_txs_to_df(transactions)
    insights = []
    health = calculate_money_health(df)

    if df.empty:
        return {
            "money_health": health,
            "insights": [
                {
                    "type": "info",
                    "title": "Welcome to MoneyLens AI",
                    "description": "Upload a CSV file or log expenses to generate automated financial insights."
                }
            ]
        }

    total_exp = get_total_expenses(df)
    cat_res = get_category_spending(df)
    cats = cat_res.get("categories", [])

    # 1. Top Category Insight
    if cats:
        top_cat = cats[0]
        insights.append({
            "type": "top_category",
            "title": f"Shopping is currently your highest spending category." if top_cat['category'].lower() == 'shopping' else f"{top_cat['category']} is your highest spending category.",
            "description": f"You spent ₹{top_cat['total_amount']:,.2f} on {top_cat['category']} ({top_cat['percentage']}% of total spending)."
        })

    # 2. Monthly Trend Insight
    monthly = get_monthly_spending(df)
    if len(monthly) >= 2:
        curr_m = monthly[-1]
        prev_m = monthly[-2]
        if curr_m["expenses"] > prev_m["expenses"]:
            insights.append({
                "type": "trend",
                "title": "Your spending increased this month.",
                "description": f"Expenses rose from ₹{prev_m['expenses']:,.2f} to ₹{curr_m['expenses']:,.2f}."
            })
        elif curr_m["expenses"] < prev_m["expenses"]:
            insights.append({
                "type": "trend",
                "title": "Your spending decreased this month.",
                "description": f"Expenses reduced from ₹{prev_m['expenses']:,.2f} to ₹{curr_m['expenses']:,.2f}."
            })

    # 3. Balance Insight
    bal = get_remaining_balance(df)
    if bal > 0:
        insights.append({
            "type": "balance",
            "title": "You have a positive balance this month.",
            "description": f"Your current net balance reserve is ₹{bal:,.2f}."
        })
    elif bal < 0:
        insights.append({
            "type": "balance",
            "title": "Your expenses are higher than your income.",
            "description": f"Current deficit stands at ₹{abs(bal):,.2f}."
        })

    # 4. Highest Transaction Insight
    highest = get_highest_expense(df)
    if highest and total_exp > 0:
        if highest["amount"] >= total_exp * 0.20:
            insights.append({
                "type": "large_expense",
                "title": f"Largest single expense: {highest['description']}",
                "description": f"A single payment of ₹{highest['amount']:,.2f} on {highest['date']} represents a significant portion of spending."
            })

    return {
        "money_health": health,
        "insights": insights
    }
