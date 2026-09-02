import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from typing import List, Dict, Any
from app.models.schemas import AnomalyItem
from app.analytics.engine import transactions_to_df

def detect_anomalies(transactions: List[Any], contamination: float = 0.05) -> List[AnomalyItem]:
    """
    Detects unusual transactions using IsolationForest combined with category baseline IQR.
    Returns a list of AnomalyItem objects with clear explanations.
    """
    df = transactions_to_df(transactions)
    expenses = df[df["transaction_type"] == "expense"].copy()

    if len(expenses) < 3:
        return []

    anomalies: List[AnomalyItem] = []

    # Calculate overall baseline stats per category
    category_baselines = {}
    for cat, group in expenses.groupby("category"):
        amounts = group["amount"].values
        mean_val = float(np.mean(amounts))
        median_val = float(np.median(amounts))
        q75, q25 = np.percentile(amounts, [75, 25])
        iqr = q75 - q25
        category_baselines[cat] = {
            "mean": mean_val,
            "median": median_val,
            "q75": q75,
            "upper_bound": max(q75 + 1.5 * iqr, median_val * 2.5)
        }

    # Prepare features for Isolation Forest (Amount, Log Amount, Category Mean Ratio)
    features = []
    for _, row in expenses.iterrows():
        amt = float(row["amount"])
        cat = row["category"]
        base_median = category_baselines.get(cat, {}).get("median", amt)
        ratio = amt / base_median if base_median > 0 else 1.0
        features.append([amt, np.log1p(amt), ratio])

    X = np.array(features)

    # Fit IsolationForest
    # Adjust contamination based on dataset size
    cont = min(max(3 / len(expenses), 0.03), 0.15)
    model = IsolationForest(contamination=cont, random_state=42)
    predictions = model.fit_predict(X)  # -1 for anomaly, 1 for normal
    raw_scores = -model.score_samples(X)  # Higher raw score = more anomalous

    for i, (_, row) in enumerate(expenses.iterrows()):
        amt = float(row["amount"])
        cat = row["category"]
        is_iso_anomaly = (predictions[i] == -1)
        
        baseline = category_baselines.get(cat, {})
        median_val = baseline.get("median", amt)
        upper_bound = baseline.get("upper_bound", amt * 2.0)

        # Flag as anomaly if IsolationForest flags it OR amount > 3x category median / upper bound
        if is_iso_anomaly or (amt > upper_bound and amt > 3000):
            score = float(raw_scores[i])
            normalized_score = min(max(round((score - 0.4) / 0.4, 2), 0.55), 0.99)
            
            mult = round(amt / median_val, 1) if median_val > 0 else 2.0
            
            if mult >= 2.0:
                explanation = f"This transaction of ₹{amt:,.2f} is significantly higher ({mult}x) than your typical '{cat}' spending (avg ₹{median_val:,.2f})."
            else:
                explanation = f"This transaction of ₹{amt:,.2f} is unusually large relative to your overall spending pattern."

            item = AnomalyItem(
                id=str(row["id"]),
                date=str(row["date"]),
                description=str(row["description"]),
                amount=round(amt, 2),
                category=str(cat),
                anomaly_score=normalized_score,
                explanation=explanation
            )
            anomalies.append(item)

    # Sort by anomaly score descending
    anomalies.sort(key=lambda x: x.anomaly_score, reverse=True)
    return anomalies
