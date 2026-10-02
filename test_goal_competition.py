from agent.goal_competition import GoalCompetitionEngine


class DemoGoal:
    def __init__(self, name, target_amount, current_amount, priority, monthly_contribution=0):
        self.name = name
        self.target_amount = target_amount
        self.current_amount = current_amount
        self.priority = priority
        self.monthly_contribution = monthly_contribution

    def get_progress(self):
        return (self.current_amount / self.target_amount) * 100

    def get_goal_state(self):
        return {
            "name": self.name,
            "target_amount": self.target_amount,
            "current_amount": self.current_amount,
            "priority": self.priority,
            "progress": self.get_progress(),
        }


goals = [
    DemoGoal("Emergency Fund", 300000, 200000, 1, 10000),
    DemoGoal("Debt Reduction", 200000, 80000, 2, 12000),
    DemoGoal("Education Fund", 500000, 100000, 3, 5000),
]

observation = {
    "income": 100000,
    "expenses": 55000,
    "savings": 350000,
    "debt": 80000,
    "emergency_fund": 250000,
    "monthly_surplus": 45000,
}

engine = GoalCompetitionEngine()
result = engine.evaluate(
    goals,
    observation,
    {"state": "STABLE", "severity": "LOW"},
)

print("MULTI-GOAL COMPETITION TEST")
print("=" * 50)
for item in result["goals"]:
    print(
        f"{item['name']}: "
        f"score={item['score']}/100, "
        f"progress={item['progress']:.1f}%, "
        f"priority={item['priority']}"
    )

print("=" * 50)
print("Selected:", result["selected_goal"]["name"])
print("Reason:", result["reason"])
print("MULTI-GOAL COMPETITION TEST SUCCESSFUL")
