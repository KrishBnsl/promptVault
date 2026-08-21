"""Tests for prompt versioning logic."""

import pytest

from core.versioning import VersioningEngine


class TestVersioningEngine:
    """Tests for VersioningEngine."""

    def test_create_prompt(self, db_session):
        """Test creating a new prompt."""
        engine = VersioningEngine(db_session)
        prompt, version = engine.create_prompt(
            name="test-prompt",
            content="Hello {name}",
            description="A test prompt",
            variables={"name": "string"},
            commit_message="Initial version",
            tags=["test"],
        )

        assert prompt.name == "test-prompt"
        assert prompt.description == "A test prompt"
        assert prompt.tags == ["test"]
        assert version.version_number == 1
        assert version.content == "Hello {name}"
        assert version.variables == {"name": "string"}
        assert version.commit_message == "Initial version"

    def test_create_duplicate_prompt(self, db_session):
        """Test that creating a duplicate prompt raises error."""
        engine = VersioningEngine(db_session)
        engine.create_prompt(name="test-prompt", content="Hello")

        with pytest.raises(ValueError, match="already exists"):
            engine.create_prompt(name="test-prompt", content="World")

    def test_get_prompt(self, db_session):
        """Test getting a prompt by name."""
        engine = VersioningEngine(db_session)
        engine.create_prompt(name="test-prompt", content="Hello")

        prompt = engine.get_prompt("test-prompt")
        assert prompt is not None
        assert prompt.name == "test-prompt"

    def test_get_nonexistent_prompt(self, db_session):
        """Test getting a nonexistent prompt."""
        engine = VersioningEngine(db_session)
        assert engine.get_prompt("nonexistent") is None

    def test_get_version(self, db_session):
        """Test getting a specific version."""
        engine = VersioningEngine(db_session)
        engine.create_prompt(name="test-prompt", content="Hello v1")

        version = engine.get_version("test-prompt", 1)
        assert version is not None
        assert version.version_number == 1
        assert version.content == "Hello v1"

    def test_get_latest_version(self, db_session):
        """Test getting the latest version."""
        engine = VersioningEngine(db_session)
        engine.create_prompt(name="test-prompt", content="Hello v1")

        from db import crud

        prompt = crud.get_prompt(db_session, "test-prompt")
        crud.create_prompt_version(db_session, prompt.id, "Hello v2")

        version = engine.get_version("test-prompt")
        assert version is not None
        assert version.version_number == 2
        assert version.content == "Hello v2"

    def test_create_version(self, db_session):
        """Creating updated content appends an immutable version."""
        engine = VersioningEngine(db_session)
        engine.create_prompt(
            name="test-prompt",
            content="Hello v1",
            variables={"name": "string"},
            model_config={"provider": "ollama"},
        )

        version = engine.create_version(
            "test-prompt", "Hello v2", commit_message="Improve greeting"
        )

        assert version.version_number == 2
        assert version.content == "Hello v2"
        assert version.variables == {"name": "string"}
        assert version.model_config == {"provider": "ollama"}
        assert engine.get_version("test-prompt", 1).content == "Hello v1"

    def test_list_versions(self, db_session):
        """Test listing all versions of a prompt."""
        engine = VersioningEngine(db_session)
        engine.create_prompt(name="test-prompt", content="Hello v1")

        from db import crud

        prompt = crud.get_prompt(db_session, "test-prompt")
        crud.create_prompt_version(db_session, prompt.id, "Hello v2")
        crud.create_prompt_version(db_session, prompt.id, "Hello v3")

        versions = engine.list_versions("test-prompt")
        assert len(versions) == 3
        assert [v.version_number for v in versions] == [1, 2, 3]

    def test_list_prompts(self, db_session):
        """Test listing prompts."""
        engine = VersioningEngine(db_session)
        engine.create_prompt(name="prompt-1", content="Hello 1", tags=["tag1"])
        engine.create_prompt(name="prompt-2", content="Hello 2", tags=["tag2"])

        prompts = engine.list_prompts()
        assert len(prompts) == 2

    def test_list_prompts_with_tags(self, db_session):
        """Test listing prompts filtered by tags."""
        engine = VersioningEngine(db_session)
        engine.create_prompt(name="prompt-1", content="Hello 1", tags=["tag1"])
        engine.create_prompt(name="prompt-2", content="Hello 2", tags=["tag2"])

        prompts = engine.list_prompts(tags=["tag1"])
        assert len(prompts) == 1
        assert prompts[0].name == "prompt-1"

    def test_tag_filter_does_not_match_substrings(self, db_session):
        """Tag filtering uses exact tag membership."""
        engine = VersioningEngine(db_session)
        engine.create_prompt(name="exact", content="Hello", tags=["foo"])
        engine.create_prompt(name="substring", content="Hello", tags=["foobar"])

        assert [prompt.name for prompt in engine.list_prompts(tags=["foo"])] == ["exact"]

    def test_rollback(self, db_session):
        """Test rolling back to a previous version."""
        engine = VersioningEngine(db_session)
        engine.create_prompt(name="test-prompt", content="Hello v1")

        from db import crud

        prompt = crud.get_prompt(db_session, "test-prompt")
        crud.create_prompt_version(db_session, prompt.id, "Hello v2")
        crud.create_prompt_version(db_session, prompt.id, "Hello v3")

        rolled_back = engine.rollback("test-prompt", 1, "Rollback to v1")
        assert rolled_back.version_number == 4
        assert rolled_back.content == "Hello v1"
        assert rolled_back.commit_message == "Rollback to v1"

    def test_rollback_nonexistent_version(self, db_session):
        """Test rolling back to a nonexistent version."""
        engine = VersioningEngine(db_session)
        engine.create_prompt(name="test-prompt", content="Hello v1")

        with pytest.raises(ValueError, match="not found"):
            engine.rollback("test-prompt", 5)
