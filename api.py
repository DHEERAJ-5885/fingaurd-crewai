from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# 🔥 CORS FIX (important for frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------- INPUT MODEL --------
class FinanceInput(BaseModel):
    balance: int
    rent: int
    food: int
    upcoming: int
    spend: int
    future_spend: int
    months: int

# -------- ROOT --------
@app.get("/")
def home():
    return {"message": "FinGuard API is running 🚀"}

# -------- MAIN API --------
@app.post("/analyze")
def analyze_finance(data: FinanceInput):

    # 🔹 Basic validation (avoids weird UI bugs)
    if data.months <= 0:
        return {"error": "Months must be greater than 0"}

    # 🔹 Core calculations
    total_fixed = data.rent + data.food
    remaining = data.balance - total_fixed

    safe_spend = max(0, remaining - data.upcoming)

    monthly_expense = data.rent + data.food + data.upcoming
    projected_balance = data.balance - (monthly_expense * data.months)

    future_safe = max(0, projected_balance - data.future_spend)

    # 🔹 Risk logic
    if remaining < data.upcoming:
        risk = "HIGH"
    elif remaining == data.upcoming:
        risk = "MEDIUM"
    else:
        risk = "LOW"

    # 🔹 Decision logic
    decision = "NOT SAFE" if data.spend > safe_spend else "SAFE"
    future_decision = "NOT SAFE" if future_safe == 0 else "SAFE"

    # 🔹 Final response (UI-friendly)
    return {
        "remaining": remaining,
        "risk": risk,
        "safe_spend": safe_spend,
        "final_decision": decision,
        "future_decision": future_decision,
        "projected_balance": projected_balance
    }