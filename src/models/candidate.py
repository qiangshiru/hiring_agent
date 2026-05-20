from datetime import UTC, datetime
from enum import StrEnum
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum, Index, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base

if TYPE_CHECKING:
    from src.models.interview import Interview


class CandidateStatus(StrEnum):
    NEW = "new"
    SCREENING = "screening"
    INTERVIEWING = "interviewing"
    OFFERED = "offered"
    HIRED = "hired"
    REJECTED = "rejected"


class Candidate(Base):
    __tablename__ = "candidates"
    __table_args__ = (
        UniqueConstraint("email", name="uq_candidates_email"),
        Index("ix_candidates_status_created_at", "status", "created_at"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str] = mapped_column(String(320), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    resume_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[CandidateStatus] = mapped_column(
        Enum(
            CandidateStatus,
            name="candidate_status",
            values_callable=lambda enum: [member.value for member in enum],
        ),
        nullable=False,
        default=CandidateStatus.NEW,
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

    interviews: Mapped[list["Interview"]] = relationship(
        back_populates="candidate",
        cascade="all, delete-orphan",
    )
