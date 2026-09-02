import re
from typing import Tuple, Dict
from sqlalchemy.orm import Session
from app.models.db import DBCategoryRule

# Standard built-in keyword dictionary mapping keyword substrings to categories
DEFAULT_KEYWORD_MAP: Dict[str, str] = {
    # Food & Dining
    "swiggy": "Food",
    "zomato": "Food",
    "starbucks": "Food",
    "mcdonald": "Food",
    "domino": "Food",
    "pizza": "Food",
    "restaurant": "Food",
    "cafe": "Food",
    "biryani": "Food",
    "bakery": "Food",
    "kfc": "Food",
    "subway": "Food",
    "dunkin": "Food",

    # Groceries
    "grocery": "Groceries",
    "groceries": "Groceries",
    "supermarket": "Groceries",
    "bigbasket": "Groceries",
    "grofers": "Groceries",
    "blinkit": "Groceries",
    "zepto": "Groceries",
    "smart fresh": "Groceries",
    "reliance fresh": "Groceries",
    "d mart": "Groceries",
    "dmart": "Groceries",
    "nature basket": "Groceries",
    "mart": "Groceries",

    # Transport
    "uber": "Transport",
    "ola": "Transport",
    "rapido": "Transport",
    "cab": "Transport",
    "taxi": "Transport",
    "metro": "Transport",
    "fuel": "Transport",
    "petrol": "Transport",
    "diesel": "Transport",
    "shell station": "Transport",
    "hpcl": "Transport",
    "bpcl": "Transport",
    "toll": "Transport",
    "parking": "Transport",

    # Shopping
    "amazon": "Shopping",
    "flipkart": "Shopping",
    "myntra": "Shopping",
    "ajio": "Shopping",
    "zara": "Shopping",
    "h&m": "Shopping",
    "trends": "Shopping",
    "apparel": "Shopping",
    "clothing": "Shopping",
    "electronics": "Shopping",
    "watch": "Shopping",
    "luxury": "Shopping",

    # Subscriptions
    "netflix": "Subscriptions",
    "spotify": "Subscriptions",
    "prime video": "Subscriptions",
    "hotstar": "Subscriptions",
    "youtube": "Subscriptions",
    "apple": "Subscriptions",
    "cloud": "Subscriptions",
    "chatgpt": "Subscriptions",

    # Bills & Utilities
    "electricity": "Bills & Utilities",
    "water utility": "Bills & Utilities",
    "broadband": "Bills & Utilities",
    "fiber": "Bills & Utilities",
    "airtel": "Bills & Utilities",
    "jio": "Bills & Utilities",
    "vi bill": "Bills & Utilities",
    "gas cylinder": "Bills & Utilities",
    "mobile recharge": "Bills & Utilities",

    # Healthcare
    "pharmacy": "Healthcare",
    "hospital": "Healthcare",
    "clinic": "Healthcare",
    "doctor": "Healthcare",
    "apollo": "Healthcare",
    "medplus": "Healthcare",
    "1mg": "Healthcare",
    "dental": "Healthcare",
    "pathology": "Healthcare",

    # Rent & Housing
    "rent": "Rent",
    "house rent": "Rent",
    "landlord": "Rent",
    "maintenance fee": "Rent",

    # Entertainment
    "pvr": "Entertainment",
    "inox": "Entertainment",
    "cinema": "Entertainment",
    "movie": "Entertainment",
    "bookmyshow": "Entertainment",
    "concert": "Entertainment",
    "bowling": "Entertainment",

    # Education
    "udemy": "Education",
    "coursera": "Education",
    "school": "Education",
    "college": "Education",
    "tuition": "Education",
    "books": "Education",

    # Travel
    "flight": "Travel",
    "indigo": "Travel",
    "air india": "Travel",
    "hotel": "Travel",
    "resort": "Travel",
    "airbnb": "Travel",
    "makemytrip": "Travel",
    "goibibo": "Travel",
    "yatra": "Travel",

    # Income Keywords
    "salary": "Salary",
    "payroll": "Salary",
    "stipend": "Salary",
    "freelance": "Salary",
    "dividend": "Investment",
}

def categorize_description(description: str, db: Session = None) -> Tuple[str, float]:
    """
    Categorizes a transaction description.
    First checks database user overrides, then default keyword rules, then falls back to 'Other'.
    Returns (category_name, confidence_score).
    """
    if not description:
        return "Other", 0.5

    clean_desc = description.lower().strip()

    # 1. Check user override rules from DB
    if db is not None:
        try:
            overrides = db.query(DBCategoryRule).all()
            for rule in overrides:
                if rule.keyword.lower() in clean_desc:
                    return rule.category, 0.98
        except Exception:
            pass

    # 2. Check default keyword map
    for keyword, cat in DEFAULT_KEYWORD_MAP.items():
        if keyword in clean_desc:
            return cat, 0.90

    # 3. Fallback heuristic matching based on regex words
    words = re.findall(r'\b[a-zA-Z]{3,}\b', clean_desc)
    for word in words:
        if word in DEFAULT_KEYWORD_MAP:
            return DEFAULT_KEYWORD_MAP[word], 0.75

    return "Other", 0.50

def add_or_update_user_category_rule(db: Session, keyword: str, category: str):
    """
    Saves a user category preference to improve future auto-categorization.
    """
    clean_keyword = keyword.lower().strip()
    rule = db.query(DBCategoryRule).filter(DBCategoryRule.keyword == clean_keyword).first()
    if rule:
        rule.category = category
        rule.is_user_override = True
    else:
        rule = DBCategoryRule(keyword=clean_keyword, category=category, is_user_override=True)
        db.add(rule)
    db.commit()
