import sqlite3
from pathlib import Path


class FinancialDatabase:
    """
    SQLite database manager for the AI Financial Advisor.
    """

    def __init__(self, database_name="financial_advisor.db"):

        # Find the project root folder
        project_root = Path(__file__).resolve().parent.parent

        self.database_path = (
            project_root / database_name
        )

        self.initialize_database()

    # =========================================================
    # DATABASE CONNECTION
    # =========================================================

    def connect(self):

        return sqlite3.connect(
            self.database_path
        )

    # =========================================================
    # INITIALIZE DATABASE
    # =========================================================

    def initialize_database(self):

        connection = self.connect()

        cursor = connection.cursor()

        # -----------------------------------------------------
        # USERS
        # -----------------------------------------------------

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP
                    DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # -----------------------------------------------------
        # FINANCIAL PROFILES
        # -----------------------------------------------------

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS financial_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                monthly_income REAL DEFAULT 0,
                monthly_expenses REAL DEFAULT 0,
                savings REAL DEFAULT 0,
                debt REAL DEFAULT 0,
                emergency_fund REAL DEFAULT 0,
                risk_preference TEXT DEFAULT 'Moderate',

                FOREIGN KEY (user_id)
                    REFERENCES users(id)
            )
        """)

        # -----------------------------------------------------
        # FINANCIAL GOALS
        # -----------------------------------------------------

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                target_amount REAL NOT NULL,
                current_amount REAL DEFAULT 0,
                priority INTEGER DEFAULT 1,
                monthly_contribution REAL DEFAULT 0,

                FOREIGN KEY (user_id)
                    REFERENCES users(id)
            )
        """)

        # -----------------------------------------------------
        # TRANSACTIONS
        # -----------------------------------------------------

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                transaction_type TEXT NOT NULL,
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                description TEXT,
                transaction_date TIMESTAMP
                    DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (user_id)
                    REFERENCES users(id)
            )
        """)

        # -----------------------------------------------------
        # AGENT ACTIVITY
        # -----------------------------------------------------

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_activity (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                activity_type TEXT,
                decision TEXT,
                action TEXT,
                reason TEXT,
                created_at TIMESTAMP
                    DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (user_id)
                    REFERENCES users(id)
            )
        """)

        connection.commit()

        connection.close()

    # =========================================================
    # ADD USER
    # =========================================================

    def add_user(self, name, email):

        connection = self.connect()

        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO users (name, email)
            VALUES (?, ?)
        """, (name, email))

        user_id = cursor.lastrowid

        connection.commit()

        connection.close()

        return user_id

    # =========================================================
    # SAVE FINANCIAL PROFILE
    # =========================================================

    def save_financial_profile(
        self,
        user_id,
        income,
        expenses,
        savings,
        debt,
        emergency_fund,
        risk_preference="Moderate"
    ):

        connection = self.connect()

        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO financial_profiles
            (
                user_id,
                monthly_income,
                monthly_expenses,
                savings,
                debt,
                emergency_fund,
                risk_preference
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            income,
            expenses,
            savings,
            debt,
            emergency_fund,
            risk_preference
        ))

        connection.commit()

        connection.close()

    # =========================================================
    # ADD GOAL
    # =========================================================

    def add_goal(
        self,
        user_id,
        name,
        target_amount,
        current_amount,
        priority,
        monthly_contribution
    ):

        connection = self.connect()

        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO goals
            (
                user_id,
                name,
                target_amount,
                current_amount,
                priority,
                monthly_contribution
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            name,
            target_amount,
            current_amount,
            priority,
            monthly_contribution
        ))

        connection.commit()

        connection.close()

    # =========================================================
    # ADD TRANSACTION
    # =========================================================

    def add_transaction(
        self,
        user_id,
        transaction_type,
        category,
        amount,
        description=""
    ):

        connection = self.connect()

        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO transactions
            (
                user_id,
                transaction_type,
                category,
                amount,
                description
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            user_id,
            transaction_type,
            category,
            amount,
            description
        ))

        connection.commit()

        connection.close()

    # =========================================================
    # SAVE AGENT ACTIVITY
    # =========================================================

    def save_agent_activity(
        self,
        user_id,
        activity_type,
        decision,
        action,
        reason
    ):

        connection = self.connect()

        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO agent_activity
            (
                user_id,
                activity_type,
                decision,
                action,
                reason
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            user_id,
            activity_type,
            decision,
            action,
            reason
        ))

        connection.commit()

        connection.close()

            # =========================================================
    # GET USER
    # =========================================================

    def get_user(self, user_id):

        connection = self.connect()

        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                id,
                name,
                email,
                created_at
            FROM users
            WHERE id = ?
        """, (user_id,))

        user = cursor.fetchone()

        connection.close()

        return user

    # =========================================================
    # GET FINANCIAL PROFILE
    # =========================================================

    def get_financial_profile(self, user_id):

        connection = self.connect()

        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                monthly_income,
                monthly_expenses,
                savings,
                debt,
                emergency_fund,
                risk_preference
            FROM financial_profiles
            WHERE user_id = ?
            ORDER BY id DESC
            LIMIT 1
        """, (user_id,))

        profile = cursor.fetchone()

        connection.close()

        return profile

    # =========================================================
    # GET GOALS
    # =========================================================

    def get_goals(self, user_id):

        connection = self.connect()

        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                id,
                name,
                target_amount,
                current_amount,
                priority,
                monthly_contribution
            FROM goals
            WHERE user_id = ?
            ORDER BY priority ASC
        """, (user_id,))

        goals = cursor.fetchall()

        connection.close()

        return goals

    # =========================================================
    # GET TRANSACTIONS
    # =========================================================

    def get_transactions(self, user_id):

        connection = self.connect()

        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                id,
                transaction_type,
                category,
                amount,
                description,
                transaction_date
            FROM transactions
            WHERE user_id = ?
            ORDER BY transaction_date DESC
        """, (user_id,))

        transactions = cursor.fetchall()

        connection.close()

        return transactions

    # =========================================================
    # GET AGENT ACTIVITY
    # =========================================================

    def get_agent_activity(self, user_id):

        connection = self.connect()

        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                id,
                activity_type,
                decision,
                action,
                reason,
                created_at
            FROM agent_activity
            WHERE user_id = ?
            ORDER BY created_at DESC
        """, (user_id,))

        activities = cursor.fetchall()

        connection.close()

        return activities

    # =========================================================
    # DATABASE PATH
    # =========================================================

    def get_database_path(self):

        return str(self.database_path)
        # =========================================================
    # UPDATE FINANCIAL PROFILE
    # =========================================================

    def update_financial_profile(
        self,
        user_id,
        income,
        expenses,
        savings,
        debt,
        emergency_fund,
        risk_preference="Moderate"
    ):

        connection = self.connect()
        cursor = connection.cursor()

        cursor.execute("""
            UPDATE financial_profiles
            SET
                monthly_income = ?,
                monthly_expenses = ?,
                savings = ?,
                debt = ?,
                emergency_fund = ?,
                risk_preference = ?
            WHERE id = (
                SELECT id
                FROM financial_profiles
                WHERE user_id = ?
                ORDER BY id DESC
                LIMIT 1
            )
        """, (
            income,
            expenses,
            savings,
            debt,
            emergency_fund,
            risk_preference,
            user_id
        ))

        connection.commit()
        connection.close()