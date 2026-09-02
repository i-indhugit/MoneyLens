import re

"""
Rule-Based Categorization System
Easily customizable keyword mapping dictionary for beginner developers.
"""

CATEGORY_KEYWORDS = {
    "Food": [
        "swiggy", "zomato", "restaurant", "cafe", "mcdonald", "starbucks",
        "domino", "pizza", "burger", "biryani", "bakery", "kfc", "subway",
        "dunkin", "groceries", "supermarket", "bigbasket", "blinkit", "zepto",
        "grofers", "smart fresh", "d mart", "dmart", "food"
    ],
    "Travel": [
        "uber", "ola", "rapido", "cab", "taxi", "metro", "fuel", "petrol",
        "diesel", "shell", "hpcl", "bpcl", "toll", "parking", "flight",
        "indigo", "air india", "train", "irctc", "bus", "redbus", "travel"
    ],
    "Shopping": [
        "amazon", "flipkart", "myntra", "ajio", "zara", "h&m", "trends",
        "apparel", "clothing", "electronics", "watch", "luxury", "footwear",
        "shopping"
    ],
    "Entertainment": [
        "netflix", "spotify", "prime video", "hotstar", "youtube", "pvr",
        "inox", "cinema", "movie", "bookmyshow", "concert", "game", "gaming",
        "fun", "entertainment"
    ],
    "Bills": [
        "electricity", "water utility", "broadband", "fiber", "airtel", "jio",
        "vi bill", "gas cylinder", "recharge", "utility", "phone bill", "bills"
    ],
    "Healthcare": [
        "pharmacy", "hospital", "clinic", "doctor", "apollo", "medplus",
        "1mg", "dental", "lab", "pathology", "medical", "healthcare"
    ],
    "Housing": [
        "rent", "house rent", "maintenance fee", "landlord", "housing", "society"
    ],
    "Education": [
        "udemy", "coursera", "school", "college", "tuition", "books", "course",
        "fee", "education"
    ],
    "Income": [
        "salary", "payroll", "stipend", "freelance", "dividend", "interest credit", "bonus"
    ]
}

def categorize_transaction(description: str, transaction_type: str = "expense") -> str:
    """
    Categorizes a transaction based on description keyword rules.
    If no rule matches, returns 'Income' for income transactions or 'Other' for expenses.
    """
    if transaction_type == "income":
        return "Income"

    if not description:
        return "Other"

    desc_lower = description.lower().strip()

    for category, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            pattern = r'\b' + re.escape(kw) + r'\b'
            if re.search(pattern, desc_lower) or kw in desc_lower:
                return category

    return "Other"
