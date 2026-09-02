import pytest
from fastapi.testclient import TestClient

from main import app
from services.csv_parser import parse_csv_file
from services.categorizer import categorize_transaction
from services.analytics import (
    db_txs_to_df, get_total_income, get_total_expenses, get_remaining_balance,
    get_category_spending, get_monthly_spending
)
from services.anomaly_detector import detect_unusual_transactions
from services.insights import generate_financial_insights, calculate_money_mood
from services.question_engine import answer_user_question

client = TestClient(app)

def test_categorization_rules():
    assert categorize_transaction("Swiggy Biryani Order") == "Food"
    assert categorize_transaction("Zomato Dinner") == "Food"
    assert categorize_transaction("Uber Auto Ride") == "Travel"
    assert categorize_transaction("Ola Cab") == "Travel"
    assert categorize_transaction("Amazon Electronics") == "Shopping"
    assert categorize_transaction("Flipkart Fashion") == "Shopping"
    assert categorize_transaction("Netflix Subscription") == "Entertainment"
    assert categorize_transaction("Spotify Premium") == "Entertainment"
    assert categorize_transaction("Apollo Pharmacy") == "Healthcare"
    assert categorize_transaction("Electricity Power Bill") == "Bills"
    assert categorize_transaction("House Rent Payment") == "Housing"
    assert categorize_transaction("Monthly Payroll Salary", "income") == "Income"
    assert categorize_transaction("Random Unmatched Merchant 123") == "Other"

def test_csv_parser_valid_and_invalid():
    valid_csv = b"Date,Description,Amount\n2026-09-01,Swiggy,450\n2026-09-02,Uber,250\n"
    records = parse_csv_file(valid_csv)
    assert len(records) == 2
    assert records[0]["category"] == "Food"
    assert records[1]["category"] == "Travel"

    invalid_csv = b"Date,Description,Quantity\n2026-09-01,Swiggy,2\n"
    with pytest.raises(ValueError) as excinfo:
        parse_csv_file(invalid_csv)
    assert "We couldn't find an Amount column" in str(excinfo.value)

def test_analytics_math():
    txs = [
        {"id": "1", "date": "2026-09-01", "description": "Salary", "amount": 30000.0, "transaction_type": "income", "category": "Income"},
        {"id": "2", "date": "2026-09-02", "description": "Swiggy", "amount": 450.0, "transaction_type": "expense", "category": "Food"},
        {"id": "3", "date": "2026-09-03", "description": "Amazon", "amount": 1200.0, "transaction_type": "expense", "category": "Shopping"},
    ]
    df = db_txs_to_df(txs)
    assert get_total_income(df) == 30000.0
    assert get_total_expenses(df) == 1650.0
    assert get_remaining_balance(df) == 28350.0

def test_money_mood_engine():
    txs = [
        {"id": "1", "date": "2026-09-01", "description": "Salary", "amount": 30000.0, "transaction_type": "income", "category": "Income"},
        {"id": "2", "date": "2026-09-02", "description": "Rent", "amount": 8500.0, "transaction_type": "expense", "category": "Housing"},
    ]
    df = db_txs_to_df(txs)
    mood_res = calculate_money_mood(df)
    assert "mood" in mood_res
    assert "Balanced" in mood_res["mood"]

def test_question_engine():
    txs = [
        {"id": "1", "date": "2026-09-01", "description": "Salary", "amount": 30000.0, "transaction_type": "income", "category": "Income"},
        {"id": "2", "date": "2026-09-02", "description": "Swiggy", "amount": 450.0, "transaction_type": "expense", "category": "Food"},
    ]

    q1 = answer_user_question("How much did I spend on food?", txs)
    assert "₹450.00" in q1["answer"]

    q2 = answer_user_question("What is my balance?", txs)
    assert "₹29,550.00" in q2["answer"]

def test_api_endpoints():
    res = client.get("/")
    assert res.status_code == 200
    assert "MoneyLens AI MVP" in res.json()["app"]

    res_insights = client.get("/insights")
    assert res_insights.status_code == 200
    assert "money_mood" in res_insights.json()
