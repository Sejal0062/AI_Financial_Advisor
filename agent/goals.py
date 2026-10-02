class FinancialGoal:
    """
    Represents a financial goal managed by the Intelligent Agent.
    """

    def __init__(
        self,
        name,
        target_amount,
        current_amount=0,
        priority=1,
        monthly_contribution=0
    ):
        self.name = name
        self.target_amount = target_amount
        self.current_amount = current_amount
        self.priority = priority
        self.monthly_contribution = monthly_contribution

    def get_progress(self):
        """
        Calculate percentage completion of the goal.
        """

        if self.target_amount <= 0:
            return 0

        progress = (
            self.current_amount / self.target_amount
        ) * 100

        return min(progress, 100)

    def remaining_amount(self):
        """
        Calculate how much money is still required.
        """

        return max(
            self.target_amount - self.current_amount,
            0
        )

    def update_progress(self, amount):
        """
        Update the amount saved toward the goal.
        """

        self.current_amount += amount

        if self.current_amount > self.target_amount:
            self.current_amount = self.target_amount

    def get_goal_state(self):
        """
        Return the current goal information.
        """

        return {
            "name": self.name,
            "target_amount": self.target_amount,
            "current_amount": self.current_amount,
            "remaining_amount": self.remaining_amount(),
            "progress": self.get_progress(),
            "priority": self.priority,
            "monthly_contribution": self.monthly_contribution
        }


class GoalManager:
    """
    Manages multiple financial goals for the Intelligent Agent.
    """

    def __init__(self):
        self.goals = []

    def add_goal(self, goal):
        """
        Add a new financial goal.
        """

        self.goals.append(goal)

    def remove_goal(self, goal_name):
        """
        Remove a goal by name.
        """

        self.goals = [
            goal for goal in self.goals
            if goal.name != goal_name
        ]

    def get_goals(self):
        """
        Return all goals.
        """

        return self.goals

    def get_highest_priority_goal(self):
        """
        Find the highest-priority goal.
        Lower priority number = higher priority.
        """

        if not self.goals:
            return None

        return min(
            self.goals,
            key=lambda goal: goal.priority
        )

    def get_goal_summary(self):
        """
        Return the current state of all goals.
        """

        return [
            goal.get_goal_state()
            for goal in self.goals
        ]