"""Pydantic request/response models for REST API."""

from pydantic import BaseModel, ConfigDict, Field


class PromptCreate(BaseModel):
    """Request model for creating a prompt."""

    model_config = ConfigDict(populate_by_name=True)

    name: str = Field(min_length=1)
    content: str = Field(min_length=1)
    description: str = ""
    variables: dict | None = None
    llm_config: dict | None = Field(None, alias="model_config")
    commit_message: str = ""
    tags: list[str] | None = None


class PromptVersionCreate(BaseModel):
    """Request model for creating a new immutable prompt version."""

    model_config = ConfigDict(populate_by_name=True)

    content: str = Field(min_length=1)
    variables: dict | None = None
    llm_config: dict | None = Field(None, alias="model_config")
    commit_message: str = ""


class PromptResponse(BaseModel):
    """Response model for a prompt."""

    id: str
    name: str
    description: str
    tags: list[str]
    current_version_id: str | None
    created_at: str | None
    updated_at: str | None


class PromptVersionResponse(BaseModel):
    """Response model for a prompt version."""

    id: str
    prompt_id: str
    version_number: int
    content: str
    variables: dict
    llm_config: dict = Field(alias="model_config")
    commit_message: str
    created_at: str | None


class RollbackRequest(BaseModel):
    """Request model for rolling back a prompt."""

    version: int
    commit_message: str = ""


class DatasetItemCreate(BaseModel):
    """Validated dataset item."""

    input: dict
    expected_output: str | None = None
    metadata: dict = Field(default_factory=dict)


class DatasetCreate(BaseModel):
    """Request model for creating a dataset."""

    name: str = Field(min_length=1)
    description: str = ""
    items: list[DatasetItemCreate]


class DatasetResponse(BaseModel):
    """Response model for a dataset."""

    id: str
    name: str
    description: str
    items_count: int
    created_at: str | None


class EvaluationRunRequest(BaseModel):
    """Request model for running an evaluation."""

    model_config = ConfigDict(populate_by_name=True)

    prompt_name: str
    version: int | None = None
    dataset_name: str
    llm_config: dict | None = Field(None, alias="model_config")


class EvaluationResponse(BaseModel):
    """Response model for an evaluation."""

    id: str
    status: str
    llm_config: dict = Field(alias="model_config")
    metrics: dict
    created_at: str | None
    completed_at: str | None
