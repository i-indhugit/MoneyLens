from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from app.database.session import init_db
from app.api.routers import imports, transactions, analytics, assistant, system

app = FastAPI(
    title="MoneyLens AI Backend API",
    description="Privacy-first AI-powered personal expense analysis and natural language assistant API",
    version="1.0.0"
)

# Configure CORS
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database tables on startup
@app.on_event("startup")
def startup_event():
    init_db()

# Include routers
app.include_router(imports.router)
app.include_router(transactions.router)
app.include_router(analytics.router)
app.include_router(assistant.router)
app.include_router(system.router)

@app.get("/")
def root():
    return {
        "status": "online",
        "app": "MoneyLens AI Backend",
        "version": "1.0.0",
        "privacy": "MoneyLens AI does not require or request banking credentials."
    }
