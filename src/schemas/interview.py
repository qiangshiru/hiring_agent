from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr

from src.models.interview import InterviewStatus


class InterviewBase(BaseModel):
    candidate_id: UUID
    job_id: UUID
    scheduled_at: datetime
    interviewer_email: EmailStr
    notes: str | None = None
    status: InterviewStatus = InterviewStatus.SCHEDULED


class InterviewCreate(InterviewBase):
    """Payload for creating an interview."""


class InterviewUpdate(BaseModel):
    scheduled_at: datetime | None = None
    interviewer_email: EmailStr | None = None
    notes: str | None = None
    status: InterviewStatus | None = None


class InterviewRead(InterviewBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime
