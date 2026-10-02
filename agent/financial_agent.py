from agent.agent_state import AgentState
from agent.goals import GoalManager
from agent.financial_plan import FinancialPlan
from agent.agent_memory import AgentMemory
from agent.decision_engine import MultiFactorDecisionEngine
from agent.goal_competition import GoalCompetitionEngine


class FinancialAgent:
    """
    Autonomous Intelligent Agent for personal financial decision support.

    Agent cycle:

        PERCEIVE
            ↓
        EVALUATE GOALS
            ↓
        CONSULT MEMORY
            ↓
        MULTI-FACTOR EVALUATION
            ↓
        DECIDE
            ↓
        ACT
            ↓
        STORE EXPERIENCE
            ↓
        MONITOR
    """

    def __init__(
        self,
        state: AgentState,
        goal_manager=None,
        financial_plan=None,
        memory=None,
        memory_key="default_user"
    ):
        self.state = state
        self.goal_manager = goal_manager or GoalManager()
        self.financial_plan = financial_plan or FinancialPlan()
        self.memory = memory or AgentMemory(memory_key=memory_key)
        self.decision_engine = MultiFactorDecisionEngine()
        self.goal_competition = GoalCompetitionEngine()
        self.last_health_state = None

        self.previous_income = state.income
        self.previous_expenses = state.expenses
        self.previous_savings = state.savings
        self.previous_debt = state.debt

        self.activity_log = []

    # =========================================================
    # PERCEPTION
    # =========================================================

    def perceive(self):
        current_income = self.state.income
        current_expenses = self.state.expenses
        current_savings = self.state.savings
        current_debt = self.state.debt

        observation = {
            "income": current_income,
            "expenses": current_expenses,
            "savings": current_savings,
            "debt": current_debt,
            "emergency_fund": self.state.emergency_fund,
            "monthly_surplus": self.state.monthly_surplus,
            "income_change": self._percentage_change(self.previous_income, current_income),
            "expense_change": self._percentage_change(self.previous_expenses, current_expenses),
            "savings_change": self._percentage_change(self.previous_savings, current_savings),
            "debt_change": self._percentage_change(self.previous_debt, current_debt),
        }

        observation["memory_cycles"] = self.memory.count()
        observation["recent_memory"] = self.memory.get_recent(3)

        self.state.last_observation = observation
        self.activity_log.append("Environment observed")

        return observation

    # =========================================================
    # GOAL EVALUATION
    # =========================================================

    def evaluate_goals(self):
        goals = self.goal_manager.get_goals()

        if not goals:
            self.activity_log.append("No financial goals configured")
            return None

        highest_priority_goal = self.goal_manager.get_highest_priority_goal()

        self.activity_log.append(
            f"Goals evaluated: {len(goals)} goals monitored"
        )

        return highest_priority_goal

    # =========================================================
    # MEMORY CONTEXT
    # =========================================================

    def evaluate_memory(self):
        recent = self.memory.get_recent(5)

        if not recent:
            return {
                "history_available": False,
                "recent_decisions": [],
                "repeated_decision": False,
            }

        recent_decisions = [
            item.get("decision")
            for item in recent
            if item.get("decision")
        ]

        repeated_decision = (
            len(recent_decisions) >= 2
            and len(set(recent_decisions[:2])) == 1
        )

        self.activity_log.append(
            f"Agent memory consulted: {len(recent)} recent cycles"
        )

        return {
            "history_available": True,
            "recent_decisions": recent_decisions,
            "repeated_decision": repeated_decision,
        }

    # =========================================================
    # MULTI-FACTOR DECISION
    # =========================================================

    def decide(self, observation):
        priority_goal = self.evaluate_goals()
        memory_context = self.evaluate_memory()

        evaluation = self.decision_engine.evaluate(
            observation,
            priority_goal=priority_goal,
            memory_context=memory_context,
        )

        # Build the explicit financial health state from the SAME
        # observation used by the multi-factor engine.
        # This must happen before goal competition so both components
        # reason over the same financial environment.
        health_state = self._evaluate_financial_health(observation, evaluation)
        self.last_health_state = health_state
        evaluation["financial_health_state"] = health_state

        # Compare all configured goals using the current health state.
        goal_competition = self.goal_competition.evaluate(
            self.goal_manager.get_goals(),
            observation,
            health_state,
        )

        selected = evaluation["selected"]
        action_type = selected["key"]

        if action_type == "CASH_FLOW_PROTECTION":
            decision = "Critical cash-flow problem detected"
            action = "Reduce discretionary spending and protect available savings"
            reason = (
                "Monthly expenses are higher than income. The multi-factor engine "
                "prioritizes immediate financial stability."
            )

        elif action_type == "EXPENSE_CONTROL":
            decision = "Significant expense increase detected"
            action = "Reduce discretionary spending and review the financial plan"
            reason = (
                f"Expenses increased by {observation['expense_change']:.1f}%. "
                "The agent increases expense-control priority."
            )

        elif action_type == "INCOME_PROTECTION":
            decision = "Significant income reduction detected"
            action = "Temporarily reduce flexible allocations and preserve cash reserves"
            reason = (
                f"Income decreased by {abs(observation['income_change']):.1f}%. "
                "The agent prioritizes cash preservation."
            )

        elif action_type == "DEBT_REDUCTION":
            decision = "High debt level detected"
            action = "Increase debt repayment priority"
            reason = (
                "Debt pressure is elevated relative to current savings. "
                "The multi-factor engine prioritizes debt reduction."
            )

        elif action_type == "EMERGENCY_FUND":
            decision = "Emergency fund requires improvement"
            action = "Increase emergency fund allocation"
            reason = (
                "Emergency-fund coverage is below the three-month reference level. "
                "The agent increases emergency-fund priority."
            )

        elif action_type == "GOAL_PRIORITY":
            selected_goal = goal_competition.get("selected_goal")

            if selected_goal is not None:
                goal_name = selected_goal["name"]
                progress = selected_goal["progress"]
                selected_score = selected_goal["score"]
                decision = f"Goal monitoring: {goal_name}"
                action = f"Prioritize monthly contribution toward {goal_name}"
                reason = (
                    f"The goal competition engine evaluated all {len(goal_competition['goals'])} "
                    f"configured goals. {goal_name} received the highest goal score "
                    f"({selected_score:.1f}/100) with {progress:.1f}% completion."
                )
            else:
                decision = "No financial goal requires prioritization"
                action = "Continue monitoring configured goals"
                reason = "No configured financial goals were available for competition."

        else:
            decision = "Financial condition is stable"
            action = "Continue the current financial plan"
            reason = (
                "No dominant financial pressure was detected across the evaluated factors."
            )

        if memory_context["history_available"]:
            reason += (
                f" Agent memory contains {self.memory.count()} previous completed "
                "cycle(s) and was consulted before this decision."
            )

        self.state.last_decision = decision
        self.state.last_action = action
        self.activity_log.append(f"Decision selected: {decision}")
        self.activity_log.append(
            f"Multi-factor evaluation completed: {selected['score']}/100 priority score"
        )

        return {
            "decision": decision,
            "action": action,
            "reason": reason,
            "action_type": action_type,
            "priority_goal": (
                priority_goal.get_goal_state()
                if priority_goal is not None
                else None
            ),
            "memory_context": memory_context,
            "multi_factor_evaluation": evaluation,
            "goal_competition": goal_competition,
        }

    # =========================================================
    # FINANCIAL HEALTH STATE
    # =========================================================

    def _evaluate_financial_health(self, observation, evaluation):
        """
        Convert the observed financial environment into an explicit
        internal state used by the autonomous agent and goal competition.

        This is rule-based state assessment inside the Intelligent Agent;
        it is not a separate AI technique.
        """
        income = float(observation.get("income", 0) or 0)
        expenses = float(observation.get("expenses", 0) or 0)
        savings = float(observation.get("savings", 0) or 0)
        debt = float(observation.get("debt", 0) or 0)
        emergency_fund = float(observation.get("emergency_fund", 0) or 0)
        surplus = float(observation.get("monthly_surplus", income - expenses) or 0)

        # Emergency-fund coverage measured in months of current expenses.
        emergency_months = (
            emergency_fund / expenses if expenses > 0 else 0.0
        )

        # Debt pressure relative to savings.
        debt_savings_ratio = (
            debt / savings if savings > 0 else (1.0 if debt > 0 else 0.0)
        )

        factors = evaluation.get("factors", {})
        selected = evaluation.get("selected", {})
        selected_key = selected.get("key", "")

        # Determine the dominant financial condition.
        if surplus < 0 or selected_key == "CASH_FLOW_PROTECTION":
            state = "CASH_FLOW_STRESS"
            severity = "HIGH"
            description = (
                "Expenses exceed income, so the agent is prioritizing "
                "cash-flow protection."
            )
        elif selected_key == "INCOME_PROTECTION":
            state = "CAUTION"
            severity = "HIGH"
            description = (
                "A significant income reduction was detected, so the agent "
                "is prioritizing cash preservation."
            )
        elif selected_key == "EXPENSE_CONTROL":
            state = "CAUTION"
            severity = "MEDIUM"
            description = (
                "Expense pressure has increased and the agent is reviewing "
                "flexible spending."
            )
        elif debt_savings_ratio > 0.50 or selected_key == "DEBT_REDUCTION":
            state = "DEBT_PRESSURE"
            severity = "HIGH"
            description = (
                "Debt is elevated relative to available savings, so debt "
                "reduction receives additional attention."
            )
        elif emergency_months < 3.0 or selected_key == "EMERGENCY_FUND":
            state = "EMERGENCY_RISK"
            severity = "MEDIUM"
            description = (
                "Emergency-fund coverage is below the three-month reference "
                "level."
            )
        else:
            state = "STABLE"
            severity = "LOW"
            description = (
                "Cash flow is positive and no major financial pressure "
                "dominates the current environment."
            )

        # The dominant factor is useful for explainability.
        dominant_factor = None
        dominant_score = 0
        for factor_name, factor_data in factors.items():
            if not isinstance(factor_data, dict):
                continue
            score = float(factor_data.get("score", 0) or 0)
            if score > dominant_score:
                dominant_score = score
                dominant_factor = factor_name

        return {
            "state": state,
            "severity": severity,
            "description": description,
            "emergency_coverage_months": round(emergency_months, 1),
            "debt_savings_ratio": round(debt_savings_ratio * 100, 1),
            "monthly_surplus": surplus,
            "dominant_factor": dominant_factor,
            "dominant_factor_score": dominant_score,
        }

    # =========================================================
    # ACTION
    # =========================================================

    def act(self, decision):
        action = decision["action"]

        self.financial_plan.adjust_for_decision(
            decision,
            self.state.monthly_surplus
        )

        self.state.last_action = action
        self.activity_log.append(f"Action executed: {action}")
        self.activity_log.append("Financial plan autonomously adjusted")

        return action

    # =========================================================
    # AUTONOMOUS CYCLE
    # =========================================================

    def run_cycle(self):
        self.activity_log.append("Agent cycle started")

        observation = self.perceive()
        decision = self.decide(observation)
        action = self.act(decision)
        updated_plan = self.financial_plan.get_plan()

        self.memory.record_cycle(
            observation=observation,
            decision=decision,
            action=action,
            plan=updated_plan,
            outcome="Agent action completed and simulated plan updated."
        )

        self.previous_income = self.state.income
        self.previous_expenses = self.state.expenses
        self.previous_savings = self.state.savings
        self.previous_debt = self.state.debt

        self.activity_log.append("Agent memory updated")
        self.activity_log.append("Agent monitoring resumed")

        return {
            "observation": observation,
            "decision": decision,
            "action": action,
            "updated_plan": updated_plan,
            "memory": self.memory.get_last_record(),
            "memory_count": self.memory.count(),
        }

    # =========================================================
    # HELPERS / ACCESSORS
    # =========================================================

    @staticmethod
    def _percentage_change(previous, current):
        if previous == 0:
            return 0 if current == 0 else 100
        return ((current - previous) / previous) * 100

    def get_financial_plan(self):
        return self.financial_plan.get_plan()

    def get_activity_log(self):
        return self.activity_log

    def get_memory_history(self, limit=None):
        return self.memory.get_history(limit)

    def get_memory_statistics(self):
        return self.memory.get_statistics()
