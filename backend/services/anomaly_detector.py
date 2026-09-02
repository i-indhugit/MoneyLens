import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from typing import List, Dict, Any
from services.analytics import db_txs_to_df

def detect_unusual_transactions(transactions: List[Any]) -> Dict[str, Any]:
    """
    Detects unusual transactions using Scikit-Learn IsolationForest.
    Returns flagged transactions list or insufficient data message.
    """
    df = db_txs_to_df(transactions)
    exp = df[df["transaction_type"] == "expense"].copy()

    # Graceful message if too few transactions
    if len(exp) < 5:
        return {
            "total_anomalies": 0,
            "anomalies": [],
            "message": "Add more transactions to improve unusual spending detection."
        }

    # Features: Amount & Log Amount
    amounts = exp["amount"].values.reshape(-1, 1)
    log_amounts = np.log1p(amounts)
    X = np.hstack([amounts, log_amounts])

    # Contamination threshold
    cont = min(max(2 / len(exp), 0.05), 0.15)
    model = IsolationForest(contamination=cont, random_state=42)
    preds = model.fit_predict(X)  # -1 for anomaly, 1 for normal

    anomalies = []
    category_medians = exp.groupby("category")["amount"].median().to_dict()

    for idx, (_, row) in enumerate(exp.iterrows()):
        amt = float(row["amount"])
        cat = str(row["category"])
        cat_median = category_medians.get(cat, amt)

        is_iso_anomaly = (preds[idx] == -1)
        is_large_outlier = (amt > cat_median * 2.5 and amt > 1500)

        if is_iso_anomaly or is_large_outlier:
            reason = f"This transaction of ₹{amt:,.2f} looks unusual compared with your normal spending (avg for {cat} is ~₹{cat_median:,.2f})."
            anomalies.append({
                "id": str(row["id"]),
                "date": str(row["date"]),
                "description": str(row["description"]),
                "amount": round(amt, 2),
                "category": cat,
                "reason": reason
            })

    # Sort largest amount first
    anomalies.sort(key=lambda x: x["amount"], reverse=True)

    return {
        "total_anomalies": len(anomalies),
        "anomalies": anomalies,
        "message": None
    }
