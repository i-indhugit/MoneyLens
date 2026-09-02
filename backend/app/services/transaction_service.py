from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.models.db import DBTransaction, DBCategoryRule, DBUserSettings
from app.models.schemas import TransactionCreate, TransactionUpdate, ParsedTransaction
from app.analytics.engine import (
    transactions_to_df, get_total_expenses, get_total_income, get_net_cash_flow,
    get_average_transaction, get_average_daily_spending, get_largest_transaction,
    get_smallest_transaction, get_category_spending, get_monthly_spending,
    get_top_expenses, get_month_comparison, get_weekend_spending, get_subscription_spending
)
from app.anomaly.detector import detect_anomalies
from app.categorization.engine import add_or_update_user_category_rule

def get_all_transactions(db: Session) -> List[DBTransaction]:
    return db.query(DBTransaction).order_by(DBTransaction.date.desc()).all()

def create_transaction(db: Session, tx_in: TransactionCreate) -> DBTransaction:
    db_tx = DBTransaction(
        date=tx_in.date,
        description=tx_in.description,
        amount=tx_in.amount,
        transaction_type=tx_in.transaction_type,
        category=tx_in.category,
        source=tx_in.source,
        confidence=tx_in.confidence
    )
    db.add(db_tx)
    db.commit()
    db.refresh(db_tx)
    return db_tx

def bulk_create_transactions(db: Session, tx_list: List[TransactionCreate]) -> int:
    db_objs = []
    for item in tx_list:
        db_objs.append(DBTransaction(
            date=item.date,
            description=item.description,
            amount=item.amount,
            transaction_type=item.transaction_type,
            category=item.category,
            source=item.source,
            confidence=item.confidence
        ))
    db.bulk_save_objects(db_objs)
    db.commit()
    return len(db_objs)

def update_transaction(db: Session, tx_id: str, tx_update: TransactionUpdate) -> Optional[DBTransaction]:
    tx = db.query(DBTransaction).filter(DBTransaction.id == tx_id).first()
    if not tx:
        return None

    update_data = tx_update.model_dump(exclude_unset=True)
    
    # If category changed by user, store keyword rule for future categorization!
    if "category" in update_data and update_data["category"] != tx.category:
        add_or_update_user_category_rule(db, tx.description, update_data["category"])

    for key, value in update_data.items():
        setattr(tx, key, value)

    db.commit()
    db.refresh(tx)
    return tx

def delete_transaction(db: Session, tx_id: str) -> bool:
    tx = db.query(DBTransaction).filter(DBTransaction.id == tx_id).first()
    if not tx:
        return False
    db.delete(tx)
    db.commit()
    return True

def delete_all_user_data(db: Session) -> bool:
    """Wipes all user transaction records, rules, and resets default settings."""
    try:
        db.query(DBTransaction).delete()
        db.query(DBCategoryRule).delete()
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        return False

def get_financial_summary(db: Session) -> Dict[str, Any]:
    txs = get_all_transactions(db)
    df = transactions_to_df(txs)

    tot_exp = get_total_expenses(df)
    tot_inc = get_total_income(df)
    net_cf = get_net_cash_flow(df)
    avg_tx = get_average_transaction(df)
    avg_daily = get_average_daily_spending(df)
    largest = get_largest_transaction(df)
    smallest = get_smallest_transaction(df)

    cat_spending = get_category_spending(df)
    cat_count = len(cat_spending.get("categories", []))

    mom = get_month_comparison(df)

    return {
        "total_expenses": tot_exp,
        "total_income": tot_inc,
        "net_cash_flow": net_cf,
        "average_transaction": avg_tx,
        "average_daily_spending": avg_daily,
        "largest_transaction": largest,
        "smallest_transaction": smallest,
        "transaction_count": len(txs),
        "category_count": cat_count,
        "current_month_spending": mom.get("current_month_spending", 0.0),
        "previous_month_spending": mom.get("previous_month_spending", 0.0),
        "month_over_month_change_pct": mom.get("change_pct", 0.0)
    }

def get_automated_insights(db: Session) -> Dict[str, Any]:
    txs = get_all_transactions(db)
    df = transactions_to_df(txs)
    
    settings = db.query(DBUserSettings).filter(DBUserSettings.id == 1).first()
    currency = settings.currency if settings else "₹"

    insights = []
    savings_suggestions = []

    if df.empty:
        return {
            "insights": [
                {
                    "type": "breakdown",
                    "title": "No Transactions Imported",
                    "description": "Import a CSV, Excel, or PDF bank statement to generate dynamic financial insights.",
                    "impact_amount": None,
                    "category": None
                }
            ],
            "savings_suggestions": [],
            "disclaimer": "MoneyLens AI provides spending insights based on transaction data and is not professional financial advice."
        }

    # 1. Largest category insight
    cats = get_category_spending(df).get("categories", [])
    if cats:
        top_cat = cats[0]
        insights.append({
            "type": "breakdown",
            "title": f"Top Category: {top_cat['category']}",
            "description": f"{top_cat['category']} accounts for {top_cat['percentage']}% of your total expenses ({currency}{top_cat['total_amount']:,.2f}).",
            "impact_amount": top_cat["total_amount"],
            "category": top_cat["category"]
        })

    # 2. Month-over-Month change
    mom = get_month_comparison(df)
    if mom.get("previous_month"):
        chg = mom.get("change_pct", 0.0)
        direction = "increased" if chg >= 0 else "decreased"
        insights.append({
            "type": "trend",
            "title": "Month-over-Month Spending Trend",
            "description": f"Spending in {mom.get('current_month')} has {direction} by {abs(chg)}% compared with {mom.get('previous_month')}.",
            "impact_amount": abs(mom.get("current_month_spending", 0) - mom.get("previous_month_spending", 0)),
            "category": None
        })

    # 3. Subscriptions alert
    subs = get_subscription_spending(df)
    if subs.get("total_subscriptions", 0) > 0:
        insights.append({
            "type": "trend",
            "title": "Recurring Subscriptions",
            "description": f"You spend {currency}{subs['total_subscriptions']:,.2f} across {subs['count']} recurring digital subscription services.",
            "impact_amount": subs['total_subscriptions'],
            "category": "Subscriptions"
        })

    # 4. Weekend ratio alert
    wknd = get_weekend_spending(df)
    if wknd.get("weekend_pct", 0) > 35.0:
        insights.append({
            "type": "alert",
            "title": "High Weekend Spending",
            "description": f"Weekend spending represents {wknd['weekend_pct']}% of your total expenses ({currency}{wknd['weekend_total']:,.2f}).",
            "impact_amount": wknd['weekend_total'],
            "category": None
        })

    # 5. Anomalies count alert
    anoms = detect_anomalies(txs)
    if anoms:
        insights.append({
            "type": "alert",
            "title": "Unusual Transactions Flagged",
            "description": f"MoneyLens AI detected {len(anoms)} unusual transaction(s) relative to your normal spending baseline.",
            "impact_amount": sum(a.amount for a in anoms),
            "category": None
        })

    # 6. Savings calculation (Deterministic 20% potential savings on non-fixed top categories)
    for c in cats[:3]:
        cat_name = c["category"]
        if cat_name not in ["Rent", "Salary", "Healthcare"]:
            curr_amt = c["total_amount"]
            pot_save = round(curr_amt * 0.20, 2)
            savings_suggestions.append({
                "category": cat_name,
                "current_spending": curr_amt,
                "potential_savings": pot_save,
                "suggestion": f"Based on your recent spending, reducing {cat_name} expenses by 20% could potentially save approximately {currency}{pot_save:,.2f} per month."
            })

    return {
        "insights": insights,
        "savings_suggestions": savings_suggestions,
        "disclaimer": "MoneyLens AI provides spending insights based on transaction data and is not professional financial advice."
    }
