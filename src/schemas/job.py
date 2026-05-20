from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.models.job import JobStatus


class JobBase(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    department: str = Field(min_length=1, max_length=120)
    location: str | None = Field(default=None, max_length=200)
    description: str = Field(min_length=1)
    requirements: str = Field(min_length=1)
    status: JobStatus = JobStatus.DRAFT


class JobCreate(JobBase):
    """Payload for creating a job."""


class JobUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    department: str | None = Field(default=None, min_length=1, max_length=120)
    location: str | None = Field(default=None, max_length=200)
    description: str | None = Field(default=None, min_length=1)
    requirements: str | None = Field(default=None, min_length=1)
    status: JobStatus | None = None


class JobRead(JobBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime
