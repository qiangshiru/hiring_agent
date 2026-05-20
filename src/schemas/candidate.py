from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, HttpUrl

from src.models.candidate import CandidateStatus


class CandidateBase(BaseModel):
    full_name: str = Field(min_length=1, max_length=200)
    email: EmailStr
    phone: str | None = Field(default=None, max_length=50)
    resume_url: HttpUrl | None = None
    summary: str | None = None
    status: CandidateStatus = CandidateStatus.NEW


class CandidateCreate(CandidateBase):
    """Payload for creating a candidate."""


class CandidateUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=1, max_length=200)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=50)
    resume_url: HttpUrl | None = None
    summary: str | None = None
    status: CandidateStatus | None = None


class CandidateRead(CandidateBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime
