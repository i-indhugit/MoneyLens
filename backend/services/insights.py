import pandas as pd
from typing import List, Dict, Any
from services.analytics import (
    db_txs_to_df, get_total_income, get_total_expenses, get_remaining_balance,
    get_category_spending, get_monthly_spending, get_highest_expense
)

def calculate_money_mood(df: pd.DataFrame) -> Dict[str, str]:
    """
    Generates simple Python rule-based Money Mood state:
    - 🌿 Balanced
    - 📈 Spending More
    - 💡 Improving
    - ⚠️ Watch Your Spending
    """
    if df.empty:
        return {
            "mood": "🌿 Balanced",
            "description": "Your spending story starts here. Import data or add expenses to unlock your Money Mood."
        }

    total_inc = get_total_income(df)
    total_exp = get_total_expenses(df)
    balance = get_remaining_balance(df)

    monthly = get_monthly_spending(df)

    if len(monthly) >= 2:
        curr_m = monthly[-1]["expenses"]
        prev_m = monthly[-2]["expenses"]
        if curr_m > prev_m * 1.2:
            return {
                "mood": "📈 Spending More",
                "description": "Your expenses increased compared to last month. Take a look at your top spending categories."
            }
        elif curr_m < prev_m * 0.9:
            return {
                "mood": "💡 Improving",
                "description": "You've reduced your spending compared to last month. Great job keeping your money healthy!"
            }

    if total_inc > 0 and total_exp > total_inc * 0.85:
        return {
            "mood": "⚠️ Watch Your Spending",
            "description": "Your expenses are taking up over 85% of your income. Keep an eye on non-essential categories."
        }

    return {
        "mood": "🌿 Balanced",
        "description": "Your spending is currently well balanced and under control."
    }

def generate_financial_insights(transactions: List[Any]) -> Dict[str, Any]:
    """
    Rule-based financial insights and Money Mood generator.
    100% Local Python logic — No external AI APIs required.
    """
    df = db_txs_to_df(transactions)
    insights = []
    money_mood = calculate_money_mood(df)

    if df.empty:
        return {
            "money_mood": money_mood,
            "insights": [
                {
                    "type": "info",
                    "title": "Your money story starts here ✦",
                    "description": "Upload a CSV statement or add expenses to see your visual spending cards."
                }
            ]
        }

    total_exp = get_total_expenses(df)
    cat_res = get_category_spending(df)
    cats = cat_res.get("categories", [])

    # 1. Top category insight
    if cats:
        top_cat = cats[0]
        insights.append({
            "type": "top_category",
            "title": f"{top_cat['category']} is your highest spending category this month.",
            "description": f"You spent ₹{top_cat['total_amount']:,.2f} on {top_cat['category']}, accounting for {top_cat['percentage']}% of total spending."
        })

        if top_cat['percentage'] >= 30.0:
            insights.append({
                "type": "high_category",
                "title": f"High {top_cat['category']} spending",
                "description": f"{top_cat['category']} is one of your biggest spending categories this month."
            })

    # 2. Monthly comparison
    monthly = get_monthly_spending(df)
    if len(monthly) >= 2:
        curr_m = monthly[-1]
        prev_m = monthly[-2]
        if curr_m["expenses"] > prev_m["expenses"]:
            insights.append({
                "type": "trend",
                "title": "Spending increased",
                "description": "Your spending increased compared with last month."
            })
        elif curr_m["expenses"] < prev_m["expenses"]:
            insights.append({
                "type": "trend",
                "title": "Spending lower",
                "description": "Your spending is lower than last month. Keep it up."
            })

    # 3. Unusually large single transaction
    highest = get_highest_expense(df)
    if highest and total_exp > 0:
        if highest["amount"] >= total_exp * 0.25 and highest["amount"] > 1000:
            insights.append({
                "type": "large_expense",
                "title": "Unusually large transaction",
                "description": f"You made an unusually large transaction recently: {highest['description']} for ₹{highest['amount']:,.2f}."
            })

    return {
        "money_mood": money_mood,
        "insights": insights
    }
