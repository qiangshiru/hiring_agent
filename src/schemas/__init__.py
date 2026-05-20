__all__ = [
    "CandidateCreate",
    "CandidateRead",
    "CandidateUpdate",
    "InterviewCreate",
    "InterviewRead",
    "InterviewUpdate",
    "JDParseRequest",
    "JDParseResponse",
    "JDParseResult",
    "JobCreate",
    "JobRead",
    "JobUpdate",
]


def __getattr__(name: str):
    if name in __all__:
        if name.startswith("Candidate"):
            from src.schemas.candidate import (
                CandidateCreate,
                CandidateRead,
                CandidateUpdate,
            )
            return locals()[name]
        elif name.startswith("Interview"):
            from src.schemas.interview import (
                InterviewCreate,
                InterviewRead,
                InterviewUpdate,
            )
            return locals()[name]
        elif name.startswith("JD"):
            from src.schemas.jd import JDParseRequest, JDParseResponse, JDParseResult
            return locals()[name]
        elif name.startswith("Job"):
            from src.schemas.job import JobCreate, JobRead, JobUpdate
            return locals()[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
