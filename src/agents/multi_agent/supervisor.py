import time
from typing import Dict, Any, List
from datetime import datetime, timedelta

from src.agents.multi_agent.shared_state import SharedState, WorkflowStatus
from src.agents.multi_agent.message_bus import MessageBus, Message


class Supervisor:
    def __init__(self, message_bus: MessageBus, shared_state: SharedState):
        self.message_bus = message_bus
        self.shared_state = shared_state
        self.agent_status: Dict[str, str] = {}
        self.agent_start_times: Dict[str, float] = {}
        self.timeout_seconds = 60
        self.message_bus.subscribe("agent.completed", self._handle_agent_completed)
        self.message_bus.subscribe("agent.error", self._handle_agent_error)

    def _handle_agent_completed(self, message: Message):
        agent_name = message.payload.get("agent")
        if agent_name:
            self.agent_status[agent_name] = "completed"
            elapsed = time.time() - self.agent_start_times.get(agent_name, time.time())
            print(f"Agent {agent_name} completed in {elapsed:.2f}s")

    def _handle_agent_error(self, message: Message):
        agent_name = message.payload.get("agent")
        error = message.payload.get("error")
        if agent_name:
            self.agent_status[agent_name] = "error"
            self.shared_state.add_error(f"{agent_name}: {error}")

    def start_monitoring(self, agents: List[str]):
        for agent in agents:
            self.agent_status[agent] = "running"
            self.agent_start_times[agent] = time.time()

    def check_timeout(self, agent_name: str) -> bool:
        start_time = self.agent_start_times.get(agent_name)
        if start_time:
            elapsed = time.time() - start_time
            return elapsed > self.timeout_seconds
        return False

    def get_status(self) -> Dict[str, Any]:
        return {
            "agent_status": self.agent_status,
            "workflow_status": self.shared_state.status.value,
            "errors": self.shared_state.errors,
        }

    def wait_for_completion(self, agents: List[str], timeout: int = 120) -> bool:
        start_time = time.time()
        while time.time() - start_time < timeout:
            completed_count = sum(
                1 for status in self.agent_status.values() if status == "completed"
            )
            if completed_count == len(agents):
                return True

            for agent in agents:
                if self.check_timeout(agent):
                    self.agent_status[agent] = "timeout"
                    self.shared_state.add_error(f"{agent} timeout")

            time.sleep(0.5)

        return False

    def resolve_conflicts(self) -> str:
        agent_results = self.shared_state.agent_results
        recommendations = []

        for agent_name, result in agent_results.items():
            if isinstance(result, dict) and "recommendation" in result:
                recommendations.append(result["recommendation"])

        if not recommendations:
            return "待定"

        if all(r == "强烈推荐" for r in recommendations):
            return "强烈推荐"
        elif all(r in ["强烈推荐", "推荐"] for r in recommendations):
            return "推荐"
        elif any(r == "不推荐" for r in recommendations):
            return "不推荐"
        else:
            return "待定"

    def aggregate_results(self) -> Dict[str, Any]:
        results = {}
        agent_results = self.shared_state.agent_results

        for agent_name, result in agent_results.items():
            if isinstance(result, dict):
                results[agent_name] = {
                    "overall_score": result.get("overall_score", 0.0),
                    "recommendation": result.get("recommendation", "待定"),
                }

        return results
