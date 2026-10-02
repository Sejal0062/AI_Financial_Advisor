import sys

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QStackedWidget,
    QLineEdit,
    QComboBox,
    QMessageBox,
    QScrollArea,
    QProgressBar,
    QTextEdit,
    QGridLayout,
    QSizePolicy,
)
from PySide6.QtCore import Qt

import os
import sys

# Ensure the project root is available when running: python gui/dashboard.py
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from database.database import FinancialDatabase
from services.financial_service import FinancialService
from agent.financial_agent import FinancialAgent
from agent.agent_state import AgentState
from simulation.multi_month_evaluation import MultiMonthEvaluation


class DashboardWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("FINADVISOR AI")
        self.setMinimumSize(1280, 820)
        self.resize(1400, 900)

        # ---------------------------------------------------------
        # DATABASE AND SERVICES
        # ---------------------------------------------------------

        self.database = FinancialDatabase()
        self.service = FinancialService(self.database)
        self.user_id = 1
        self.last_evaluation = None

        self.reload_financial_data()

        self.setup_ui()

    # =============================================================
    # LOAD DATABASE DATA
    # =============================================================

    def reload_financial_data(self):

        financial_data = self.service.load_user_financial_data(
            self.user_id
        )

        self.state = financial_data["state"]
        self.goal_manager = financial_data["goal_manager"]

        self.goals = self.goal_manager.get_goals()

        self.agent = FinancialAgent(
            self.state,
            self.goal_manager,
            memory_key=f"user_{self.user_id}"
        )

    # =============================================================
    # MAIN UI
    # =============================================================

    def setup_ui(self):

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ---------------------------------------------------------
        # SIDEBAR
        # ---------------------------------------------------------

        sidebar = QFrame()
        sidebar.setFixedWidth(255)

        sidebar.setStyleSheet("""
            QFrame {
                background-color: #0B1220;
            }

            QLabel {
                color: white;
            }

            QPushButton {
                background-color: transparent;
                color: #D1D5DB;
                border: none;
                text-align: left;
                padding: 12px 18px;
                font-size: 13px;
                border-radius: 9px;
            }

            QPushButton:hover {
                background-color: #1F2937;
                color: white;
            }
        """)

        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(
            15, 25, 15, 20
        )

        logo = QLabel("FINADVISOR AI")

        logo.setStyleSheet("""
            font-size: 22px;
            font-weight: bold;
            color: white;
            padding: 10px;
        """)

        subtitle = QLabel(
            "Intelligent Financial Agent"
        )

        subtitle.setStyleSheet("""
            color: #9CA3AF;
            font-size: 11px;
            padding-left: 10px;
        """)

        sidebar_layout.addWidget(logo)
        sidebar_layout.addWidget(subtitle)

        sidebar_layout.addSpacing(30)

        sidebar_buttons = [
            "Dashboard",
            "Financial Profile",
            "Goals",
            "Agent Center",
            "Activity Log",
            "Simulation Lab",
            "Agent Evaluation",
            "Reports & Analytics",
            "Settings"
        ]

        # Keep references so the active page can be highlighted.
        self.sidebar_buttons = {}

        for name in sidebar_buttons:

            button = QPushButton(name)

            button.clicked.connect(
                lambda checked=False, n=name:
                self.show_page(n)
            )

            self.sidebar_buttons[name] = button
            sidebar_layout.addWidget(button)

        sidebar_layout.addStretch()

        agent_status = QLabel(
            "●  AGENT ACTIVE"
        )

        agent_status.setStyleSheet("""
            color: #34D399;
            font-weight: bold;
            padding: 10px;
        """)

        sidebar_layout.addWidget(agent_status)

        # ---------------------------------------------------------
        # CONTENT AREA
        # ---------------------------------------------------------

        content = QFrame()

        content.setStyleSheet("""
            QFrame { background-color: #F5F7FB; }
        """)

        content_layout = QVBoxLayout(content)

        content_layout.setContentsMargins(
            30, 25, 30, 25
        )

        # ---------------------------------------------------------
        # HEADER
        # ---------------------------------------------------------

        header_layout = QHBoxLayout()

        self.page_title = QLabel(
            "Financial Dashboard"
        )

        self.page_title.setStyleSheet("""
            font-size: 30px;
            font-weight: 800;
            color: #0F172A;
            padding-bottom: 2px;
        """)

        header_layout.addWidget(
            self.page_title
        )

        header_layout.addStretch()

        status = QLabel(
            "● Intelligent Agent Online"
        )

        status.setStyleSheet("""
            color: #059669;
            font-weight: 700;
            background-color: #ECFDF5;
            border: 1px solid #A7F3D0;
            padding: 9px 14px;
            border-radius: 16px;
        """)

        header_layout.addWidget(status)

        content_layout.addLayout(
            header_layout
        )

        # ---------------------------------------------------------
        # STACKED PAGES
        # ---------------------------------------------------------

        self.pages = QStackedWidget()

        self.dashboard_page = (
            self.create_dashboard_page()
        )

        self.financial_profile_page = (
            self.create_financial_profile_page()
        )

        self.goals_page = (
            self.create_goals_page()
        )

        self.agent_center_page = (
            self.create_agent_center_page()
        )

        self.simulation_page = (
            self.create_simulation_page()
        )

        self.agent_evaluation_page = (
            self.create_agent_evaluation_page()
        )

        self.reports_page = (
            self.create_reports_page()
        )

        self.activity_log_page = (
            self.create_activity_log_page()
        )

        pages = [
            self.dashboard_page,
            self.financial_profile_page,
            self.goals_page,
            self.agent_center_page,
            self.activity_log_page,
            self.simulation_page,
            self.agent_evaluation_page,
            self.reports_page
        ]

        for page in pages:
            self.pages.addWidget(page)

        content_layout.addWidget(
            self.pages
        )

        main_layout.addWidget(
            sidebar
        )

        main_layout.addWidget(
            content
        )

        # Apply the initial active state after all navigation buttons exist.
        self.show_page("Dashboard")

    # =============================================================
    # DASHBOARD PAGE
    # =============================================================

    def create_dashboard_page(self):

        page = QWidget()
        page.setStyleSheet("background: transparent;")

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(4, 4, 12, 24)
        layout.setSpacing(18)

        # ---------------------------------------------------------
        # WELCOME / AGENT BANNER
        # ---------------------------------------------------------
        banner = QFrame()
        banner.setStyleSheet("""
            QFrame {
                background-color: #0F172A;
                border-radius: 16px;
            }
        """)
        banner_layout = QHBoxLayout(banner)
        banner_layout.setContentsMargins(24, 20, 24, 20)

        left = QVBoxLayout()
        welcome = QLabel("Financial Intelligence Overview")
        welcome.setStyleSheet("color: white; font-size: 22px; font-weight: 700;")
        subtitle = QLabel(
            "Your autonomous agent is monitoring the financial environment and goals."
        )
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet("color: #CBD5E1; font-size: 13px; margin-top: 4px;")
        left.addWidget(welcome)
        left.addWidget(subtitle)
        banner_layout.addLayout(left, 1)

        agent_pill = QLabel("●  AGENT ACTIVE")
        agent_pill.setAlignment(Qt.AlignCenter)
        agent_pill.setMinimumWidth(145)
        agent_pill.setStyleSheet("""
            QLabel {
                color: #34D399;
                background-color: #132E27;
                border: 1px solid #245D4E;
                border-radius: 18px;
                padding: 9px 14px;
                font-size: 12px;
                font-weight: 700;
            }
        """)
        banner_layout.addWidget(agent_pill, 0, Qt.AlignTop)
        layout.addWidget(banner)

        # ---------------------------------------------------------
        # SUMMARY CARDS
        # ---------------------------------------------------------
        summary_grid = QGridLayout()
        summary_grid.setHorizontalSpacing(14)
        summary_grid.setVerticalSpacing(14)

        card_data = [
            ("MONTHLY INCOME", f"₹{self.state.income:,.0f}", "Current inflow", "#2563EB"),
            ("MONTHLY EXPENSES", f"₹{self.state.expenses:,.0f}", "Current outflow", "#D97706"),
            ("MONTHLY SURPLUS", f"₹{self.state.monthly_surplus:,.0f}", "Available cash flow", "#059669"),
            ("TOTAL DEBT", f"₹{self.state.debt:,.0f}", "Liability monitored", "#DC2626"),
        ]

        for index, (title, value, hint, accent) in enumerate(card_data):
            card = QFrame()
            card.setMinimumHeight(118)
            card.setStyleSheet(f"""
                QFrame {{
                    background-color: white;
                    border: 1px solid #E2E8F0;
                    border-radius: 14px;
                }}
            """)
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(18, 16, 18, 16)

            title_label = QLabel(title)
            title_label.setStyleSheet("color: #64748B; font-size: 11px; font-weight: 700;")
            value_label = QLabel(value)
            value_label.setStyleSheet(
                f"color: {accent}; font-size: 25px; font-weight: 800; margin-top: 3px;"
            )
            hint_label = QLabel(hint)
            hint_label.setStyleSheet("color: #94A3B8; font-size: 11px;")

            card_layout.addWidget(title_label)
            card_layout.addWidget(value_label)
            card_layout.addStretch()
            card_layout.addWidget(hint_label)
            summary_grid.addWidget(card, 0, index)

        layout.addLayout(summary_grid)

        # ---------------------------------------------------------
        # HEALTH + AGENT STATUS
        # ---------------------------------------------------------
        middle = QHBoxLayout()
        middle.setSpacing(14)

        health_card = QFrame()
        health_card.setStyleSheet("""
            QFrame { background: white; border: 1px solid #E2E8F0; border-radius: 14px; }
        """)
        health_layout = QVBoxLayout(health_card)
        health_layout.setContentsMargins(20, 18, 20, 18)

        health_header = QHBoxLayout()
        health_title = QLabel("Financial Health")
        health_title.setStyleSheet("color: #0F172A; font-size: 18px; font-weight: 700;")
        health_header.addWidget(health_title)
        health_header.addStretch()

        surplus = float(self.state.monthly_surplus)
        income = max(float(self.state.income), 1.0)
        surplus_ratio = max(0.0, min(1.0, surplus / income))
        health_score = int(round(surplus_ratio * 100))
        if self.state.debt > self.state.savings * 0.5:
            health_score = max(0, health_score - 15)
        emergency_target = float(self.state.expenses) * 3
        if emergency_target > 0 and self.state.emergency_fund >= emergency_target:
            health_score = min(100, health_score + 10)
        health_score = max(0, min(100, health_score))

        score = QLabel(f"{health_score}%")
        score.setStyleSheet("color: #059669; font-size: 24px; font-weight: 800;")
        health_header.addWidget(score)
        health_layout.addLayout(health_header)

        health_bar = QProgressBar()
        health_bar.setRange(0, 100)
        health_bar.setValue(health_score)
        health_bar.setTextVisible(False)
        health_bar.setFixedHeight(10)
        health_bar.setStyleSheet("""
            QProgressBar { background: #E2E8F0; border: none; border-radius: 5px; }
            QProgressBar::chunk { background: #10B981; border-radius: 5px; }
        """)
        health_layout.addWidget(health_bar)

        health_note = QLabel(
            "Health indicator based on current surplus, debt pressure and emergency-fund coverage."
        )
        health_note.setWordWrap(True)
        health_note.setStyleSheet("color: #64748B; font-size: 12px; margin-top: 5px;")
        health_layout.addWidget(health_note)
        middle.addWidget(health_card, 1)

        agent_card = QFrame()
        agent_card.setStyleSheet("""
            QFrame { background: white; border: 1px solid #E2E8F0; border-radius: 14px; }
        """)
        agent_layout = QVBoxLayout(agent_card)
        agent_layout.setContentsMargins(20, 18, 20, 18)

        agent_title = QLabel("Agent Intelligence")
        agent_title.setStyleSheet("color: #0F172A; font-size: 18px; font-weight: 700;")
        agent_layout.addWidget(agent_title)

        state_label = QLabel(f"● {self.state.status}  •  Monitoring")
        state_label.setStyleSheet("color: #059669; font-size: 13px; font-weight: 700;")
        agent_layout.addWidget(state_label)

        risk = getattr(self.state, "risk_preference", "Moderate")
        info = QLabel(
            f"Risk preference: {risk}\n"
            f"Goals monitored: {len(self.goals)}\n"
            f"Monthly surplus: ₹{self.state.monthly_surplus:,.0f}"
        )
        info.setStyleSheet("color: #475569; font-size: 13px; line-height: 1.5;")
        agent_layout.addWidget(info)
        agent_layout.addStretch()
        middle.addWidget(agent_card, 1)

        layout.addLayout(middle)

        # ---------------------------------------------------------
        # PRIORITY GOAL + NEXT AUTONOMOUS ACTION
        # ---------------------------------------------------------
        bottom = QHBoxLayout()
        bottom.setSpacing(14)

        goal_card = QFrame()
        goal_card.setStyleSheet("""
            QFrame { background: white; border: 1px solid #E2E8F0; border-radius: 14px; }
        """)
        goal_layout = QVBoxLayout(goal_card)
        goal_layout.setContentsMargins(20, 18, 20, 18)

        goal_heading = QLabel("Priority Goal")
        goal_heading.setStyleSheet("color: #0F172A; font-size: 17px; font-weight: 700;")
        goal_layout.addWidget(goal_heading)

        if self.goals:
            priority_goal = sorted(self.goals, key=lambda g: g.priority)[0]
            progress = max(0.0, min(100.0, priority_goal.get_progress()))
            goal_name = QLabel(priority_goal.name)
            goal_name.setStyleSheet("color: #334155; font-size: 15px; font-weight: 700;")
            goal_amount = QLabel(
                f"₹{priority_goal.current_amount:,.0f} / ₹{priority_goal.target_amount:,.0f}"
            )
            goal_amount.setStyleSheet("color: #64748B; font-size: 12px;")
            bar = QProgressBar()
            bar.setValue(int(progress))
            bar.setFormat(f"{progress:.1f}%")
            bar.setMinimumHeight(18)
            bar.setStyleSheet("""
                QProgressBar { background: #E2E8F0; border: none; border-radius: 8px; text-align: center; color: #0F172A; }
                QProgressBar::chunk { background: #2563EB; border-radius: 8px; }
            """)
            goal_layout.addWidget(goal_name)
            goal_layout.addWidget(goal_amount)
            goal_layout.addWidget(bar)
        else:
            empty = QLabel("No financial goal configured yet.")
            empty.setStyleSheet("color: #64748B; font-size: 13px;")
            goal_layout.addWidget(empty)
        bottom.addWidget(goal_card, 1)

        action_card = QFrame()
        action_card.setStyleSheet("""
            QFrame { background: white; border: 1px solid #E2E8F0; border-radius: 14px; }
        """)
        action_layout = QVBoxLayout(action_card)
        action_layout.setContentsMargins(20, 18, 20, 18)

        action_title = QLabel("Autonomous Agent Focus")
        action_title.setStyleSheet("color: #0F172A; font-size: 17px; font-weight: 700;")
        action_layout.addWidget(action_title)

        if self.state.debt > self.state.savings * 0.5:
            focus = "Debt pressure detected — debt reduction is currently prioritized."
        elif self.state.monthly_surplus <= 0:
            focus = "Cash-flow stress detected — the agent will preserve available cash."
        elif self.state.emergency_fund < self.state.expenses * 3:
            focus = "Emergency-fund coverage is below the 3-month reference level."
        elif self.goals:
            focus = f"Monitoring the priority goal: {sorted(self.goals, key=lambda g: g.priority)[0].name}."
        else:
            focus = "Financial conditions are currently being monitored."

        focus_label = QLabel(focus)
        focus_label.setWordWrap(True)
        focus_label.setStyleSheet("color: #475569; font-size: 13px; line-height: 1.5;")
        action_layout.addWidget(focus_label)
        action_layout.addStretch()

        run_btn = QPushButton("▶  Run Agent Cycle")
        run_btn.setCursor(Qt.PointingHandCursor)
        run_btn.setMinimumHeight(40)
        run_btn.setStyleSheet("""
            QPushButton { background: #0F172A; color: white; border: none; border-radius: 8px; font-weight: 700; padding: 8px 14px; }
            QPushButton:hover { background: #1E293B; }
        """)
        run_btn.clicked.connect(lambda: self.show_page("Agent Center"))
        action_layout.addWidget(run_btn, 0, Qt.AlignRight)
        bottom.addWidget(action_card, 1)

        layout.addLayout(bottom)
        layout.addStretch()

        scroll.setWidget(container)
        page_layout = QVBoxLayout(page)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.addWidget(scroll)
        return page

    # =============================================================
    # FINANCIAL PROFILE PAGE
    # =============================================================

    def create_financial_profile_page(self):

        page = QWidget()

        outer_layout = QVBoxLayout(page)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        container = QWidget()

        layout = QVBoxLayout(container)

        layout.setContentsMargins(
            5, 5, 15, 20
        )

        layout.setSpacing(16)

        intro = QLabel(
            "Update the financial environment used by "
            "the Intelligent Agent. Changes are saved "
            "to the local SQLite database."
        )

        intro.setWordWrap(True)

        intro.setStyleSheet("""
            color: #4B5563;
            font-size: 14px;
            padding: 5px 0 8px 0;
        """)

        layout.addWidget(intro)

        card = QFrame()

        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #E5E7EB;
                border-radius: 12px;
            }

            QLabel {
                color: #374151;
                font-size: 14px;
            }

            QLineEdit,
            QComboBox {
                background-color: #F9FAFB;
                border: 1px solid #D1D5DB;
                border-radius: 7px;
                padding: 10px;
                color: #111827;
                font-size: 14px;
                min-height: 20px;
            }

            QLineEdit:focus,
            QComboBox:focus {
                border: 1px solid #111827;
            }
        """)

        form = QVBoxLayout(card)

        form.setContentsMargins(
            24, 22, 24, 22
        )

        form.setSpacing(13)

        title = QLabel(
            "Financial Information"
        )

        title.setStyleSheet("""
            color: #111827;
            font-size: 19px;
            font-weight: bold;
        """)

        form.addWidget(title)

        self.profile_income = (
            self.create_profile_field(
                form,
                "Monthly Income (₹)",
                self.state.income
            )
        )

        self.profile_expenses = (
            self.create_profile_field(
                form,
                "Monthly Expenses (₹)",
                self.state.expenses
            )
        )

        self.profile_savings = (
            self.create_profile_field(
                form,
                "Savings (₹)",
                self.state.savings
            )
        )

        self.profile_debt = (
            self.create_profile_field(
                form,
                "Debt (₹)",
                self.state.debt
            )
        )

        self.profile_emergency = (
            self.create_profile_field(
                form,
                "Emergency Fund (₹)",
                self.state.emergency_fund
            )
        )

        form.addWidget(
            QLabel("Risk Preference")
        )

        self.profile_risk = QComboBox()

        self.profile_risk.addItems(
            [
                "Conservative",
                "Moderate",
                "Aggressive"
            ]
        )

        current_risk = getattr(
            self.state,
            "risk_preference",
            "Moderate"
        )

        index = self.profile_risk.findText(
            str(current_risk),
            Qt.MatchFixedString
        )

        if index >= 0:
            self.profile_risk.setCurrentIndex(
                index
            )

        form.addWidget(
            self.profile_risk
        )

        save_button = QPushButton(
            "Save Financial Profile"
        )

        save_button.setMinimumHeight(46)

        save_button.setStyleSheet("""
            QPushButton {
                background-color: #111827;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 15px;
                font-weight: bold;
                padding: 10px 18px;
            }

            QPushButton:hover {
                background-color: #1F2937;
            }
        """)

        save_button.clicked.connect(
            self.save_financial_profile
        )

        form.addWidget(
            save_button
        )

        self.profile_message = QLabel("")

        self.profile_message.setWordWrap(True)

        form.addWidget(
            self.profile_message
        )

        layout.addWidget(card)

        note = QLabel(
            "Note: This application uses simulated "
            "financial planning. Saving a profile changes "
            "the data used by the local agent; it does not "
            "transfer or invest real money."
        )

        note.setWordWrap(True)

        note.setStyleSheet("""
            color: #6B7280;
            font-size: 12px;
        """)

        layout.addWidget(note)

        layout.addStretch()

        scroll.setWidget(container)

        outer_layout.addWidget(scroll)

        return page

    def create_profile_field(
        self,
        form,
        label_text,
        value
    ):

        form.addWidget(
            QLabel(label_text)
        )

        field = QLineEdit()

        field.setText(
            f"{float(value):.2f}"
        )

        field.setPlaceholderText(
            "Enter amount"
        )

        form.addWidget(field)

        return field

    # =============================================================
    # SAVE FINANCIAL PROFILE
    # =============================================================

    def save_financial_profile(self):

        try:

            income = self.read_profile_amount(
                self.profile_income,
                "Monthly income"
            )

            expenses = self.read_profile_amount(
                self.profile_expenses,
                "Monthly expenses"
            )

            savings = self.read_profile_amount(
                self.profile_savings,
                "Savings"
            )

            debt = self.read_profile_amount(
                self.profile_debt,
                "Debt"
            )

            emergency_fund = self.read_profile_amount(
                self.profile_emergency,
                "Emergency fund"
            )

            risk_preference = (
                self.profile_risk.currentText()
            )

            if income <= 0:
                raise ValueError(
                    "Monthly income must be greater than zero."
                )

            if (
                expenses < 0
                or savings < 0
                or debt < 0
                or emergency_fund < 0
            ):
                raise ValueError(
                    "Expenses, savings, debt and emergency "
                    "fund cannot be negative."
                )

            self.database.update_financial_profile(
                user_id=self.user_id,
                income=income,
                expenses=expenses,
                savings=savings,
                debt=debt,
                emergency_fund=emergency_fund,
                risk_preference=risk_preference
            )

            self.reload_financial_data()

            old_dashboard = (
                self.dashboard_page
            )

            self.dashboard_page = (
                self.create_dashboard_page()
            )

            index = self.pages.indexOf(
                old_dashboard
            )

            if index >= 0:

                self.pages.removeWidget(
                    old_dashboard
                )

                old_dashboard.deleteLater()

                self.pages.insertWidget(
                    index,
                    self.dashboard_page
                )

            self.profile_message.setStyleSheet("""
                color: #059669;
                font-size: 13px;
            """)

            self.profile_message.setText(
                "✓ Financial profile saved successfully. "
                "The Intelligent Agent is now using the "
                "updated financial environment."
            )

            QMessageBox.information(
                self,
                "Profile Saved",
                "Financial profile updated successfully.\n\n"
                "The agent state has been refreshed from SQLite."
            )

        except ValueError as e:

            self.profile_message.setStyleSheet("""
                color: #DC2626;
                font-size: 13px;
            """)

            self.profile_message.setText(
                f"✕ {str(e)}"
            )

        except Exception as e:

            self.profile_message.setStyleSheet("""
                color: #DC2626;
                font-size: 13px;
            """)

            self.profile_message.setText(
                f"✕ Could not save profile: {str(e)}"
            )

    def read_profile_amount(
        self,
        field,
        field_name
    ):

        text = (
            field.text()
            .strip()
            .replace(",", "")
            .replace("₹", "")
        )

        if not text:
            raise ValueError(
                f"{field_name} is required."
            )

        try:
            return float(text)

        except ValueError:

            raise ValueError(
                f"{field_name} must contain a valid number."
            )

    # =============================================================
    # GOALS PAGE
    # =============================================================

    def create_goals_page(self):

        page = QWidget()

        outer_layout = QVBoxLayout(page)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        container = QWidget()

        layout = QVBoxLayout(container)

        layout.setContentsMargins(
            5, 5, 15, 20
        )

        layout.setSpacing(16)

        intro = QLabel(
            "Financial goals monitored by the "
            "Intelligent Agent. The agent evaluates "
            "goal priority and progress when making "
            "autonomous financial decisions."
        )

        intro.setWordWrap(True)

        intro.setStyleSheet("""
            color: #4B5563;
            font-size: 14px;
        """)

        layout.addWidget(intro)

        form_card = QFrame()

        form_card.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #E5E7EB;
                border-radius: 12px;
            }

            QLabel {
                color: #374151;
                font-size: 13px;
            }

            QLineEdit,
            QComboBox {
                background-color: #F9FAFB;
                border: 1px solid #D1D5DB;
                border-radius: 7px;
                padding: 9px;
                color: #111827;
                font-size: 14px;
            }
        """)

        form = QVBoxLayout(form_card)

        form.setContentsMargins(
            22, 20, 22, 20
        )

        form.setSpacing(9)

        title = QLabel(
            "Add Financial Goal"
        )

        title.setStyleSheet("""
            color: #111827;
            font-size: 19px;
            font-weight: bold;
        """)

        form.addWidget(title)

        form.addWidget(
            QLabel("Goal Name")
        )

        self.goal_name_input = QLineEdit()

        self.goal_name_input.setPlaceholderText(
            "Example: House, Education, Retirement"
        )

        form.addWidget(
            self.goal_name_input
        )

        form.addWidget(
            QLabel("Target Amount (₹)")
        )

        self.goal_target_input = QLineEdit()

        self.goal_target_input.setPlaceholderText(
            "Example: 500000"
        )

        form.addWidget(
            self.goal_target_input
        )

        form.addWidget(
            QLabel("Current Amount (₹)")
        )

        self.goal_current_input = QLineEdit()

        self.goal_current_input.setText("0")

        form.addWidget(
            self.goal_current_input
        )

        form.addWidget(
            QLabel("Priority")
        )

        self.goal_priority_input = QComboBox()

        self.goal_priority_input.addItems(
            ["1", "2", "3", "4", "5"]
        )

        form.addWidget(
            self.goal_priority_input
        )

        form.addWidget(
            QLabel("Monthly Contribution (₹)")
        )

        self.goal_contribution_input = QLineEdit()

        self.goal_contribution_input.setText("0")

        form.addWidget(
            self.goal_contribution_input
        )

        add_button = QPushButton(
            "＋  Add Goal"
        )

        add_button.setMinimumHeight(44)

        add_button.setStyleSheet("""
            QPushButton {
                background-color: #111827;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #1F2937;
            }
        """)

        add_button.clicked.connect(
            self.add_financial_goal
        )

        form.addWidget(
            add_button
        )

        self.goal_message = QLabel("")

        self.goal_message.setWordWrap(True)

        form.addWidget(
            self.goal_message
        )

        layout.addWidget(
            form_card
        )

        goals_title = QLabel(
            "Current Financial Goals"
        )

        goals_title.setStyleSheet("""
            color: #111827;
            font-size: 20px;
            font-weight: bold;
        """)

        layout.addWidget(
            goals_title
        )

        self.goals_container = QVBoxLayout()

        self.goals_container.setSpacing(12)

        layout.addLayout(
            self.goals_container
        )

        self.refresh_goals_display()

        layout.addStretch()

        scroll.setWidget(
            container
        )

        outer_layout.addWidget(
            scroll
        )

        return page

    def add_financial_goal(self):

        try:

            name = (
                self.goal_name_input
                .text()
                .strip()
            )

            if not name:

                raise ValueError(
                    "Goal name is required."
                )

            target = self.read_goal_amount(
                self.goal_target_input,
                "Target amount"
            )

            current = self.read_goal_amount(
                self.goal_current_input,
                "Current amount"
            )

            contribution = self.read_goal_amount(
                self.goal_contribution_input,
                "Monthly contribution"
            )

            priority = int(
                self.goal_priority_input.currentText()
            )

            if target <= 0:

                raise ValueError(
                    "Target amount must be greater than zero."
                )

            if current < 0 or contribution < 0:

                raise ValueError(
                    "Current amount and monthly contribution "
                    "cannot be negative."
                )

            if current > target:

                raise ValueError(
                    "Current amount cannot be greater than target."
                )

            self.database.add_goal(
                user_id=self.user_id,
                name=name,
                target_amount=target,
                current_amount=current,
                priority=priority,
                monthly_contribution=contribution
            )

            self.reload_financial_data()

            self.goal_name_input.clear()
            self.goal_target_input.clear()
            self.goal_current_input.setText("0")
            self.goal_priority_input.setCurrentIndex(0)
            self.goal_contribution_input.setText("0")

            self.goal_message.setStyleSheet("""
                color: #059669;
                font-size: 13px;
            """)

            self.goal_message.setText(
                f"✓ '{name}' added successfully. "
                "The Intelligent Agent will monitor this goal."
            )

            self.refresh_goals_display()

        except ValueError as e:

            self.goal_message.setStyleSheet("""
                color: #DC2626;
                font-size: 13px;
            """)

            self.goal_message.setText(
                f"✕ {str(e)}"
            )

        except Exception as e:

            self.goal_message.setStyleSheet("""
                color: #DC2626;
                font-size: 13px;
            """)

            self.goal_message.setText(
                f"✕ Could not add goal: {str(e)}"
            )

    def read_goal_amount(
        self,
        field,
        field_name
    ):

        text = (
            field.text()
            .strip()
            .replace(",", "")
            .replace("₹", "")
        )

        if not text:

            raise ValueError(
                f"{field_name} is required."
            )

        try:

            return float(text)

        except ValueError:

            raise ValueError(
                f"{field_name} must contain a valid number."
            )

    def refresh_goals_display(self):

        while self.goals_container.count():

            item = (
                self.goals_container.takeAt(0)
            )

            widget = item.widget()

            if widget is not None:

                widget.deleteLater()

        if not self.goals:

            empty = QLabel(
                "No financial goals configured yet."
            )

            empty.setStyleSheet("""
                color: #6B7280;
                font-size: 14px;
                padding: 15px;
            """)

            self.goals_container.addWidget(
                empty
            )

            return

        for goal in sorted(
            self.goals,
            key=lambda g: g.priority
        ):

            card = QFrame()

            card.setStyleSheet("""
                QFrame {
                    background-color: white;
                    border: 1px solid #E5E7EB;
                    border-radius: 12px;
                }
            """)

            card_layout = QVBoxLayout(card)

            header = QHBoxLayout()

            title = QLabel(
                f"🎯  {goal.name}"
            )

            title.setStyleSheet("""
                color: #111827;
                font-size: 17px;
                font-weight: bold;
            """)

            header.addWidget(title)
            header.addStretch()

            priority = QLabel(
                f"Priority {goal.priority}"
            )

            priority.setStyleSheet("""
                color: #059669;
                background-color: #ECFDF5;
                border-radius: 6px;
                padding: 5px 10px;
                font-size: 12px;
                font-weight: bold;
            """)

            header.addWidget(priority)

            card_layout.addLayout(header)

            progress = max(
                0.0,
                min(
                    100.0,
                    goal.get_progress()
                )
            )

            amount = QLabel(
                f"₹{goal.current_amount:,.0f} / "
                f"₹{goal.target_amount:,.0f}"
            )

            amount.setStyleSheet("""
                color: #374151;
                font-size: 15px;
                font-weight: bold;
            """)

            card_layout.addWidget(
                amount
            )

            progress_bar = QProgressBar()

            progress_bar.setValue(
                int(progress)
            )

            progress_bar.setFormat(
                f"{progress:.1f}%"
            )

            progress_bar.setTextVisible(True)

            progress_bar.setMinimumHeight(18)

            progress_bar.setStyleSheet("""
                QProgressBar {
                    background-color: #E5E7EB;
                    border: none;
                    border-radius: 8px;
                    text-align: center;
                    color: #111827;
                }

                QProgressBar::chunk {
                    background-color: #059669;
                    border-radius: 8px;
                }
            """)

            card_layout.addWidget(
                progress_bar
            )

            remaining = max(
                0.0,
                goal.remaining_amount()
            )

            details = QLabel(
                f"Remaining: ₹{remaining:,.0f}\n"
                f"Monthly Contribution: "
                f"₹{goal.monthly_contribution:,.0f}"
            )

            details.setStyleSheet("""
                color: #6B7280;
                font-size: 13px;
            """)

            card_layout.addWidget(
                details
            )

            status = QLabel(
                "✓ Goal completed"
                if progress >= 100
                else
                "● Goal monitored by Intelligent Agent"
            )

            status.setStyleSheet(
                "color: #059669; font-size: 13px; "
                "font-weight: bold;"
                if progress >= 100
                else
                "color: #4B5563; font-size: 13px;"
            )

            card_layout.addWidget(
                status
            )

            self.goals_container.addWidget(
                card
            )

    # =============================================================
    # AGENT CENTER
    # =============================================================

    def create_agent_center_page(self):

        page = QWidget()

        outer_scroll = QScrollArea()
        outer_scroll.setWidgetResizable(True)
        outer_scroll.setFrameShape(QFrame.NoFrame)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 20)
        layout.setSpacing(16)

        description = QLabel(
            "The Intelligent Agent observes the financial environment, "
            "consults its memory, evaluates multiple financial factors, "
            "selects a priority autonomously, and adjusts the simulated plan."
        )
        description.setWordWrap(True)
        description.setStyleSheet("color: #4B5563; font-size: 14px;")
        layout.addWidget(description)

        run_button = QPushButton("▶   Run Agent Cycle")
        run_button.setMinimumHeight(48)
        run_button.setStyleSheet("""
            QPushButton {
                background-color: #111827;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 18px;
                font-size: 15px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #1F2937; }
        """)
        run_button.clicked.connect(self.run_agent_cycle)
        layout.addWidget(run_button)

        # ---------------------------------------------------------
        # MULTI-FACTOR ASSESSMENT CARD
        # ---------------------------------------------------------
        factor_card = QFrame()
        factor_card.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #E5E7EB;
                border-radius: 12px;
            }
        """)
        factor_layout = QVBoxLayout(factor_card)
        factor_layout.setContentsMargins(18, 16, 18, 16)
        factor_layout.setSpacing(10)

        factor_title = QLabel("Multi-Factor Financial Assessment")
        factor_title.setStyleSheet(
            "color: #111827; font-size: 19px; font-weight: bold;"
        )
        factor_layout.addWidget(factor_title)

        factor_subtitle = QLabel(
            "The agent evaluates six observed factors before selecting its autonomous response."
        )
        factor_subtitle.setStyleSheet("color: #6B7280; font-size: 12px;")
        factor_layout.addWidget(factor_subtitle)

        self.factor_labels = {}
        factor_names = [
            ("cash_flow", "Cash Flow"),
            ("income_stability", "Income Stability"),
            ("expense_pressure", "Expense Pressure"),
            ("debt_pressure", "Debt Pressure"),
            ("emergency_coverage", "Emergency Coverage"),
            ("goal_urgency", "Goal Urgency"),
        ]

        factor_grid = QGridLayout()
        factor_grid.setHorizontalSpacing(12)
        factor_grid.setVerticalSpacing(8)

        for index, (key, label_text) in enumerate(factor_names):
            card = QFrame()
            card.setStyleSheet("""
                QFrame {
                    background-color: #F8FAFC;
                    border: 1px solid #E5E7EB;
                    border-radius: 8px;
                }
            """)
            card_layout = QHBoxLayout(card)
            card_layout.setContentsMargins(10, 7, 10, 7)

            name = QLabel(label_text)
            name.setStyleSheet("color: #374151; font-size: 12px; font-weight: 600;")

            value = QLabel("—")
            value.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            value.setStyleSheet("color: #6B7280; font-size: 12px; font-weight: bold;")

            card_layout.addWidget(name)
            card_layout.addStretch()
            card_layout.addWidget(value)
            self.factor_labels[key] = value

            row = index // 2
            col = index % 2
            factor_grid.addWidget(card, row, col)

        factor_layout.addLayout(factor_grid)

        self.dominant_factor_label = QLabel(
            "Dominant factor: Run an agent cycle to evaluate the current state."
        )
        self.dominant_factor_label.setWordWrap(True)
        self.dominant_factor_label.setStyleSheet(
            "color: #1D4ED8; background-color: #EFF6FF; "
            "border: 1px solid #BFDBFE; border-radius: 8px; "
            "padding: 9px; font-size: 12px; font-weight: bold;"
        )
        factor_layout.addWidget(self.dominant_factor_label)

        layout.addWidget(factor_card)

        # ---------------------------------------------------------
        # FINANCIAL HEALTH STATE CARD
        # ---------------------------------------------------------
        health_card = QFrame()
        health_card.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #E5E7EB;
                border-radius: 12px;
            }
        """)
        health_layout = QVBoxLayout(health_card)
        health_layout.setContentsMargins(18, 16, 18, 16)
        health_layout.setSpacing(8)

        health_title = QLabel("Financial Health State")
        health_title.setStyleSheet(
            "color: #111827; font-size: 19px; font-weight: bold;"
        )
        health_layout.addWidget(health_title)

        health_subtitle = QLabel(
            "The agent converts the observed financial environment into an explicit internal state."
        )
        health_subtitle.setStyleSheet("color: #6B7280; font-size: 12px;")
        health_layout.addWidget(health_subtitle)

        health_row = QHBoxLayout()
        self.health_state_label = QLabel("AWAITING AGENT CYCLE")
        self.health_state_label.setStyleSheet(
            "color: #6B7280; background-color: #F8FAFC; "
            "border: 1px solid #E5E7EB; border-radius: 8px; "
            "padding: 10px 14px; font-size: 15px; font-weight: bold;"
        )
        self.health_detail_label = QLabel(
            "Run an agent cycle to evaluate the current financial state."
        )
        self.health_detail_label.setWordWrap(True)
        self.health_detail_label.setStyleSheet(
            "color: #4B5563; font-size: 12px; padding-left: 8px;"
        )
        health_row.addWidget(self.health_state_label, 0)
        health_row.addWidget(self.health_detail_label, 1)
        health_layout.addLayout(health_row)

        health_metrics = QHBoxLayout()
        self.health_coverage_label = QLabel("Emergency coverage: —")
        self.health_debt_ratio_label = QLabel("Debt / savings: —")
        self.health_surplus_label = QLabel("Monthly surplus: —")
        for widget in (
            self.health_coverage_label,
            self.health_debt_ratio_label,
            self.health_surplus_label,
        ):
            widget.setStyleSheet(
                "color: #374151; background-color: #F8FAFC; "
                "border: 1px solid #E5E7EB; border-radius: 7px; "
                "padding: 7px; font-size: 11px;"
            )
            health_metrics.addWidget(widget)
        health_layout.addLayout(health_metrics)
        layout.addWidget(health_card)

        # ---------------------------------------------------------
        # MULTI-GOAL COMPETITION CARD
        # ---------------------------------------------------------
        goal_competition_card = QFrame()
        goal_competition_card.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #E5E7EB;
                border-radius: 12px;
            }
        """)
        goal_competition_layout = QVBoxLayout(goal_competition_card)
        goal_competition_layout.setContentsMargins(18, 16, 18, 16)
        goal_competition_layout.setSpacing(9)

        goal_competition_title = QLabel("Multi-Goal Competition")
        goal_competition_title.setStyleSheet(
            "color: #111827; font-size: 19px; font-weight: bold;"
        )
        goal_competition_layout.addWidget(goal_competition_title)

        goal_competition_subtitle = QLabel(
            "The agent compares all configured goals before selecting a goal-focused response."
        )
        goal_competition_subtitle.setStyleSheet("color: #6B7280; font-size: 12px;")
        goal_competition_layout.addWidget(goal_competition_subtitle)

        self.goal_competition_output = QTextEdit()
        self.goal_competition_output.setReadOnly(True)
        self.goal_competition_output.setMinimumHeight(145)
        self.goal_competition_output.setMaximumHeight(210)
        self.goal_competition_output.setPlaceholderText(
            "Run an agent cycle to compare all financial goals."
        )
        self.goal_competition_output.setStyleSheet("""
            QTextEdit {
                background-color: #F8FAFC;
                border: 1px solid #E5E7EB;
                border-radius: 8px;
                padding: 8px;
                color: #111827;
                font-size: 12px;
            }
        """)
        goal_competition_layout.addWidget(self.goal_competition_output)

        self.goal_competition_selected = QLabel(
            "Selected goal: Run an agent cycle to evaluate competing goals."
        )
        self.goal_competition_selected.setWordWrap(True)
        self.goal_competition_selected.setStyleSheet(
            "color: #1D4ED8; background-color: #EFF6FF; "
            "border: 1px solid #BFDBFE; border-radius: 8px; "
            "padding: 9px; font-size: 12px; font-weight: bold;"
        )
        goal_competition_layout.addWidget(self.goal_competition_selected)

        layout.addWidget(goal_competition_card)

        # ---------------------------------------------------------
        # DECISION / REASONING CARD
        # ---------------------------------------------------------
        result_card = QFrame()
        result_card.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #E5E7EB;
                border-radius: 12px;
            }
        """)
        result_layout = QVBoxLayout(result_card)
        result_layout.setContentsMargins(18, 16, 18, 16)

        result_title = QLabel("Autonomous Decision & Explainability")
        result_title.setStyleSheet(
            "color: #111827; font-size: 19px; font-weight: bold;"
        )
        result_layout.addWidget(result_title)

        self.agent_output = QTextEdit()
        self.agent_output.setReadOnly(True)
        self.agent_output.setMinimumHeight(430)
        self.agent_output.setPlaceholderText(
            "Run an agent cycle to view perception, multi-factor assessment, "
            "decision, reasoning, action and updated plan."
        )
        self.agent_output.setStyleSheet("""
            QTextEdit {
                background-color: #F8FAFC;
                border: 1px solid #E5E7EB;
                border-radius: 8px;
                padding: 10px;
                color: #111827;
                font-size: 13px;
            }
        """)
        result_layout.addWidget(self.agent_output)

        layout.addWidget(result_card)
        layout.addStretch()

        outer_scroll.setWidget(container)

        page_layout = QVBoxLayout(page)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.addWidget(outer_scroll)

        return page

    # =============================================================
    # RUN REAL AGENT CYCLE
    # =============================================================

    def run_agent_cycle(self):

        try:
            result = self.agent.run_cycle()

            observation = result.get("observation", {})
            decision = result.get("decision", {})
            action = result.get("action", "")
            updated_plan = result.get("updated_plan", {})

            if isinstance(observation, dict):
                observation_text = (
                    f"Income: ₹{observation.get('income', self.state.income):,.0f}\n"
                    f"Expenses: ₹{observation.get('expenses', self.state.expenses):,.0f}\n"
                    f"Savings: ₹{observation.get('savings', self.state.savings):,.0f}\n"
                    f"Debt: ₹{observation.get('debt', self.state.debt):,.0f}\n"
                    f"Emergency Fund: ₹{observation.get('emergency_fund', self.state.emergency_fund):,.0f}\n"
                    f"Monthly Surplus: ₹{observation.get('monthly_surplus', self.state.monthly_surplus):,.0f}"
                )
            else:
                observation_text = str(observation)

            if isinstance(decision, dict):
                decision_text = decision.get("decision", "No decision recorded.")
                reason_text = decision.get("reason", "No additional reasoning provided.")
                evaluation = decision.get("multi_factor_evaluation", {}) or {}
                memory_context = decision.get("memory_context", {}) or {}
            else:
                decision_text = str(decision)
                reason_text = "No additional reasoning provided."
                evaluation = {}
                memory_context = {}

            if isinstance(action, dict):
                action_text = action.get("action", str(action))
            else:
                action_text = str(action)

            plan = updated_plan if isinstance(updated_plan, dict) else {}

            # -----------------------------------------------------
            # DISPLAY MULTI-FACTOR RESULTS
            # -----------------------------------------------------
            factors = evaluation.get("factors", {}) if isinstance(evaluation, dict) else {}
            health_state = evaluation.get("financial_health_state", {}) if isinstance(evaluation, dict) else {}

            # -----------------------------------------------------
            # DISPLAY FINANCIAL HEALTH STATE
            # -----------------------------------------------------
            state_name = health_state.get("state", "UNKNOWN")
            severity = health_state.get("severity", "")
            state_reason = health_state.get("description", health_state.get("reason", ""))
            emergency_months = health_state.get("emergency_coverage_months", health_state.get("emergency_months", 0))
            debt_ratio = health_state.get("debt_savings_ratio", health_state.get("debt_ratio", 0))
            surplus_value = health_state.get("monthly_surplus", observation.get("monthly_surplus", 0))

            state_styles = {
                "STABLE": ("#059669", "#ECFDF5", "#A7F3D0"),
                "GOAL_ACCELERATION": ("#2563EB", "#EFF6FF", "#BFDBFE"),
                "CAUTION": ("#D97706", "#FFFBEB", "#FDE68A"),
                "DEBT_PRESSURE": ("#EA580C", "#FFF7ED", "#FED7AA"),
                "EMERGENCY_RISK": ("#DC2626", "#FEF2F2", "#FECACA"),
                "CASH_FLOW_STRESS": ("#B91C1C", "#FEF2F2", "#FECACA"),
            }
            state_color, state_bg, state_border = state_styles.get(
                state_name, ("#6B7280", "#F8FAFC", "#E5E7EB")
            )
            self.health_state_label.setText(f"●  {state_name}  •  {severity}")
            self.health_state_label.setStyleSheet(
                f"color: {state_color}; background-color: {state_bg}; "
                f"border: 1px solid {state_border}; border-radius: 8px; "
                "padding: 10px 14px; font-size: 15px; font-weight: bold;"
            )
            self.health_detail_label.setText(state_reason)
            self.health_coverage_label.setText(
                f"Emergency coverage: {emergency_months:.1f} month(s)"
            )
            self.health_debt_ratio_label.setText(
                f"Debt / savings: {debt_ratio * 100:.1f}%"
            )
            self.health_surplus_label.setText(
                f"Monthly surplus: ₹{surplus_value:,.0f}"
            )

            # -----------------------------------------------------
            # DISPLAY MULTI-GOAL COMPETITION
            # -----------------------------------------------------
            goal_competition = decision.get("goal_competition", {}) if isinstance(decision, dict) else {}
            competing_goals = goal_competition.get("goals", []) if isinstance(goal_competition, dict) else []
            selected_goal = goal_competition.get("selected_goal") if isinstance(goal_competition, dict) else None
            competition_lines = []

            for goal_item in competing_goals:
                competition_lines.append(
                    f"{goal_item.get('name', 'Goal')}: "
                    f"{goal_item.get('score', 0):.1f}/100  "
                    f"| {goal_item.get('progress', 0):.1f}% complete  "
                    f"| Priority {goal_item.get('priority', '—')}"
                )

            if competition_lines:
                self.goal_competition_output.setText("\n".join(competition_lines))
            else:
                self.goal_competition_output.setText(
                    "No financial goals are currently configured."
                )

            if selected_goal:
                self.goal_competition_selected.setText(
                    f"Selected goal: {selected_goal.get('name', '—')}  •  "
                    f"Score {selected_goal.get('score', 0):.1f}/100  •  "
                    f"{goal_competition.get('reason', '')}"
                )
            else:
                self.goal_competition_selected.setText(
                    "Selected goal: No goal selected because no goals are configured."
                )

            for key, label in getattr(self, "factor_labels", {}).items():
                factor = factors.get(key, {}) if isinstance(factors, dict) else {}
                level = factor.get("level", "—")
                score = factor.get("score", "—")
                display_level = level
                if key == "emergency_coverage" and level != "—":
                    display_level = f"{level} RISK"
                label.setText(f"{display_level}  •  {score}/100")

                if level in ("CRITICAL", "HIGH"):
                    label.setStyleSheet("color: #DC2626; font-size: 12px; font-weight: bold;")
                elif level in ("MEDIUM", "MODERATE"):
                    label.setStyleSheet("color: #D97706; font-size: 12px; font-weight: bold;")
                elif level == "LOW":
                    label.setStyleSheet("color: #059669; font-size: 12px; font-weight: bold;")
                else:
                    label.setStyleSheet("color: #6B7280; font-size: 12px; font-weight: bold;")

            selected = evaluation.get("selected", {}) if isinstance(evaluation, dict) else {}
            selected_key = selected.get("key", "") if isinstance(selected, dict) else ""
            selected_score = selected.get("score", 0) if isinstance(selected, dict) else 0

            factor_key_map = {
                "CASH_FLOW_PROTECTION": ("Cash Flow", "cash_flow"),
                "INCOME_PROTECTION": ("Income Stability", "income_stability"),
                "EXPENSE_CONTROL": ("Expense Pressure", "expense_pressure"),
                "DEBT_REDUCTION": ("Debt Pressure", "debt_pressure"),
                "EMERGENCY_FUND": ("Emergency Coverage", "emergency_coverage"),
                "GOAL_PRIORITY": ("Goal Urgency", "goal_urgency"),
                "MAINTAIN_PLAN": ("No dominant risk", None),
            }

            dominant_name, dominant_key = factor_key_map.get(
                selected_key, ("Current financial state", None)
            )

            if dominant_key and dominant_key in factors:
                dominant_level = factors[dominant_key].get("level", "—")
                self.dominant_factor_label.setText(
                    f"Dominant factor: {dominant_name} • {dominant_level} • "
                    f"Priority score {selected_score}/100"
                )
            else:
                self.dominant_factor_label.setText(
                    f"Dominant factor: {dominant_name} • Priority score {selected_score}/100"
                )

            memory_cycles = self.agent.get_memory_statistics().get("cycles", 0)
            history_used = "Yes" if memory_context.get("history_available") else "No"

            output = (
                "🤖  AUTONOMOUS AGENT CYCLE COMPLETED\n\n"
                "1. ENVIRONMENT PERCEPTION\n"
                "────────────────────────────────────────\n"
                f"{observation_text}\n\n"
                "2. MULTI-FACTOR ASSESSMENT\n"
                "────────────────────────────────────────\n"
                f"Cash Flow: {factors.get('cash_flow', {}).get('level', '—')} "
                f"({factors.get('cash_flow', {}).get('score', '—')}/100)\n"
                f"Income Stability: {factors.get('income_stability', {}).get('level', '—')} "
                f"({factors.get('income_stability', {}).get('score', '—')}/100)\n"
                f"Expense Pressure: {factors.get('expense_pressure', {}).get('level', '—')} "
                f"({factors.get('expense_pressure', {}).get('score', '—')}/100)\n"
                f"Debt Pressure: {factors.get('debt_pressure', {}).get('level', '—')} "
                f"({factors.get('debt_pressure', {}).get('score', '—')}/100)\n"
                f"Emergency Coverage: {factors.get('emergency_coverage', {}).get('level', '—')} "
                f"({factors.get('emergency_coverage', {}).get('score', '—')}/100)\n"
                f"Goal Urgency: {factors.get('goal_urgency', {}).get('level', '—')} "
                f"({factors.get('goal_urgency', {}).get('score', '—')}/100)\n\n"
                "3. FINANCIAL HEALTH STATE\n"
                "────────────────────────────────────────\n"
                f"State: {state_name}\n"
                f"Severity: {severity}\n"
                f"Reason: {state_reason}\n"
                f"Emergency Coverage: {emergency_months:.1f} month(s)\n"
                f"Debt / Savings: {debt_ratio * 100:.1f}%\n\n"
                "4. MULTI-GOAL COMPETITION\n"
                "────────────────────────────────────────\n"
                + ("\n".join(
                    [
                        f"{item.get('name', 'Goal')}: {item.get('score', 0):.1f}/100 "
                        f"({item.get('progress', 0):.1f}% complete)"
                        for item in competing_goals
                    ]
                ) if competing_goals else "No financial goals configured.")
                + "\n"
                + (
                    f"Selected Goal: {selected_goal.get('name', '—')} "
                    f"({selected_goal.get('score', 0):.1f}/100)\n"
                    if selected_goal else "Selected Goal: None\n"
                )
                + "\n"
                "5. AUTONOMOUS DECISION\n"
                "────────────────────────────────────────\n"
                f"{decision_text}\n"
                f"Priority Score: {selected_score}/100\n\n"
                "6. AGENT REASONING\n"
                "────────────────────────────────────────\n"
                f"{reason_text}\n\n"
                "7. MEMORY CONTEXT\n"
                "────────────────────────────────────────\n"
                f"Previous memory consulted: {history_used}\n"
                f"Completed cycles stored: {memory_cycles}\n\n"
                "8. AUTONOMOUS ACTION\n"
                "────────────────────────────────────────\n"
                f"{action_text}\n\n"
                "9. UPDATED FINANCIAL PLAN\n"
                "────────────────────────────────────────\n"
                f"Emergency Allocation: ₹{plan.get('emergency_allocation', 0):,.0f}\n"
                f"Debt Allocation: ₹{plan.get('debt_allocation', 0):,.0f}\n"
                f"Goal Allocation: ₹{plan.get('goal_allocation', 0):,.0f}\n"
                f"Discretionary Budget: ₹{plan.get('discretionary_budget', 0):,.0f}\n\n"
                "10. AGENT STATUS\n"
                "────────────────────────────────────────\n"
                "Monitoring resumed. Decision stored in agent memory."
            )

            self.service.save_agent_decision(self.user_id, result)
            self.agent_output.setText(output)

        except Exception as e:
            self.agent_output.setText(f"Agent cycle failed:\n\n{str(e)}")
    # =============================================================
    # SIMULATION LAB
    # =============================================================

    def create_simulation_page(self):

        page = QWidget()

        outer_layout = QVBoxLayout(page)

        scroll = QScrollArea()

        scroll.setWidgetResizable(
            True
        )

        scroll.setFrameShape(
            QFrame.NoFrame
        )

        container = QWidget()

        layout = QVBoxLayout(
            container
        )

        layout.setContentsMargins(
            5, 5, 15, 25
        )

        layout.setSpacing(16)

        # ---------------------------------------------------------
        # INTRO
        # ---------------------------------------------------------

        intro = QLabel(
            "Test how the Intelligent Agent responds "
            "to changing financial conditions. "
            "Simulation changes are temporary and do "
            "not overwrite the saved SQLite financial profile."
        )

        intro.setWordWrap(True)

        intro.setStyleSheet("""
            color: #4B5563;
            font-size: 14px;
            padding: 5px 0 8px 0;
        """)

        layout.addWidget(
            intro
        )

        # ---------------------------------------------------------
        # SIMULATOR CARD
        # ---------------------------------------------------------

        scenario_card = QFrame()

        scenario_card.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #E5E7EB;
                border-radius: 12px;
            }

            QLabel {
                color: #374151;
                font-size: 14px;
            }

            QComboBox {
                background-color: #F9FAFB;
                border: 1px solid #D1D5DB;
                border-radius: 7px;
                padding: 10px;
                color: #111827;
                font-size: 14px;
                min-height: 22px;
            }
        """)

        scenario_layout = QVBoxLayout(
            scenario_card
        )

        scenario_layout.setContentsMargins(
            22, 20, 22, 20
        )

        scenario_layout.setSpacing(10)

        scenario_title = QLabel(
            "🧪 Financial Environment Simulator"
        )

        scenario_title.setStyleSheet("""
            color: #111827;
            font-size: 19px;
            font-weight: bold;
        """)

        scenario_layout.addWidget(
            scenario_title
        )

        scenario_description = QLabel(
            "Select a financial event. The agent will "
            "perceive the changed environment and "
            "independently determine how the simulated "
            "financial plan should respond."
        )

        scenario_description.setWordWrap(True)

        scenario_description.setStyleSheet("""
            color: #6B7280;
            font-size: 13px;
        """)

        scenario_layout.addWidget(
            scenario_description
        )

        scenario_layout.addWidget(
            QLabel("Select Scenario")
        )

        self.simulation_scenario = QComboBox()

        self.simulation_scenario.addItems(
            [
                "Stable Month",
                "Income Reduction",
                "Expense Increase",
                "Unexpected Expense",
                "Debt Increase"
            ]
        )

        scenario_layout.addWidget(
            self.simulation_scenario
        )

        simulate_button = QPushButton(
            "▶   Run Financial Simulation"
        )

        simulate_button.setMinimumHeight(
            48
        )

        simulate_button.setCursor(
            Qt.PointingHandCursor
        )

        simulate_button.setStyleSheet("""
            QPushButton {
                background-color: #111827;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 15px;
                font-weight: bold;
                padding: 10px 18px;
            }

            QPushButton:hover {
                background-color: #1F2937;
            }

            QPushButton:pressed {
                background-color: #374151;
            }
        """)

        simulate_button.clicked.connect(
            self.run_simulation
        )

        scenario_layout.addWidget(
            simulate_button
        )

        layout.addWidget(
            scenario_card
        )

        # ---------------------------------------------------------
        # SIMULATED ENVIRONMENT
        # ---------------------------------------------------------

        environment_card = QFrame()

        environment_card.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #E5E7EB;
                border-radius: 12px;
            }
        """)

        environment_layout = QVBoxLayout(
            environment_card
        )

        environment_layout.setContentsMargins(
            22, 18, 22, 18
        )

        environment_title = QLabel(
            "🌐 Simulated Environment"
        )

        environment_title.setStyleSheet("""
            color: #111827;
            font-size: 18px;
            font-weight: bold;
        """)

        environment_layout.addWidget(
            environment_title
        )

        self.simulation_environment = QLabel(
            "Select a scenario and run the simulation."
        )

        self.simulation_environment.setWordWrap(
            True
        )

        self.simulation_environment.setStyleSheet("""
            color: #4B5563;
            font-size: 14px;
            padding-top: 8px;
        """)

        environment_layout.addWidget(
            self.simulation_environment
        )

        layout.addWidget(
            environment_card
        )

        # ---------------------------------------------------------
        # AGENT RESPONSE
        # ---------------------------------------------------------

        response_card = QFrame()

        response_card.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #E5E7EB;
                border-radius: 12px;
            }
        """)

        response_layout = QVBoxLayout(
            response_card
        )

        response_layout.setContentsMargins(
            22, 18, 22, 18
        )

        response_title = QLabel(
            "🤖 Autonomous Agent Response"
        )

        response_title.setStyleSheet("""
            color: #111827;
            font-size: 18px;
            font-weight: bold;
        """)

        response_layout.addWidget(
            response_title
        )

        self.simulation_output = QTextEdit()

        self.simulation_output.setReadOnly(
            True
        )

        self.simulation_output.setMinimumHeight(
            400
        )

        self.simulation_output.setPlaceholderText(
            "The agent's perception, decision, "
            "reasoning, action and updated financial "
            "plan will appear here."
        )

        self.simulation_output.setStyleSheet("""
            QTextEdit {
                background-color: #F9FAFB;
                border: 1px solid #E5E7EB;
                border-radius: 8px;
                color: #111827;
                padding: 14px;
                font-size: 14px;
            }
        """)

        response_layout.addWidget(
            self.simulation_output
        )

        layout.addWidget(
            response_card
        )

        # ---------------------------------------------------------
        # RESET
        # ---------------------------------------------------------

        reset_button = QPushButton(
            "↺  Reset Simulation Environment"
        )

        reset_button.setMinimumHeight(
            42
        )

        reset_button.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #374151;
                border: 1px solid #D1D5DB;
                border-radius: 8px;
                font-size: 14px;
                padding: 8px 15px;
            }

            QPushButton:hover {
                background-color: #F9FAFB;
            }
        """)

        reset_button.clicked.connect(
            self.reset_simulation
        )

        layout.addWidget(
            reset_button
        )

        layout.addStretch()

        scroll.setWidget(
            container
        )

        outer_layout.addWidget(
            scroll
        )

        return page

    # =============================================================
    # RUN SIMULATION
    # =============================================================

    def run_simulation(self):

        try:

            scenario = (
                self.simulation_scenario.currentText()
            )

            # -----------------------------------------------------
            # ORIGINAL DATABASE VALUES
            # -----------------------------------------------------

            original_income = float(
                self.state.income
            )

            original_expenses = float(
                self.state.expenses
            )

            original_savings = float(
                self.state.savings
            )

            original_debt = float(
                self.state.debt
            )

            original_emergency = float(
                self.state.emergency_fund
            )

            # -----------------------------------------------------
            # START WITH ORIGINAL VALUES
            # -----------------------------------------------------

            simulated_income = original_income
            simulated_expenses = original_expenses
            simulated_savings = original_savings
            simulated_debt = original_debt
            simulated_emergency = original_emergency

            # -----------------------------------------------------
            # APPLY SCENARIO
            # -----------------------------------------------------

            if scenario == "Stable Month":

                scenario_reason = (
                    "No major financial change was introduced."
                )

            elif scenario == "Income Reduction":

                simulated_income = (
                    original_income * 0.70
                )

                scenario_reason = (
                    "Monthly income was temporarily "
                    "reduced by 30%."
                )

            elif scenario == "Expense Increase":

                simulated_expenses = (
                    original_expenses * 1.30
                )

                scenario_reason = (
                    "Monthly expenses were temporarily "
                    "increased by 30%."
                )

            elif scenario == "Unexpected Expense":

                unexpected_amount = max(
                    30000.0,
                    original_income * 0.30
                )

                simulated_expenses = (
                    original_expenses
                    + unexpected_amount
                )

                scenario_reason = (
                    f"An unexpected expense of "
                    f"₹{unexpected_amount:,.0f} was "
                    f"temporarily introduced."
                )

            elif scenario == "Debt Increase":

                # IMPORTANT:
                # This intentionally makes debt greater than
                # 50% of savings so the FinancialAgent can
                # detect its HIGH DEBT condition.

                simulated_debt = max(
                    original_debt + 50000.0,
                    original_savings * 0.60
                )

                scenario_reason = (
                    "Temporary debt was increased to "
                    "test the agent's debt-management "
                    "response."
                )

            # -----------------------------------------------------
            # CREATE TEMPORARY AGENT STATE
            # -----------------------------------------------------
            #
            # IMPORTANT:
            #
            # We create the temporary agent using the ORIGINAL
            # financial state first.
            #
            # Then we change the environment.
            #
            # This allows the agent to PERCEIVE the change.
            #
            # -----------------------------------------------------

            simulated_state = AgentState(
                income=original_income,
                expenses=original_expenses,
                savings=original_savings,
                debt=original_debt,
                emergency_fund=original_emergency
            )

            simulated_state.risk_preference = getattr(
                self.state,
                "risk_preference",
                "Moderate"
            )

            # Create a temporary agent.
            #
            # This agent is separate from the real running agent.

            simulated_agent = FinancialAgent(
                simulated_state,
                self.goal_manager
            )

            # -----------------------------------------------------
            # CHANGE TEMPORARY ENVIRONMENT
            # -----------------------------------------------------

            simulated_state.update_environment(
                income=simulated_income,
                expenses=simulated_expenses,
                savings=simulated_savings,
                debt=simulated_debt,
                emergency_fund=simulated_emergency
            )

            # -----------------------------------------------------
            # RUN TEMPORARY AGENT
            # -----------------------------------------------------
            #
            # IMPORTANT:
            #
            # We DO NOT call:
            #
            # self.service.save_agent_decision(...)
            #
            # Therefore simulation does not create a database
            # decision.
            #
            # -----------------------------------------------------

            result = simulated_agent.run_cycle()

            observation = result.get(
                "observation",
                {}
            )

            decision = result.get(
                "decision",
                {}
            )

            action = result.get(
                "action",
                {}
            )

            updated_plan = result.get(
                "updated_plan",
                {}
            )

            # -----------------------------------------------------
            # FORMAT OBSERVATION
            # -----------------------------------------------------

            observation_text = (
                f"Income: ₹{simulated_income:,.0f}\n"
                f"Expenses: ₹{simulated_expenses:,.0f}\n"
                f"Savings: ₹{simulated_savings:,.0f}\n"
                f"Debt: ₹{simulated_debt:,.0f}\n"
                f"Emergency Fund: ₹{simulated_emergency:,.0f}\n"
                f"Monthly Surplus: "
                f"₹{simulated_income - simulated_expenses:,.0f}"
            )

            # -----------------------------------------------------
            # FORMAT DECISION
            # -----------------------------------------------------

            if isinstance(
                decision,
                dict
            ):

                decision_text = decision.get(
                    "decision",
                    "No decision recorded."
                )

                reason_text = decision.get(
                    "reason",
                    "No reason recorded."
                )

            else:

                decision_text = str(
                    decision
                )

                reason_text = (
                    "No additional reasoning provided."
                )

            # -----------------------------------------------------
            # FORMAT ACTION
            # -----------------------------------------------------

            if isinstance(
                action,
                dict
            ):

                action_text = action.get(
                    "action",
                    str(action)
                )

            else:

                action_text = str(
                    action
                )

            # -----------------------------------------------------
            # FORMAT PLAN
            # -----------------------------------------------------

            if isinstance(
                updated_plan,
                dict
            ):

                emergency_allocation = float(
                    updated_plan.get(
                        "emergency_allocation",
                        0
                    )
                )

                debt_allocation = float(
                    updated_plan.get(
                        "debt_allocation",
                        0
                    )
                )

                goal_allocation = float(
                    updated_plan.get(
                        "goal_allocation",
                        0
                    )
                )

                discretionary_budget = float(
                    updated_plan.get(
                        "discretionary_budget",
                        0
                    )
                )

            else:

                emergency_allocation = 0.0
                debt_allocation = 0.0
                goal_allocation = 0.0
                discretionary_budget = 0.0

            # -----------------------------------------------------
            # SHOW SIMULATED ENVIRONMENT
            # -----------------------------------------------------

            self.simulation_environment.setText(
                f"<b>Scenario:</b> {scenario}<br><br>"

                f"<b>Event:</b> {scenario_reason}<br><br>"

                f"<b>Original Income:</b> "
                f"₹{original_income:,.0f}"
                f" &nbsp; → &nbsp; "
                f"<b>Simulated:</b> "
                f"₹{simulated_income:,.0f}<br>"

                f"<b>Original Expenses:</b> "
                f"₹{original_expenses:,.0f}"
                f" &nbsp; → &nbsp; "
                f"<b>Simulated:</b> "
                f"₹{simulated_expenses:,.0f}<br>"

                f"<b>Original Debt:</b> "
                f"₹{original_debt:,.0f}"
                f" &nbsp; → &nbsp; "
                f"<b>Simulated:</b> "
                f"₹{simulated_debt:,.0f}<br>"

                f"<b>Simulated Monthly Surplus:</b> "
                f"₹{simulated_income - simulated_expenses:,.0f}"
            )

            # -----------------------------------------------------
            # FINAL OUTPUT
            # -----------------------------------------------------

            output = (
                "🤖  AUTONOMOUS SIMULATION COMPLETED\n\n"

                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "1. ENVIRONMENT PERCEPTION\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"

                f"{observation_text}\n\n"

                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "2. AUTONOMOUS DECISION\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"

                f"{decision_text}\n\n"

                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "3. AGENT REASONING\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"

                f"{reason_text}\n\n"

                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "4. AUTONOMOUS ACTION\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"

                f"{action_text}\n\n"

                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "5. UPDATED FINANCIAL PLAN\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"

                f"Emergency Allocation: "
                f"₹{emergency_allocation:,.0f}\n"

                f"Debt Allocation: "
                f"₹{debt_allocation:,.0f}\n"

                f"Goal Allocation: "
                f"₹{goal_allocation:,.0f}\n"

                f"Discretionary Budget: "
                f"₹{discretionary_budget:,.0f}\n\n"

                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "6. AGENT STATUS\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"

                "Simulation completed successfully.\n"
                "The real saved financial profile was not modified."
            )

            self.simulation_output.setText(
                output
            )

        except Exception as e:

            self.simulation_output.setText(
                "Simulation failed:\n\n"
                f"{type(e).__name__}: {str(e)}"
            )

    # =============================================================
    # RESET SIMULATION
    # =============================================================

    def reset_simulation(self):

        self.simulation_scenario.setCurrentIndex(
            0
        )

        self.simulation_environment.setText(
            "Select a scenario and run the simulation."
        )

        self.simulation_output.clear()

    # =============================================================
    # AGENT PERFORMANCE EVALUATION PAGE
    # =============================================================

    def create_agent_evaluation_page(self):

        page = QWidget()
        page.setStyleSheet("background: transparent;")

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(5, 5, 15, 25)
        layout.setSpacing(16)

        intro = QLabel(
            "Run a controlled six-month experiment to evaluate how the autonomous "
            "Intelligent Agent adapts to changing financial conditions. "
            "The experiment uses a temporary environment and never modifies the saved SQLite profile."
        )
        intro.setWordWrap(True)
        intro.setStyleSheet("color: #4B5563; font-size: 14px; padding: 5px 0 8px 0;")
        layout.addWidget(intro)

        control_card = QFrame()
        control_card.setStyleSheet("""
            QFrame { background: white; border: 1px solid #E2E8F0; border-radius: 14px; }
        """)
        control_layout = QHBoxLayout(control_card)
        control_layout.setContentsMargins(20, 18, 20, 18)

        control_text = QVBoxLayout()
        title = QLabel("🧪 Multi-Month Autonomous Evaluation")
        title.setStyleSheet("color: #0F172A; font-size: 19px; font-weight: 700;")
        description = QLabel(
            "The environment changes across six controlled months. The agent perceives each change, "
            "consults memory, evaluates multiple factors, selects an action and stores the experience."
        )
        description.setWordWrap(True)
        description.setStyleSheet("color: #64748B; font-size: 13px;")
        control_text.addWidget(title)
        control_text.addWidget(description)
        control_layout.addLayout(control_text, 1)

        run_button = QPushButton("▶  Run 6-Month Evaluation")
        run_button.setMinimumHeight(48)
        run_button.setMinimumWidth(230)
        run_button.setCursor(Qt.PointingHandCursor)
        run_button.setStyleSheet("""
            QPushButton { background: #0F172A; color: white; border: none; border-radius: 8px; font-weight: 700; padding: 10px 16px; }
            QPushButton:hover { background: #1E293B; }
        """)
        run_button.clicked.connect(self.run_agent_evaluation)
        control_layout.addWidget(run_button)
        layout.addWidget(control_card)

        # KPI cards
        self.evaluation_kpi_grid = QGridLayout()
        self.evaluation_kpi_grid.setHorizontalSpacing(12)
        self.evaluation_kpi_grid.setVerticalSpacing(12)

        for col in range(4):
            self.evaluation_kpi_grid.setColumnStretch(col, 1)

        self.evaluation_kpis = {}
        for index, (key, title_text, default, accent) in enumerate([
            ("cycles", "CYCLES", "0", "#2563EB"),
            ("unique_decisions", "UNIQUE DECISIONS", "0", "#7C3AED"),
            ("adaptive_response_rate", "ADAPTIVE RESPONSE", "0%", "#059669"),
            ("average_priority_score", "AVG PRIORITY SCORE", "0/100", "#D97706"),
        ]):
            card = QFrame()
            card.setMinimumHeight(105)
            card.setStyleSheet("QFrame { background: white; border: 1px solid #E2E8F0; border-radius: 12px; }")
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(16, 14, 16, 14)
            label = QLabel(title_text)
            label.setStyleSheet("color: #64748B; font-size: 10px; font-weight: 700;")
            value = QLabel(default)
            value.setStyleSheet(f"color: {accent}; font-size: 24px; font-weight: 800;")
            card_layout.addWidget(label)
            card_layout.addWidget(value)
            self.evaluation_kpis[key] = value
            self.evaluation_kpi_grid.addWidget(card, 0, index)

        layout.addLayout(self.evaluation_kpi_grid)

        # Timeline
        timeline_card = QFrame()
        timeline_card.setStyleSheet("QFrame { background: white; border: 1px solid #E2E8F0; border-radius: 14px; }")
        timeline_layout = QVBoxLayout(timeline_card)
        timeline_layout.setContentsMargins(20, 18, 20, 18)

        timeline_title = QLabel("Six-Month Agent Response Timeline")
        timeline_title.setStyleSheet("color: #0F172A; font-size: 18px; font-weight: 700;")
        timeline_layout.addWidget(timeline_title)

        self.evaluation_table = QTextEdit()
        self.evaluation_table.setReadOnly(True)
        self.evaluation_table.setMinimumHeight(300)
        self.evaluation_table.setStyleSheet("""
            QTextEdit { background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; color: #0F172A; padding: 12px; font-size: 12px; }
        """)
        self.evaluation_table.setPlaceholderText("Run the evaluation to generate the six-month response timeline.")
        timeline_layout.addWidget(self.evaluation_table)
        layout.addWidget(timeline_card)

        # Findings / metrics
        findings_card = QFrame()
        findings_card.setStyleSheet("QFrame { background: white; border: 1px solid #E2E8F0; border-radius: 14px; }")
        findings_layout = QVBoxLayout(findings_card)
        findings_layout.setContentsMargins(20, 18, 20, 18)

        findings_title = QLabel("Evaluation Findings")
        findings_title.setStyleSheet("color: #0F172A; font-size: 18px; font-weight: 700;")
        findings_layout.addWidget(findings_title)

        self.evaluation_findings = QLabel(
            "No evaluation has been run yet."
        )
        self.evaluation_findings.setWordWrap(True)
        self.evaluation_findings.setStyleSheet("color: #475569; font-size: 13px; line-height: 1.5;")
        findings_layout.addWidget(self.evaluation_findings)
        layout.addWidget(findings_card)

        note = QLabel(
            "Evaluation note: these are controlled simulation results generated by the current agent implementation. "
            "They are not predictions of real financial outcomes and are not financial advice."
        )
        note.setWordWrap(True)
        note.setStyleSheet("color: #64748B; font-size: 11px;")
        layout.addWidget(note)

        layout.addStretch()
        scroll.setWidget(container)
        page_layout = QVBoxLayout(page)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.addWidget(scroll)
        return page

    def run_agent_evaluation(self):

        try:
            evaluation = MultiMonthEvaluation(
                self.state,
                self.goal_manager
            ).run()

            results = evaluation.get("results", [])
            metrics = evaluation.get("metrics", {})

            self.last_evaluation = evaluation

            self.evaluation_kpis["cycles"].setText(
                str(metrics.get("cycles", 0))
            )
            self.evaluation_kpis["unique_decisions"].setText(
                str(metrics.get("unique_decisions", 0))
            )
            self.evaluation_kpis["adaptive_response_rate"].setText(
                f"{metrics.get('adaptive_response_rate', 0):.1f}%"
            )
            self.evaluation_kpis["average_priority_score"].setText(
                f"{metrics.get('average_priority_score', 0):.1f}/100"
            )

            lines = []
            for row in results:
                lines.append(
                    f"MONTH {row['month']}  •  {row['label']}\n"
                    f"Environment: Income ₹{row['income']:,.0f} | Expenses ₹{row['expenses']:,.0f} | "
                    f"Surplus ₹{row['surplus']:,.0f} | Debt ₹{row['debt']:,.0f}\n"
                    f"Agent decision: {row['decision']}\n"
                    f"Action: {row['action']}\n"
                    f"Health state: {row['health_state']} ({row['health_severity']}) | "
                    f"Priority score: {row['priority_score']:.0f}/100 | "
                    f"Memory cycles: {row['memory_cycles']}\n"
                    f"Event: {row['reason']}\n"
                    + "─" * 92
                )

            self.evaluation_table.setText("\n".join(lines))

            health_states = metrics.get("health_states", {})
            action_counts = metrics.get("action_type_counts", {})
            health_text = ", ".join(
                f"{name}: {count}" for name, count in health_states.items()
            ) or "None"
            action_text = ", ".join(
                f"{name}: {count}" for name, count in action_counts.items()
            ) or "None"

            self.evaluation_findings.setText(
                f"<b>Completed cycles:</b> {metrics.get('cycles', 0)}<br>"
                f"<b>Adaptive cycles:</b> {metrics.get('adaptive_cycles', 0)} "
                f"({metrics.get('adaptive_response_rate', 0):.1f}% of the experiment)<br>"
                f"<b>Minimum monthly surplus:</b> ₹{metrics.get('minimum_monthly_surplus', 0):,.0f}<br>"
                f"<b>Final monthly surplus:</b> ₹{metrics.get('final_monthly_surplus', 0):,.0f}<br>"
                f"<b>Final memory cycles:</b> {metrics.get('memory_cycles_final', 0)}<br>"
                f"<b>Observed health states:</b> {health_text}<br>"
                f"<b>Autonomous response types:</b> {action_text}"
            )

            self.refresh_reports_page()

        except Exception as e:
            self.evaluation_findings.setStyleSheet("color: #DC2626; font-size: 13px;")
            self.evaluation_findings.setText(
                f"Evaluation failed: {type(e).__name__}: {str(e)}"
            )

    # =============================================================
    # REPORTS & ANALYTICS PAGE
    # =============================================================

    def create_reports_page(self):

        page = QWidget()
        page.setStyleSheet("background: transparent;")

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(5, 5, 15, 25)
        layout.setSpacing(16)

        intro = QFrame()
        intro.setStyleSheet("""
            QFrame { background: #0F172A; border-radius: 16px; }
        """)
        intro_layout = QVBoxLayout(intro)
        intro_layout.setContentsMargins(22, 18, 22, 18)

        title = QLabel("Agent Reports & Analytics")
        title.setStyleSheet("color: white; font-size: 21px; font-weight: 700;")
        subtitle = QLabel(
            "Analyze the measured behavior of the Intelligent Agent across the latest controlled evaluation. "
            "All values shown here come from actual experiment results generated by the application."
        )
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet("color: #CBD5E1; font-size: 13px;")
        intro_layout.addWidget(title)
        intro_layout.addWidget(subtitle)
        layout.addWidget(intro)

        # KPI cards
        self.report_kpis = {}
        kpi_grid = QGridLayout()
        kpi_grid.setHorizontalSpacing(12)
        kpi_grid.setVerticalSpacing(12)
        for col in range(4):
            kpi_grid.setColumnStretch(col, 1)

        for index, (key, label_text, default, accent) in enumerate([
            ("cycles", "EVALUATION CYCLES", "0", "#2563EB"),
            ("decisions", "UNIQUE DECISIONS", "0", "#7C3AED"),
            ("adaptive", "ADAPTIVE RESPONSE", "0%", "#059669"),
            ("score", "AVERAGE PRIORITY", "0/100", "#D97706"),
        ]):
            card = QFrame()
            card.setMinimumHeight(105)
            card.setStyleSheet("QFrame { background: white; border: 1px solid #E2E8F0; border-radius: 12px; }")
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(16, 14, 16, 14)
            label = QLabel(label_text)
            label.setStyleSheet("color: #64748B; font-size: 10px; font-weight: 700;")
            value = QLabel(default)
            value.setStyleSheet(f"color: {accent}; font-size: 24px; font-weight: 800;")
            card_layout.addWidget(label)
            card_layout.addWidget(value)
            self.report_kpis[key] = value
            kpi_grid.addWidget(card, 0, index)

        layout.addLayout(kpi_grid)

        # Two-column distribution area
        distribution = QHBoxLayout()
        distribution.setSpacing(14)

        decision_card = QFrame()
        decision_card.setStyleSheet("QFrame { background: white; border: 1px solid #E2E8F0; border-radius: 14px; }")
        decision_layout = QVBoxLayout(decision_card)
        decision_layout.setContentsMargins(20, 18, 20, 18)
        decision_title = QLabel("Decision Distribution")
        decision_title.setStyleSheet("color: #0F172A; font-size: 18px; font-weight: 700;")
        decision_layout.addWidget(decision_title)
        decision_note = QLabel("How often each autonomous decision was selected during the evaluation.")
        decision_note.setWordWrap(True)
        decision_note.setStyleSheet("color: #64748B; font-size: 12px;")
        decision_layout.addWidget(decision_note)
        self.report_decisions_layout = QVBoxLayout()
        self.report_decisions_layout.setSpacing(10)
        decision_layout.addLayout(self.report_decisions_layout)
        decision_layout.addStretch()
        distribution.addWidget(decision_card, 1)

        health_card = QFrame()
        health_card.setStyleSheet("QFrame { background: white; border: 1px solid #E2E8F0; border-radius: 14px; }")
        health_layout = QVBoxLayout(health_card)
        health_layout.setContentsMargins(20, 18, 20, 18)
        health_title = QLabel("Financial Health States")
        health_title.setStyleSheet("color: #0F172A; font-size: 18px; font-weight: 700;")
        health_layout.addWidget(health_title)
        health_note = QLabel("Distribution of internal financial states observed by the agent.")
        health_note.setWordWrap(True)
        health_note.setStyleSheet("color: #64748B; font-size: 12px;")
        health_layout.addWidget(health_note)
        self.report_health_layout = QVBoxLayout()
        self.report_health_layout.setSpacing(10)
        health_layout.addLayout(self.report_health_layout)
        health_layout.addStretch()
        distribution.addWidget(health_card, 1)

        layout.addLayout(distribution)

        # Monthly response report
        timeline_card = QFrame()
        timeline_card.setStyleSheet("QFrame { background: white; border: 1px solid #E2E8F0; border-radius: 14px; }")
        timeline_layout = QVBoxLayout(timeline_card)
        timeline_layout.setContentsMargins(20, 18, 20, 18)
        timeline_title = QLabel("Monthly Analytical Summary")
        timeline_title.setStyleSheet("color: #0F172A; font-size: 18px; font-weight: 700;")
        timeline_layout.addWidget(timeline_title)
        self.report_monthly_text = QTextEdit()
        self.report_monthly_text.setReadOnly(True)
        self.report_monthly_text.setMinimumHeight(250)
        self.report_monthly_text.setStyleSheet("""
            QTextEdit { background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; color: #0F172A; padding: 12px; font-size: 12px; }
        """)
        self.report_monthly_text.setPlaceholderText("Run the six-month evaluation to populate the analytics report.")
        timeline_layout.addWidget(self.report_monthly_text)
        layout.addWidget(timeline_card)

        # Action distribution + findings
        bottom = QHBoxLayout()
        bottom.setSpacing(14)

        action_card = QFrame()
        action_card.setStyleSheet("QFrame { background: white; border: 1px solid #E2E8F0; border-radius: 14px; }")
        action_layout = QVBoxLayout(action_card)
        action_layout.setContentsMargins(20, 18, 20, 18)
        action_title = QLabel("Autonomous Action Types")
        action_title.setStyleSheet("color: #0F172A; font-size: 18px; font-weight: 700;")
        action_layout.addWidget(action_title)
        self.report_actions_layout = QVBoxLayout()
        self.report_actions_layout.setSpacing(10)
        action_layout.addLayout(self.report_actions_layout)
        action_layout.addStretch()
        bottom.addWidget(action_card, 1)

        finding_card = QFrame()
        finding_card.setStyleSheet("QFrame { background: white; border: 1px solid #E2E8F0; border-radius: 14px; }")
        finding_layout = QVBoxLayout(finding_card)
        finding_layout.setContentsMargins(20, 18, 20, 18)
        finding_title = QLabel("Experiment Findings")
        finding_title.setStyleSheet("color: #0F172A; font-size: 18px; font-weight: 700;")
        finding_layout.addWidget(finding_title)
        self.report_findings = QLabel("No evaluation has been run yet.")
        self.report_findings.setWordWrap(True)
        self.report_findings.setStyleSheet("color: #475569; font-size: 13px; line-height: 1.5;")
        finding_layout.addWidget(self.report_findings)
        finding_layout.addStretch()
        bottom.addWidget(finding_card, 1)

        layout.addLayout(bottom)

        note = QLabel(
            "Report note: these analytics describe the behavior of the current simulated Intelligent Agent. "
            "They are not predictions of real financial outcomes and are not financial advice."
        )
        note.setWordWrap(True)
        note.setStyleSheet("color: #64748B; font-size: 11px;")
        layout.addWidget(note)

        layout.addStretch()
        scroll.setWidget(container)
        page_layout = QVBoxLayout(page)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.addWidget(scroll)
        return page

    def _clear_report_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            child_layout = item.layout()
            if widget is not None:
                widget.deleteLater()
            elif child_layout is not None:
                self._clear_report_layout(child_layout)

    def _add_report_distribution_row(self, layout, label_text, count, total, accent):
        row = QWidget()
        row_layout = QVBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(4)

        top = QHBoxLayout()
        name = QLabel(str(label_text))
        name.setStyleSheet("color: #334155; font-size: 12px; font-weight: 600;")
        top.addWidget(name)
        top.addStretch()
        percentage = (count / total * 100) if total else 0
        value = QLabel(f"{count}  •  {percentage:.1f}%")
        value.setStyleSheet("color: #64748B; font-size: 11px;")
        top.addWidget(value)
        row_layout.addLayout(top)

        bar = QProgressBar()
        bar.setRange(0, max(1, total))
        bar.setValue(int(count))
        bar.setTextVisible(False)
        bar.setFixedHeight(8)
        bar.setStyleSheet(f"""
            QProgressBar {{ background: #E2E8F0; border: none; border-radius: 4px; }}
            QProgressBar::chunk {{ background: {accent}; border-radius: 4px; }}
        """)
        row_layout.addWidget(bar)
        layout.addWidget(row)

    def refresh_reports_page(self):
        if not hasattr(self, "report_kpis"):
            return

        evaluation = self.last_evaluation
        if not evaluation:
            return

        metrics = evaluation.get("metrics", {}) or {}
        results = evaluation.get("results", []) or []
        cycles = int(metrics.get("cycles", len(results)) or 0)

        self.report_kpis["cycles"].setText(str(cycles))
        self.report_kpis["decisions"].setText(str(metrics.get("unique_decisions", 0)))
        self.report_kpis["adaptive"].setText(f"{metrics.get('adaptive_response_rate', 0):.1f}%")
        self.report_kpis["score"].setText(f"{metrics.get('average_priority_score', 0):.1f}/100")

        decision_counts = metrics.get("decision_counts", {}) or {}
        health_counts = metrics.get("health_states", {}) or {}
        action_counts = metrics.get("action_type_counts", {}) or {}

        self._clear_report_layout(self.report_decisions_layout)
        for name, count in decision_counts.items():
            self._add_report_distribution_row(
                self.report_decisions_layout, name, int(count), cycles, "#2563EB"
            )

        self._clear_report_layout(self.report_health_layout)
        for name, count in health_counts.items():
            self._add_report_distribution_row(
                self.report_health_layout, name, int(count), cycles, "#059669"
            )

        self._clear_report_layout(self.report_actions_layout)
        for name, count in action_counts.items():
            self._add_report_distribution_row(
                self.report_actions_layout, name, int(count), cycles, "#7C3AED"
            )

        monthly_lines = []
        for row in results:
            monthly_lines.append(
                f"MONTH {row.get('month')}  •  {row.get('label', '')}\n"
                f"Income ₹{row.get('income', 0):,.0f}  |  Expenses ₹{row.get('expenses', 0):,.0f}  |  "
                f"Surplus ₹{row.get('surplus', 0):,.0f}  |  Debt ₹{row.get('debt', 0):,.0f}\n"
                f"Decision: {row.get('decision', '')}\n"
                f"Action: {row.get('action', '')}\n"
                f"Health: {row.get('health_state', 'UNKNOWN')} ({row.get('health_severity', '')})  |  "
                f"Priority: {row.get('priority_score', 0):.0f}/100  |  Memory cycles: {row.get('memory_cycles', 0)}\n"
                + "─" * 88
            )
        self.report_monthly_text.setText("\n".join(monthly_lines))

        min_surplus = metrics.get("minimum_monthly_surplus", 0)
        final_surplus = metrics.get("final_monthly_surplus", 0)
        adaptive = metrics.get("adaptive_response_rate", 0)
        memory_final = metrics.get("memory_cycles_final", 0)
        self.report_findings.setText(
            f"<b>Experiment length:</b> {cycles} controlled cycles<br>"
            f"<b>Adaptive response:</b> {adaptive:.1f}% of cycles required a non-stable response<br>"
            f"<b>Minimum observed surplus:</b> ₹{min_surplus:,.0f}<br>"
            f"<b>Final observed surplus:</b> ₹{final_surplus:,.0f}<br>"
            f"<b>Final agent memory:</b> {memory_final} completed cycles<br>"
            f"<b>Distinct decisions:</b> {metrics.get('unique_decisions', 0)}"
        )

    # =============================================================
    # AGENT MEMORY / ACTIVITY LOG PAGE
    # =============================================================

    def create_activity_log_page(self):

        page = QWidget()
        page.setStyleSheet("background: transparent;")

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet(
            "QScrollArea { border: none; background: transparent; }"
        )

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(4, 4, 12, 24)
        layout.setSpacing(16)

        intro = QFrame()
        intro.setStyleSheet("""
            QFrame {
                background-color: #0F172A;
                border-radius: 16px;
            }
        """)
        intro_layout = QVBoxLayout(intro)
        intro_layout.setContentsMargins(22, 18, 22, 18)

        intro_title = QLabel("Agent Memory & Activity")
        intro_title.setStyleSheet(
            "color: white; font-size: 21px; font-weight: 700;"
        )
        intro_text = QLabel(
            "Persistent memory of the Intelligent Agent's previous "
            "observations, decisions, actions and simulated outcomes."
        )
        intro_text.setWordWrap(True)
        intro_text.setStyleSheet(
            "color: #CBD5E1; font-size: 13px; padding-top: 4px;"
        )
        intro_layout.addWidget(intro_title)
        intro_layout.addWidget(intro_text)
        layout.addWidget(intro)

        stats_frame = QFrame()
        stats_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #E2E8F0;
                border-radius: 14px;
            }
        """)
        stats_layout = QHBoxLayout(stats_frame)
        stats_layout.setContentsMargins(16, 14, 16, 14)
        stats_layout.setSpacing(12)

        self.memory_cycles_label = QLabel("0")
        self.memory_decisions_label = QLabel("0")
        self.memory_actions_label = QLabel("0")
        self.memory_last_label = QLabel("No activity yet")

        stat_items = [
            ("MEMORY CYCLES", self.memory_cycles_label),
            ("DECISIONS RECORDED", self.memory_decisions_label),
            ("ACTIONS RECORDED", self.memory_actions_label),
            ("LAST ACTIVITY", self.memory_last_label),
        ]

        for title, value_label in stat_items:
            card = QFrame()
            card.setStyleSheet("""
                QFrame {
                    background-color: #F8FAFC;
                    border: 1px solid #E2E8F0;
                    border-radius: 10px;
                }
            """)
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(12, 10, 12, 10)
            title_label = QLabel(title)
            title_label.setStyleSheet(
                "color: #64748B; font-size: 10px; font-weight: 700;"
            )
            value_label.setStyleSheet(
                "color: #0F172A; font-size: 17px; font-weight: 700;"
            )
            value_label.setWordWrap(True)
            card_layout.addWidget(title_label)
            card_layout.addWidget(value_label)
            stats_layout.addWidget(card, 1)

        layout.addWidget(stats_frame)

        history_frame = QFrame()
        history_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #E2E8F0;
                border-radius: 14px;
            }
        """)
        history_layout = QVBoxLayout(history_frame)
        history_layout.setContentsMargins(18, 16, 18, 16)
        history_layout.setSpacing(10)

        history_title = QLabel("Recent Agent Experiences")
        history_title.setStyleSheet(
            "color: #0F172A; font-size: 18px; font-weight: 700;"
        )
        history_layout.addWidget(history_title)

        self.activity_history_text = QTextEdit()
        self.activity_history_text.setReadOnly(True)
        self.activity_history_text.setMinimumHeight(420)
        self.activity_history_text.setStyleSheet("""
            QTextEdit {
                background-color: #F8FAFC;
                color: #0F172A;
                border: 1px solid #E2E8F0;
                border-radius: 10px;
                padding: 12px;
                font-size: 13px;
            }
        """)
        history_layout.addWidget(self.activity_history_text)

        refresh_button = QPushButton("Refresh Agent Memory")
        refresh_button.setCursor(Qt.PointingHandCursor)
        refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #0F172A;
                color: white;
                border: none;
                border-radius: 9px;
                padding: 11px 16px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #1E293B;
            }
        """)
        refresh_button.clicked.connect(self.refresh_agent_activity_page)
        history_layout.addWidget(refresh_button, alignment=Qt.AlignRight)

        layout.addWidget(history_frame)
        layout.addStretch()

        scroll.setWidget(container)
        outer_layout = QVBoxLayout(page)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(scroll)

        self.refresh_agent_activity_page()
        return page

    def refresh_agent_activity_page(self):
        """Refresh visible Agent Memory data from persistent agent memory."""
        if not hasattr(self, "activity_history_text"):
            return

        try:
            statistics = self.agent.get_memory_statistics()
            history = self.agent.get_memory_history(limit=10)

            self.memory_cycles_label.setText(
                str(statistics.get("cycles", 0))
            )

            self.memory_decisions_label.setText(
                str(sum(statistics.get("decision_counts", {}).values()))
            )

            self.memory_actions_label.setText(
                str(sum(statistics.get("action_counts", {}).values()))
            )

            last_timestamp = statistics.get("last_timestamp")
            self.memory_last_label.setText(
                last_timestamp.replace("T", " ") if last_timestamp
                else "No activity yet"
            )

            if not history:
                self.activity_history_text.setHtml(
                    "<p style='color:#64748B;'>"
                    "No completed agent cycles have been recorded yet. "
                    "Run an autonomous agent cycle to create memory."
                    "</p>"
                )
                return

            blocks = []
            for index, record in enumerate(history, start=1):
                observation = record.get("observation", {}) or {}
                decision = record.get("decision") or "Unknown decision"
                reason = record.get("reason") or "No reasoning recorded."
                action = record.get("action") or "Unknown action"
                outcome = record.get("outcome") or "No outcome recorded."
                timestamp = record.get("timestamp") or "Unknown time"

                income = observation.get("income", 0) or 0
                expenses = observation.get("expenses", 0) or 0
                debt = observation.get("debt", 0) or 0
                surplus = observation.get("monthly_surplus", 0) or 0

                blocks.append(
                    f"""
                    <div style='background:#FFFFFF; border:1px solid #E2E8F0;
                                border-radius:10px; padding:12px; margin-bottom:10px;'>
                        <div style='color:#64748B; font-size:11px;'>
                            CYCLE {index} &nbsp;•&nbsp; {timestamp}
                        </div>
                        <div style='color:#0F172A; font-size:16px;
                                    font-weight:700; margin-top:5px;'>
                            {decision}
                        </div>
                        <div style='color:#475569; margin-top:7px;'>
                            <b>Observed:</b> Income ₹{income:,.0f} &nbsp;|&nbsp;
                            Expenses ₹{expenses:,.0f} &nbsp;|&nbsp;
                            Debt ₹{debt:,.0f} &nbsp;|&nbsp;
                            Surplus ₹{surplus:,.0f}
                        </div>
                        <div style='color:#334155; margin-top:6px;'>
                            <b>Reason:</b> {reason}
                        </div>
                        <div style='color:#334155; margin-top:6px;'>
                            <b>Action:</b> {action}
                        </div>
                        <div style='color:#059669; margin-top:6px;'>
                            <b>Outcome:</b> {outcome}
                        </div>
                    </div>
                    """
                )

            self.activity_history_text.setHtml("".join(blocks))

        except Exception as error:
            self.activity_history_text.setPlainText(
                "Could not load agent memory.\n\n"
                f"{type(error).__name__}: {error}"
            )

    # =============================================================
    # PAGE NAVIGATION
    # =============================================================

    def show_page(
        self,
        page_name
    ):

        page_map = {

            "Dashboard": (
                self.dashboard_page,
                "Financial Dashboard"
            ),

            "Financial Profile": (
                self.financial_profile_page,
                "Financial Profile"
            ),

            "Goals": (
                self.goals_page,
                "Financial Goals"
            ),

            "Agent Center": (
                self.agent_center_page,
                "Agent Center"
            ),

            "Activity Log": (
                self.activity_log_page,
                "Agent Memory & Activity"
            ),

            "Simulation Lab": (
                self.simulation_page,
                "Simulation Lab"
            ),

            "Agent Evaluation": (
                self.agent_evaluation_page,
                "Agent Performance Evaluation"
            ),

            "Reports & Analytics": (
                self.reports_page,
                "Reports & Analytics"
            )
        }

        if page_name in page_map:

            page, title = page_map[
                page_name
            ]

            if page_name == "Activity Log":
                self.refresh_agent_activity_page()

            self.pages.setCurrentWidget(
                page
            )

            self.page_title.setText(
                title
            )

            # Keep the sidebar highlight synchronized with the visible page.
            for name, button in self.sidebar_buttons.items():

                if name == page_name:
                    button.setStyleSheet("""
                        QPushButton {
                            background-color: #1F2937;
                            color: white;
                            font-weight: 600;
                            border: 1px solid #334155;
                            border-radius: 9px;
                            padding: 12px 18px;
                            text-align: left;
                        }
                        QPushButton:hover {
                            background-color: #263449;
                            color: white;
                        }
                    """)

                else:
                    button.setStyleSheet("""
                        QPushButton {
                            background-color: transparent;
                            color: #D1D5DB;
                            font-weight: normal;
                            border: none;
                            border-radius: 9px;
                            padding: 12px 18px;
                            text-align: left;
                        }
                        QPushButton:hover {
                            background-color: #1F2937;
                            color: white;
                        }
                    """)

        else:

            print(
                f"Selected page: {page_name}"
            )


# =============================================================
# APPLICATION START
# =============================================================

if __name__ == "__main__":

    app = QApplication(
        sys.argv
    )

    window = DashboardWindow()

    window.show()

    sys.exit(
        app.exec()
    )