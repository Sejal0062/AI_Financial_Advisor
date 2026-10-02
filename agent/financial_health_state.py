"""
Financial health state evaluator for FINADVISOR AI.

This module is part of the Intelligent Agent. It converts the agent's
observed financial conditions into an explicit internal health state.
It uses deterministic state rules; it does not introduce ML, fuzzy logic,
genetic algorithms, or swarm intelligence.
"""


class FinancialHealthState:
    """Determine the current overall financial state from agent observations."""

    def evaluate(self, observation, factors=None, priority_goal=None):
        factors = factors or {}

        surplus = observation.get("monthly_surplus", 0) or 0
        income = observation.get("income", 0) or 0
        expenses = observation.get("expenses", 0) or 0
        debt = observation.get("debt", 0) or 0
        savings = observation.get("savings", 0) or 0
        emergency_fund = observation.get("emergency_fund", 0) or 0

        emergency_months = (
            emergency_fund / expenses if expenses > 0 else 0
        )
        debt_ratio = (
            debt / savings if savings > 0 else (1.0 if debt > 0 else 0.0)
        )

        cash_score = factors.get("cash_flow", {}).get("score", 0)
        income_score = factors.get("income_stability", {}).get("score", 0)
        expense_score = factors.get("expense_pressure", {}).get("score", 0)
        debt_score = factors.get("debt_pressure", {}).get("score", 0)
        emergency_score = factors.get("emergency_coverage", {}).get("score", 0)
        goal_score = factors.get("goal_urgency", {}).get("score", 0)

        # Highest-risk conditions take precedence so the state represents
        # the most important current condition.
        if surplus < 0:
            state = "CASH_FLOW_STRESS"
            severity = "CRITICAL"
            reason = "Monthly expenses exceed income, creating negative cash flow."

        elif emergency_months < 1:
            state = "EMERGENCY_RISK"
            severity = "CRITICAL"
            reason = (
                f"Emergency funds cover approximately {emergency_months:.1f} "
                "month(s) of current expenses."
            )

        elif debt_ratio >= 0.75 or debt_score >= 100:
            state = "DEBT_PRESSURE"
            severity = "HIGH"
            reason = (
                f"Debt is approximately {debt_ratio * 100:.1f}% of current savings."
            )

        elif emergency_months < 2 or debt_score >= 80 or cash_score >= 80:
            state = "CAUTION"
            severity = "MEDIUM"
            reason = "One or more financial risk factors require closer monitoring."

        elif goal_score >= 80 and max(
            income_score, expense_score, emergency_score, debt_score, cash_score
        ) < 50:
            state = "GOAL_ACCELERATION"
            severity = "MEDIUM"
            goal_name = getattr(priority_goal, "name", "the priority goal")
            reason = (
                f"Current financial conditions are stable while {goal_name} "
                "has significant remaining progress."
            )

        else:
            state = "STABLE"
            severity = "LOW"
            reason = (
                "Cash flow is positive and no major financial pressure "
                "dominates the current environment."
            )

        return {
            "state": state,
            "severity": severity,
            "reason": reason,
            "emergency_months": emergency_months,
            "debt_ratio": debt_ratio,
            "monthly_surplus": surplus,
            "risk_scores": {
                "cash_flow": cash_score,
                "income_stability": income_score,
                "expense_pressure": expense_score,
                "debt_pressure": debt_score,
                "emergency_coverage": emergency_score,
                "goal_urgency": goal_score,
            },
        }
