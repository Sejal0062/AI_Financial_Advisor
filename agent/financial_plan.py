class FinancialPlan:
    """
    Represents the financial plan controlled by the
    Intelligent Agent.

    The agent can autonomously adjust these allocations
    according to the perceived financial environment.
    """

    def __init__(self, monthly_surplus=0):

        self.emergency_allocation = 0
        self.debt_allocation = 0
        self.goal_allocation = 0
        self.discretionary_budget = 0

        self.total_allocations = 0

        self.last_adjustment = "Initial financial plan"

        self.create_initial_plan(monthly_surplus)

    # =========================================================
    # INITIAL PLAN
    # =========================================================

    def create_initial_plan(self, monthly_surplus):
        """
        Create an initial allocation from the
        available monthly surplus.
        """

        if monthly_surplus <= 0:

            self.emergency_allocation = 0
            self.debt_allocation = 0
            self.goal_allocation = 0
            self.discretionary_budget = 0

        else:

            self.emergency_allocation = (
                monthly_surplus * 0.30
            )

            self.debt_allocation = (
                monthly_surplus * 0.30
            )

            self.goal_allocation = (
                monthly_surplus * 0.25
            )

            self.discretionary_budget = (
                monthly_surplus * 0.15
            )

        self.update_total()

    # =========================================================
    # UPDATE TOTAL
    # =========================================================

    def update_total(self):

        self.total_allocations = (
            self.emergency_allocation
            + self.debt_allocation
            + self.goal_allocation
            + self.discretionary_budget
        )

    # =========================================================
    # AUTONOMOUS ADJUSTMENT
    # =========================================================

    def adjust_for_decision(
        self,
        decision,
        monthly_surplus
    ):
        """
        Modify the financial plan according to the
        decision selected by the Intelligent Agent.
        """

        decision_text = decision["decision"]

        # -----------------------------------------------------
        # CRITICAL CASH FLOW
        # -----------------------------------------------------

        if "Critical cash-flow" in decision_text:

            self.emergency_allocation = 0
            self.debt_allocation = 0
            self.goal_allocation = 0
            self.discretionary_budget = 0

            self.last_adjustment = (
                "Allocations suspended because "
                "monthly cash flow is negative."
            )

        # -----------------------------------------------------
        # EXPENSE INCREASE
        # -----------------------------------------------------

        elif "expense increase" in decision_text:

            self.emergency_allocation = (
                monthly_surplus * 0.40
            )

            self.debt_allocation = (
                monthly_surplus * 0.25
            )

            self.goal_allocation = (
                monthly_surplus * 0.15
            )

            self.discretionary_budget = (
                monthly_surplus * 0.20
            )

            self.last_adjustment = (
                "Emergency savings increased and "
                "goal allocation reduced due to "
                "higher expenses."
            )

        # -----------------------------------------------------
        # INCOME REDUCTION
        # -----------------------------------------------------

        elif "income reduction" in decision_text:

            self.emergency_allocation = (
                monthly_surplus * 0.45
            )

            self.debt_allocation = (
                monthly_surplus * 0.20
            )

            self.goal_allocation = (
                monthly_surplus * 0.10
            )

            self.discretionary_budget = (
                monthly_surplus * 0.25
            )

            self.last_adjustment = (
                "Cash preservation increased because "
                "income decreased."
            )

        # -----------------------------------------------------
        # HIGH DEBT
        # -----------------------------------------------------

        elif "High debt" in decision_text:

            self.emergency_allocation = (
                monthly_surplus * 0.20
            )

            self.debt_allocation = (
                monthly_surplus * 0.50
            )

            self.goal_allocation = (
                monthly_surplus * 0.20
            )

            self.discretionary_budget = (
                monthly_surplus * 0.10
            )

            self.last_adjustment = (
                "Debt repayment allocation increased "
                "because debt level is high."
            )

        # -----------------------------------------------------
        # EMERGENCY FUND
        # -----------------------------------------------------

        elif "Emergency fund" in decision_text:

            self.emergency_allocation = (
                monthly_surplus * 0.50
            )

            self.debt_allocation = (
                monthly_surplus * 0.20
            )

            self.goal_allocation = (
                monthly_surplus * 0.20
            )

            self.discretionary_budget = (
                monthly_surplus * 0.10
            )

            self.last_adjustment = (
                "Emergency fund allocation increased "
                "to strengthen financial safety."
            )

        # -----------------------------------------------------
        # STABLE CONDITION
        # -----------------------------------------------------

        else:

            self.create_initial_plan(
                monthly_surplus
            )

            self.last_adjustment = (
                "Financial conditions stable. "
                "Current allocation maintained."
            )

        self.update_total()

    # =========================================================
    # GET PLAN
    # =========================================================

    def get_plan(self):

        return {
            "emergency_allocation":
                self.emergency_allocation,

            "debt_allocation":
                self.debt_allocation,

            "goal_allocation":
                self.goal_allocation,

            "discretionary_budget":
                self.discretionary_budget,

            "total_allocations":
                self.total_allocations,

            "last_adjustment":
                self.last_adjustment
        }