class GoalCompetitionEngine:
    """
    Rule-based goal competition component for the Intelligent Agent.

    The engine compares every configured financial goal using:
      - user-defined priority
      - completion/progress
      - remaining amount
      - current financial-health state
      - the current monthly cash-flow environment

    It does not use ML, fuzzy logic, genetic algorithms, or swarm intelligence.
    """

    def evaluate(self, goals, observation, financial_health_state=None):
        if not goals:
            return {
                "goals": [],
                "selected_goal": None,
                "selected_score": 0,
                "reason": "No financial goals are configured."
            }

        health_state = "STABLE"
        if isinstance(financial_health_state, dict):
            health_state = financial_health_state.get("state", "STABLE")

        scored_goals = []

        for goal in goals:
            progress = self._safe_progress(goal)
            remaining = max(0.0, float(goal.target_amount) - float(goal.current_amount))
            target = max(float(goal.target_amount), 1.0)
            remaining_ratio = min(1.0, remaining / target)

            # Lower numeric priority means higher user-defined priority.
            priority_score = max(0.0, min(100.0, (6 - int(goal.priority)) * 20.0))
            progress_urgency = max(0.0, min(100.0, 100.0 - progress))
            remaining_score = remaining_ratio * 100.0

            score = (
                priority_score * 0.45
                + progress_urgency * 0.30
                + remaining_score * 0.25
            )

            modifier = 0.0
            modifier_reason = ""
            goal_type = self._goal_type(goal.name)

            if health_state == "DEBT_PRESSURE" and goal_type == "DEBT_REDUCTION":
                modifier = 20.0
                modifier_reason = "Debt-pressure state increased debt-goal urgency."
            elif health_state in ("EMERGENCY_RISK", "CASH_FLOW_STRESS") and goal_type == "EMERGENCY_FUND":
                modifier = 20.0
                modifier_reason = "Financial stress increased emergency-fund urgency."
            elif health_state == "GOAL_ACCELERATION":
                modifier = 5.0
                modifier_reason = "Positive cash-flow conditions allow goal acceleration."

            final_score = max(0.0, min(100.0, score + modifier))

            scored_goals.append({
                "name": goal.name,
                "priority": int(goal.priority),
                "progress": progress,
                "remaining_amount": remaining,
                "goal_type": goal_type,
                "base_score": round(score, 1),
                "modifier": round(modifier, 1),
                "score": round(final_score, 1),
                "modifier_reason": modifier_reason,
                "goal_state": goal.get_goal_state(),
            })

        # Highest score wins. Ties are resolved by user-defined priority,
        # then by greater remaining amount.
        scored_goals.sort(
            key=lambda item: (
                -item["score"],
                item["priority"],
                -item["remaining_amount"],
            )
        )

        selected = scored_goals[0]

        reason = (
            f"{selected['name']} received the highest autonomous goal score "
            f"({selected['score']:.1f}/100) after considering priority, "
            "completion and remaining funding needs."
        )
        if selected["modifier_reason"]:
            reason += " " + selected["modifier_reason"]

        return {
            "goals": scored_goals,
            "selected_goal": selected,
            "selected_score": selected["score"],
            "reason": reason,
        }

    @staticmethod
    def _safe_progress(goal):
        try:
            return max(0.0, min(100.0, float(goal.get_progress())))
        except Exception:
            target = max(float(goal.target_amount), 1.0)
            return max(0.0, min(100.0, float(goal.current_amount) / target * 100.0))

    @staticmethod
    def _goal_type(name):
        text = str(name).lower()
        if any(word in text for word in ("debt", "loan", "repayment")):
            return "DEBT_REDUCTION"
        if any(word in text for word in ("emergency", "rainy day", "safety")):
            return "EMERGENCY_FUND"
        if any(word in text for word in ("retirement", "pension")):
            return "RETIREMENT"
        if any(word in text for word in ("education", "study", "college")):
            return "EDUCATION"
        if any(word in text for word in ("house", "home", "property")):
            return "HOUSING"
        return "GENERAL"
