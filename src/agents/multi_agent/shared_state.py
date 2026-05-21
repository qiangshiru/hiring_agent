from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

from src.schemas.jd import JDParseResult
from src.schemas.resume import ResumeParseResult


class WorkflowStatus(str, Enum):
    INITIALIZED = "initialized"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class SharedState:
    def __init__(self):
        self.data: Dict[str, Any] = {}
        self.status = WorkflowStatus.INITIALIZED
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.agent_results: Dict[str, Any] = {}
        self.errors: List[str] = []

    def set_jd(self, jd: JDParseResult):
        self.data["jd"] = jd
        self._update()

    def set_resume(self, resume: ResumeParseResult):
        self.data["resume"] = resume
        self._update()

    def get_jd(self) -> Optional[JDParseResult]:
        return self.data.get("jd")

    def get_resume(self) -> Optional[ResumeParseResult]:
        return self.data.get("resume")

    def set_agent_result(self, agent_name: str, result: Any):
        self.agent_results[agent_name] = result
        self._update()

    def get_agent_result(self, agent_name: str) -> Optional[Any]:
        return self.agent_results.get(agent_name)

    def add_error(self, error: str):
        self.errors.append(error)
        self._update()

    def has_errors(self) -> bool:
        return len(self.errors) > 0

    def set_status(self, status: WorkflowStatus):
        self.status = status
        self._update()

    def _update(self):
        self.updated_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "agent_results": {k: str(v) for k, v in self.agent_results.items()},
            "has_errors": self.has_errors(),
            "error_count": len(self.errors),
        }
