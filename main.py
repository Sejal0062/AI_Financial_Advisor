from database.database import FinancialDatabase
from services.financial_service import FinancialService
from agent.financial_agent import FinancialAgent


# ============================================================
# DISPLAY AGENT RESULT
# ============================================================

def display_result(month, result):

    observation = result["observation"]
    decision = result["decision"]

    print("\n")
    print("=" * 65)
    print(f"                         MONTH {month}")
    print("=" * 65)

    print("\nCURRENT FINANCIAL ENVIRONMENT")
    print("-" * 45)

    print(f"Income:          ₹{observation['income']:,.2f}")
    print(f"Expenses:        ₹{observation['expenses']:,.2f}")

    print(
        f"Monthly Surplus: ₹"
        f"{observation['monthly_surplus']:,.2f}"
    )

    print(f"Savings:         ₹{observation['savings']:,.2f}")
    print(f"Debt:            ₹{observation['debt']:,.2f}")

    print(
        f"Emergency Fund:  ₹"
        f"{observation['emergency_fund']:,.2f}"
    )

    print("\nCHANGES DETECTED")
    print("-" * 45)

    print(
        f"Income change:   "
        f"{observation['income_change']:.1f}%"
    )

    print(
        f"Expense change:  "
        f"{observation['expense_change']:.1f}%"
    )

    print("\nAUTONOMOUS AGENT DECISION")
    print("-" * 45)

    print(
        f"Decision: {decision['decision']}"
    )

    print(
        f"Action:   {decision['action']}"
    )

    print(
        f"\nReason:\n{decision['reason']}"
    )

    # --------------------------------------------------------
    # Show priority goal
    # --------------------------------------------------------

    if decision["priority_goal"] is not None:

        goal = decision["priority_goal"]

        print("\nPRIORITY FINANCIAL GOAL")
        print("-" * 45)

        print(
            f"Goal:              {goal['name']}"
        )

        print(
            f"Target Amount:     "
            f"₹{goal['target_amount']:,.2f}"
        )

        print(
            f"Current Amount:    "
            f"₹{goal['current_amount']:,.2f}"
        )

        print(
            f"Remaining Amount:  "
            f"₹{goal['remaining_amount']:,.2f}"
        )

        print(
            f"Progress:          "
            f"{goal['progress']:.1f}%"
        )

        print(
            f"Priority:          "
            f"{goal['priority']}"
        )


# ============================================================
# DISPLAY FINANCIAL PLAN
# ============================================================

def display_financial_plan(
    plan,
    title="CURRENT FINANCIAL PLAN"
):

    print("\n")
    print(title)
    print("-" * 45)

    print(
        f"Emergency Allocation:  "
        f"₹{plan['emergency_allocation']:,.2f}"
    )

    print(
        f"Debt Allocation:       "
        f"₹{plan['debt_allocation']:,.2f}"
    )

    print(
        f"Goal Allocation:       "
        f"₹{plan['goal_allocation']:,.2f}"
    )

    print(
        f"Discretionary Budget:  "
        f"₹{plan['discretionary_budget']:,.2f}"
    )

    print(
        f"Total Allocations:     "
        f"₹{plan['total_allocations']:,.2f}"
    )

    print(
        f"Last Adjustment:       "
        f"{plan['last_adjustment']}"
    )


# ============================================================
# DATABASE AND FINANCIAL SERVICE
# ============================================================

database = FinancialDatabase()

financial_service = FinancialService(
    database
)


# ============================================================
# LOAD USER FINANCIAL DATA
# ============================================================

user_id = 1

user_data = financial_service.load_user_financial_data(
    user_id
)

state = user_data["state"]

goal_manager = user_data["goal_manager"]


# ============================================================
# DISPLAY LOADED FINANCIAL PROFILE
# ============================================================

print("\n")
print("=" * 65)
print("          FINANCIAL PROFILE LOADED FROM DATABASE")
print("=" * 65)

print(
    f"\nIncome:          ₹{state.income:,.2f}"
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
# DISPLAY FINANCIAL GOALS
# ============================================================

print("\n")
print("=" * 65)
print("                  FINANCIAL GOALS")
print("=" * 65)

for goal in goal_manager.get_goals():

    print(
        f"\nGoal: {goal.name}"
    )

    print(
        f"Target: ₹"
        f"{goal.target_amount:,.2f}"
    )

    print(
        f"Current: ₹"
        f"{goal.current_amount:,.2f}"
    )

    print(
        f"Progress: "
        f"{goal.get_progress():.1f}%"
    )

    print(
        f"Priority: "
        f"{goal.priority}"
    )


# ============================================================
# CREATE INTELLIGENT AGENT
# ============================================================

agent = FinancialAgent(
    state,
    goal_manager
)


# ============================================================
# INITIAL FINANCIAL PLAN
# ============================================================

print("\n")
print("=" * 65)
print("              INITIAL AGENT FINANCIAL PLAN")
print("=" * 65)

display_financial_plan(
    agent.get_financial_plan()
)


# ============================================================
# MONTH 1
# Stable financial condition
# ============================================================

result = agent.run_cycle()

display_result(
    1,
    result
)

display_financial_plan(
    result["updated_plan"],
    "AGENT-UPDATED FINANCIAL PLAN"
)


# ============================================================
# MONTH 2
# Expenses increase significantly
# ============================================================

state.update_environment(
    expenses=52000
)

result = agent.run_cycle()

display_result(
    2,
    result
)

display_financial_plan(
    result["updated_plan"],
    "AGENT-UPDATED FINANCIAL PLAN"
)


# ============================================================
# MONTH 3
# Income decreases
# ============================================================

state.update_environment(
    income=70000
)

result = agent.run_cycle()

display_result(
    3,
    result
)

display_financial_plan(
    result["updated_plan"],
    "AGENT-UPDATED FINANCIAL PLAN"
)


# ============================================================
# MONTH 4
# Income improves and expenses decrease
# ============================================================

state.update_environment(
    income=85000,
    expenses=46000
)

result = agent.run_cycle()

display_result(
    4,
    result
)

display_financial_plan(
    result["updated_plan"],
    "AGENT-UPDATED FINANCIAL PLAN"
)


# ============================================================
# FINAL GOAL STATUS
# ============================================================

print("\n")
print("=" * 65)
print("                    FINAL GOAL STATUS")
print("=" * 65)

for goal in goal_manager.get_goals():

    print(
        f"\n{goal.name}: "
        f"{goal.get_progress():.1f}% complete"
    )

    print(
        f"Remaining: "
        f"₹{goal.remaining_amount():,.2f}"
    )


# ============================================================
# AGENT ACTIVITY LOG
# ============================================================

print("\n")
print("=" * 65)
print("                   AGENT ACTIVITY LOG")
print("=" * 65)

for activity in agent.get_activity_log():

    print("✓", activity)