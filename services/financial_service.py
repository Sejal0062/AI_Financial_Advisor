from database.database import FinancialDatabase
from agent.agent_state import AgentState
from agent.goals import FinancialGoal, GoalManager


class FinancialService:
    """
    Connects persistent database data with
    the Intelligent Agent.
    """

    def __init__(self, database=None):

        if database is None:
            database = FinancialDatabase()

        self.database = database

    # =========================================================
    # LOAD FINANCIAL STATE
    # =========================================================

    def load_agent_state(self, user_id):

        profile = self.database.get_financial_profile(
            user_id
        )

        if profile is None:

            raise ValueError(
                "Financial profile not found "
                f"for user ID {user_id}."
            )

        (
            income,
            expenses,
            savings,
            debt,
            emergency_fund,
            risk_preference
        ) = profile

        state = AgentState(
            income=income,
            expenses=expenses,
            savings=savings,
            debt=debt,
            emergency_fund=emergency_fund
        )

        # Store risk preference as part of the state
        state.risk_preference = risk_preference

        return state

    # =========================================================
    # LOAD FINANCIAL GOALS
    # =========================================================

    def load_goal_manager(self, user_id):

        goal_manager = GoalManager()

        goals = self.database.get_goals(
            user_id
        )

        for goal in goals:

            (
                goal_id,
                name,
                target_amount,
                current_amount,
                priority,
                monthly_contribution
            ) = goal

            financial_goal = FinancialGoal(
                name=name,
                target_amount=target_amount,
                current_amount=current_amount,
                priority=priority,
                monthly_contribution=monthly_contribution
            )

            goal_manager.add_goal(
                financial_goal
            )

        return goal_manager

    # =========================================================
    # LOAD COMPLETE USER FINANCIAL DATA
    # =========================================================

    def load_user_financial_data(self, user_id):

        state = self.load_agent_state(
            user_id
        )

        goal_manager = self.load_goal_manager(
            user_id
        )

        return {
            "state": state,
            "goal_manager": goal_manager
        }

    # =========================================================
    # SAVE AGENT DECISION
    # =========================================================

    def save_agent_decision(
        self,
        user_id,
        result
    ):

        decision = result["decision"]

        self.database.save_agent_activity(
            user_id=user_id,
            activity_type="AUTONOMOUS_DECISION",
            decision=decision["decision"],
            action=decision["action"],
            reason=decision["reason"]
        )