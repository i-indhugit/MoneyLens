# MoneyLens AI — Personal Expense & Financial Insights Assistant

> **Tagline:** Understand your money. Make better decisions.

MoneyLens AI is a mobile-first, privacy-focused personal finance and analytics application that allows users to add expenses manually, upload CSV statements, automatically categorize spending, analyze finances, detect unusual transactions, and receive actionable financial insights.

The entire application runs **100% locally with zero paid services or external AI APIs** (No OpenAI, Gemini, Groq, Claude, bank APIs, or credentials required).

---

## 🌟 Key Features

- **Professional Fintech SaaS UI**: Light gray background, deep navy primary, slate text, teal accents, and financial metric hierarchy.
- **Single-Application Deployment**: FastAPI serves the built React static frontend at `/` so the application deploys on one single web URL.
- **PWA & Android APK**: Built with Progressive Web App manifest and Capacitor (`com.moneylens.ai`) to generate installable Android APKs.
- **CSV Import Validation**: Robust CSV parser with error detection for missing Amount columns or malformed files.
- **Keyword Categorization**: Case-insensitive Python categorizer mapping transactions to `Food`, `Travel`, `Shopping`, `Entertainment`, `Bills`, `Healthcare`, `Housing`, `Education`, `Income`, and `Other`.
- **Pandas Analytics**: Automated calculation of Total Income, Total Expenses, Balance, Average Expense, Highest Expense, Top Spending Category, and Monthly Spending Trends.
- **IsolationForest Anomaly Detection**: Scikit-Learn machine learning outlier detection to flag unusual transactions safely.
- **MoneyLens Insights & Money Health**: Automated rule-based financial insights engine.
- **Ask MoneyLens Assistant**: Local keyword intent matching question interface.
- **Privacy Guarantee**: 100% local processing with full data deletion support.

---

## 🛠️ Technology Stack

- **Frontend**: React 18, TypeScript, Tailwind CSS, Vite, Recharts, Lucide Icons, PWA Support.
- **Mobile Packaging**: Capacitor Android (`@capacitor/core`, `@capacitor/android`, `@capacitor/cli`).
- **Backend**: Python 3.12, FastAPI, Pandas, Scikit-Learn, SQLAlchemy, SQLite (`moneylens.db`).
- **Testing**: Pytest unit & API test suite.

---

## 🚀 Quick Setup & Local Execution

### 1. Prerequisites
- Python 3.10+
- Node.js 18+ and `npm`

### 2. Backend Setup
```bash
# Navigate to backend directory
cd backend

# Install dependencies
pip install -r requirements.txt

# Run FastAPI server
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

### 3. Frontend Development Server
```bash
# Open a new terminal and navigate to frontend directory
cd frontend

# Install npm dependencies
npm install

# Run Vite dev server
npm run dev
```
Open `http://localhost:5173/` in your browser.

---

## 📱 Building Single App Deployment & Android APK

### Single Web Application Build
To serve the frontend directly from FastAPI on a single port (`http://127.0.0.1:8000/`):
```bash
cd frontend
npm run build
```
FastAPI automatically detects `frontend/dist` and serves the static files at `/` with API endpoints routed under `/api/...`.

### Building Android APK (Capacitor)
```bash
cd frontend

# 1. Build web production bundle
npm run build

# 2. Sync build with native Android project
npx cap sync android

# 3. Open project in Android Studio to build APK
npx cap open android
```

---

## 🧪 Running Automated Tests

```bash
# Run pytest backend suite
python -m pytest backend/tests
```

---

## 🔒 Privacy Guarantee

MoneyLens AI MVP does not use external AI APIs or remote LLMs. All financial calculations, categorizations, insights, and anomaly detections are performed locally using Python, Pandas, Scikit-learn, and rule-based application logic.

No bank credentials, card numbers, or API keys are ever requested or transmitted.
