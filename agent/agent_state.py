class AgentState:
    """
    Stores the current internal state of the financial environment
    as perceived by the Intelligent Agent.
    """

    def __init__(
        self,
        income=0,
        expenses=0,
        savings=0,
        debt=0,
        emergency_fund=0
    ):
        self.income = income
        self.expenses = expenses
        self.savings = savings
        self.debt = debt
        self.emergency_fund = emergency_fund

        # Derived value
        self.monthly_surplus = income - expenses

        # Agent state
        self.status = "ACTIVE"
        self.last_observation = None
        self.last_decision = None
        self.last_action = None

    def update_environment(
        self,
        income=None,
        expenses=None,
        savings=None,
        debt=None,
        emergency_fund=None
    ):
        """
        Update the financial environment.

        Any value can change independently.
        """

        if income is not None:
            self.income = income

        if expenses is not None:
            self.expenses = expenses

        if savings is not None:
            self.savings = savings

        if debt is not None:
            self.debt = debt

        if emergency_fund is not None:
            self.emergency_fund = emergency_fund

        # Recalculate after every environmental change
        self.monthly_surplus = self.income - self.expenses

    def get_state(self):
        """
        Return the current financial state.
        """

        return {
            "income": self.income,
            "expenses": self.expenses,
            "savings": self.savings,
            "debt": self.debt,
            "emergency_fund": self.emergency_fund,
            "monthly_surplus": self.monthly_surplus,
            "status": self.status,
            "last_observation": self.last_observation,
            "last_decision": self.last_decision,
            "last_action": self.last_action
        }