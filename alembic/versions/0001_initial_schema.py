"""initial schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-05-20 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001_initial_schema"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    candidate_status = sa.Enum(
        "new",
        "screening",
        "interviewing",
        "offered",
        "hired",
        "rejected",
        name="candidate_status",
    )
    job_status = sa.Enum("draft", "open", "paused", "closed", name="job_status")
    interview_status = sa.Enum(
        "scheduled",
        "completed",
        "cancelled",
        "no_show",
        name="interview_status",
    )
    candidate_status.create(op.get_bind(), checkfirst=True)
    job_status.create(op.get_bind(), checkfirst=True)
    interview_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "candidates",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("full_name", sa.String(length=200), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("phone", sa.String(length=50), nullable=True),
        sa.Column("resume_url", sa.String(length=2048), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("status", candidate_status, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_candidates")),
        sa.UniqueConstraint("email", name="uq_candidates_email"),
    )
    op.create_index("ix_candidates_status_created_at", "candidates", ["status", "created_at"])

    op.create_table(
        "jobs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("department", sa.String(length=120), nullable=False),
        sa.Column("location", sa.String(length=200), nullable=True),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("requirements", sa.Text(), nullable=False),
        sa.Column("status", job_status, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_jobs")),
        sa.UniqueConstraint("title", "department", name="uq_jobs_title_department"),
    )
    op.create_index("ix_jobs_status_created_at", "jobs", ["status", "created_at"])

    op.create_table(
        "interviews",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("candidate_id", sa.Uuid(), nullable=False),
        sa.Column("job_id", sa.Uuid(), nullable=False),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("interviewer_email", sa.String(length=320), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("status", interview_status, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["candidate_id"],
            ["candidates.id"],
            name=op.f("fk_interviews_candidate_id_candidates"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["job_id"],
            ["jobs.id"],
            name=op.f("fk_interviews_job_id_jobs"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_interviews")),
        sa.UniqueConstraint("candidate_id", "job_id", "scheduled_at", name="uq_interview_slot"),
    )
    op.create_index(op.f("ix_interviews_candidate_id"), "interviews", ["candidate_id"])
    op.create_index(op.f("ix_interviews_job_id"), "interviews", ["job_id"])
    op.create_index("ix_interviews_status_scheduled_at", "interviews", ["status", "scheduled_at"])


def downgrade() -> None:
    op.drop_index("ix_interviews_status_scheduled_at", table_name="interviews")
    op.drop_index(op.f("ix_interviews_job_id"), table_name="interviews")
    op.drop_index(op.f("ix_interviews_candidate_id"), table_name="interviews")
    op.drop_table("interviews")
    op.drop_index("ix_jobs_status_created_at", table_name="jobs")
    op.drop_table("jobs")
    op.drop_index("ix_candidates_status_created_at", table_name="candidates")
    op.drop_table("candidates")

    sa.Enum(name="interview_status").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="job_status").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="candidate_status").drop(op.get_bind(), checkfirst=True)
