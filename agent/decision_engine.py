"""
Multi-factor autonomous decision engine for FINADVISOR AI.

This module remains part of the Intelligent Agent technique. It does not use
machine learning, fuzzy logic, genetic algorithms, or swarm intelligence.
"""


class MultiFactorDecisionEngine:
    """Evaluate several financial factors before selecting an agent response."""

    def evaluate(self, observation, priority_goal=None, memory_context=None):
        memory_context = memory_context or {}
        factors = self._assess_factors(observation, priority_goal)
        candidates = self._score_candidates(observation, factors, priority_goal)

        selected = max(
            candidates,
            key=lambda item: (item["score"], item["priority"])
        )

        return {
            "factors": factors,
            "candidates": candidates,
            "selected": selected,
            "memory_influence": {
                "history_available": bool(memory_context.get("history_available")),
                "repeated_decision": bool(memory_context.get("repeated_decision")),
            },
        }

    def _assess_factors(self, observation, priority_goal):
        surplus = observation.get("monthly_surplus", 0) or 0
        income = observation.get("income", 0) or 0
        expenses = observation.get("expenses", 0) or 0
        savings = observation.get("savings", 0) or 0
        debt = observation.get("debt", 0) or 0
        emergency_fund = observation.get("emergency_fund", 0) or 0
        income_change = observation.get("income_change", 0) or 0
        expense_change = observation.get("expense_change", 0) or 0

        if surplus < 0:
            cash_flow = {"level": "CRITICAL", "score": 100}
        elif income > 0 and surplus / income < 0.10:
            cash_flow = {"level": "HIGH", "score": 80}
        elif income > 0 and surplus / income < 0.20:
            cash_flow = {"level": "MEDIUM", "score": 55}
        else:
            cash_flow = {"level": "LOW", "score": 20}

        if income_change <= -20:
            income_stability = {"level": "CRITICAL", "score": 100}
        elif income_change <= -10:
            income_stability = {"level": "HIGH", "score": 80}
        elif income_change < 0:
            income_stability = {"level": "MEDIUM", "score": 50}
        else:
            income_stability = {"level": "LOW", "score": 15}

        if expense_change >= 25:
            expense_pressure = {"level": "CRITICAL", "score": 100}
        elif expense_change >= 15:
            expense_pressure = {"level": "HIGH", "score": 80}
        elif expense_change > 0:
            expense_pressure = {"level": "MEDIUM", "score": 50}
        else:
            expense_pressure = {"level": "LOW", "score": 15}

        debt_ratio = debt / savings if savings > 0 else (1.0 if debt > 0 else 0.0)
        if debt_ratio >= 0.75:
            debt_pressure = {"level": "CRITICAL", "score": 100, "ratio": debt_ratio}
        elif debt_ratio > 0.50:
            debt_pressure = {"level": "HIGH", "score": 80, "ratio": debt_ratio}
        elif debt_ratio > 0.30:
            debt_pressure = {"level": "MEDIUM", "score": 50, "ratio": debt_ratio}
        else:
            debt_pressure = {"level": "LOW", "score": 15, "ratio": debt_ratio}

        # Emergency coverage is measured in months of current expenses.
        # Three months is the reference threshold used by the agent.
        months = emergency_fund / expenses if expenses > 0 else 0
        if expenses <= 0:
            emergency_coverage = {
                "level": "LOW", "score": 15, "months": 0,
                "coverage_status": "No current expenses recorded"
            }
        elif months < 1:
            emergency_coverage = {
                "level": "CRITICAL", "score": 100, "months": months,
                "coverage_status": f"{months:.1f} month(s) covered; below 1-month minimum"
            }
        elif months < 2:
            emergency_coverage = {
                "level": "HIGH", "score": 80, "months": months,
                "coverage_status": f"{months:.1f} month(s) covered; below 2-month level"
            }
        elif months < 3:
            emergency_coverage = {
                "level": "MEDIUM", "score": 55, "months": months,
                "coverage_status": f"{months:.1f} month(s) covered; below 3-month reference"
            }
        else:
            emergency_coverage = {
                "level": "LOW", "score": 15, "months": months,
                "coverage_status": f"{months:.1f} month(s) covered; meets 3-month reference"
            }

        goal_urgency = self._goal_urgency(priority_goal)

        return {
            "cash_flow": cash_flow,
            "income_stability": income_stability,
            "expense_pressure": expense_pressure,
            "debt_pressure": debt_pressure,
            "emergency_coverage": emergency_coverage,
            "goal_urgency": goal_urgency,
        }

    def _goal_urgency(self, goal):
        if goal is None:
            return {"level": "NONE", "score": 0, "progress": None}

        progress = goal.get_progress()
        if progress < 25:
            score, level = 80, "HIGH"
        elif progress < 50:
            score, level = 60, "MEDIUM"
        elif progress < 75:
            score, level = 40, "MODERATE"
        else:
            score, level = 20, "LOW"

        return {"level": level, "score": score, "progress": progress}

    def _score_candidates(self, observation, factors, priority_goal):
        candidates = [
            {"key": "CASH_FLOW_PROTECTION", "label": "Critical cash-flow problem detected", "score": factors["cash_flow"]["score"], "priority": 100},
            {"key": "INCOME_PROTECTION", "label": "Significant income reduction detected", "score": factors["income_stability"]["score"], "priority": 90},
            {"key": "EXPENSE_CONTROL", "label": "Significant expense increase detected", "score": factors["expense_pressure"]["score"], "priority": 85},
            {"key": "DEBT_REDUCTION", "label": "High debt level detected", "score": factors["debt_pressure"]["score"], "priority": 80},
            {"key": "EMERGENCY_FUND", "label": "Emergency fund requires improvement", "score": factors["emergency_coverage"]["score"], "priority": 75},
        ]

        if priority_goal is not None:
            candidates.append({
                "key": "GOAL_PRIORITY",
                "label": f"Goal monitoring: {priority_goal.name}",
                "score": factors["goal_urgency"]["score"],
                "priority": 50,
            })

        candidates.append({
            "key": "MAINTAIN_PLAN",
            "label": "Financial condition is stable",
            "score": 20,
            "priority": 10,
        })

        return sorted(candidates, key=lambda item: (-item["score"], -item["priority"]))
