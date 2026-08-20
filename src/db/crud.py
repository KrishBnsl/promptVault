"""Database CRUD operations for PromptVault."""

from sqlalchemy.orm import Session

from db.models import (
    Dataset,
    DatasetItem,
    Evaluation,
    EvaluationResult,
    Prompt,
    PromptVersion,
)

# --- Prompt Operations ---


def create_prompt(
    db: Session,
    name: str,
    content: str,
    description: str = "",
    variables: dict | None = None,
    model_config: dict | None = None,
    commit_message: str = "",
    tags: list[str] | None = None,
) -> tuple[Prompt, PromptVersion]:
    """Create a new prompt with its first version."""
    prompt = Prompt(
        name=name,
        description=description,
        tags=tags or [],
    )
    db.add(prompt)
    db.flush()

    version = PromptVersion(
        prompt_id=prompt.id,
        version_number=1,
        content=content,
        variables=variables or {},
        model_config=model_config or {},
        commit_message=commit_message,
        parent_version_id=None,
    )
    db.add(version)
    db.flush()

    prompt.current_version_id = version.id
    db.commit()
    db.refresh(prompt)
    db.refresh(version)
    return prompt, version


def get_prompt(db: Session, name: str) -> Prompt | None:
    """Get a prompt by name."""
    return db.query(Prompt).filter(Prompt.name == name).first()


def get_prompt_by_id(db: Session, prompt_id: str) -> Prompt | None:
    """Get a prompt by ID."""
    return db.query(Prompt).filter(Prompt.id == prompt_id).first()


def list_prompts(
    db: Session, tags: list[str] | None = None, limit: int = 50, offset: int = 0
) -> list[Prompt]:
    """List prompts with optional tag filtering."""
    query = db.query(Prompt)
    if tags:
        for tag in tags:
            query = query.filter(Prompt.tags.contains(tag))
    return query.order_by(Prompt.created_at.desc()).offset(offset).limit(limit).all()


def get_prompt_version(
    db: Session, prompt_id: str, version_number: int
) -> PromptVersion | None:
    """Get a specific version of a prompt."""
    return (
        db.query(PromptVersion)
        .filter(
            PromptVersion.prompt_id == prompt_id,
            PromptVersion.version_number == version_number,
        )
        .first()
    )


def get_latest_version(db: Session, prompt_id: str) -> PromptVersion | None:
    """Get the latest version of a prompt."""
    return (
        db.query(PromptVersion)
        .filter(PromptVersion.prompt_id == prompt_id)
        .order_by(PromptVersion.version_number.desc())
        .first()
    )


def list_prompt_versions(db: Session, prompt_id: str) -> list[PromptVersion]:
    """List all versions of a prompt."""
    return (
        db.query(PromptVersion)
        .filter(PromptVersion.prompt_id == prompt_id)
        .order_by(PromptVersion.version_number)
        .all()
    )


def create_prompt_version(
    db: Session,
    prompt_id: str,
    content: str,
    variables: dict | None = None,
    model_config: dict | None = None,
    commit_message: str = "",
    parent_version_id: str | None = None,
) -> PromptVersion:
    """Create a new version of an existing prompt."""
    latest = get_latest_version(db, prompt_id)
    version_number = (latest.version_number + 1) if latest else 1

    version = PromptVersion(
        prompt_id=prompt_id,
        version_number=version_number,
        content=content,
        variables=variables or (latest.variables if latest else {}),
        model_config=model_config or (latest.model_config if latest else {}),
        commit_message=commit_message,
        parent_version_id=parent_version_id or (latest.id if latest else None),
    )
    db.add(version)
    db.flush()

    prompt = get_prompt_by_id(db, prompt_id)
    if prompt:
        prompt.current_version_id = version.id

    db.commit()
    db.refresh(version)
    return version


def rollback_prompt(
    db: Session, prompt_id: str, target_version: int, commit_message: str = ""
) -> PromptVersion:
    """Rollback to a previous version by creating a new version with its content."""
    target = get_prompt_version(db, prompt_id, target_version)
    if not target:
        raise ValueError(f"Version {target_version} not found")

    latest = get_latest_version(db, prompt_id)
    new_version_number = (latest.version_number + 1) if latest else 1

    new_version = PromptVersion(
        prompt_id=prompt_id,
        version_number=new_version_number,
        content=target.content,
        variables=target.variables,
        model_config=target.model_config,
        commit_message=commit_message or f"Rollback to version {target_version}",
        parent_version_id=latest.id if latest else None,
    )
    db.add(new_version)
    db.flush()

    prompt = get_prompt_by_id(db, prompt_id)
    if prompt:
        prompt.current_version_id = new_version.id

    db.commit()
    db.refresh(new_version)
    return new_version


# --- Dataset Operations ---


def create_dataset(
    db: Session, name: str, description: str = "", items: list[dict] | None = None
) -> Dataset:
    """Create a new dataset with items."""
    dataset = Dataset(name=name, description=description)
    db.add(dataset)
    db.flush()

    if items:
        for item_data in items:
            item = DatasetItem(
                dataset_id=dataset.id,
                input=item_data.get("input", {}),
                expected_output=item_data.get("expected_output"),
                item_metadata=item_data.get("metadata", {}),
            )
            db.add(item)

    db.commit()
    db.refresh(dataset)
    return dataset


def get_dataset(db: Session, name: str) -> Dataset | None:
    """Get a dataset by name."""
    return db.query(Dataset).filter(Dataset.name == name).first()


def get_dataset_by_id(db: Session, dataset_id: str) -> Dataset | None:
    """Get a dataset by ID."""
    return db.query(Dataset).filter(Dataset.id == dataset_id).first()


def list_datasets(db: Session, limit: int = 50, offset: int = 0) -> list[Dataset]:
    """List all datasets."""
    return (
        db.query(Dataset)
        .order_by(Dataset.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


# --- Evaluation Operations ---


def create_evaluation(
    db: Session,
    prompt_version_id: str,
    dataset_id: str,
    model_config: dict | None = None,
) -> Evaluation:
    """Create a new evaluation record."""
    evaluation = Evaluation(
        prompt_version_id=prompt_version_id,
        dataset_id=dataset_id,
        model_config=model_config or {},
        status="pending",
    )
    db.add(evaluation)
    db.commit()
    db.refresh(evaluation)
    return evaluation


def get_evaluation(db: Session, evaluation_id: str) -> Evaluation | None:
    """Get an evaluation by ID."""
    return db.query(Evaluation).filter(Evaluation.id == evaluation_id).first()


def update_evaluation_status(
    db: Session, evaluation_id: str, status: str, metrics: dict | None = None
) -> Evaluation | None:
    """Update evaluation status and optionally metrics."""
    evaluation = get_evaluation(db, evaluation_id)
    if evaluation:
        evaluation.status = status
        if metrics:
            evaluation.metrics = metrics
        if status in ("completed", "failed"):
            from datetime import datetime

            evaluation.completed_at = datetime.utcnow()
        db.commit()
        db.refresh(evaluation)
    return evaluation


def create_evaluation_result(
    db: Session,
    evaluation_id: str,
    dataset_item_id: str,
    input_data: dict,
    expected_output: str | None = None,
    actual_output: str | None = None,
    latency_ms: int | None = None,
    token_usage: dict | None = None,
    cost: float | None = None,
    scores: dict | None = None,
    error: str | None = None,
) -> EvaluationResult:
    """Create a single evaluation result."""
    result = EvaluationResult(
        evaluation_id=evaluation_id,
        dataset_item_id=dataset_item_id,
        input=input_data,
        expected_output=expected_output,
        actual_output=actual_output,
        latency_ms=latency_ms,
        token_usage=token_usage or {},
        cost=cost,
        scores=scores or {},
        error=error,
    )
    db.add(result)
    db.commit()
    db.refresh(result)
    return result


def get_evaluation_results(
    db: Session, evaluation_id: str
) -> list[EvaluationResult]:
    """Get all results for an evaluation."""
    return (
        db.query(EvaluationResult)
        .filter(EvaluationResult.evaluation_id == evaluation_id)
        .all()
    )
