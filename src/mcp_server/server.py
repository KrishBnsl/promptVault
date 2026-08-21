"""MCP server implementation for PromptVault."""

import json
from inspect import Parameter, signature
from typing import Annotated, Any, cast

from mcp.server.mcpserver import MCPServer
from pydantic import Field

from core.diffing import compute_diff
from core.evaluation import EvaluationEngine
from core.versioning import VersioningEngine
from db import crud
from db.engine import SessionLocal, init_db


def _prompt_create_schema() -> dict:
    return {
        "type": "object",
        "properties": {
            "name": {"type": "string", "description": "Prompt name"},
            "content": {"type": "string", "description": "Prompt content"},
            "description": {"type": "string", "description": "Prompt description"},
            "variables": {"type": "object", "description": "Variables dict"},
            "model_config": {"type": "object", "description": "Model configuration"},
            "commit_message": {"type": "string", "description": "Commit message"},
            "tags": {"type": "array", "items": {"type": "string"}, "description": "Tags"},
        },
        "required": ["name", "content"],
    }


def create_mcp_server() -> MCPServer:
    """Create and configure the MCP server."""
    server = MCPServer(
        name="pvlt-mcp",
        instructions="PromptVault MCP server for prompt versioning, evaluation, and management.",
    )

    def aliased_tool(*, name: str, description: str):
        """Register a tool while hiding kwargs used for Pydantic field aliases."""
        def decorator(function):
            parameters = [
                parameter
                for parameter in signature(function).parameters.values()
                if parameter.kind is not Parameter.VAR_KEYWORD
            ]
            function.__signature__ = signature(function).replace(parameters=parameters)
            return server.tool(name=name, description=description)(function)

        return decorator

    @aliased_tool(name="prompt_create", description="Create a new prompt with initial version")
    async def prompt_create(
        name: str,
        content: str,
        description: str = "",
        variables: dict | None = None,
        llm_config: Annotated[dict | None, Field(alias="model_config")] = None,
        commit_message: str = "",
        tags: list[str] | None = None,
        **kwargs: Any,
    ) -> str:
        """Create a new prompt with initial version."""
        db = SessionLocal()
        try:
            engine = VersioningEngine(db)
            prompt, version = engine.create_prompt(
                name=name,
                content=content,
                description=description,
                variables=variables,
                model_config=cast(dict | None, kwargs.get("model_config", llm_config)),
                commit_message=commit_message,
                tags=tags,
            )
            return json.dumps({
                "prompt_id": prompt.id,
                "name": prompt.name,
                "version": version.version_number,
                "version_id": version.id,
            }, indent=2)
        except Exception as e:
            return json.dumps({"error": str(e)}, indent=2)
        finally:
            db.close()

    @aliased_tool(name="prompt_update", description="Create the next immutable version of a prompt")
    async def prompt_update(
        name: str,
        content: str,
        variables: dict | None = None,
        llm_config: Annotated[dict | None, Field(alias="model_config")] = None,
        commit_message: str = "",
        **kwargs: Any,
    ) -> str:
        """Create the next immutable version of an existing prompt."""
        db = SessionLocal()
        try:
            version = VersioningEngine(db).create_version(
                name=name,
                content=content,
                variables=variables,
                model_config=cast(dict | None, kwargs.get("model_config", llm_config)),
                commit_message=commit_message,
            )
            return json.dumps({
                "prompt_id": version.prompt_id,
                "name": name,
                "version": version.version_number,
                "version_id": version.id,
            }, indent=2)
        except Exception as exc:
            return json.dumps({"error": str(exc)}, indent=2)
        finally:
            db.close()

    @server.tool(name="prompt_get", description="Retrieve a specific version of a prompt")
    async def prompt_get(
        name: str,
        version: int | None = None,
    ) -> str:
        """Retrieve a specific version of a prompt."""
        db = SessionLocal()
        try:
            engine = VersioningEngine(db)
            pv = engine.get_version(name, version)
            if not pv:
                return json.dumps({"error": f"Prompt '{name}' not found"}, indent=2)
            return json.dumps({
                "prompt_id": pv.prompt_id,
                "name": name,
                "version": pv.version_number,
                "content": pv.content,
                "variables": pv.variables,
                "model_config": pv.model_config,
                "commit_message": pv.commit_message,
                "created_at": pv.created_at.isoformat() if pv.created_at else None,
            }, indent=2)
        finally:
            db.close()

    @server.tool(name="prompt_list", description="List all prompts")
    async def prompt_list(
        tags: list[str] | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> str:
        """List all prompts."""
        db = SessionLocal()
        try:
            engine = VersioningEngine(db)
            prompts = engine.list_prompts(tags=tags, limit=limit, offset=offset)
            result = [
                {
                    "id": p.id,
                    "name": p.name,
                    "description": p.description,
                    "tags": p.tags,
                    "created_at": p.created_at.isoformat() if p.created_at else None,
                }
                for p in prompts
            ]
            return json.dumps(result, indent=2)
        finally:
            db.close()

    @server.tool(name="prompt_versions", description="List all versions of a prompt")
    async def prompt_versions(name: str) -> str:
        """List all versions of a prompt."""
        db = SessionLocal()
        try:
            engine = VersioningEngine(db)
            versions = engine.list_versions(name)
            result = [
                {
                    "version": v.version_number,
                    "commit_message": v.commit_message,
                    "created_at": v.created_at.isoformat() if v.created_at else None,
                }
                for v in versions
            ]
            return json.dumps(result, indent=2)
        finally:
            db.close()

    @server.tool(name="prompt_diff", description="Show diff between two prompt versions")
    async def prompt_diff(
        name: str,
        version_a: int,
        version_b: int,
    ) -> str:
        """Show diff between two prompt versions."""
        db = SessionLocal()
        try:
            engine = VersioningEngine(db)
            ver_a = engine.get_version(name, version_a)
            ver_b = engine.get_version(name, version_b)
            if not ver_a or not ver_b:
                return json.dumps({"error": "One or both versions not found"}, indent=2)
            diff = compute_diff(
                ver_a.content,
                ver_b.content,
                from_file=f"{name}:v{version_a}",
                to_file=f"{name}:v{version_b}",
            )
            return json.dumps({"diff": diff}, indent=2)
        finally:
            db.close()

    @server.tool(name="prompt_rollback", description="Rollback to a previous prompt version")
    async def prompt_rollback(
        name: str,
        version: int,
        commit_message: str = "",
    ) -> str:
        """Rollback to a previous prompt version."""
        db = SessionLocal()
        try:
            engine = VersioningEngine(db)
            new_version = engine.rollback(name, version, commit_message)
            return json.dumps({
                "prompt_id": new_version.prompt_id,
                "name": name,
                "version": new_version.version_number,
                "rolled_back_to": version,
                "commit_message": new_version.commit_message,
            }, indent=2)
        except Exception as e:
            return json.dumps({"error": str(e)}, indent=2)
        finally:
            db.close()

    @server.tool(name="dataset_create", description="Create a new dataset from items")
    async def dataset_create(
        name: str,
        items: list[dict],
        description: str = "",
    ) -> str:
        """Create a new dataset from items."""
        db = SessionLocal()
        try:
            dataset = crud.create_dataset(db, name=name, description=description, items=items)
            return json.dumps({
                "dataset_id": dataset.id,
                "name": dataset.name,
                "items_count": len(dataset.items),
            }, indent=2)
        except Exception as e:
            return json.dumps({"error": str(e)}, indent=2)
        finally:
            db.close()

    @server.tool(name="dataset_list", description="List datasets")
    async def dataset_list(
        limit: int = 50,
        offset: int = 0,
    ) -> str:
        """List datasets."""
        db = SessionLocal()
        try:
            datasets = crud.list_datasets(db, limit=limit, offset=offset)
            result = [
                {
                    "id": d.id,
                    "name": d.name,
                    "description": d.description,
                    "items_count": len(d.items),
                    "created_at": d.created_at.isoformat() if d.created_at else None,
                }
                for d in datasets
            ]
            return json.dumps(result, indent=2)
        finally:
            db.close()

    @server.tool(name="dataset_get", description="Get a dataset with items")
    async def dataset_get(name: str) -> str:
        """Get a dataset with items."""
        db = SessionLocal()
        try:
            dataset = crud.get_dataset(db, name)
            if not dataset:
                return json.dumps({"error": f"Dataset '{name}' not found"}, indent=2)
            return json.dumps({
                "id": dataset.id,
                "name": dataset.name,
                "description": dataset.description,
                "items": [
                    {
                        "id": item.id,
                        "input": item.input,
                        "expected_output": item.expected_output,
                    }
                    for item in dataset.items
                ],
            }, indent=2)
        finally:
            db.close()

    @aliased_tool(name="evaluation_run", description="Run evaluation of a prompt version against a dataset")
    async def evaluation_run(
        prompt_name: str,
        dataset_name: str,
        version: int | None = None,
        llm_config: Annotated[dict | None, Field(alias="model_config")] = None,
        **kwargs: Any,
    ) -> str:
        """Run evaluation of a prompt version against a dataset."""
        db = SessionLocal()
        try:
            engine = EvaluationEngine(db)
            eval_id = engine.run_evaluation(
                prompt_name=prompt_name,
                dataset_name=dataset_name,
                version=version,
                model_config=cast(dict | None, kwargs.get("model_config", llm_config)),
            )
            status = engine.get_status(eval_id)
            return json.dumps(status, indent=2)
        except Exception as e:
            return json.dumps({"error": str(e)}, indent=2)
        finally:
            db.close()

    @server.tool(name="evaluation_status", description="Check status of an evaluation run")
    async def evaluation_status(evaluation_id: str) -> str:
        """Check status of an evaluation run."""
        db = SessionLocal()
        try:
            engine = EvaluationEngine(db)
            status = engine.get_status(evaluation_id)
            if not status:
                return json.dumps({"error": "Evaluation not found"}, indent=2)
            return json.dumps(status, indent=2)
        finally:
            db.close()

    @server.tool(name="evaluation_report", description="Get full evaluation report with results and metrics")
    async def evaluation_report(evaluation_id: str) -> str:
        """Get full evaluation report with results and metrics."""
        db = SessionLocal()
        try:
            engine = EvaluationEngine(db)
            report = engine.get_report(evaluation_id)
            if not report:
                return json.dumps({"error": "Evaluation not found"}, indent=2)
            return json.dumps(report, indent=2)
        finally:
            db.close()

    @server.tool(name="evaluation_compare", description="Compare two evaluation runs")
    async def evaluation_compare(
        evaluation_id_a: str,
        evaluation_id_b: str,
    ) -> str:
        """Compare two evaluation runs."""
        db = SessionLocal()
        try:
            engine = EvaluationEngine(db)
            comparison = engine.compare(evaluation_id_a, evaluation_id_b)
            if not comparison:
                return json.dumps({"error": "One or both evaluations not found"}, indent=2)
            return json.dumps(comparison, indent=2)
        finally:
            db.close()

    @server.resource(
        "prompt://{name}/latest",
        name="prompt_latest",
        description="Latest version of a prompt",
        mime_type="application/json",
    )
    async def prompt_latest_resource(name: str) -> str:
        db = SessionLocal()
        try:
            version = VersioningEngine(db).get_version(name)
            if not version:
                return json.dumps({"error": f"Prompt '{name}' not found"})
            return json.dumps({
                "name": name,
                "version": version.version_number,
                "content": version.content,
                "variables": version.variables,
                "model_config": version.model_config,
            }, indent=2)
        finally:
            db.close()

    @server.resource(
        "prompt://{name}/version/{version}",
        name="prompt_version",
        description="Specific version of a prompt",
        mime_type="application/json",
    )
    async def prompt_version_resource(name: str, version: int) -> str:
        db = SessionLocal()
        try:
            prompt_version = VersioningEngine(db).get_version(name, version)
            if not prompt_version:
                return json.dumps({"error": f"Prompt '{name}' version {version} not found"})
            return json.dumps({
                "name": name,
                "version": prompt_version.version_number,
                "content": prompt_version.content,
                "variables": prompt_version.variables,
                "model_config": prompt_version.model_config,
            }, indent=2)
        finally:
            db.close()

    @server.resource(
        "dataset://{dataset_name}",
        name="dataset",
        description="Dataset with all items",
        mime_type="application/json",
    )
    async def dataset_resource(dataset_name: str) -> str:
        db = SessionLocal()
        try:
            dataset = crud.get_dataset(db, dataset_name)
            if not dataset:
                return json.dumps({"error": f"Dataset '{dataset_name}' not found"})
            return json.dumps({
                "name": dataset.name,
                "description": dataset.description,
                "items": [
                    {
                        "id": item.id,
                        "input": item.input,
                        "expected_output": item.expected_output,
                    }
                    for item in dataset.items
                ],
            }, indent=2)
        finally:
            db.close()

    @server.resource(
        "evaluation://{evaluation_id}/report",
        name="evaluation_report",
        description="Full evaluation report",
        mime_type="application/json",
    )
    async def evaluation_report_resource(evaluation_id: str) -> str:
        db = SessionLocal()
        try:
            report = EvaluationEngine(db).get_report(evaluation_id)
            return json.dumps(report or {"error": "Evaluation not found"}, indent=2)
        finally:
            db.close()

    return server


def run_server() -> None:
    """Run the MCP server over stdio."""
    init_db()
    create_mcp_server().run(transport="stdio")


def run_server_sync() -> None:
    """Synchronous entry point for the MCP server."""
    run_server()


if __name__ == "__main__":
    run_server_sync()
