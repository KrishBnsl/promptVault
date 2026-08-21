"""SQLAlchemy ORM models for PromptVault."""

from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import (
    JSON,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.engine import Base


def generate_uuid() -> str:
    """Generate a new UUID string."""
    return str(uuid4())


def utcnow() -> datetime:
    """Return a naive UTC timestamp for SQLite compatibility."""
    return datetime.now(UTC).replace(tzinfo=None)


class Prompt(Base):
    """A prompt with metadata and version history."""

    __tablename__ = "prompts"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    tags: Mapped[list[str]] = mapped_column(JSON, default=[])
    current_version_id: Mapped[str | None] = mapped_column(
        String, ForeignKey("prompt_versions.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=utcnow, onupdate=utcnow
    )
    versions: Mapped[list["PromptVersion"]] = relationship(
        back_populates="prompt",
        order_by="PromptVersion.version_number",
        foreign_keys="[PromptVersion.prompt_id]",
    )


class PromptVersion(Base):
    """An immutable version of a prompt."""

    __tablename__ = "prompt_versions"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    prompt_id: Mapped[str] = mapped_column(String, ForeignKey("prompts.id"), index=True)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    variables: Mapped[dict] = mapped_column(JSON, default={})
    model_config: Mapped[dict] = mapped_column(JSON, default={})
    commit_message: Mapped[str] = mapped_column(Text, default="")
    parent_version_id: Mapped[str | None] = mapped_column(
        String, ForeignKey("prompt_versions.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    created_by: Mapped[str] = mapped_column(String, default="local")
    prompt: Mapped["Prompt"] = relationship(
        back_populates="versions",
        foreign_keys="[PromptVersion.prompt_id]",
    )


class Dataset(Base):
    """A dataset of input/output examples for evaluation."""

    __tablename__ = "datasets"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    items: Mapped[list["DatasetItem"]] = relationship(
        back_populates="dataset", cascade="all, delete-orphan"
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class DatasetItem(Base):
    """A single input/output pair in a dataset."""

    __tablename__ = "dataset_items"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    dataset_id: Mapped[str] = mapped_column(String, ForeignKey("datasets.id"), index=True)
    input: Mapped[dict] = mapped_column(JSON, nullable=False)
    expected_output: Mapped[str | None] = mapped_column(Text, nullable=True)
    item_metadata: Mapped[dict] = mapped_column("metadata", JSON, default={})
    dataset: Mapped["Dataset"] = relationship(back_populates="items")


class Evaluation(Base):
    """An evaluation run of a prompt version against a dataset."""

    __tablename__ = "evaluations"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    prompt_version_id: Mapped[str] = mapped_column(String, ForeignKey("prompt_versions.id"))
    dataset_id: Mapped[str] = mapped_column(String, ForeignKey("datasets.id"))
    model_config: Mapped[dict] = mapped_column(JSON, default={})
    status: Mapped[str] = mapped_column(String, default="pending")
    metrics: Mapped[dict] = mapped_column(JSON, default={})
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    results: Mapped[list["EvaluationResult"]] = relationship(
        back_populates="evaluation", cascade="all, delete-orphan"
    )


class EvaluationResult(Base):
    """A single result from an evaluation run."""

    __tablename__ = "evaluation_results"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    evaluation_id: Mapped[str] = mapped_column(String, ForeignKey("evaluations.id"), index=True)
    dataset_item_id: Mapped[str] = mapped_column(String, ForeignKey("dataset_items.id"))
    input: Mapped[dict] = mapped_column(JSON, nullable=False)
    expected_output: Mapped[str | None] = mapped_column(Text, nullable=True)
    actual_output: Mapped[str | None] = mapped_column(Text, nullable=True)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    token_usage: Mapped[dict] = mapped_column(JSON, default={})
    cost: Mapped[float | None] = mapped_column(Float, nullable=True)
    scores: Mapped[dict] = mapped_column(JSON, default={})
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    evaluation: Mapped["Evaluation"] = relationship(back_populates="results")
