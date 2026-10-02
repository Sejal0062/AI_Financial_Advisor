from agent.decision_engine import MultiFactorDecisionEngine

engine = MultiFactorDecisionEngine()

cases = [
    (
        "Negative cash flow",
        {
            "income": 40000, "expenses": 55000, "savings": 200000,
            "debt": 50000, "emergency_fund": 150000,
            "monthly_surplus": -15000, "income_change": 0, "expense_change": 0,
        },
    ),
    (
        "High debt",
        {
            "income": 100000, "expenses": 55000, "savings": 350000,
            "debt": 210000, "emergency_fund": 250000,
            "monthly_surplus": 45000, "income_change": 0, "expense_change": 0,
        },
    ),
    (
        "Income reduction",
        {
            "income": 70000, "expenses": 55000, "savings": 350000,
            "debt": 80000, "emergency_fund": 250000,
            "monthly_surplus": 15000, "income_change": -30, "expense_change": 0,
        },
    ),
]

for name, observation in cases:
    result = engine.evaluate(observation)
    print(f"\n{name}")
    print("Selected:", result["selected"]["key"])
    print("Score:", result["selected"]["score"])
    print("Factors:")
    for factor, values in result["factors"].items():
        print(f"  {factor}: {values['level']} ({values['score']})")

print("\nMULTI-FACTOR ENGINE TEST SUCCESSFUL")
