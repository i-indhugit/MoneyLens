import os
import re
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from google import genai

from app.analytics.engine import (
    transactions_to_df, get_total_expenses, get_total_income, get_net_cash_flow,
    get_category_spending, get_monthly_spending, get_top_expenses,
    get_month_comparison, get_weekend_spending, get_subscription_spending,
    get_average_transaction, get_average_daily_spending
)
from app.anomaly.detector import detect_anomalies
from app.models.db import DBUserSettings

KNOWN_CATEGORIES = [
    "food", "groceries", "transport", "shopping", "subscriptions",
    "bills & utilities", "healthcare", "rent", "entertainment",
    "education", "travel", "other", "salary"
]

def determine_intent(question: str) -> Tuple[str, Dict[str, Any]]:
    """
    Parses the user's natural language question into an intent classification and parameters.
    """
    q = question.lower().strip()

    # Category query check
    for cat in KNOWN_CATEGORIES:
        if cat in q or (cat == "food" and any(k in q for k in ["dining", "swiggy", "zomato", "restaurant", "eating out"])):
            return "category_spending", {"category": cat.capitalize()}

    # Specific intent matching
    if any(k in q for k in ["unusual", "anomaly", "anomalies", "suspicious", "flagged", "strange"]):
        return "anomalies", {}

    if any(k in q for k in ["subscription", "subscriptions", "recurring", "netflix", "spotify"]):
        return "subscriptions", {}

    if any(k in q for k in ["weekend", "weekends", "saturday", "sunday"]):
        return "weekend_spending", {}

    if any(k in q for k in ["biggest", "largest", "highest", "top expense", "top spending", "most expensive"]):
        return "top_expenses", {}

    if any(k in q for k in ["compare", "comparison", "growth", "increased", "increase", "versus", "vs"]):
        return "month_comparison", {}

    if any(k in q for k in ["most", "where am i spending", "highest category", "biggest category", "breakdown"]):
        return "category_breakdown", {}

    if any(k in q for k in ["reduce", "save", "savings", "cut back", "spend smarter", "optimize"]):
        return "savings_insights", {}

    if any(k in q for k in ["average", "avg"]):
        return "average_spending", {}

    if any(k in q for k in ["income", "earned", "salary"]):
        return "total_income", {}

    if any(k in q for k in ["net", "cash flow", "balance"]):
        return "net_cash_flow", {}

    # Default to total expenses summary
    return "total_summary", {}

def execute_analytics_for_intent(intent: str, params: Dict[str, Any], transactions: List[Any]) -> Dict[str, Any]:
    """
    Executes Python/Pandas calculation routines for the matched intent.
    Never relies on LLM to compute math!
    """
    df = transactions_to_df(transactions)

    if intent == "category_spending":
        cat = params.get("category", "Food")
        return get_category_spending(df, category=cat)

    elif intent == "anomalies":
        anoms = detect_anomalies(transactions)
        return {
            "total_anomalies": len(anoms),
            "anomalies": [a.model_dump() for a in anoms]
        }

    elif intent == "subscriptions":
        return get_subscription_spending(df)

    elif intent == "weekend_spending":
        return get_weekend_spending(df)

    elif intent == "top_expenses":
        return {"top_expenses": get_top_expenses(df, limit=5)}

    elif intent == "month_comparison":
        return get_month_comparison(df)

    elif intent == "category_breakdown":
        return get_category_spending(df, category=None)

    elif intent == "savings_insights":
        cats = get_category_spending(df, category=None).get("categories", [])
        total_exp = get_total_expenses(df)
        savings = []
        for c in cats[:3]:  # Top 3 spending categories
            if c["total_amount"] > 0 and c["category"] not in ["Rent", "Salary"]:
                pot = round(c["total_amount"] * 0.20, 2)
                savings.append({
                    "category": c["category"],
                    "current_monthly": c["total_amount"],
                    "potential_savings_20pct": pot
                })
        return {"total_expenses": total_exp, "savings_opportunities": savings}

    elif intent == "average_spending":
        return {
            "average_transaction": get_average_transaction(df),
            "average_daily": get_average_daily_spending(df)
        }

    elif intent == "total_income":
        return {"total_income": get_total_income(df)}

    elif intent == "net_cash_flow":
        return {"net_cash_flow": get_net_cash_flow(df)}

    else:
        return {
            "total_expenses": get_total_expenses(df),
            "total_income": get_total_income(df),
            "net_cash_flow": get_net_cash_flow(df),
            "transaction_count": len(df)
        }

def format_natural_explanation(
    question: str,
    intent: str,
    results: Dict[str, Any],
    currency_symbol: str = "₹",
    db: Session = None
) -> str:
    """
    Generates a natural language explanation of the verified mathematical results.
    If a Gemini API key is configured, uses Gemini. Otherwise uses deterministic structured template generator.
    """
    api_key = os.getenv("GEMINI_API_KEY", "")
    if db is not None:
        try:
            st = db.query(DBUserSettings).filter(DBUserSettings.id == 1).first()
            if st and st.llm_api_key:
                api_key = st.llm_api_key
        except Exception:
            pass

    # Try Gemini if key is provided
    if api_key:
        try:
            client = genai.Client(api_key=api_key)
            prompt = f"""You are MoneyLens AI, a smart financial assistant.
The user asked: "{question}"
Here is the exact, verified calculation result computed deterministically by Python/Pandas:
{results}

Write a concise, friendly, and helpful 2-3 sentence answer explaining these exact numbers to the user.
Use the currency symbol {currency_symbol}. Do NOT invent any numbers. Stick strictly to the provided data."""
            
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
            )
            if response and response.text:
                return response.text.strip()
        except Exception:
            pass  # fallback to local explanation engine seamlessly

    # Local deterministic natural language explanation generator
    if intent == "category_spending":
        cat = results.get("category", "Target Category")
        amt = results.get("total_amount", 0.0)
        pct = results.get("percentage", 0.0)
        cnt = results.get("count", 0)
        return f"You spent a total of {currency_symbol}{amt:,.2f} on **{cat}** across {cnt} transaction(s), which represents **{pct}%** of your total expenses."

    elif intent == "anomalies":
        cnt = results.get("total_anomalies", 0)
        if cnt == 0:
            return "No unusual transactions were detected in your current dataset."
        anoms = results.get("anomalies", [])
        top = anoms[0] if anoms else {}
        return f"We detected **{cnt} unusual transaction(s)**. The most notable is **{top.get('description')}** on {top.get('date')} for **{currency_symbol}{top.get('amount', 0):,.2f}** ({top.get('category')})."

    elif intent == "subscriptions":
        tot = results.get("total_subscriptions", 0.0)
        cnt = results.get("count", 0)
        return f"You currently spend **{currency_symbol}{tot:,.2f}** across **{cnt} recurring subscription(s)**."

    elif intent == "weekend_spending":
        w_tot = results.get("weekend_total", 0.0)
        pct = results.get("weekend_pct", 0.0)
        return f"Your weekend spending totals **{currency_symbol}{w_tot:,.2f}**, accounting for **{pct}%** of your overall expense volume."

    elif intent == "top_expenses":
        items = results.get("top_expenses", [])
        if not items:
            return "No expense records found."
        first = items[0]
        return f"Your largest single expense was **{first.get('description')}** on {first.get('date')} for **{currency_symbol}{first.get('amount', 0):,.2f}** under {first.get('category')}."

    elif intent == "month_comparison":
        curr_m = results.get("current_month", "current month")
        curr_amt = results.get("current_month_spending", 0.0)
        prev_amt = results.get("previous_month_spending", 0.0)
        pct = results.get("change_pct", 0.0)
        direction = "increased" if pct >= 0 else "decreased"
        return f"In {curr_m}, your spending was **{currency_symbol}{curr_amt:,.2f}**, which has {direction} by **{abs(pct)}%** compared to the previous month ({currency_symbol}{prev_amt:,.2f})."

    elif intent == "category_breakdown":
        cats = results.get("categories", [])
        if not cats:
            return "No categories available."
        top_cat = cats[0]
        return f"Your highest spending category is **{top_cat.get('category')}** at **{currency_symbol}{top_cat.get('total_amount', 0):,.2f}** ({top_cat.get('percentage')}% of total spending)."

    elif intent == "savings_insights":
        opps = results.get("savings_opportunities", [])
        if not opps:
            return "Based on your spending patterns, your expenses are currently well-balanced across categories."
        o1 = opps[0]
        return f"Based on your recent spending, reducing your **{o1.get('category')}** spending by 20% could potentially save approximately **{currency_symbol}{o1.get('potential_savings_20pct'):,.2f}/month**."

    elif intent == "average_spending":
        avg_tx = results.get("average_transaction", 0.0)
        avg_daily = results.get("average_daily", 0.0)
        return f"Your average transaction size is **{currency_symbol}{avg_tx:,.2f}**, and your average daily spending is **{currency_symbol}{avg_daily:,.2f}**."

    elif intent == "total_income":
        inc = results.get("total_income", 0.0)
        return f"Your total recorded income is **{currency_symbol}{inc:,.2f}**."

    elif intent == "net_cash_flow":
        net = results.get("net_cash_flow", 0.0)
        status = "positive" if net >= 0 else "negative"
        return f"Your net cash flow is **{currency_symbol}{net:,.2f}** ({status})."

    else:
        tot = results.get("total_expenses", 0.0)
        cnt = results.get("transaction_count", 0)
        return f"Your total recorded expenses amount to **{currency_symbol}{tot:,.2f}** across {cnt} transactions."

def process_user_question(question: str, transactions: List[Any], currency_symbol: str = "₹", db: Session = None) -> Dict[str, Any]:
    """
    Full pipeline execution for AI assistant user question answering.
    """
    intent, params = determine_intent(question)
    calculation_results = execute_analytics_for_intent(intent, params, transactions)
    answer = format_natural_explanation(question, intent, calculation_results, currency_symbol=currency_symbol, db=db)

    return {
        "question": question,
        "intent_detected": intent,
        "calculation_results": calculation_results,
        "answer": answer
    }
