from services.financial_service import FinancialService


# ============================================================
# CREATE SERVICE
# ============================================================

service = FinancialService()


# ============================================================
# LOAD USER DATA
# ============================================================

user_id = 1

data = service.load_user_financial_data(
    user_id
)


# ============================================================
# GET STATE
# ============================================================

state = data["state"]

print("\n")
print("=" * 60)
print("LOADED FINANCIAL STATE")
print("=" * 60)

print(
    f"Income:          ₹{state.income:,.2f}"
)

print(
    f"Expenses:        ₹{state.expenses:,.2f}"
)

print(
    f"Savings:         ₹{state.savings:,.2f}"
)

print(
    f"Debt:            ₹{state.debt:,.2f}"
)

print(
    f"Emergency Fund:  ₹{state.emergency_fund:,.2f}"
)

print(
    f"Risk Preference: {state.risk_preference}"
)


# ============================================================
# GET GOALS
# ============================================================

goal_manager = data["goal_manager"]

print("\n")
print("=" * 60)
print("LOADED FINANCIAL GOALS")
print("=" * 60)

for goal in goal_manager.get_goals():

    print(
        f"\nGoal: {goal.name}"
    )

    print(
        f"Target: ₹{goal.target_amount:,.2f}"
    )

    print(
        f"Current: ₹{goal.current_amount:,.2f}"
    )

    print(
        f"Progress: {goal.get_progress():.1f}%"
    )

    print(
        f"Priority: {goal.priority}"
    )


print("\n")
print("=" * 60)
print("FINANCIAL SERVICE TEST SUCCESSFUL")
print("=" * 60)