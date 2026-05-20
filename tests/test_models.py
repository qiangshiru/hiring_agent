from src.models.candidate import Candidate, CandidateStatus
from src.models.interview import Interview
from src.models.job import Job, JobStatus


def test_candidate_model_constraints_are_declared() -> None:
    constraint_names = {constraint.name for constraint in Candidate.__table__.constraints}
    index_names = {index.name for index in Candidate.__table__.indexes}

    assert "uq_candidates_email" in constraint_names
    assert "ix_candidates_status_created_at" in index_names
    assert CandidateStatus.NEW.value == "new"


def test_job_model_constraints_are_declared() -> None:
    constraint_names = {constraint.name for constraint in Job.__table__.constraints}
    index_names = {index.name for index in Job.__table__.indexes}

    assert "uq_jobs_title_department" in constraint_names
    assert "ix_jobs_status_created_at" in index_names
    assert JobStatus.OPEN.value == "open"


def test_interview_model_constraints_are_declared() -> None:
    constraint_names = {constraint.name for constraint in Interview.__table__.constraints}
    index_names = {index.name for index in Interview.__table__.indexes}

    assert "uq_interview_slot" in constraint_names
    assert "ix_interviews_status_scheduled_at" in index_names
