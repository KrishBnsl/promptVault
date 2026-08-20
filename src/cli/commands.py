"""Typer CLI commands for PromptVault."""

import json
from pathlib import Path

import typer
from sqlalchemy.orm import Session

from config import settings
from core.diffing import compute_diff
from core.evaluation import EvaluationEngine
from core.versioning import VersioningEngine
from db import crud
from db.engine import SessionLocal, init_db

app = typer.Typer(name="promptctl", help="PromptVault CLI - Prompt versioning and evaluation")
prompt_app = typer.Typer(help="Prompt management commands")
dataset_app = typer.Typer(help="Dataset management commands")
eval_app = typer.Typer(help="Evaluation commands")

app.add_typer(prompt_app, name="prompt")
app.add_typer(dataset_app, name="dataset")
app.add_typer(eval_app, name="eval")


def get_db() -> Session:
    """Get a database session and ensure tables exist."""
    init_db()
    return SessionLocal()


@app.callback()
def main(
    db_path: str = typer.Option(
        None, "--db-path", envvar="PROMPTVAULT_DB_PATH", help="SQLite database path"
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """PromptVault CLI - Prompt versioning and evaluation."""
    if db_path:
        settings.db_path = db_path


# --- Prompt Commands ---


@prompt_app.command("create")
def prompt_create(
    name: str = typer.Argument(help="Prompt name"),
    content: str = typer.Option(..., "--content", "-c", help="Prompt content or @file"),
    description: str = typer.Option("", "--description", "-d", help="Description"),
    variables: str = typer.Option(None, "--variables", help="JSON variables dict"),
    model_config: str = typer.Option(None, "--model-config", help="JSON model config"),
    commit_message: str = typer.Option("", "--commit-message", "-m", help="Commit message"),
    tags: str = typer.Option(None, "--tags", help="Comma-separated tags"),
):
    """Create a new prompt with initial version."""
    db = get_db()
    try:
        if content.startswith("@"):
            content = Path(content[1:]).read_text()

        variables_dict = json.loads(variables) if variables else {}
        model_config_dict = json.loads(model_config) if model_config else {}
        tags_list = [t.strip() for t in tags.split(",")] if tags else []

        engine = VersioningEngine(db)
        prompt, version = engine.create_prompt(
            name=name,
            content=content,
            description=description,
            variables=variables_dict,
            model_config=model_config_dict,
            commit_message=commit_message,
            tags=tags_list,
        )

        result = {
            "prompt_id": prompt.id,
            "name": prompt.name,
            "version": version.version_number,
            "version_id": version.id,
        }
        typer.echo(json.dumps(result, indent=2))

    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)
    finally:
        db.close()


@prompt_app.command("list")
def prompt_list(
    tags: str = typer.Option(None, "--tags", help="Filter by comma-separated tags"),
    limit: int = typer.Option(50, "--limit", "-l", help="Max results"),
    offset: int = typer.Option(0, "--offset", "-o", help="Offset"),
    output_json: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """List all prompts."""
    db = get_db()
    try:
        tags_list = [t.strip() for t in tags.split(",")] if tags else None
        engine = VersioningEngine(db)
        prompts = engine.list_prompts(tags=tags_list, limit=limit, offset=offset)

        if output_json:
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
            typer.echo(json.dumps(result, indent=2))
        else:
            if not prompts:
                typer.echo("No prompts found.")
                return
            typer.echo(f"{'Name':<30} {'Description':<40} {'Tags'}")
            typer.echo("-" * 90)
            for p in prompts:
                tags_str = ", ".join(p.tags) if p.tags else ""
                typer.echo(f"{p.name:<30} {(p.description or '')[:40]:<40} {tags_str}")

    finally:
        db.close()


@prompt_app.command("show")
def prompt_show(
    name: str = typer.Argument(help="Prompt name"),
    version: int = typer.Option(None, "--version", "-v", help="Version number"),
    output_json: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Show prompt content and metadata."""
    db = get_db()
    try:
        engine = VersioningEngine(db)
        prompt_version = engine.get_version(name, version)

        if not prompt_version:
            typer.echo(f"Prompt '{name}' or version not found.", err=True)
            raise typer.Exit(1)

        if output_json:
            result = {
                "prompt_id": prompt_version.prompt_id,
                "version": prompt_version.version_number,
                "content": prompt_version.content,
                "variables": prompt_version.variables,
                "model_config": prompt_version.model_config,
                "commit_message": prompt_version.commit_message,
                "created_at": prompt_version.created_at.isoformat()
                if prompt_version.created_at
                else None,
            }
            typer.echo(json.dumps(result, indent=2))
        else:
            typer.echo(f"Prompt: {name} (v{prompt_version.version_number})")
            typer.echo(f"Commit: {prompt_version.commit_message}")
            typer.echo(f"Created: {prompt_version.created_at}")
            typer.echo("---")
            typer.echo(prompt_version.content)

    finally:
        db.close()


@prompt_app.command("versions")
def prompt_versions(
    name: str = typer.Argument(help="Prompt name"),
    output_json: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """List all versions of a prompt."""
    db = get_db()
    try:
        engine = VersioningEngine(db)
        versions = engine.list_versions(name)

        if not versions:
            typer.echo(f"No versions found for prompt '{name}'.")
            return

        if output_json:
            result = [
                {
                    "version": v.version_number,
                    "commit_message": v.commit_message,
                    "created_at": v.created_at.isoformat() if v.created_at else None,
                }
                for v in versions
            ]
            typer.echo(json.dumps(result, indent=2))
        else:
            typer.echo(f"Versions for '{name}':")
            typer.echo(f"{'Version':<10} {'Commit Message':<40} {'Created'}")
            typer.echo("-" * 70)
            for v in versions:
                typer.echo(
                    f"{v.version_number:<10} {(v.commit_message or '')[:40]:<40} {v.created_at}"
                )

    finally:
        db.close()


@prompt_app.command("diff")
def prompt_diff(
    name: str = typer.Argument(help="Prompt name"),
    version_a: int = typer.Argument(help="First version number"),
    version_b: int = typer.Argument(help="Second version number"),
):
    """Show diff between two prompt versions."""
    db = get_db()
    try:
        engine = VersioningEngine(db)
        ver_a = engine.get_version(name, version_a)
        ver_b = engine.get_version(name, version_b)

        if not ver_a or not ver_b:
            typer.echo("One or both versions not found.", err=True)
            raise typer.Exit(1)

        diff = compute_diff(
            ver_a.content,
            ver_b.content,
            from_file=f"{name}:v{version_a}",
            to_file=f"{name}:v{version_b}",
        )

        if diff:
            typer.echo(diff)
        else:
            typer.echo("No differences found.")

    finally:
        db.close()


@prompt_app.command("rollback")
def prompt_rollback(
    name: str = typer.Argument(help="Prompt name"),
    version: int = typer.Option(..., "--version", "-v", help="Target version"),
    commit_message: str = typer.Option("", "--commit-message", "-m", help="Commit message"),
):
    """Rollback to a previous prompt version."""
    db = get_db()
    try:
        engine = VersioningEngine(db)
        new_version = engine.rollback(name, version, commit_message)

        result = {
            "prompt_id": new_version.prompt_id,
            "name": name,
            "version": new_version.version_number,
            "rolled_back_to": version,
            "commit_message": new_version.commit_message,
        }
        typer.echo(json.dumps(result, indent=2))

    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)
    finally:
        db.close()


# --- Dataset Commands ---


@dataset_app.command("create")
def dataset_create(
    name: str = typer.Argument(help="Dataset name"),
    file: str = typer.Option(..., "--file", "-f", help="JSONL or JSON file path"),
    description: str = typer.Option("", "--description", "-d", help="Description"),
):
    """Create a new dataset from JSONL or JSON file."""
    db = get_db()
    try:
        file_path = Path(file)
        if not file_path.exists():
            typer.echo(f"File not found: {file}", err=True)
            raise typer.Exit(1)

        content = file_path.read_text()
        if file_path.suffix == ".jsonl":
            items = [json.loads(line) for line in content.strip().split("\n") if line.strip()]
        else:
            items = json.loads(content)

        dataset = crud.create_dataset(db, name=name, description=description, items=items)

        result = {
            "dataset_id": dataset.id,
            "name": dataset.name,
            "items_count": len(dataset.items),
        }
        typer.echo(json.dumps(result, indent=2))

    except json.JSONDecodeError as e:
        typer.echo(f"Invalid JSON: {e}", err=True)
        raise typer.Exit(1)
    finally:
        db.close()


@dataset_app.command("list")
def dataset_list(
    limit: int = typer.Option(50, "--limit", "-l", help="Max results"),
    offset: int = typer.Option(0, "--offset", "-o", help="Offset"),
    output_json: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """List all datasets."""
    db = get_db()
    try:
        datasets = crud.list_datasets(db, limit=limit, offset=offset)

        if output_json:
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
            typer.echo(json.dumps(result, indent=2))
        else:
            if not datasets:
                typer.echo("No datasets found.")
                return
            typer.echo(f"{'Name':<30} {'Description':<40} {'Items'}")
            typer.echo("-" * 80)
            for d in datasets:
                typer.echo(f"{d.name:<30} {(d.description or '')[:40]:<40} {len(d.items)}")

    finally:
        db.close()


# --- Evaluation Commands ---


@eval_app.command("run")
def eval_run(
    prompt_name: str = typer.Argument(help="Prompt name"),
    version: int = typer.Option(None, "--version", "-v", help="Prompt version"),
    dataset: str = typer.Option(..., "--dataset", "-d", help="Dataset name"),
    model_config: str = typer.Option(None, "--model-config", help="JSON model config"),
):
    """Run evaluation of a prompt version against a dataset."""
    db = get_db()
    try:
        model_config_dict = json.loads(model_config) if model_config else None

        engine = EvaluationEngine(db)
        eval_id = engine.run_evaluation(
            prompt_name=prompt_name,
            dataset_name=dataset,
            version=version,
            model_config=model_config_dict,
        )

        result = {"evaluation_id": eval_id, "status": "completed"}
        typer.echo(json.dumps(result, indent=2))

    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)
    finally:
        db.close()


@eval_app.command("report")
def eval_report(
    evaluation_id: str = typer.Argument(help="Evaluation ID"),
    output_format: str = typer.Option("json", "--format", "-f", help="Output format: json or table"),
):
    """Get evaluation report."""
    db = get_db()
    try:
        engine = EvaluationEngine(db)
        report = engine.get_report(evaluation_id)

        if not report:
            typer.echo(f"Evaluation '{evaluation_id}' not found.", err=True)
            raise typer.Exit(1)

        if output_format == "table":
            typer.echo(f"Evaluation: {report['evaluation_id']}")
            typer.echo(f"Status: {report['status']}")
            typer.echo("\nMetrics:")
            for key, value in report["metrics"].items():
                typer.echo(f"  {key}: {value}")
            typer.echo(f"\nResults ({len(report['results'])} items):")
            for i, r in enumerate(report["results"], 1):
                typer.echo(f"\n  Item {i}:")
                typer.echo(f"    Output: {(r['actual_output'] or '')[:100]}...")
                typer.echo(f"    Scores: {r['scores']}")
                if r.get("error"):
                    typer.echo(f"    Error: {r['error']}")
        else:
            typer.echo(json.dumps(report, indent=2))

    finally:
        db.close()


@app.command("serve")
def serve(
    stdio: bool = typer.Option(True, "--stdio", help="Run MCP server over stdio"),
    http: bool = typer.Option(False, "--http", help="Run REST API over HTTP"),
    port: int = typer.Option(8000, "--port", "-p", help="HTTP port"),
):
    """Start the MCP server or REST API."""
    init_db()
    if http:
        import uvicorn

        from api.main import create_app

        api_app = create_app()
        uvicorn.run(api_app, host="127.0.0.1", port=port)
    else:
        from mcp_server.server import run_server

        run_server()


@app.command("web")
def web(
    port: int = typer.Option(8080, "--port", "-p", help="Web UI port"),
):
    """Start the optional web UI."""
    typer.echo(f"Web UI would start on port {port} (not yet implemented)")


if __name__ == "__main__":
    app()
