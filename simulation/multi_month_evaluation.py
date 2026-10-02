"""
Multi-month autonomous evaluation for FINADVISOR AI.

This module evaluates the existing Intelligent Agent across a changing
six-month financial environment. It does not write the simulated state to
SQLite and it does not use machine learning, fuzzy logic, genetic algorithms,
or swarm intelligence.
"""

from copy import deepcopy
from datetime import datetime

from agent.agent_state import AgentState
from agent.financial_agent import FinancialAgent


class MultiMonthEvaluation:
    """Run a controlled multi-month experiment using the existing agent."""

    def __init__(self, base_state, goal_manager):
        self.base_state = base_state
        self.goal_manager = goal_manager
        self.results = []
        self.metrics = {}

    def _build_months(self):
        """Create a deterministic six-month test environment from the saved profile."""
        income = float(self.base_state.income)
        expenses = float(self.base_state.expenses)
        savings = float(self.base_state.savings)
        debt = float(self.base_state.debt)
        emergency = float(self.base_state.emergency_fund)

        return [
            {
                "month": 1,
                "label": "Baseline",
                "reason": "Starting financial environment",
                "income": income,
                "expenses": expenses,
                "savings": savings,
                "debt": debt,
                "emergency_fund": emergency,
            },
            {
                "month": 2,
                "label": "Expense Pressure",
                "reason": "Monthly expenses increase by 10%",
                "income": income,
                "expenses": expenses * 1.10,
                "savings": savings,
                "debt": debt,
                "emergency_fund": emergency,
            },
            {
                "month": 3,
                "label": "Income Reduction",
                "reason": "Monthly income decreases by 15%",
                "income": income * 0.85,
                "expenses": expenses * 1.10,
                "savings": savings,
                "debt": debt,
                "emergency_fund": emergency,
            },
            {
                "month": 4,
                "label": "Debt Pressure",
                "reason": "Debt increases by 30%",
                "income": income * 0.85,
                "expenses": expenses,
                "savings": savings,
                "debt": debt * 1.30,
                "emergency_fund": emergency,
            },
            {
                "month": 5,
                "label": "Emergency Shock",
                "reason": "Emergency-fund balance falls by 20%",
                "income": income * 0.85,
                "expenses": expenses * 1.15,
                "savings": savings,
                "debt": debt * 1.30,
                "emergency_fund": emergency * 0.80,
            },
            {
                "month": 6,
                "label": "Recovery",
                "reason": "Income improves and expenses return to baseline",
                "income": income * 1.05,
                "expenses": expenses,
                "savings": savings,
                "debt": debt * 1.20,
                "emergency_fund": emergency,
            },
        ]

    def run(self):
        """Run the six-month autonomous experiment and return actual metrics."""
        state = AgentState(
            income=float(self.base_state.income),
            expenses=float(self.base_state.expenses),
            savings=float(self.base_state.savings),
            debt=float(self.base_state.debt),
            emergency_fund=float(self.base_state.emergency_fund),
        )
        state.risk_preference = getattr(
            self.base_state, "risk_preference", "Moderate"
        )

        # Deep-copy goals so simulated progress can never change saved goals.
        goals = deepcopy(self.goal_manager)
        run_key = "evaluation_" + datetime.now().strftime("%Y%m%d_%H%M%S_%f")

        agent = FinancialAgent(
            state,
            goals,
            memory_key=run_key,
        )

        self.results = []

        for month in self._build_months():
            state.update_environment(
                income=month["income"],
                expenses=month["expenses"],
                savings=month["savings"],
                debt=month["debt"],
                emergency_fund=month["emergency_fund"],
            )

            result = agent.run_cycle()
            observation = result.get("observation", {})
            decision = result.get("decision", {})
            plan = result.get("updated_plan", {})

            evaluation = {}
            if isinstance(decision, dict):
                evaluation = decision.get("multi_factor_evaluation", {}) or {}

            selected = evaluation.get("selected", {}) or {}
            health = evaluation.get("financial_health_state", {}) or {}

            decision_text = (
                decision.get("decision", "Unknown")
                if isinstance(decision, dict)
                else str(decision)
            )
            action_text = (
                decision.get("action", "Unknown")
                if isinstance(decision, dict)
                else str(result.get("action", "Unknown"))
            )

            self.results.append({
                "month": month["month"],
                "label": month["label"],
                "reason": month["reason"],
                "income": float(observation.get("income", state.income)),
                "expenses": float(observation.get("expenses", state.expenses)),
                "surplus": float(observation.get("monthly_surplus", state.monthly_surplus)),
                "debt": float(observation.get("debt", state.debt)),
                "emergency_fund": float(observation.get("emergency_fund", state.emergency_fund)),
                "decision": decision_text,
                "action": action_text,
                "action_type": selected.get("key", "UNKNOWN"),
                "priority_score": float(selected.get("score", 0) or 0),
                "health_state": health.get("state", "UNKNOWN"),
                "health_severity": health.get("severity", "UNKNOWN"),
                "emergency_coverage_months": float(
                    health.get("emergency_coverage_months", 0) or 0
                ),
                "debt_savings_ratio": float(
                    health.get("debt_savings_ratio", 0) or 0
                ),
                "plan": plan,
                "memory_cycles": int(result.get("memory_count", 0) or 0),
            })

        self.metrics = self._calculate_metrics()
        return {
            "results": self.results,
            "metrics": self.metrics,
        }

    def _calculate_metrics(self):
        if not self.results:
            return {}

        decisions = [row["decision"] for row in self.results]
        action_types = [row["action_type"] for row in self.results]
        health_states = [row["health_state"] for row in self.results]
        scores = [row["priority_score"] for row in self.results]
        surpluses = [row["surplus"] for row in self.results]

        stable_type = "STABLE"
        adaptive_cycles = sum(
            1 for item in action_types
            if item not in {stable_type, "UNKNOWN"}
        )

        return {
            "cycles": len(self.results),
            "unique_decisions": len(set(decisions)),
            "adaptive_cycles": adaptive_cycles,
            "adaptive_response_rate": round(
                adaptive_cycles / len(self.results) * 100, 1
            ),
            "average_priority_score": round(
                sum(scores) / len(scores), 1
            ),
            "minimum_monthly_surplus": round(min(surpluses), 2),
            "final_monthly_surplus": round(surpluses[-1], 2),
            "health_states": {
                state: health_states.count(state)
                for state in dict.fromkeys(health_states)
            },
            "decision_counts": {
                decision: decisions.count(decision)
                for decision in dict.fromkeys(decisions)
            },
            "action_type_counts": {
                action: action_types.count(action)
                for action in dict.fromkeys(action_types)
            },
            "memory_cycles_final": self.results[-1]["memory_cycles"],
        }
