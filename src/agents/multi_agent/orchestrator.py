from typing import Dict, Any
import time

from src.schemas.jd import JDParseResult
from src.schemas.resume import ResumeParseResult
from src.agents.multi_agent.message_bus import MessageBus, Message
from src.agents.multi_agent.shared_state import SharedState, WorkflowStatus
from src.agents.multi_agent.supervisor import Supervisor
from src.agents.multi_agent.agents import (
    HRAgent,
    TechAgent,
    ArchitectAgent,
    RiskAgent,
)


class MultiAgentOrchestrator:
    def __init__(self):
        self.message_bus = MessageBus()
        self.shared_state = SharedState()
        self.supervisor = Supervisor(self.message_bus, self.shared_state)

        self.agents = {
            "hr_agent": HRAgent(self.message_bus, self.shared_state),
            "tech_agent": TechAgent(self.message_bus, self.shared_state),
            "architect_agent": ArchitectAgent(self.message_bus, self.shared_state),
            "risk_agent": RiskAgent(self.message_bus, self.shared_state),
        }

    def run_full_interview(
        self, jd: JDParseResult, resume: ResumeParseResult
    ) -> Dict[str, Any]:
        self._initialize(jd, resume)
        self._execute_agents()
        return self._aggregate_results()

    def _initialize(self, jd: JDParseResult, resume: ResumeParseResult):
        self.shared_state.set_jd(jd)
        self.shared_state.set_resume(resume)
        self.shared_state.set_status(WorkflowStatus.RUNNING)

    def _execute_agents(self):
        agent_names = list(self.agents.keys())
        self.supervisor.start_monitoring(agent_names)

        for agent_name in agent_names:
            self.message_bus.publish(
                Message(
                    sender="orchestrator",
                    recipient=agent_name,
                    topic=f"{agent_name.split('_')[0]}.evaluate",
                    payload={},
                )
            )

        self.supervisor.wait_for_completion(agent_names)

        self.shared_state.set_status(WorkflowStatus.COMPLETED)

    def _aggregate_results(self) -> Dict[str, Any]:
        final_recommendation = self.supervisor.resolve_conflicts()
        aggregated = self.supervisor.aggregate_results()

        return {
            "hr_agent_output": self.shared_state.get_agent_result("hr_agent"),
            "tech_agent_output": self.shared_state.get_agent_result("tech_agent"),
            "architect_agent_output": self.shared_state.get_agent_result("architect_agent"),
            "risk_agent_output": self.shared_state.get_agent_result("risk_agent"),
            "final_recommendation": final_recommendation,
            "agent_recommendations": {
                name: result.get("recommendation", "待定")
                for name, result in aggregated.items()
            },
            "errors": self.shared_state.errors,
            "status": self.shared_state.status.value,
        }

    def get_status(self) -> Dict[str, Any]:
        return self.supervisor.get_status()

    def run_step(self, step_name: str) -> Dict[str, Any]:
        steps = {
            "hr": lambda: self._run_agent("hr_agent"),
            "tech": lambda: self._run_agent("tech_agent"),
            "architect": lambda: self._run_agent("architect_agent"),
            "risk": lambda: self._run_agent("risk_agent"),
        }

        if step_name in steps:
            return steps[step_name]()
        return {"error": f"Unknown step: {step_name}"}

    def _run_agent(self, agent_name: str) -> Dict[str, Any]:
        self.supervisor.agent_status[agent_name] = "running"
        self.supervisor.agent_start_times[agent_name] = time.time()

        topic = f"{agent_name.split('_')[0]}.evaluate"
        self.message_bus.publish(
            Message(
                sender="orchestrator",
                recipient=agent_name,
                topic=topic,
                payload={},
            )
        )

        time.sleep(0.5)
        result = self.shared_state.get_agent_result(agent_name)
        return result if result else {"status": "pending"}
