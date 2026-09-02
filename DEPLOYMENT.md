# MoneyLens AI — Deployment Guide

Because **MoneyLens AI** is configured as a **single unified application** (FastAPI backend serving the built React static frontend), you can deploy the entire application to the web for **100% FREE** using any of the platforms below.

---

## 🚀 Option 1: Render.com (Recommended — 100% Free Web Host)

Render provides a free Web Service tier that will run both your FastAPI backend and React frontend under one free domain (e.g. `https://moneylens-ai.onrender.com`).

### Steps to Deploy on Render:
1. Go to [https://render.com](https://render.com) and sign up for a free account.
2. Click **New +** → **Web Service**.
3. Connect your GitHub repository: `https://github.com/i-indhugit/MoneyLens.git`.
4. Configure the Web Service settings:
   - **Name**: `moneylens-ai`
   - **Environment**: `Python 3`
   - **Region**: Select closest region (e.g. Singapore or Frankfurt)
   - **Branch**: `main`
   - **Build Command**:
     ```bash
     cd frontend && npm install && npm run build && cd ../backend && pip install -r requirements.txt
     ```
   - **Start Command**:
     ```bash
     cd backend && python -m uvicorn main:app --host 0.0.0.0 --port $PORT
     ```
   - **Instance Type**: `Free`
5. Click **Create Web Service**.

Render will automatically build your React frontend, install Python dependencies, and launch FastAPI serving your application live with free HTTPS!

---

## ⚡ Option 2: Railway.app (1-Click Deployment)

Railway provides simple automated deployments directly from GitHub repositories:

1. Sign up at [https://railway.app](https://railway.app) using your GitHub account.
2. Click **New Project** → **Deploy from GitHub Repo**.
3. Select `i-indhugit/MoneyLens`.
4. Add environment variables if needed (none required for local SQLite).
5. Railway will automatically build and assign a free `https://moneylens-production.up.railway.app` URL.

---

## 📱 Option 3: Android Phone (Installing Native APK)

To install MoneyLens AI directly on your Android phone as a native mobile app:

1. Open your terminal in `c:\Users\INDU\Desktop\MoneyLens\frontend`:
   ```bash
   npm run build
   npx cap sync android
   npx cap open android
   ```
2. Android Studio will open the native Android project.
3. In Android Studio, go to top menu: **Build** → **Build Bundle(s) / APK(s)** → **Build APK(s)**.
4. Locate the generated `.apk` file in `frontend/android/app/build/outputs/apk/debug/app-debug.apk`.
5. Transfer `app-debug.apk` to your Android phone via USB, Google Drive, or WhatsApp, and tap to install!

---

## 🌐 Option 4: Local Network Access (Testing on Mobile Phone via Wi-Fi)

You can also test MoneyLens AI directly on your phone connected to the same Wi-Fi network:

1. Find your computer's local Wi-Fi IP address:
   ```cmd
   ipconfig
   ```
   *(Look for `IPv4 Address`, e.g., `192.168.1.10`)*
2. Start FastAPI listening on all local network interfaces:
   ```bash
   cd backend
   python -m uvicorn main:app --host 0.0.0.0 --port 8000
   ```
3. Open your mobile phone browser and visit: `http://192.168.1.10:8000/`
