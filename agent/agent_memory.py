"""
Persistent memory for the FINADVISOR AI Intelligent Agent.

The memory stores previous agent cycles so the agent can retain a history of
observations, decisions, actions and simulated financial plans across cycles
and application restarts.
"""

import json
from datetime import datetime
from pathlib import Path


class AgentMemory:
    """Persistent, lightweight memory for the Intelligent Agent."""

    def __init__(self, memory_key="default_user", storage_path=None, max_records=200):
        self.memory_key = str(memory_key)
        self.max_records = max_records

        if storage_path is None:
            project_root = Path(__file__).resolve().parents[1]
            storage_path = project_root / "data" / "agent_memory.json"

        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._memory = self._load()

    def _load(self):
        if not self.storage_path.exists():
            return {}

        try:
            with self.storage_path.open("r", encoding="utf-8") as file:
                data = json.load(file)

            if isinstance(data, dict):
                return data

        except (json.JSONDecodeError, OSError):
            # Corrupted/unreadable memory should not stop the financial agent.
            pass

        return {}

    def _save(self):
        temporary_path = self.storage_path.with_suffix(".tmp")

        with temporary_path.open("w", encoding="utf-8") as file:
            json.dump(self._memory, file, indent=2, ensure_ascii=False)

        temporary_path.replace(self.storage_path)

    def _records(self):
        records = self._memory.setdefault(self.memory_key, [])
        if not isinstance(records, list):
            records = []
            self._memory[self.memory_key] = records
        return records

    @staticmethod
    def _copy_state(observation):
        if not isinstance(observation, dict):
            return {}

        keys = [
            "income",
            "expenses",
            "savings",
            "debt",
            "emergency_fund",
            "monthly_surplus",
            "income_change",
            "expense_change",
            "savings_change",
            "debt_change",
        ]

        return {
            key: observation.get(key)
            for key in keys
            if key in observation
        }

    def record_cycle(self, observation, decision, action, plan, outcome=None):
        """Store one complete autonomous agent cycle."""
        decision = decision if isinstance(decision, dict) else {}

        record = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "observation": self._copy_state(observation),
            "decision": decision.get("decision"),
            "reason": decision.get("reason"),
            "action": action,
            "action_type": decision.get("action_type"),
            "priority_goal": decision.get("priority_goal"),
            "financial_plan": dict(plan) if isinstance(plan, dict) else {},
            "outcome": outcome or "Financial plan adjusted by the agent.",
        }

        records = self._records()
        records.append(record)
        self._memory[self.memory_key] = records[-self.max_records:]
        self._save()

        return record

    def get_history(self, limit=None):
        """Return newest memory records first."""
        records = list(self._records())
        records.reverse()

        if limit is not None:
            records = records[:max(0, int(limit))]

        return records

    def get_recent(self, limit=5):
        return self.get_history(limit)

    def count(self):
        return len(self._records())

    def get_last_record(self):
        records = self._records()
        return records[-1] if records else None

    def get_statistics(self):
        records = self._records()

        decision_counts = {}
        action_counts = {}

        for record in records:
            decision = record.get("decision") or "Unknown"
            action = record.get("action") or "Unknown"
            decision_counts[decision] = decision_counts.get(decision, 0) + 1
            action_counts[action] = action_counts.get(action, 0) + 1

        return {
            "cycles": len(records),
            "decision_counts": decision_counts,
            "action_counts": action_counts,
            "last_timestamp": records[-1].get("timestamp") if records else None,
        }

    def clear(self):
        """Clear only this user's agent memory."""
        self._memory[self.memory_key] = []
        self._save()
