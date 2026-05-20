from datetime import UTC, datetime
from enum import StrEnum
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum, ForeignKey, Index, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base

if TYPE_CHECKING:
    from src.models.candidate import Candidate
    from src.models.job import Job


class InterviewStatus(StrEnum):
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class Interview(Base):
    __tablename__ = "interviews"
    __table_args__ = (
        UniqueConstraint("candidate_id", "job_id", "scheduled_at", name="uq_interview_slot"),
        Index("ix_interviews_status_scheduled_at", "status", "scheduled_at"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    candidate_id: Mapped[UUID] = mapped_column(
        ForeignKey("candidates.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    job_id: Mapped[UUID] = mapped_column(
        ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    interviewer_email: Mapped[str] = mapped_column(String(320), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[InterviewStatus] = mapped_column(
        Enum(
            InterviewStatus,
            name="interview_status",
            values_callable=lambda enum: [member.value for member in enum],
        ),
        nullable=False,
        default=InterviewStatus.SCHEDULED,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    candidate: Mapped["Candidate"] = relationship(back_populates="interviews")
    job: Mapped["Job"] = relationship(back_populates="interviews")
