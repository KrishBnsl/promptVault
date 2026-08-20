"""Tests for the REST API."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from promptvault.api.main import create_app
from promptvault.db.engine import Base, get_db


@pytest.fixture
def client():
    """Create a test client with an in-memory database."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    test_session = sessionmaker(bind=engine)

    def override_get_db():
        db = test_session()
        try:
            yield db
        finally:
            db.close()

    app = create_app()
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c


class TestPromptAPI:
    """Tests for prompt API endpoints."""

    def test_create_prompt(self, client):
        """Test creating a prompt."""
        response = client.post(
            "/api/prompts",
            json={
                "name": "test-prompt",
                "content": "Hello {name}",
                "description": "A test prompt",
                "variables": {"name": "string"},
                "tags": ["test"],
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "test-prompt"

    def test_list_prompts(self, client):
        """Test listing prompts."""
        client.post(
            "/api/prompts",
            json={"name": "test-prompt", "content": "Hello"},
        )
        response = client.get("/api/prompts")
        assert response.status_code == 200
        assert len(response.json()) >= 1

    def test_get_prompt(self, client):
        """Test getting a prompt."""
        client.post(
            "/api/prompts",
            json={"name": "test-prompt", "content": "Hello"},
        )
        response = client.get("/api/prompts/test-prompt")
        assert response.status_code == 200
        assert response.json()["name"] == "test-prompt"

    def test_get_prompt_not_found(self, client):
        """Test getting a nonexistent prompt."""
        response = client.get("/api/prompts/nonexistent")
        assert response.status_code == 404

    def test_list_versions(self, client):
        """Test listing versions."""
        client.post(
            "/api/prompts",
            json={"name": "test-prompt", "content": "Hello v1"},
        )
        response = client.get("/api/prompts/test-prompt/versions")
        assert response.status_code == 200
        assert len(response.json()) == 1


class TestDatasetAPI:
    """Tests for dataset API endpoints."""

    def test_create_dataset(self, client):
        """Test creating a dataset."""
        response = client.post(
            "/api/datasets",
            json={
                "name": "test-dataset",
                "description": "A test dataset",
                "items": [{"input": {"x": 1}, "expected_output": "yes"}],
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "test-dataset"
        assert data["items_count"] == 1

    def test_list_datasets(self, client):
        """Test listing datasets."""
        client.post(
            "/api/datasets",
            json={"name": "test-dataset", "items": []},
        )
        response = client.get("/api/datasets")
        assert response.status_code == 200
        assert len(response.json()) >= 1

    def test_get_dataset(self, client):
        """Test getting a dataset."""
        client.post(
            "/api/datasets",
            json={"name": "test-dataset", "items": [{"input": {}, "expected_output": "yes"}]},
        )
        response = client.get("/api/datasets/test-dataset")
        assert response.status_code == 200
        assert response.json()["name"] == "test-dataset"
