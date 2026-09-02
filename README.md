# MoneyLens AI — Vercel & Mobile-First Personal Expense Assistant

> **Tagline:** Understand your money. Make better decisions.

MoneyLens AI is a mobile-first, privacy-focused personal finance and analytics application that allows users to add expenses manually, upload CSV statements, automatically categorize spending, analyze finances, detect unusual transactions, and receive actionable financial insights.

The entire application runs **100% locally with zero paid services or external AI APIs** (No OpenAI, Gemini, Groq, Claude, bank APIs, or credentials required).

---

## 🌟 Key Architectural Features

- **Single Vercel Project Architecture**: Built with Vite React + TypeScript frontend and FastAPI Python backend using Vercel Serverless Functions (`api/index.py` & `vercel.json`).
- **Configurable API Routes**: Uses `/api/...` relative endpoint routes for Vercel deployment and dynamic `VITE_API_BASE_URL` for native Android WebView builds.
- **Vercel-Compatible Database Isolation**: Database access isolated in `backend/database.py` with automatic `/tmp/moneylens.db` fallback for Vercel serverless functions.
- **PWA Installation Experience**: Full Progressive Web App web manifest (`manifest.json`) and "Install MoneyLens App" experience on the Settings page.
- **Capacitor Android Packaging**: Native Android project configured (`com.moneylens.ai`) generating `MoneyLens-AI-debug.apk` without requiring Google Play Store publication.
- **Zero Paid / External AI APIs**: Rule-based Python categorizer, Pandas financial analytics, and Scikit-Learn IsolationForest anomaly detection running 100% local.

---

## 🛠️ Local Development

### 1. Frontend Setup & Execution
```bash
# Navigate to frontend folder
cd frontend

# Install Node dependencies
npm install

# Start Vite local development server
npm run dev
```

### 2. Backend Setup & Execution
```bash
# Navigate to backend folder
cd backend

# Install Python requirements
pip install -r requirements.txt

# Start FastAPI dev server with auto-reload
python -m uvicorn main:app --reload
```

---

## 🚀 Vercel Deployment Instructions

Deploying MoneyLens AI on Vercel is completely free and requires zero complex configuration:

1. Push your latest code to GitHub (`https://github.com/i-indhugit/MoneyLens.git`).
2. Log into **[https://vercel.com](https://vercel.com)** and click **Add New...** → **Project**.
3. Import your **`i-indhugit/MoneyLens`** repository.
4. Vercel automatically detects `vercel.json`:
   - **Framework Preset**: Vite
   - **Build Command**: `cd frontend && npm install && npm run build`
   - **Output Directory**: `frontend/dist`
5. Click **Deploy**.

Vercel will deploy your React frontend and expose your FastAPI backend serverless endpoints at `https://YOUR-PROJECT.vercel.app/api/...`.

---

## 📱 Progressive Web App (PWA) Installation

1. Open your deployed Vercel URL on your mobile phone or desktop browser.
2. Navigate to **Settings**.
3. Tap **Install App** (or use Chrome's "Add to Home Screen" / Safari's "Share -> Add to Home Screen").
4. MoneyLens AI will install directly to your home screen as a standalone application.

---

## 🤖 Android APK Generation & Personal Installation

You can generate the Android `.apk` file locally and install it directly on any Android phone for testing without publishing to Google Play Store:

```bash
# 1. Build React production bundle
cd frontend
npm run build

# 2. Sync web assets with native Android project
npx cap sync android

# 3. Compile debug APK using Gradle wrapper
cd android
.\gradlew assembleDebug
```

The compiled APK will be located at:
`frontend/android/app/build/outputs/apk/debug/app-debug.apk` (and copied to `MoneyLens-AI-debug.apk` in project root).

### Installing on Android Phone:
1. Transfer `MoneyLens-AI-debug.apk` to your phone via USB, Google Drive, or messaging.
2. Tap the `.apk` file on your phone and select **Install**.
3. Open **MoneyLens AI** from your phone app launcher!

---

## 🧪 Testing & Verification

```bash
# Run pytest test suite
python -m pytest backend/tests
```
