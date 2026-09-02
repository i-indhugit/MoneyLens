import re
from typing import List, Dict, Any
from services.analytics import (
    db_txs_to_df, get_total_income, get_total_expenses, get_remaining_balance,
    get_average_expense, get_highest_expense, get_category_spending, get_monthly_spending
)
from services.anomaly_detector import detect_unusual_transactions

KNOWN_CATEGORIES = [
    "food", "travel", "shopping", "entertainment", "bills",
    "healthcare", "housing", "education", "income", "other"
]

def answer_user_question(question: str, transactions: List[Any]) -> Dict[str, Any]:
    """
    Keyword & Intent matching Question Engine.
    Processes user query and calculates exact Pandas answer.
    NO external LLM APIs used.
    """
    if not question or not question.strip():
        return {
            "question": question,
            "answer": "Please ask a question about your expenses.",
            "intent": "unknown"
        }

    q = question.lower().strip()
    df = db_txs_to_df(transactions)

    # 1. Specific Category Spending Question (e.g. "How much did I spend on food?")
    for cat in KNOWN_CATEGORIES:
        if cat in q or (cat == "food" and any(k in q for k in ["swiggy", "zomato", "dining", "groceries"])):
            cat_name = cat.capitalize()
            if cat == "food" and "food" not in q:
                cat_name = "Food"
            
            cat_data = get_category_spending(df)
            matched_cat = next((c for c in cat_data.get("categories", []) if c["category"].lower() == cat_name.lower()), None)
            amt = matched_cat["total_amount"] if matched_cat else 0.0

            return {
                "question": question,
                "answer": f"You spent ₹{amt:,.2f} on {cat_name}.",
                "intent": "category_total",
                "result_data": {"category": cat_name, "amount": amt}
            }

    # 2. Total Income Question (e.g. "How much did I earn?")
    if any(k in q for k in ["earn", "earned", "income", "salary"]):
        inc = get_total_income(df)
        return {
            "question": question,
            "answer": f"Your total income is ₹{inc:,.2f}.",
            "intent": "total_income",
            "result_data": {"income": inc}
        }

    # 3. Remaining Balance Question (e.g. "What is my balance?")
    if any(k in q for k in ["balance", "remaining", "leftover", "saved"]):
        bal = get_remaining_balance(df)
        return {
            "question": question,
            "answer": f"Your remaining balance is ₹{bal:,.2f}.",
            "intent": "balance",
            "result_data": {"balance": bal}
        }

    # 4. Highest Expense Question (e.g. "What is my biggest expense?")
    if any(k in q for k in ["biggest expense", "largest expense", "highest expense", "most expensive"]):
        highest = get_highest_expense(df)
        if highest:
            ans = f"Your largest expense was {highest['description']} for ₹{highest['amount']:,.2f} ({highest['category']})."
        else:
            ans = "No expense records found."
        return {
            "question": question,
            "answer": ans,
            "intent": "highest_expense",
            "result_data": highest
        }

    # 5. Top Category Question (e.g. "What category did I spend the most on?")
    if any(k in q for k in ["spend the most on", "highest category", "biggest category", "top category", "most spending"]):
        cat_data = get_category_spending(df)
        cats = cat_data.get("categories", [])
        if cats:
            top = cats[0]
            ans = f"{top['category']} is your highest spending category at ₹{top['total_amount']:,.2f} ({top['percentage']}% of total spending)."
        else:
            ans = "No categories available."
        return {
            "question": question,
            "answer": ans,
            "intent": "top_category",
            "result_data": cats[0] if cats else None
        }

    # 6. Monthly Spending Question (e.g. "How much did I spend this month?")
    if any(k in q for k in ["this month", "monthly spend", "month's spend"]):
        monthly = get_monthly_spending(df)
        if monthly:
            curr = monthly[-1]
            ans = f"You spent ₹{curr['expenses']:,.2f} in {curr['month']}."
        else:
            ans = "No monthly spending recorded yet."
        return {
            "question": question,
            "answer": ans,
            "intent": "monthly_spending",
            "result_data": monthly[-1] if monthly else None
        }

    # 7. Unusual Transactions Question (e.g. "Show my unusual transactions")
    if any(k in q for k in ["unusual", "anomaly", "anomalies", "strange", "suspicious"]):
        anom_res = detect_unusual_transactions(transactions)
        count = anom_res.get("total_anomalies", 0)
        if count == 0:
            ans = anom_res.get("message") or "No unusual transactions detected."
        else:
            first = anom_res["anomalies"][0]
            ans = f"We detected {count} unusual transaction(s). Most notable: {first['description']} for ₹{first['amount']:,.2f} ({first['category']})."
        return {
            "question": question,
            "answer": ans,
            "intent": "anomalies",
            "result_data": anom_res
        }

    # 8. Total Expenses Question (e.g. "How much did I spend?")
    if any(k in q for k in ["how much did i spend", "total spend", "total expense", "all expenses"]):
        tot = get_total_expenses(df)
        return {
            "question": question,
            "answer": f"Your total expenses are ₹{tot:,.2f}.",
            "intent": "total_expenses",
            "result_data": {"total_expenses": tot}
        }

    # 9. Unsupported Question Fallback (Requirement #13)
    return {
        "question": question,
        "answer": "I can currently answer questions about your spending, income, categories, monthly totals, and unusual transactions.",
        "intent": "unsupported"
    }
