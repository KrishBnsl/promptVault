"""Prompt versioning logic."""

from sqlalchemy.orm import Session

from db import crud
from db.models import Prompt, PromptVersion


class VersioningEngine:
    """Handles prompt versioning operations."""

    def __init__(self, db: Session):
        self.db = db

    def create_prompt(
        self,
        name: str,
        content: str,
        description: str = "",
        variables: dict | None = None,
        model_config: dict | None = None,
        commit_message: str = "",
        tags: list[str] | None = None,
    ) -> tuple[Prompt, PromptVersion]:
        """Create a new prompt with initial version."""
        existing = crud.get_prompt(self.db, name)
        if existing:
            raise ValueError(f"Prompt '{name}' already exists")
        return crud.create_prompt(
            self.db,
            name=name,
            content=content,
            description=description,
            variables=variables,
            model_config=model_config,
            commit_message=commit_message,
            tags=tags,
        )

    def get_prompt(self, name: str) -> Prompt | None:
        """Get a prompt by name."""
        return crud.get_prompt(self.db, name)

    def get_version(
        self, name: str, version_number: int | None = None
    ) -> PromptVersion | None:
        """Get a specific version or the latest version of a prompt."""
        prompt = crud.get_prompt(self.db, name)
        if not prompt:
            return None
        if version_number is not None:
            return crud.get_prompt_version(self.db, prompt.id, version_number)
        return crud.get_latest_version(self.db, prompt.id)

    def list_versions(self, name: str) -> list[PromptVersion]:
        """List all versions of a prompt."""
        prompt = crud.get_prompt(self.db, name)
        if not prompt:
            return []
        return crud.list_prompt_versions(self.db, prompt.id)

    def list_prompts(
        self, tags: list[str] | None = None, limit: int = 50, offset: int = 0
    ) -> list[Prompt]:
        """List all prompts."""
        return crud.list_prompts(self.db, tags=tags, limit=limit, offset=offset)

    def rollback(
        self,
        name: str,
        target_version: int,
        commit_message: str = "",
    ) -> PromptVersion:
        """Rollback to a previous version."""
        prompt = crud.get_prompt(self.db, name)
        if not prompt:
            raise ValueError(f"Prompt '{name}' not found")
        return crud.rollback_prompt(
            self.db,
            prompt_id=prompt.id,
            target_version=target_version,
            commit_message=commit_message,
        )
