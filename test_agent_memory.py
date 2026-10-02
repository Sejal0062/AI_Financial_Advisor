from agent.agent_state import AgentState
from agent.financial_agent import FinancialAgent
from agent.goals import GoalManager
from agent.agent_memory import AgentMemory


memory = AgentMemory(memory_key="test_memory", storage_path="data/test_agent_memory.json")
# Start the test cleanly.
memory.clear()

state = AgentState(
    income=100000,
    expenses=55000,
    savings=350000,
    debt=80000,
    emergency_fund=250000
)

goals = GoalManager()
agent = FinancialAgent(
    state,
    goals,
    memory=memory
)

result = agent.run_cycle()

print("AGENT MEMORY TEST SUCCESSFUL")
print("Decision:", result["decision"]["decision"])
print("Memory cycles:", result["memory_count"])
print("Stored decision:", result["memory"]["decision"])
print("Stored action:", result["memory"]["action"])
print("Statistics:", agent.get_memory_statistics())
