from crewai import Agent, Task, Crew
import os

# 🔑 API KEY (keep yours here)
os.environ["GROQ_API_KEY"] = ""

# ✅ Model
llm = "groq/llama-3.1-8b-instant"

# ----------- USER INPUT -----------

balance = int(input("Enter your balance: "))
rent = int(input("Enter rent: "))
food = int(input("Enter food expense: "))
upcoming = int(input("Enter upcoming bill: "))
spend = int(input("How much do you want to spend? "))

# 🔮 FUTURE SIMULATION INPUT
future_spend = int(input("Planned future expense (trip etc): "))
months_ahead = int(input("After how many months? "))

# ----------- CORE CALCULATIONS (SOURCE OF TRUTH) -----------

total_expense = rent + food
remaining = balance - total_expense

safe_spend = max(0, remaining - upcoming)

monthly_expense = rent + food + upcoming
projected_balance = balance - (monthly_expense * months_ahead)
future_safe = max(0, projected_balance - future_spend)

# ----------- RISK ENGINE -----------

if remaining < upcoming:
    risk = "HIGH"
elif remaining == upcoming:
    risk = "MEDIUM"
else:
    risk = "LOW"

# ----------- DECISION ENGINE -----------

decision = "NOT SAFE" if spend > safe_spend else "SAFE"
future_decision = "NOT SAFE" if future_safe == 0 else "SAFE"

# ----------- AGENTS -----------

analyzer = Agent(
    role="Analyzer",
    goal="Return exact remaining balance",
    backstory="Strict accountant. Outputs only given numbers.",
    llm=llm,
    verbose=False,
    max_iter=1
)

predictor = Agent(
    role="Risk Explainer",
    goal="Explain risk without recalculating",
    backstory="Only explains based on given values. No math.",
    llm=llm,
    verbose=False,
    max_iter=1
)

decision_maker = Agent(
    role="Decision Explainer",
    goal="Explain decision using exact comparison",
    backstory="Follows strict comparison logic only.",
    llm=llm,
    verbose=False,
    max_iter=1
)

advisor = Agent(
    role="Financial Advisor",
    goal="Give realistic advice using exact values",
    backstory="Never invents numbers. Only uses given data.",
    llm=llm,
    verbose=False,
    max_iter=1
)

simulator = Agent(
    role="Future Simulator",
    goal="Explain future outcome strictly",
    backstory="Explains based only on projected values.",
    llm=llm,
    verbose=False,
    max_iter=1
)

# ----------- TASKS -----------

# Task 1
task1 = Task(
    description=f"""
    Remaining balance: {remaining}
    Output ONLY this number.
    """,
    expected_output="Number only",
    agent=analyzer
)

# Task 2
task2 = Task(
    description=f"""
    Remaining: {remaining}
    Upcoming: {upcoming}
    Risk: {risk}

    Explain in ONE SHORT LINE.
    Do NOT calculate.
    """,
    expected_output="One-line explanation",
    agent=predictor
)

# Task 3
task3 = Task(
    description=f"""
    Spend: {spend}
    Safe limit: {safe_spend}
    Decision: {decision}

    Output EXACT format:

    Spend (₹X) vs Safe Limit (₹Y) → RESULT because ...

    Replace X, Y, RESULT correctly.
    No extra text.
    """,
    expected_output="Strict comparison",
    agent=decision_maker
)

# Task 4
task4 = Task(
    description=f"""
    DATA:
    Safe spend: {safe_spend}
    Decision: {decision}

    RULES:

    If safe_spend == 0:
        Warning: Cannot afford any spending.
        Suggestion: Delay completely.

    If NOT SAFE:
        Warning: Overspending.
        Suggestion: Reduce to ₹{safe_spend}

    If SAFE:
        Warning: Within safe limit.
        Suggestion: Spend up to 70% of ₹{safe_spend}

    IMPORTANT:
    - No extra numbers
    - No recalculation
    - Keep it short

    OUTPUT:

    Warning:
    Suggestion:
    Future Tip:
    """,
    expected_output="Controlled advice",
    agent=advisor
)

# Task 5
task5 = Task(
    description=f"""
    FUTURE RESULT:

    Projected balance: {projected_balance}
    Future safe: {future_safe}
    Final decision: {future_decision}

    RULES (STRICT):

    - DO NOT think
    - DO NOT calculate
    - DO NOT change decision

    If decision is NOT SAFE:
        Explain that future expenses exceed balance

    If decision is SAFE:
        Explain that balance is sufficient

    OUTPUT:
    One line explanation ONLY.
    """,
    expected_output="Strict explanation only",
    agent=simulator
)
# ----------- CREW -----------

crew = Crew(
    agents=[analyzer, predictor, decision_maker, advisor, simulator],
    tasks=[task1, task2, task3, task4, task5],
    memory=False,
    verbose=False
)

# ----------- RUN -----------

if __name__ == "__main__":
    result = crew.kickoff()

    print("\n========== FINAL OUTPUT ==========\n")

    print(f"Remaining Balance: ₹{remaining}")
    print(f"Risk Level: {risk}")
    print(f"Safe Spend: ₹{safe_spend}")
    print(f"Final Decision: {decision}")

    print("\n🔮 FUTURE SIMULATION 🔮")
    print(f"Projected Balance: ₹{projected_balance}")
    print(f"Future Safe Balance: ₹{future_safe}")
    print(f"Future Decision: {future_decision}")

    for i, res in enumerate(result.tasks_output):
        print(f"\n--- Task {i+1} Output ---\n")
        print(res)